"""
API ENDPOINTS LINKED TOGETHER

Sign In Flow:
1. POST /auth/login-start - Initiates OAuth flow
2. POST /auth/callback - Completes OAuth authentication
3. GET /auth/logout - Logs out user

User Profile:
1. GET /api/users/me - Get current user profile
2. GET /api/users/{user_id} - Get public user profile (anonymized)

Course Discovery:
1. GET /api/courses - List all courses with filtering
2. GET /api/courses/{course_id} - Get specific course with sections
3. GET /api/courses/sections - List course sections with filtering
4. GET /api/courses/sections/{section_id} - Get specific section
5. GET /api/courses/professors - List all professors with filtering
6. GET /api/courses/professors/{professor_id} - Get specific professor

Review Management:
1. GET /api/reviews - List approved reviews with filtering & pagination
2. GET /api/reviews/{review_id} - Get specific review
3. POST /api/reviews - Create new review (pending approval)
4. PUT /api/reviews/{review_id} - Update own review
5. DELETE /api/reviews/{review_id} - Delete own review (soft delete)
6. POST /api/reviews/{review_id}/like - Like a review
7. POST /api/reviews/{review_id}/dislike - Dislike a review

KEY FEATURES IMPLEMENTED:

✅ Anonymity Enforcement:
  - Reviews only show anonymous usernames
  - Email/identity hidden from public
  - Only user sees their own email (/api/users/me)

✅ Sign In Integration:
  - OAuth2 with Entra ID (existing auth.py)
  - Anonymous username generated on first login
  - User object linked to reviews

✅ Course Listing:
  - Search by department, course number, or name
  - Filter sections by semester, year, professor
  - Full course/section/professor relationships

✅ Review Posting:
  - Create reviews linked to course/professor/section
  - Support for ratings (1-5 stars) and attributes/tags
  - Moderation workflow (pending → approved)
  - Only approved reviews visible to others
  - Owners can edit/delete their own reviews

✅ Smart Ranking:
  - Like/dislike reviews to affect visibility
  - Net rating = likes - dislikes
  - Sort by created_at, rating, or net_rating
  - Each user can only have one interaction per review

✅ Pagination & Filtering:
  - Reviews with cursor-based pagination
  - Filter by course, professor, semester, rating
  - Return anonymized data in all responses

ANONYMITY PROTECTION:
- User model stores entra_oid + entra_email (private)
- Reviews reference user by ID, but only return username
- Review responses use _build_review_response() helper
- API never exposes PII except to the user themselves
- All queries on public endpoints filter for approved reviews only
"""
