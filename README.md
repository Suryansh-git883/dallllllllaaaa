# PW Skills API Documentation (observational)

Documentation of the HTTP API that the public `pwskills.com` web app calls, derived from
publicly served frontend assets (Next.js bundles + the source maps that pwskills.com serves
publicly) and from unauthenticated requests to public endpoints.

This is an **unofficial compatibility reference**. There is no published/official public API
contract, so paths, parameters and payloads may change at any time.

## Contents

| Document | What it covers |
| --- | --- |
| [docs/overview.md](docs/overview.md) | Hosts, path prefixes, headers, response envelope, errors, pagination |
| [docs/authentication.md](docs/authentication.md) | Token model, which routes need auth, what an unauthenticated call returns |
| [docs/catalog-and-batches.md](docs/catalog-and-batches.md) | Listing categories, courses/batches, search, filters, "my batches" |
| [docs/batch-content.md](docs/batch-content.md) | Sections → lessons traversal, lesson detail, lesson types, progress |
| [docs/video-playback.md](docs/video-playback.md) | How a lesson's video metadata is returned and how each provider is played |
| [docs/endpoint-reference.md](docs/endpoint-reference.md) | Flat table of every endpoint found, with method + auth requirement |
| [docs/frontend-routes.md](docs/frontend-routes.md) | Website page routes and their URL parameters |
| [docs/verification.md](docs/verification.md) | How this was derived, and exactly what was verified vs. read from published source maps |
| [examples/](examples/) | Runnable Python examples: public catalog, batch content, playback metadata |

## Quickstart

```bash
# Public: categories (note: use .categoryId, not ._id, for the batch listing below)
curl -s https://api.pwskills.com/v2/course/list-categories | jq '.data[0]'

# Public: all batches of one category, paginated
curl -s 'https://api.pwskills.com/v2/course/category/64b6b23440d0450268c09ff8/?skip=0&limit=50' \
  | jq '.data.meta, [.data.recommendedCourses[] | {_id, name, slug, startDate}]'

# Public: one batch
curl -s 'https://api.pwskills.com/v2/course/<courseId>' | jq '.data | {_id, name, batchCode, startDate}'
```

```bash
# Your own batches + content + playback metadata (requires your own session token)
export PWSKILLS_TOKEN='<token from your logged-in browser session>'
python3 examples/public_catalog.py
python3 examples/list_my_batches.py
python3 examples/load_batch_content.py <courseId>
python3 examples/lesson_playback.py <courseId> <lessonId>
```

## Scope and limits

* Everything here describes endpoints as *observed*. Nothing in this repo bypasses login,
  entitlement checks, signed URLs, or DRM.
* Content endpoints (`/learn/**`, `/enrol/**`) return data only for batches the calling
  account is enrolled in. Without a valid token they return `401`.
* Video playback values (VdoCipher `otp`/`playbackInfo`, `centralVideoUrl`) are short-lived
  and bound to the requesting session. They are meant to be handed to the corresponding
  player SDK, not stored, shared, or re-distributed.
* Use your own account and respect the site's Terms of Service and rate limits.
