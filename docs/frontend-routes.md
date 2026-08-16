# Website (frontend) routes

Next.js page routes served by `https://pwskills.com`, with the API calls they map to.

## Public

| Route | Purpose | Backing API |
| --- | --- | --- |
| `/` | homepage | `GET /v2/course/revampedHome`, `POST /v2/course/search`, `GET /v1/banners?type=WEB` |
| `/courses` | catalog with filters | `POST /v2/course/search?page=&limit=` |
| `/course/[courseSlug]` | batch description | `GET /v2/course/{slug}?isSlug=true` |
| `/[categorySlug]/[courseSlug]` | batch description under a category | same |
| `/[categorySlug]/` · `/category/[categorySlug]` | category landing | `GET /v2/course/page/{slug}?isSlug=true` |
| `/masterclass/` · `/masterclass/[masterclassSlug]` | masterclasses | `GET /v2/masterclass/list/` |
| `/online-degree` · `/degree/[degreeSlug]` | degree programs | `GET /v2/course/online-degree` |
| `/campus-edge`, `/career-services`, `/about-us`, `/contact-us`, `/faqs`, `/privacy-policy`, `/terms-and-conditions` | static/marketing | — |
| `/login` · `/callback` | auth flow | `/v3/oauth/token`, `/v1/auth/token/verify/{code}` |

## Logged in

| Route | Purpose | Backing API |
| --- | --- | --- |
| `/dashboard/overview/` | dashboard | `GET /v2/user/recently-accessed-course`, `/v2/user/upcoming-events`, `/v2/progress-streak/streak` |
| `/dashboard/mycourse/` | my batches | `GET /{prefix}/learn/user/courses`, `GET /v2/enrol/list` |
| `/dashboard/allCourses/` | all enrolled | same |
| `/dashboard/overview/course/[slug]` | batch overview | `GET /v2/course/{courseId}`, progress |
| `/dashboard/overview/masterclass/[slug]` | masterclass overview | `GET /v2/masterclass/my-list/` |
| `/dashboard/profile/` · `/user-profile` | profile | `GET /v1/users/my-profile` |
| `/dashboard/support/` · `/support/` | support | — |
| `/purchases/` · `/checkout` · `/transaction` | payments | `/{prefix}/checkout/{courseId}` |

## Learning (lecture track)

| Route | Purpose |
| --- | --- |
| `/learn/course/[courseName]/[courseId]/lesson/[lessonId]/` | lesson player page — sidebar from `getAllSections`, player from `lesson/details` |
| `…/lesson/[lessonId]/quiz/` | quiz attempt |
| `…/lesson/[lessonId]/test/` | test attempt |
| `…/lesson/[lessonId]/solutions/` | solutions view |
| `…/lesson/[lessonId]/coding-project/attempt/` | coding project IDE |
| `…/lesson/[lessonId]/coding-project/solution/` | coding project solution |
| `/learn/course/[courseName]/[courseId]/zoom/` | live Zoom class |
| `/learn/career-path/[career-path-name]/[career-path-id]/dashboard/` | career-path dashboard |
| `/learn/career-path/[career-path-name]/[career-path-id]/doubts/` | career-path doubts |
| `/learn/career-path/[career-path-name]/[career-path-id]/support/` | career-path support |
| `/learn/certificate/[id]` | certificate view |

`[courseName]` is a display slug only — the API keys off `[courseId]`.

### Query parameters used by the lesson page

| Param | Meaning |
| --- | --- |
| `t` | lesson type (`video`, `quiz`, `notes`, `assignment_v2`, …) — selects which container renders |
| `sectionId` | section the lesson belongs to; sent back with progress updates |
| `milestoneId` | career-path milestone; forwarded to section/lesson/progress calls |
| `courseName` | display title |
| `eventClass` | flags a live event class (hides completion hints) |

Example:

```
https://pwskills.com/learn/course/<course-slug>/<courseId>/lesson/<lessonId>/?t=video&sectionId=<sectionId>
```
