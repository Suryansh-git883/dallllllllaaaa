# Catalog, courses and batches

On PW Skills a "batch" is a **course document** (`courseId`) with a start date, mentors,
sections and lessons. Career-path/degree programs add one more level above sections called a
**milestone** (`milestoneId`), which most learning endpoints accept as an optional query
parameter.

```
category → course (batch)  → [milestone] → section → lesson → (video | quiz | assignment | notes | …)
```

## 1. Categories (public)

```http
GET /v2/course/list-categories
GET /v2/course/list-categories?categoryType=SKILLS
```

Verified unauthenticated. Each item:

```json
{
  "_id": "6633a25462b2c482c3b366d2",
  "title": "Data Science & Analytics",
  "slug": "data-science-and-analytics",
  "categoryId": "64b6b23440d0450268c09ff8",
  "icon": "",
  "weightage": 90
}
```

**Important:** `_id` is the *category page* id, `categoryId` is the actual category id. The
batch-listing route below needs `categoryId`; passing `_id` returns an empty list.

`GET /v2/course/sitemeta?platformType=main` returns the same categories with a `courseCount`
per category plus the embedded `categoryPage` object, which is handy for planning a crawl.

Related public endpoints:

```http
GET  /v2/category-banner
GET  /v2/category-banner/{categoryId}
GET  /v2/category-news/{categoryId}
GET  /v2/course/page/{slug}?isSlug=true&random_id={uuid}   # category landing page content
GET  /v2/course/online-degree
GET  /v2/course/offlineCentre
GET  /v1/banners?type=WEB
GET  /v1/country
GET  /v2/course/sitemeta?platformType=main&random_id={uuid}
```

## 2. List all batches (public)

The reliable way to enumerate batches is **per category**:

```http
GET /v2/course/category/{categoryId}/?skip=0&limit=50
GET /v2/course/category/{categoryId}/?skip=0&limit=50&isFree=true
GET /v2/course/category/{categoryId}/?skip=0&limit=50&masterclass=true
GET /v2/course/category/{categoryId}/?skip=0&limit=50&institutionId={institutionId}
```

Verified unauthenticated. Response:

```json
{
  "data": {
    "recommendedCourses": [ { "_id": "…", "name": "…", "batchName": "…", "slug": "…" } ],
    "partnerInstitutes": [],
    "meta": { "skip": "0", "limit": "50", "recommendedCoursesCount": 4, "masterClassesCount": 0 }
  }
}
```

Page with `skip`/`limit` until `skip + len(recommendedCourses) >= meta.recommendedCoursesCount`.
Passing a slug, or the category-page `_id` instead of `categoryId`, yields an empty list or `500`.

Each entry is the full batch document (see §3 for the notable fields).

### Catalog search

The `/courses` listing page uses a POST search whose **body carries filters** and whose
**query string carries pagination**:

```http
POST /v2/course/search?page=1&limit=6
content-type: application/json

{"level":"","programType":"","text":"","instructors":[],"categories":[],
 "languages":[],"subcategories":[],"domains":[],"isFree":"","hashTag":[]}
```

Response envelope:

```json
{
  "data": {
    "featured": [],
    "courses": [],
    "meta": [{ "metadata": [{ "total": 0, "totalPages": 0 }], "programType": [], "levels": [],
               "onlineDegreeType": [], "language": [], "hashTags": [], "instructors": [], "pricing": [] }],
    "offeringFilters": [],
    "categoryDetail": null
  }
}
```

Caveat, verified: this route returned `total: 0` with empty `courses`/`featured` for every body
tried — including the exact payload the live site sends from the browser (the site itself even
sends `page=NaN`). The cards visible on `/courses` come from server-rendered data, not from this
call. So don't rely on `/v2/course/search` for a catalog dump; use the per-category route above.

Other catalog-wide variants seen in the frontend:

```http
POST /v2/course/search?limit=10000&page=1&fullText=true   # tag filter, body {"programType": "…"}
POST /v2/course/home
GET  /v2/course/revampedHome[?freeCourseFilter=…]          # returns homeCourses[] = categories
GET  /v2/course/searchByName?…
```

Additional filter keys observed at other call sites: `showOnHomePage`, `filterConfigSlug`,
`filterConfigSrc`, `filterConfigCohortId`.

### Masterclasses

```http
GET /v2/masterclass/list/?…        # public
GET /v2/masterclass/my-list/?…     # auth: masterclasses of the logged-in user
POST /v2/masterclass/certificate/{courseId}
```

## 3. Batch detail

```http
GET /v2/course/{slug}?isSlug=true&random_id={uuid}[&userId={userId}]   # public description page
GET /v2/course/{courseId}                                             # full course document
```

Both forms verified public. The slug form is what `pwskills.com/course/<slug>` and
`pwskills.com/<category>/<courseSlug>` call; an id/slug that does not exist returns `404`.

Notable batch-document fields (it is a batch, hence the naming):

| Field | Meaning |
| --- | --- |
| `_id` | the `courseId` used by every learning endpoint |
| `name`, `batchName`, `byName`, `batchCode` | display + internal batch identity |
| `slug` | URL slug |
| `startDate`, `endDate`, `classEndDate`, `registrationStartDate`, `registrationEndDate` | schedule |
| `status` (`Active`…), `mode`, `language`, `class`, `type`, `courseType` (`REGULAR`, `MASTERCLASS`, …) | classification |
| `pricing`, `feeId`, `isFree`, `cashbackValue`, `isPayLaterEnabled` | commercials |
| `userCount`, `userLimit` | capacity |
| `previewImageUrl`, `shortDescription`, `description`, `banners`, `batchPdfUrl` | presentation |
| `cohortId`, `programId`, `batchCategoryId(s)`, `organizationId` | grouping |
| `isDoubtEnabled`, `enableCommunity`, `enableMentorship`, `videoAnalytics`, `newVideoPlayerConfig`, `isBatchContentSecurityEnabled` | feature flags that affect the lecture page and player |

Supporting:

```http
GET  /{prefix}/learn/user/isCourseBought/{courseId}        # auth
POST /{prefix}/course/trackUserCourseActivity/{courseId}   # body {"activity":"explore"}
GET  /v2/course/redirection-handler?redirectionUrl=…&queryParams=…
```

## 4. My batches (auth required)

Two equivalent-ish entry points:

```http
GET /v2/enrol/list?skip=0&limit=100&select=courseId,recentlyAccessedLessons
```

Lightweight: enrollment records with the embedded `courseId` object and the last lesson
touched in each. This is what the app uses to decide "continue watching".

```http
GET /{prefix}/learn/user/courses?skip=0&limit=1000&order=-1&search=&isCareerPath=false
```

Richer "My Courses" listing. Parameters:

| Param | Meaning |
| --- | --- |
| `skip`, `limit` | pagination |
| `order` | `-1` newest first, `1` oldest first |
| `search` | free-text over course titles (also used to filter by course *type* in one call site) |
| `isCareerPath` | `true` returns only career-path programs |

Also:

```http
GET /v2/user/recently-accessed-course
GET /v2/user/upcoming-events
GET /v2/user/live-events
GET /v2/progress-streak/streak
GET /v2/progress-streak/{routeParam}?date={ISO date}
GET /{prefix}/learn/user/expiring-courses
GET /{prefix}/learn/user/courses/expiry/{courseId}
```

## 5. Career-path / degree extras (auth)

```http
GET  /v2/learn/career-path/course-details/{courseId}
GET  /v2/learn/career-path/years-tracker
GET  /v2/learn/career-path/progress/{courseId}/{yearId}
GET  /v2/learn/career-path/percentile/{courseId}/{yearId}
POST /v2/learn/career-path/choose-milestone/{courseId}
POST /v2/learn/career-path/remind-me/{courseId}
```

`{prefix}` = `v1` on pwskills.com — see [overview.md](overview.md#path-prefixes).
