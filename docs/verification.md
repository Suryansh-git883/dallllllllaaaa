# How this was derived, and what was actually verified

## Method

1. Loaded public pages of `pwskills.com` in a browser and recorded the requests they make
   (hosts, methods, paths, headers, request bodies).
2. Read the publicly served frontend bundles and the **source maps that pwskills.com publishes**
   (`*.js.map`), which contain the original `src/api/*.ts` modules. Route strings, query
   parameters, payload shapes and the player dispatch logic in this documentation come from
   those files verbatim.
3. Called the public endpoints unauthenticated to confirm behaviour, and confirmed that the
   learning endpoints reject unauthenticated calls.

No authentication was bypassed, no credentials were used or collected, no protected content or
DRM was touched.

## Verified by direct request (unauthenticated)

| Request | Result |
| --- | --- |
| `GET /` | `200`, text `Hello from PW Skills` |
| `GET /v2/course/list-categories` | `200`, 19 categories with `_id`, `title`, `slug`, `categoryId` |
| `GET /v2/course/sitemeta?platformType=main` | `200`, `categories` (with `courseCount`), `categoriesArrangement`, `main.{companies,faq}` |
| `GET /v2/course/revampedHome` | `200`, `homeCourses[]` = categories with imagery/meta |
| `GET /v2/course/category/64b6b23440d0450268c09ff8/?skip=0&limit=50` | `200`, 4 batch documents + `meta.recommendedCoursesCount` |
| `GET /v2/course/category/6633a25462b2c482c3b366d2/` (category-page `_id`) | `200` but empty `recommendedCourses` |
| `GET /v2/course/category/data-science-and-analytics` (slug) | `500` |
| `GET /v2/course/{courseId}` | `200`, full batch document |
| `GET /v2/course/{slug}?isSlug=true&random_id=…` | `200`, same document; unknown slug/id → `404` |
| `GET /v2/course/page/{slug}?isSlug=true` | `200`, category landing-page content |
| `GET /v2/course/offlineCentre` | `200` |
| `GET /v2/masterclass/list/` | `200`, empty in the observed environment |
| `POST /v2/course/search?page=1&limit=5` with `{}`, with the site's own filter payload, and with `categoryId`/`filterConfig*` variants | `200` but `courses: []`, `total: 0` every time |
| `GET /v2/learn/section/getAllSections/{courseId}` | `401` |
| `GET /v2/learn/lesson/details/{courseId}/{lessonId}` | `401` |
| `GET /v2/enrol/list` | `401` |
| `GET /v1/learn/user/courses` | `401` |
| `GET /v1/cohort/recent-cohorts` | `401` |

Observed in the browser on `pwskills.com/courses`: the page's own `POST /v2/course/search`
request is sent as `?page=NaN&limit=6` and also comes back with `total: 0` — the visible cards
are server-rendered. That is why [catalog-and-batches.md](catalog-and-batches.md) recommends the
per-category route for listing batches.

Request headers observed from the live site: `authorization: Bearer undefined` (anonymous),
`client-id: 5eb393ee95fab7468a79d189`, `organizationid: 5eb393ee95fab7468a79d189`,
`client-type: WEB`, `randomid: <uuid>`, `content-type: application/json`.

## Derived from published source maps (not exercised)

Everything requiring a session: `/v2/learn/**`, `/v2/enrol/**`, `/{prefix}/learn/**`, progress
and video-session payloads, and the provider dispatch in the video player. Paths, parameter
names and payload keys are copied from the frontend's own API modules
(`src/api/lectureTrack.ts`, `src/api/learn.ts`, `src/api/userCourses.ts`, `src/api/postLogin.ts`,
`src/components/LectureTrack/**`), so field names should be accurate, but the exact response
bodies are not reproduced here because that would require an enrolled account's data.

Third-party hosts the site also talks to (not part of this API surface): Unleash feature flags
(`unleash-edge-prod.penpencil.co`), analytics (`analytics-api.penpencil.co`,
`faro-platform.penpencil.co`, `api.penpencil.co/web-vitals`), CDN (`cdn.pwskills.com`).

## Stability

Unofficial surface: route names, the `v1`/`v2` split, and payload keys can change without
notice. Re-run the checks above before trusting anything here.
