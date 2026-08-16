# Video links and playback

## Where the video metadata comes from

There is no "give me the mp4 link" endpoint. The only source of playback data is the
authenticated lesson-detail call for a lesson you are enrolled in and that is unlocked:

```http
GET /v2/learn/lesson/details/{courseId}/{lessonId}[?milestoneId={milestoneId}]
authorization: Bearer <token>
organizationid: 5eb393ee95fab7468a79d189
```

The relevant fields, after the app merges `data.vdocipherData` into `data.lesson.data`:

| Field | Meaning |
| --- | --- |
| `provider` | which player to use: `central`, `vdocipher`, `vimeo`, `zoom`, `powerbatch`, or another/absent value |
| `centralVideoUrl` | video identifier/URL for the first-party ("central") DRM player |
| `url` | direct or embeddable URL (Vimeo embed, HLS `.m3u8`, DASH `.mpd`, MP4, YouTube, live URL) |
| `otp`, `playbackInfo` | short-lived VdoCipher credentials, from `vdocipherData` |
| `drmVendor` | DRM system to request (`widevine` / `fairplay` / `playready`) |
| `duration`, `thumbnail` | display metadata |
| `lectureMode` | `recorded` / `live` / `session` |

These values are per-request and entitlement-bound: they expire, they are tied to the calling
session, and they are not usable as permanent shareable links. Treat them as ephemeral input to
a player, not as assets to download or redistribute.

## Provider dispatch

The lesson page picks a player exactly like this (`components/LectureTrack/VideoPlayer/Container.tsx`):

```ts
const PROVIDER = {
  CENTRAL: 'central',
  VDOCIPHER: 'vdocipher',
  ZOOM: 'zoom',
  POWERBATCH: 'powerbatch',
  VIMEO: 'vimeo',
};

if (otp && playbackInfo && provider === PROVIDER.VDOCIPHER)  → VdoCipher player
else if (provider === PROVIDER.CENTRAL)                      → first-party DRM player (PENPENCILVDO)
else if (provider === PROVIDER.VIMEO && url)                 → <iframe src={url}>
else                                                          → generic ReactPlayer with url
```

Live lessons (`lectureMode === 'live'`, providers `zoom` / `powerbatch`) render a live container
instead; Zoom join details come from `GET /v2/learn/lesson/zoom/{courseId}/{lessonId}`.

### 1. `vdocipher`

Hand `otp` + `playbackInfo` to VdoCipher's own embed — that is the documented, supported path:

```html
<iframe
  src="https://player.vdocipher.com/v2/?otp=OTP&playbackInfo=PLAYBACK_INFO"
  allow="encrypted-media; fullscreen; autoplay"
  allowfullscreen>
</iframe>
```

Both values are single-use/short-lived; re-fetch lesson details to get fresh ones.

### 2. `central` (first-party player)

`centralVideoUrl` is played by PW's own player through a protected iframe. The app normalises the
URL by inserting a `/drm/` path segment when absent:

```ts
const modifyUrl = (inputUrl: string) => {
  if (inputUrl.includes('/drm/')) return inputUrl;
  const parts = inputUrl.split('/');
  parts.splice(3, 0, 'drm');
  return parts.join('/');
};
```

and renders the player iframe with the lesson context:

```ts
<iframe
  id="pw-video-player"
  src={`${watchBase}/watch/?type=PENPENCILVDO&src=${src}&drmVendor=${drmVendor}`
     + `&typeId=${lessonId}&entityId=${courseId}&childId=${courseId}&secondaryChildId=${lessonId}`
     + `&vType=SKILLS&playingSource=SKILLS&entryPoint=${entryPoint}`
     + `&disableSeek=${disableSeek}&isComplete=${isComplete}&trim_start=${trimStart}`
     + `&video_id=${videoDetails.id}&video_details=${base64EncodedLessonDetails}&random_id=${randomId}`}
  allow="accelerometer; autoplay; fullscreen; encrypted-media; gyroscope; picture-in-picture"
/>
```

The page talks to it over `postMessage`:

```ts
document.getElementById('pw-video-player').contentWindow.postMessage(data, '*');
```

Commands/events carried this way cover play/pause, seek, playback speed, quality, fullscreen and
periodic watch-progress reporting, which the page then persists via the video-session endpoint.

This stream is DRM-protected (`drmVendor`). Playing it requires a DRM-capable player with a
valid license from PW's license server, i.e. the first-party player in a logged-in session.
Nothing here defeats that, and this document deliberately does not describe how to obtain
license keys or decrypt segments.

### 3. `vimeo`

`url` is an embeddable Vimeo URL:

```html
<iframe src="URL" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>
```

### 4. Anything else

`url` goes straight into a generic player (the app uses ReactPlayer), which handles HLS
(`.m3u8`), DASH (`.mpd`), progressive MP4 and YouTube links. Equivalent minimal setup:

```html
<video id="v" controls></video>
<script src="https://cdn.jsdelivr.net/npm/hls.js@1/dist/hls.min.js"></script>
<script>
  const url = 'URL_FROM_LESSON_DETAILS';
  const v = document.getElementById('v');
  if (url.includes('.m3u8') && Hls.isSupported()) { const h = new Hls(); h.loadSource(url); h.attachMedia(v); }
  else { v.src = url; }
</script>
```

Requests for the media segments may still require the same session headers/cookies as the
originating API call.

### 5. Live classes

For `lectureMode === 'live'`:

* `powerbatch` – join via the live URL in `data.url` / `liveVideoLink`.
* `zoom` – call `GET /v2/learn/lesson/zoom/{courseId}/{lessonId}` and use the returned join
  details. The site's own page for this is `/learn/course/{courseName}/{courseId}/zoom/`.

Upcoming live items also appear in `GET /v2/user/live-events` and
`GET /v2/user/upcoming-events` (each entry carries `courseId`, `lessonId`, `sectionId`,
`startTime`, `liveVideoLink`).

## Reporting playback progress

While playing, mirror what the app does so progress and completion work:

```http
PATCH /{prefix}/learn/lesson/video-session/{courseId}/lesson/{lessonId}
PATCH /v2/learn/progress/{courseId}
PATCH /v2/learn/progress/{courseId}/recently-accessed-lessons
PATCH /{prefix}/learn/analytics/lastPlayed/course/{courseId}
```

Payloads are in [batch-content.md § 5](batch-content.md#5-progress-and-watch-tracking). Mandatory
lessons only flip to `isCompleted` when the reported watch coverage approaches the full duration,
and the player disables seeking (`disableSeek`) for those lessons.

## Don'ts

* Don't request playback metadata for accounts/batches you are not entitled to.
* Don't cache, share, or publish `otp`, `playbackInfo`, `centralVideoUrl`, or signed media URLs.
* Don't strip or work around DRM, and don't fake watch statistics.
