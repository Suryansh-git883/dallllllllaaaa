# Loading a batch's content (sections → lessons)

All endpoints on this page require `Authorization: Bearer <token>` for an account enrolled in
`{courseId}`.

## 1. All sections with their lessons — one call

```http
GET /v2/learn/section/getAllSections/{courseId}
GET /v2/learn/section/getAllSections/{courseId}?milestoneId={milestoneId}
```

This is the single call the lecture page sidebar makes; it returns the whole curriculum tree
(sections, each with its lesson list). Frontend signature:

```ts
LectureTrackApi.getSectionsWithLessons({ courseId, milestoneId });
```

For career-path programs, `milestoneId` selects the year/milestone; omit it for regular batches.

Section-scoped variant (used to lazily reload one section with filters):

```http
GET /v2/learn/section/{courseId}/{sectionId}
      ?milestoneId={milestoneId}
      &lessonType={video|quiz|assignment|notes|test|…}
      &lectureMode={recorded|live|session}
      &isMandatory={true|false}
```

## 2. Lesson object

Lesson entries in the section tree, and the full lesson returned by the detail call, share this
shape (from the app's own TypeScript types):

```ts
interface ILesson {
  _id: string;
  title: string;
  description: string;
  courseId: string;
  milestoneId: string;
  batchId?: string;
  type: LessonTypes;          // see below
  lectureMode: 'recorded' | 'live' | 'session';
  status: 'locked' | 'unlocked' | 'showLocked';
  isCompleted: boolean;
  isMandatory: boolean;       // must be watched fully to complete
  startDate: string;
  endDate: string;
  mentors: string[];
  overview: string;
  attachment: string[];
  resources: { title: string; url: string }[];
  data: {                     // playback / payload block
    provider: string;
    url: string;
    thumbnail: string;
    duration: number;
    resourceURL: string;
    maxPoints: number;
  };
  mcqDetail: IMcqDetails;     // quizzes/tests only
}
```

`LessonTypes`:

| value | meaning |
| --- | --- |
| `video` | recorded or live class |
| `notes` | HTML notes (rendered, exportable to PDF) |
| `sectionResource` | downloadable resource |
| `assignment`, `assignment_v2` | file-upload assignment |
| `quiz`, `quiz_v2`, `test` | MCQ assessments |
| `coding_quiz`, `coding_assessment`, `project`, `project_labs` | coding/compiler-backed work |
| `partner_exam` | proctored partner exam |

`status: locked` / `showLocked` lessons are returned as metadata only — the detail call will not
hand out playback data for them.

## 3. Lesson detail (includes video metadata)

```http
GET /v2/learn/lesson/details/{courseId}/{lessonId}
GET /v2/learn/lesson/details/{courseId}/{lessonId}?milestoneId={milestoneId}
```

Response:

```json
{
  "data": {
    "lesson": { "…ILesson…", "data": { "provider": "…", "url": "…", "centralVideoUrl": "…", "drmVendor": "…" } },
    "vdocipherData": { "otp": "…", "playbackInfo": "…" },
    "mentorsName": ["…"]
  },
  "time_now": "…",
  "status_code": 200
}
```

The app merges `vdocipherData` into `lesson.data` before handing it to the player, which is why
the player consumes a single flat object:

```ts
const { centralVideoUrl, url, otp, playbackInfo, provider, drmVendor } = lectureDetails.data;
```

See [video-playback.md](video-playback.md) for what to do with each of those fields.

Older/alternative lesson endpoint (used by assignment and career-path screens):

```http
GET /{prefix}/learn/lesson/course/{courseId}/{lessonId}[?milestoneId={milestoneId}]
```

## 4. Other lesson-type endpoints

```http
GET  /v2/learn/lesson/zoom/{courseId}/{lessonId}                     # live Zoom join details
POST /v2/learn/lesson/mettl/{courseId}/{sectionId}/{lessonId}        # start partner exam
GET  /v2/learn/lesson/mettl-result/{courseId}/{lessonId}
POST /{prefix}/learn/submission/{courseId}/quiz/{lessonId}
POST /{prefix}/learn/submission/{courseId}/assignment/{lessonId}
POST /v2/assignment/{courseId}/{sectionId}/{lessonId}[?milestoneId=…]  # multipart upload
```

Notes:

```http
GET    /v2/learn/lesson/notes/{courseId}/?order=-1&limit=10&skip=0[&lessonId=…][&milestoneId=…]
POST   /v2/learn/lesson/notes/{courseId}/{lessonId}     # {description, timestamp, milestoneId?}
DELETE /v2/learn/lesson/notes/{courseId}/{lessonId}/{noteId}
```

Doubts:

```http
GET    /v2/learn/doubt/{courseId}/{lessonId}?limit=10&skip=0&order=1&sort={sort}
GET    /v2/learn/doubt/{courseId}/{lessonId}/{doubtId}/replies?limit=10&skip=0
POST   /v2/learn/doubt/{courseId}/{lessonId}
DELETE /v2/learn/doubt/{courseId}/{lessonId}/{doubtId}
PATCH  /v2/learn/doubt/{courseId}/{lessonId}/{doubtId}/like-action
PATCH  /v2/learn/doubt/{courseId}/{lessonId}/{doubtId}/lesson-doubt-status
POST   /v2/learn/doubt/{courseId}/{lessonId}/{doubtId}/report-doubt
```

Feedback:

```http
GET/POST /v2/learn/lesson/feedback/{courseId}/lesson/{lessonId}
POST     /v2/learn/lesson/feedback/rating/{courseId}/lesson/{lessonId}
POST     /v2/learn/lesson/feedback/comment/{courseId}/lesson/{lessonId}
GET      /v2/learn/lesson/feedback/status/{courseId}/lesson/{lessonId}
GET      /v2/learn/lesson/feedback/{courseId}/lesson/{lessonId}/comment-thread
DELETE   /v2/learn/lesson/feedback/{courseId}/lesson/{lessonId}/{commentId}
```

## 5. Progress and watch tracking

```http
GET   /v2/learn/progress/{courseId}
PATCH /v2/learn/progress/{courseId}
```

```json
{
  "watchPercentage": 42,
  "lessonId": "<lessonId>",
  "sectionId": "<sectionId>",
  "milestoneId": "<milestoneId>"
}
```

```http
GET   /v2/learn/progress/milestone-progress/{courseId}/{milestoneId}
PATCH /v2/learn/progress/{courseId}/recently-accessed-lessons   # {lessonId, milestoneId}
GET   /{prefix}/learn/analytics/lastPlayed/course/{courseId}
PATCH /{prefix}/learn/analytics/lastPlayed/course/{courseId}     # {lessonId}
```

Per-video watch sessions (drives resume position and "mandatory watched" completion):

```http
GET   /{prefix}/learn/lesson/video-session/{courseId}/lesson/{lessonId}
PATCH /{prefix}/learn/lesson/video-session/{courseId}/lesson/{lessonId}
```

The PATCH body is a session object with watch intervals:

```json
{
  "lessonId": "<lessonId>",
  "sectionId": "<sectionId>",
  "lastWatchedInSeconds": 512,
  "videoLengthInSeconds": 3600,
  "totalWatchMs": 480,
  "session": {
    "watchStats": [
      { "startTime": 0, "endTime": 512, "startTimeStamp": 1750000000000, "endTimeStamp": 1750000480000 }
    ]
  }
}
```

`startTime`/`endTime` are positions in the video (seconds); `*TimeStamp` are wall-clock epoch
milliseconds. `GET` returns `lastWatchedInSeconds`, which the player seeks to on load.

## 6. Traversal recipe

```text
GET /v2/enrol/list                                  → courseIds you own
GET /v2/course/{courseId}                           → batch metadata
GET /v2/learn/section/getAllSections/{courseId}     → sections[] with lessons[]
for each lesson where status == 'unlocked':
    GET /v2/learn/lesson/details/{courseId}/{lessonId}
        → lesson.data.provider decides how to play (video-playback.md)
while playing:
    PATCH /{prefix}/learn/lesson/video-session/{courseId}/lesson/{lessonId}
    PATCH /v2/learn/progress/{courseId}
```
