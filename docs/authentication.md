# Authentication

## Model

The web app is a bearer-token client:

1. The user logs in through the PW/PenPencil identity flow (`/login`, then a `/callback` page).
2. The resulting access token is kept in `localStorage` (`AuthEnums.TOKEN`) and/or in a
   PenPencil cookie (`PP_TOKEN`).
3. Every subsequent API call adds `Authorization: Bearer <token>` plus `organizationid`.

Auth-related endpoints the frontend calls:

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/v3/oauth/token` | password grant (`username`, `password`, `client_id`, `client_secret`, `grant_type=password`, `organizationId`) |
| `POST` | `/v1/auth/token/verify/{code}` | exchange/verify a login code |
| `POST` | `/v2/auth/verifyEmail/{code}` | e-mail verification |
| `POST` | `/v1/auth/sendVerificationEmail` | resend verification mail |
| `GET` | `/v1/users/my-profile` (PenPencil host) | current user profile |
| `PUT` | `/v1/users` (PenPencil host) | update profile |
| `POST` | `/v1/auth/logout` | invalidate session |

OTP login also exists against the ambassador portal host (`/v3/otp`, `/v3/otp/verify`).

## Getting a token for your own experiments

The supported way is to log in normally in a browser and read your own session token from the
logged-in tab (DevTools → Application → Local Storage), then:

```bash
export PWSKILLS_TOKEN='<your token>'
curl -s https://api.pwskills.com/v2/enrol/list?skip=0\&limit=100 \
  -H "authorization: Bearer $PWSKILLS_TOKEN" \
  -H 'organizationid: 5eb393ee95fab7468a79d189' | jq
```

Tokens expire. On expiry the API returns `401` and the frontend logs the user out.

Do not script credential collection, share tokens, or use a token that is not yours.

## Which routes need auth

| Class | Auth | Behaviour without a token |
| --- | --- | --- |
| Catalog (`/v2/course/list-categories`, `/v2/course/search`, `/v2/course/{slug}?isSlug=true`, `/v2/masterclass/list/`, `/v1/banners`, `/v1/country`, `/v2/course/sitemeta`) | none | `200` with public data |
| Enrollment (`/v2/enrol/list`, `/{prefix}/learn/user/courses`) | required | `401` |
| Batch content (`/v2/learn/section/**`, `/v2/learn/lesson/**`) | required + enrollment | `401`, or `404`/locked lesson status |
| Progress (`/v2/learn/progress/**`, video-session) | required | `401` |
| Cohorts (`/v1/cohort/recent-cohorts`) | required | `401` (verified) |

Enrollment is enforced per course: a valid token for an account that does not own a batch does
not return that batch's lessons or playback metadata.
