# Endpoint reference

Base host `https://api.pwskills.com` unless noted. `{prefix}` = `v1` on pwskills.com.
Auth column: `–` public, `T` bearer token, `T+E` token **and** enrollment in the course.

## Catalog

| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| GET | `/` | – | health text `Hello from PW Skills` |
| GET | `/v2/course/list-categories[?categoryType=SKILLS]` | – | categories (verified) |
| GET | `/v2/category-banner` · `/v2/category-banner/{categoryId}` | – | banners |
| GET | `/v2/category-news/{categoryId}` | – | news cards |
| POST | `/v2/course/search?page={n}&limit={n}` | – | filter body, paginated; verified to return `total: 0` even with the site's own payload |
| POST | `/v2/course/search?limit=10000&page=1&fullText=true` | – | tag filter |
| POST | `/v2/course/home` | – | homepage payload |
| GET | `/v2/course/revampedHome[?freeCourseFilter=…]` | – | homepage v2 |
| GET | `/v2/course/searchByName?…` | – | name search |
| GET | `/v2/course/category/{categoryId}/?skip={n}&limit={n}[&isFree=][&masterclass=][&institutionId=]` | – | **batches of a category (verified)** — `categoryId` = `categoryId` field of `list-categories` |
| GET | `/v2/course/{slug}?isSlug=true&random_id={uuid}[&userId=]` | – | batch description (verified) |
| GET | `/v2/course/{courseId}` | – | batch document (verified) |
| GET | `/v2/course/page/{slug}?isSlug=true&random_id={uuid}` | – | category landing page |
| GET | `/v2/course/sitemeta?platformType=main&random_id={uuid}` | – | companies/FAQs/sitemap meta |
| GET | `/v2/course/online-degree` | – | degree programs |
| GET | `/v2/course/offlineCentre[?…]` | – | offline centres (verified) |
| GET | `/v2/course/redirection-handler?redirectionUrl=…&queryParams=…` | – | canonical redirect resolver |
| GET | `/v2/masterclass/list/?…` | – | masterclasses (verified, may be empty) |
| GET | `/v2/masterclass/my-list/?…` | T | user's masterclasses |
| POST | `/v2/masterclass/certificate/{courseId}` | T | generate certificate |
| GET | `/v1/banners?type=WEB` | – | web banners |
| GET | `/v1/country` | – | country/ISD list |
| GET | `/v1/course` | – | course list |
| GET | `/v2/partnerInstitute/fetch-all` | – | partner institutes |

## Auth / user

| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| POST | `/v3/oauth/token` | – | password grant |
| POST | `/v1/auth/token/verify/{code}` | – | verify login code |
| POST | `/v2/auth/verifyEmail/{code}` | T | e-mail verification |
| POST | `/v1/auth/sendVerificationEmail` | T | resend verification |
| POST | `/v1/auth/logout` | T | logout |
| GET | `/v1/users/my-profile` *(PenPencil host)* | T | profile |
| PUT | `/v1/users` *(PenPencil host)* | T | update profile |
| POST | `/v1/files` *(PenPencil host)* | T | multipart upload (avatar) |
| PATCH | `/v1/auth/profile` · `/v1/auth/profile/profilePicture` | T | legacy profile update |
| POST | `/v2/user/preferences` | T | preferences |
| GET | `/v2/organizations/fetch-state-by-pincode?pincode=` *(PenPencil host)* | – | address autofill |

## My batches / dashboard

| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| GET | `/v2/enrol/list?skip=&limit=&select=courseId,recentlyAccessedLessons` | T | enrollments (401 verified without token) |
| POST | `/v2/enrol/users-enrollments-count` | T | bulk counts, body `{userIds}` |
| GET | `/{prefix}/learn/user/courses?skip=&limit=&order=&search=&isCareerPath=` | T | my batches (401 verified without token) |
| GET | `/{prefix}/learn/user/isCourseBought/{courseId}` | T | purchase check |
| GET | `/{prefix}/learn/user/expiring-courses` | T | expiring access |
| GET | `/{prefix}/learn/user/courses/expiry/{courseId}` | T | expiry for one course |
| GET | `/v2/user/recently-accessed-course` | T | continue-watching |
| GET | `/v2/user/upcoming-events` · `/v2/user/live-events` | T | schedule |
| GET | `/v2/progress-streak/streak` · `/v2/progress-streak/{param}?date=` | T | streaks |
| GET | `/v1/cohort/recent-cohorts` | T | cohorts (401 verified without token) |

## Batch content

| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| GET | `/v2/learn/section/getAllSections/{courseId}[?milestoneId=]` | T+E | full curriculum (401 verified without token) |
| GET | `/v2/learn/section/{courseId}/{sectionId}?milestoneId=&lessonType=&lectureMode=&isMandatory=` | T+E | one section, filtered |
| GET | `/v2/learn/lesson/details/{courseId}/{lessonId}[?milestoneId=]` | T+E | lesson + playback metadata (401 verified without token) |
| GET | `/{prefix}/learn/lesson/course/{courseId}/{lessonId}[?milestoneId=]` | T+E | lesson (assignment/career-path) |
| GET | `/v2/learn/lesson/zoom/{courseId}/{lessonId}` | T+E | Zoom join details |
| POST | `/v2/learn/lesson/mettl/{courseId}/{sectionId}/{lessonId}` | T+E | start partner exam |
| GET | `/v2/learn/lesson/mettl-result/{courseId}/{lessonId}` | T+E | exam result |
| POST | `/{prefix}/learn/submission/{courseId}/quiz/{lessonId}` | T+E | quiz submit |
| POST | `/{prefix}/learn/submission/{courseId}/assignment/{lessonId}` | T+E | assignment submit |
| POST | `/v2/assignment/{courseId}/{sectionId}/{lessonId}[?milestoneId=]` | T+E | multipart upload |

## Progress / playback tracking

| Method | Path | Auth | Notes |
| --- | --- | --- | --- |
| GET/PATCH | `/v2/learn/progress/{courseId}` | T+E | course progress, watch percentage |
| GET | `/v2/learn/progress/milestone-progress/{courseId}/{milestoneId}` | T+E | milestone progress |
| PATCH | `/v2/learn/progress/{courseId}/recently-accessed-lessons` | T+E | `{lessonId, milestoneId}` |
| GET/PATCH | `/{prefix}/learn/lesson/video-session/{courseId}/lesson/{lessonId}` | T+E | resume position, watch stats |
| GET/PATCH | `/{prefix}/learn/analytics/lastPlayed/course/{courseId}` | T+E | last played lesson |

## Notes / doubts / feedback

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/v2/learn/lesson/notes/{courseId}/?order=&limit=&skip=[&lessonId=][&milestoneId=]` | T+E |
| POST | `/v2/learn/lesson/notes/{courseId}/{lessonId}` | T+E |
| DELETE | `/v2/learn/lesson/notes/{courseId}/{lessonId}/{noteId}` | T+E |
| GET | `/v2/learn/doubt/{courseId}/{lessonId}?limit=&skip=&order=&sort=` | T+E |
| GET | `/v2/learn/doubt/{courseId}/{lessonId}/{doubtId}/replies?limit=&skip=` | T+E |
| POST | `/v2/learn/doubt/{courseId}/{lessonId}` | T+E |
| DELETE | `/v2/learn/doubt/{courseId}/{lessonId}/{doubtId}` | T+E |
| PATCH | `/v2/learn/doubt/{courseId}/{lessonId}/{doubtId}/like-action` | T+E |
| PATCH | `/v2/learn/doubt/{courseId}/{lessonId}/{doubtId}/lesson-doubt-status` | T+E |
| POST | `/v2/learn/doubt/{courseId}/{lessonId}/{doubtId}/report-doubt` | T+E |
| GET/POST | `/v2/learn/lesson/feedback/{courseId}/lesson/{lessonId}` | T+E |
| POST | `/v2/learn/lesson/feedback/rating/{courseId}/lesson/{lessonId}` | T+E |
| POST | `/v2/learn/lesson/feedback/comment/{courseId}/lesson/{lessonId}` | T+E |
| GET | `/v2/learn/lesson/feedback/status/{courseId}/lesson/{lessonId}` | T+E |
| GET | `/v2/learn/lesson/feedback/{courseId}/lesson/{lessonId}/comment-thread` | T+E |
| DELETE | `/v2/learn/lesson/feedback/{courseId}/lesson/{lessonId}/{commentId}` | T+E |

## Career path

| Method | Path | Auth |
| --- | --- | --- |
| GET | `/v2/learn/career-path/course-details/{courseId}` | T+E |
| GET | `/v2/learn/career-path/years-tracker` | T |
| GET | `/v2/learn/career-path/progress/{courseId}/{yearId}` | T+E |
| GET | `/v2/learn/career-path/percentile/{courseId}/{yearId}` | T+E |
| POST | `/v2/learn/career-path/choose-milestone/{courseId}` | T+E |
| POST | `/v2/learn/career-path/remind-me/{courseId}` | T+E |

## Checkout / leads / misc

| Method | Path | Auth |
| --- | --- | --- |
| GET/POST | `/{prefix}/checkout/{courseId}` | T |
| POST | `/v2/checkout/verify-upi` | T |
| GET | `/v2/assisted-sales/{userId}/checkout-details/{courseId}` | T |
| POST | `/{prefix}/public/user/enquiry` | – |
| POST | `/{prefix}/course/sendCourseLeadToLeadSquared/{courseId}` | – |
| POST | `/{prefix}/course/sendCategoryPageLeadToLeadSquared/{categoryPageId}` | – |
| POST | `/{prefix}/course/trackUserCourseActivity/{courseId}` | – |
| POST | `/v2/lead/signup-events` · GET `/v2/lead/kapture` | – |
| POST | `/v2/ga-events` | – |
| GET | `/v2/nsdc/{courseId}` (header `nsdcToken`) | T |
| GET/POST | `/v2/rating/{courseId}` | T |

Lead-capture routes accept a `g-recaptcha-response` field; without a valid captcha token they are
rejected.
