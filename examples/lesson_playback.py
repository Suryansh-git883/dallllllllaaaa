"""Fetch a lesson's playback metadata and report how it should be played.

Usage:
    PWSKILLS_TOKEN='…' python3 examples/lesson_playback.py <courseId> <lessonId> [milestoneId]

Only works for a lesson in a batch the token's account is enrolled in. Secrets in the
response (VdoCipher otp/playbackInfo, video URLs) are short-lived and printed truncated on
purpose: hand them to the matching player, do not store or share them.
"""

from __future__ import annotations

import sys

import pwskills

PROVIDER_VDOCIPHER = 'vdocipher'
PROVIDER_CENTRAL = 'central'
PROVIDER_VIMEO = 'vimeo'
LIVE_PROVIDERS = ('zoom', 'powerbatch')


def mask(value: str | None, keep: int = 8) -> str:
    if not value:
        return '<absent>'
    return f'{value[:keep]}…({len(value)} chars)'


def describe(lesson: dict) -> None:
    data = lesson.get('data') or {}
    provider = (data.get('provider') or '').lower()
    print(f'title       : {lesson.get("title")}')
    print(f'type        : {lesson.get("type")}  lectureMode={lesson.get("lectureMode")}')
    print(f'status      : {lesson.get("status")}  isCompleted={lesson.get("isCompleted")}')
    print(f'provider    : {provider or "<none>"}  drmVendor={data.get("drmVendor")}')
    print(f'duration    : {data.get("duration")}')
    print(f'url         : {mask(data.get("url"), 40)}')
    print(f'centralVideo: {mask(data.get("centralVideoUrl"), 24)}')
    print(f'otp         : {mask(data.get("otp"))}')
    print(f'playbackInfo: {mask(data.get("playbackInfo"))}')

    print('\nhow to play:')
    if data.get('otp') and data.get('playbackInfo') and provider == PROVIDER_VDOCIPHER:
        print('  VdoCipher embed:')
        print('  <iframe src="https://player.vdocipher.com/v2/'
              '?otp=<otp>&playbackInfo=<playbackInfo>" allow="encrypted-media" allowfullscreen>')
    elif provider == PROVIDER_CENTRAL:
        print('  First-party DRM player (type=PENPENCILVDO). centralVideoUrl is DRM-protected')
        print(f'  ({data.get("drmVendor") or "widevine/fairplay"}); it plays inside the PW')
        print('  /watch/ iframe in a logged-in session. See docs/video-playback.md.')
    elif provider == PROVIDER_VIMEO and data.get('url'):
        print('  Vimeo iframe: <iframe src="<url>" allowfullscreen>')
    elif provider in LIVE_PROVIDERS or lesson.get('lectureMode') == 'live':
        print('  Live class: use data.url / liveVideoLink, or')
        print('  GET /v2/learn/lesson/zoom/{courseId}/{lessonId} for Zoom join details.')
    elif data.get('url'):
        print('  Generic player: pass url to any HLS/DASH/MP4-capable player (hls.js, ffplay, …).')
    else:
        print('  No playback payload returned (locked, non-video, or not yet published).')


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    course_id, lesson_id = sys.argv[1], sys.argv[2]
    milestone_id = sys.argv[3] if len(sys.argv) > 3 else None

    try:
        payload = pwskills.lesson_details(course_id, lesson_id, milestone_id)
    except pwskills.ApiError as exc:
        sys.exit(f'lesson details failed: {exc}')

    data = payload.get('data') or {}
    lesson = data.get('lesson') or {}
    vdocipher = data.get('vdocipherData') or {}
    if vdocipher:
        lesson.setdefault('data', {}).update(vdocipher)

    print(f'server time : {payload.get("time_now")}')
    print(f'mentors     : {", ".join(data.get("mentorsName") or []) or "-"}')
    describe(lesson)

    try:
        session = pwskills.video_session(course_id, lesson_id).get('data') or {}
        print(f'\nresume at   : {session.get("lastWatchedInSeconds")}s '
              f'of {session.get("videoLengthInSeconds")}s')
    except pwskills.ApiError as exc:
        print(f'\nvideo session unavailable: {exc}')


if __name__ == '__main__':
    main()
