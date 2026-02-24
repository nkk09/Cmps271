# Frontend-Backend Integration Summary

## What's Now Linked

### ✅ Authentication (Sign In)
- **Auth Flow**: OAuth2 with Entra ID (email verification)
- **Frontend**: `src/components/AuthCard.jsx` handles login
- **Backend**: `/auth/login-start`, `/auth/callback`, `/auth/logout`
- **Status**: User endpoint changed from `/auth/me` to `/api/users/me`

### ✅ Course Listing
- **Frontend**: `src/pages/Landing.jsx` 
- **Backend**: 
  - `GET /api/courses` - List all courses
  - `GET /api/courses/{id}` - Get specific course
  - `GET /api/courses/sections` - List course sections
  - `GET /api/courses/professors` - List professors
  
- **Features**:
  - Real-time filtering by department
  - Search by course number or name
  - Fetches data from backend on load
  - Handles loading and error states

### ✅ Review Management (NEW)
- **Frontend**: `src/pages/Reviews.jsx` (new component)
- **Backend**:
  - `GET /api/reviews` - List approved reviews with filtering
  - `POST /api/reviews` - Create new review (pending approval)
  - `PUT /api/reviews/{id}` - Edit own review
  - `DELETE /api/reviews/{id}` - Delete own review
  - `POST /api/reviews/{id}/like` - Like a review
  - `POST /api/reviews/{id}/dislike` - Dislike a review

- **Features**:
  - Filter by course, professor, section
  - Create reviews with title, content, rating (1-5), tags
  - Like/dislike reviews for smart ranking
  - Shows anonymized reviewer username only
  - Real-time net rating (likes - dislikes)

### ✅ User Profile
- **Frontend**: `src/App.jsx`, `src/pages/Landing.jsx`
- **Backend**: `GET /api/users/me`
- **Features**:
  - Displays anonymous username
  - Shows role and member join date
  - Email hidden from public view

---

## API Integration Layer

### File: `src/api.js`
Central API utility with all endpoints. Usage:

```javascript
import api from "./api"

// Courses
const courses = await api.getCourses({ department: "Engineering" })
const course = await api.getCourse(1)

// Reviews
const reviews = await api.getReviews({ course_id: 1, sort_by: "net_rating" })
const newReview = await api.createReview({
  course_id: 1,
  professor_id: 1,
  title: "Great course!",
  content: "...",
  rating: 5,
  attributes: "difficulty,workload"
})

// Like/Dislike
await api.likeReview(reviewId)
await api.dislikeReview(reviewId)

// User
const user = await api.getCurrentUser()
```

---

## Frontend Components Updated

### 1. **App.jsx** - Main entry point
- Routes between Login, Landing, and Reviews pages
- Navigation bar for switching pages
- Auth state management

### 2. **Landing.jsx** - Course discovery
- Fetches real courses from backend
- Filters by department and search
- Shows loading/error states
- User profile display

### 3. **Reviews.jsx** (NEW) - Review hub
- List approved reviews with filters
- Create new reviews form
- Like/dislike functionality
- Anonymous reviewer display

### 4. **Me.jsx** - User profile page
- Displays current user info from `/api/users/me`
- No longer shows personal email in profile

---

## Navigation Structure

```
App.jsx
├── Login.jsx (when not authenticated)
├── Landing.jsx (default - course discovery)
│   ├── Course listing with filters
│   ├── Department filter
│   └── User profile section
└── Reviews.jsx (new reviews page)
    ├── Create review form
    ├── Filter reviews by course/professor
    ├── Like/dislike reviews
    └── Smart ranking display
```

---

## How to Test

### 1. Sign In
- Navigate to login page
- Use an AUB email (@mail.aub.edu for students)
- Complete OAuth flow

### 2. Browse Courses
- Go to "Courses" tab (default)
- Search by course number or name
- Filter by department
- View course details

### 3. Write a Review
- Go to "Reviews" tab
- Click "Write a Review"
- Select course and professor
- Enter review details and rating
- Submit (sets status to "pending" until admin approves)

### 4. View Reviews
- Scroll through approved reviews
- Filter by course/professor
- Like/dislike to affect ranking
- Reviews sorted by newest, rating, or net_rating

---

## Key Features Implemented

✅ **Anonymity**: Only anonymous usernames shown in reviews  
✅ **Sign-In**: OAuth2 with Entra ID integration  
✅ **Course Discovery**: Real-time filtering and search  
✅ **Review Posting**: Full CRUD with moderation workflow  
✅ **Smart Ranking**: Like/dislike affects visibility order  
✅ **Error Handling**: Loading states and error messages  
✅ **Responsive Design**: Mobile-friendly layouts  

---

## Environment Variables

Frontend needs `.env` file:

```
VITE_BACKEND_URL=http://localhost:8000
```

Or defaults to `http://localhost:8000` if not set.

---

## What's Not Yet Implemented

- Admin moderation dashboard (skipped as requested)
- Professo approval for account creation
- Analytics/aggregated insights
- Review edit history
- Flagging inappropriate content (frontend side)
- Advanced filtering (by semester, year, etc.)
