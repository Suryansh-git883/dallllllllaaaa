# Overview: hosts, prefixes, headers, envelope

## Hosts

| Purpose | Host | Notes |
| --- | --- | --- |
| Website | `https://pwskills.com` | Next.js app |
| Skills API | `https://api.pwskills.com` | main API used by the site (`NEXT_PUBLIC_BASE_API_URL`) |
| Identity / profile API ("PenPencil") | `https://api.penpencil.co` | user profile, files, org lookups (`NEXT_PUBLIC_PEN_PENCIL_API_URL`) |
| Player origin | first-party `/watch/` iframe host | used by the in-house DRM player |

`GET https://api.pwskills.com/` responds with the plain text `Hello from PW Skills`.

## Path prefixes

The frontend builds request URLs as `<base>/<version>/<path>`:

* `…/v1/…` – country, banners, auth token verify, profile.
* `…/v2/…` – the bulk of the catalog + learning API.
* `…/skills/v1/…` – used only for white-label/SaaS domains. On `pwskills.com` the prefix
  variable resolves to `v1`:

  ```ts
  export const saasDomainprefixUrl = 'skills/v1';
  export const skillsDomainprefixUrl = 'v1';
  const prefixUrl = saasDomains.includes(domainName) ? saasDomainprefixUrl : skillsDomainprefixUrl;
  ```

  So a documented `/{prefix}/learn/user/courses` means `/v1/learn/user/courses` on pwskills.com.

## Request headers

Observed on requests made by the public site:

| Header | Value | When |
| --- | --- | --- |
| `content-type` | `application/json` | JSON requests |
| `authorization` | `Bearer <token>` | when a session token exists; anonymous page loads send `Bearer undefined` |
| `organizationid` | `5eb393ee95fab7468a79d189` | organisation the web client belongs to |
| `client-id` | `5eb393ee95fab7468a79d189` | PenPencil-targeted calls |
| `client-type` | `WEB` | PenPencil-targeted calls |
| `randomid` | generated UUID, persisted in `localStorage.randomId` | request/device correlation |

How the frontend assembles them:

```ts
function commonHeaders(url: string): Record<string, string> {
  const headers: Record<string, string> = {};
  const token = localStorage.getItem(AuthEnums.TOKEN) || getCookies(PP_TOKEN) || '';
  if (token) headers.Authorization = `Bearer ${token}`;
  const organisationId = getPPClientDetails()?.organisationId || penPencilClientId;
  if (organisationId) headers.organizationid = organisationId;
  return headers;
}

function penPencilExtraHeaders(): Record<string, string> {
  return {
    'Client-Id': `${getPPClientDetails()?.clientId || penPencilClientId}`,
    randomId: getRandomIdFromSDK() || getRandomId() || randomId(),
    organizationid: getPPClientDetails()?.organisationId || '',
  };
}
```

For public catalog endpoints, `content-type` alone is enough; the other headers are harmless
but not required.

## Response envelope

Success:

```json
{
  "data": {},
  "success": true,
  "status_code": 200,
  "requestId": "…",
  "time_now": "2026-08-16T12:00:00.000Z"
}
```

`time_now` is present on lesson/test endpoints and is what the player uses as the server clock
(the frontend stores it as `localStorage.systemTime`).

Error:

```json
{
  "error": "Unauthorized",
  "success": false,
  "status_code": 401,
  "data": {},
  "requestId": "…"
}
```

Observed status codes: `200`, `400` (validation, e.g. "must be a valid ObjectId"), `401`
(missing/expired token), `404` (unknown id/slug), `500` (bad route parameter shape).

## Pagination

Two conventions coexist:

* `skip` + `limit` (+ `order`, `select`, `search`) on `/learn/**` and `/enrol/**`:
  `?skip=0&limit=100&order=-1`. `order=-1` is newest-first.
* `page` + `limit` on catalog search: `?page=1&limit=6`.

Both are query parameters, including on the `POST /v2/course/search` route whose *body* holds
the filters.

## Identifiers

All ids (`courseId`, `lessonId`, `sectionId`, `milestoneId`, `doubtId`) are 24-character
MongoDB ObjectId hex strings. Sending anything else typically yields `400` with a validation
message, or `500` on routes that interpolate the value into a lookup. Slug-based routes take a
human-readable slug plus `isSlug=true`.

One trap: category objects carry **two** ids — `_id` (the category *page*) and `categoryId` (the
category itself). `/v2/course/category/{…}` needs `categoryId`; the other id returns an empty list.
