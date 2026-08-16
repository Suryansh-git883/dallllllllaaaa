"""Minimal dependency-free client for the pwskills.com API.

Token is read from the PWSKILLS_TOKEN environment variable. Use your own logged-in
session's token; public endpoints work without it.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASE_URL = os.environ.get('PWSKILLS_API', 'https://api.pwskills.com')
ORGANIZATION_ID = os.environ.get('PWSKILLS_ORG_ID', '5eb393ee95fab7468a79d189')
PREFIX = 'v1'  # `skills/v1` on white-label domains


class ApiError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f'HTTP {status}: {body[:400]}')
        self.status = status
        self.body = body


def _headers() -> dict[str, str]:
    headers = {
        'content-type': 'application/json',
        'accept': 'application/json',
        'organizationid': ORGANIZATION_ID,
        'client-id': ORGANIZATION_ID,
        'client-type': 'WEB',
        'randomid': str(uuid.uuid4()),
    }
    token = os.environ.get('PWSKILLS_TOKEN')
    if token:
        headers['authorization'] = f'Bearer {token}'
    return headers


def request(method: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
    url = f'{BASE_URL}/{path.lstrip("/")}'
    if params:
        url = f'{url}?{urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})}'
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read().decode())
    except urllib.error.HTTPError as exc:
        raise ApiError(exc.code, exc.read().decode(errors='replace')) from exc


def get(path: str, **params) -> dict:
    return request('GET', path, params=params)


def post(path: str, body: dict | None = None, **params) -> dict:
    return request('POST', path, params=params, body=body or {})


def patch(path: str, body: dict | None = None, **params) -> dict:
    return request('PATCH', path, params=params, body=body or {})


# --- catalog (public) -------------------------------------------------------

def list_categories(category_type: str | None = None) -> list:
    """Categories. Note: item['_id'] is the category *page* id, item['categoryId'] is the
    category id required by courses_by_category()."""
    return get('/v2/course/list-categories', categoryType=category_type).get('data', [])


def sitemeta() -> dict:
    return get('/v2/course/sitemeta', platformType='main', random_id=str(uuid.uuid4())).get('data', {})


def search_courses(filters: dict | None = None, page: int = 1, limit: int = 6) -> dict:
    return post('/v2/course/search', filters or {}, page=page, limit=limit)


def iter_all_courses(filters: dict | None = None, limit: int = 24):
    """Page through the public catalog until a short page is returned."""
    page = 1
    while True:
        payload = search_courses(filters, page=page, limit=limit)
        items = payload.get('data') or []
        if isinstance(items, dict):
            items = items.get('courses') or items.get('data') or []
        yield from items
        if len(items) < limit:
            return
        page += 1


def courses_by_category(category_id: str, skip: int = 0, limit: int = 50, **extra) -> dict:
    """Batches in a category. `category_id` is the `categoryId` field from list_categories()."""
    return get(f'/v2/course/category/{category_id}/', skip=skip, limit=limit, **extra)


def iter_category_batches(category_id: str, limit: int = 50, **extra):
    """Page through every batch of a category (verified public route)."""
    skip = 0
    while True:
        data = courses_by_category(category_id, skip=skip, limit=limit, **extra).get('data') or {}
        batches = data.get('recommendedCourses') or []
        yield from batches
        total = int((data.get('meta') or {}).get('recommendedCoursesCount') or 0)
        skip += len(batches)
        if not batches or skip >= total:
            return


def iter_all_batches(limit: int = 50, **extra):
    """Every batch of every category."""
    for category in list_categories():
        category_id = category.get('categoryId')
        if not category_id:
            continue
        for batch in iter_category_batches(category_id, limit=limit, **extra):
            yield category, batch


def course_by_slug(slug: str) -> dict:
    return get(f'/v2/course/{slug}', isSlug='true', random_id=str(uuid.uuid4()))


def course(course_id: str) -> dict:
    return get(f'/v2/course/{course_id}')


# --- my batches (auth) -----------------------------------------------------

def enrollments(skip: int = 0, limit: int = 100) -> dict:
    return get('/v2/enrol/list', skip=skip, limit=limit,
               select='courseId,recentlyAccessedLessons')


def my_courses(skip: int = 0, limit: int = 1000, order: int = -1,
               search: str = '', is_career_path: bool = False) -> dict:
    return get(f'/{PREFIX}/learn/user/courses', skip=skip, limit=limit, order=order,
               search=search, isCareerPath=str(is_career_path).lower())


# --- batch content (auth + enrollment) -------------------------------------

def sections(course_id: str, milestone_id: str | None = None) -> dict:
    return get(f'/v2/learn/section/getAllSections/{course_id}', milestoneId=milestone_id)


def section(course_id: str, section_id: str, milestone_id: str | None = None,
            lesson_type: str | None = None, lecture_mode: str | None = None) -> dict:
    return get(f'/v2/learn/section/{course_id}/{section_id}', milestoneId=milestone_id,
               lessonType=lesson_type, lectureMode=lecture_mode)


def lesson_details(course_id: str, lesson_id: str, milestone_id: str | None = None) -> dict:
    return get(f'/v2/learn/lesson/details/{course_id}/{lesson_id}', milestoneId=milestone_id)


def video_session(course_id: str, lesson_id: str) -> dict:
    return get(f'/{PREFIX}/learn/lesson/video-session/{course_id}/lesson/{lesson_id}')


def update_video_session(course_id: str, lesson_id: str, payload: dict) -> dict:
    return patch(f'/{PREFIX}/learn/lesson/video-session/{course_id}/lesson/{lesson_id}', payload)


def progress(course_id: str) -> dict:
    return get(f'/v2/learn/progress/{course_id}')


def update_progress(course_id: str, lesson_id: str, section_id: str,
                    watch_percentage: float, milestone_id: str | None = None) -> dict:
    body = {
        'watchPercentage': watch_percentage,
        'lessonId': lesson_id,
        'sectionId': section_id,
    }
    if milestone_id:
        body['milestoneId'] = milestone_id
    return patch(f'/v2/learn/progress/{course_id}', body)
