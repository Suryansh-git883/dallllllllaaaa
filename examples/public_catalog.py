"""List every public category and every batch in each category.

Usage:
    python3 examples/public_catalog.py [max_categories]

No token required. Uses GET /v2/course/list-categories then paginates
GET /v2/course/category/{categoryId}/?skip=&limit=
"""

from __future__ import annotations

import sys

import pwskills


def main() -> None:
    max_categories = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    categories = pwskills.list_categories()
    if max_categories:
        categories = categories[:max_categories]

    total = 0
    for category in categories:
        category_id = category.get('categoryId')
        print(f'\n# {category.get("title")}  slug={category.get("slug")}  categoryId={category_id}')
        if not category_id:
            print('  (no categoryId on this entry)')
            continue
        try:
            batches = list(pwskills.iter_category_batches(category_id))
        except pwskills.ApiError as exc:
            print(f'  failed: {exc}')
            continue
        for batch in batches:
            total += 1
            print(f'  {batch.get("_id")}  {batch.get("name")}'
                  f'  slug={batch.get("slug")}'
                  f'  start={(batch.get("startDate") or "")[:10]}'
                  f'  status={batch.get("status")}  lang={batch.get("language")}')
        print(f'  -> {len(batches)} batch(es)')

    print(f'\n{total} batch(es) across {len(categories)} category(ies).')


if __name__ == '__main__':
    main()
