"""Print the full section/lesson tree of one batch.

Usage:
    PWSKILLS_TOKEN='…' python3 examples/load_batch_content.py <courseId> [milestoneId]
"""

from __future__ import annotations

import sys

import pwskills


def lesson_list(section: dict) -> list:
    for key in ('lessons', 'lesson', 'lessonsData', 'data'):
        value = section.get(key)
        if isinstance(value, list):
            return value
    return []


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    course_id = sys.argv[1]
    milestone_id = sys.argv[2] if len(sys.argv) > 2 else None

    payload = pwskills.sections(course_id, milestone_id)
    data = payload.get('data')
    sections = data if isinstance(data, list) else (data or {}).get('sections') or []

    print(f'{len(sections)} section(s) in {course_id}')
    for index, section in enumerate(sections, start=1):
        print(f'\n{index}. {section.get("name") or section.get("title")}  [{section.get("_id")}]')
        for lesson in lesson_list(section):
            flags = []
            if lesson.get('isMandatory'):
                flags.append('mandatory')
            if lesson.get('isCompleted'):
                flags.append('completed')
            if lesson.get('lectureMode') == 'live':
                flags.append('live')
            print(f'   - [{lesson.get("type")}] {lesson.get("title")}'
                  f'  id={lesson.get("_id")}  status={lesson.get("status")}'
                  f'{"  " + ",".join(flags) if flags else ""}')


if __name__ == '__main__':
    main()
