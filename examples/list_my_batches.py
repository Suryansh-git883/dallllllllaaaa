"""List the batches (courses) the authenticated user is enrolled in.

Usage:
    PWSKILLS_TOKEN='<your session token>' python3 examples/list_my_batches.py
"""

from __future__ import annotations

import os
import sys

import pwskills


def main() -> None:
    if not os.environ.get('PWSKILLS_TOKEN'):
        sys.exit('Set PWSKILLS_TOKEN to your own logged-in session token.')

    try:
        enrolments = pwskills.enrollments().get('data') or []
    except pwskills.ApiError as exc:
        sys.exit(f'/v2/enrol/list failed: {exc}')

    print(f'{len(enrolments)} enrolment(s):')
    for record in enrolments:
        course = record.get('courseId') or {}
        if isinstance(course, str):
            print(f'  {course}')
            continue
        recent = record.get('recentlyAccessedLessons') or []
        last = recent[0].get('lessonId') if recent and isinstance(recent[0], dict) else None
        print(f'  {course.get("_id")}  {course.get("title")}'
              f'{f"  (last lesson {last})" if last else ""}')

    try:
        my = pwskills.my_courses(limit=1000).get('data') or []
        print(f'\n/{pwskills.PREFIX}/learn/user/courses returned {len(my)} item(s).')
    except pwskills.ApiError as exc:
        print(f'\nmy_courses failed: {exc}')


if __name__ == '__main__':
    main()
