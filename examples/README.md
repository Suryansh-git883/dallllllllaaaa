# Examples

Dependency-free Python 3.9+ scripts (stdlib only). Run them from this directory so that
`pwskills.py` is importable.

| Script | Auth | What it does |
| --- | --- | --- |
| `public_catalog.py [max_categories]` | none | lists categories and paginates every batch of each category |
| `list_my_batches.py` | token | lists the enrolments of the calling account |
| `load_batch_content.py <courseId> [milestoneId]` | token + enrolment | prints the section → lesson tree |
| `lesson_playback.py <courseId> <lessonId> [milestoneId]` | token + enrolment | fetches lesson detail and reports which player applies |

```bash
cd examples
python3 public_catalog.py 4     # first 4 categories

export PWSKILLS_TOKEN='<your own session token>'
python3 list_my_batches.py
python3 load_batch_content.py <courseId>
python3 lesson_playback.py <courseId> <lessonId>
```

Environment variables: `PWSKILLS_TOKEN`, optional `PWSKILLS_API` (default
`https://api.pwskills.com`) and `PWSKILLS_ORG_ID`.

`lesson_playback.py` masks tokens/URLs in its output on purpose — playback credentials are
short-lived and session-bound and should not be logged or shared.
