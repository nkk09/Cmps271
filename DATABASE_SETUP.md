# Database Setup - PostgreSQL with Anonymous Users

## Overview

Users are authenticated via Entra ID (Microsoft) but stored anonymously in the database. Each user gets a pseudorandom username like `ColorfulFlower4521` instead of storing their real name or email.

## Architecture

### User Anonymization

```
Entra ID Login
    ↓
Entra ID verifies email + password
    ↓
App receives entra_oid (unique object ID)
    ↓
App generates pseudorandom username: ColorfulFlower4521
    ↓
User stored in DB with anonymous username
    ↓
Session cookie contains: {user_id, username, role, entra_oid}
```

### Data Flow

1. **Authentication**: Handled by Microsoft Entra ID
2. **Identity Storage**: Tracked by `entra_oid` (unique, immutable)
3. **Public Identity**: Pseudorandom username for reviews/posts
4. **Privacy**: Real email stored internally but not displayed

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,        -- e.g., "ColorfulFlower4521"
    entra_oid VARCHAR(255) UNIQUE NOT NULL,      -- Microsoft's Object ID
    entra_email VARCHAR(255) NOT NULL,           -- User's email (internal only)
    role VARCHAR(20) DEFAULT 'student',          -- "student" or "professor"
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);
```

### Username Generation

Usernames are generated using:
- **Adjectives** (50 options): colorful, bright, swift, bold, calm, etc.
- **Nouns** (50 options): flower, river, mountain, forest, ocean, etc.
- **Numbers** (0-9999): 0-9999

**Format**: `[Adjective][Noun][Number]`

**Examples**:
- `ColorfulFlower4521`
- `BrightStar823`
- `SwiftEagle156`
- `CalmOcean9999`

**Uniqueness**: System ensures no duplicate usernames. If collision occurs (extremely rare), generates new one.

**Privacy**: Usernames are completely unrelated to real identity.

## Setup

### Prerequisites

```bash
# Install PostgreSQL 12+
# Create a database and user for the application
```

### 1. PostgreSQL Setup

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE aub_reviews;

# Create user
CREATE USER reviews_user WITH PASSWORD 'your-secure-password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE aub_reviews TO reviews_user;

# Exit
\q
```

### 2. Configure .env

```env
ENV=dev
DATABASE_URL=postgresql://reviews_user:your-secure-password@localhost:5432/aub_reviews
```

### 3. Run Application

```bash
uvicorn app.main:app --reload
```

**On startup**, the app automatically:
1. Connects to PostgreSQL
2. Creates tables (if they don't exist)
3. Ready to accept logins

## User Creation Flow

When a user logs in via Entra ID:

```python
# 1. After OAuth2 callback:
claims = decode_id_token(id_token)
user_info = entra_client.extract_user_info(claims)
# user_info = {
#   'user_id': 'entra-oid-123...',
#   'email': 'student@aub.edu.lb',
#   'name': 'John Doe',
#   'role': 'student'
# }

# 2. Create or update in database:
user = User.create_or_update(
    db,
    entra_oid=user_info['user_id'],
    entra_email=user_info['email'],
    role=user_info['role']
)
# Returns: User(id=1, username='ColorfulFlower4521', role='student')

# 3. Session cookie contains:
# {
#   'user_id': 1,
#   'username': 'ColorfulFlower4521',
#   'role': 'student',
#   'entra_oid': 'entra-oid-123...'
# }
```

## Querying Users

### Get User by Session

```python
from app.core.session import require_user

# In an endpoint:
@app.get("/me")
def get_me(request: Request):
    user_session = require_user(request, settings.SESSION_SECRET)
    # Returns: {user_id, username, role, entra_oid}
    return user_session
```

### Query from Database

```python
from app.models.user import User

# Get by username
user = db.query(User).filter(User.username == "ColorfulFlower4521").first()

# Get by entra_oid (linked to Entra ID)
user = db.query(User).filter(User.entra_oid == "entra-uuid").first()

# Get all active users
users = db.query(User).filter(User.is_active == True).all()
```

## Privacy & Security

### What's Stored
✅ Pseudorandom anonymous username
✅ Unique Entra ID object ID
✅ Email (for internal reference only)
✅ Role (student/professor)
✅ Login timestamps

### What's NOT Stored
❌ Real name
❌ Password (handled by Microsoft)
❌ Personal information
❌ Phone number
❌ Address

### Email Handling
- Email stored in `entra_email` column (for validation)
- **Never displayed** publicly
- Used only to prevent duplicate enrollments
- Only accessible to admins via direct DB query

### Anonymity on Reviews/Posts
When a student writes a review, it shows:
- Username: `ColorfulFlower4521`
- Role: `student`
- **NOT** their real name or email

## Production Deployment

### 1. Use Strong Database Password
```bash
# Generate secure password
openssl rand -base64 32
```

### 2. Configure Production Database
```env
DATABASE_URL=postgresql://reviews_user:YOUR-STRONG-PASSWORD@prod-db-host:5432/aub_reviews
```

### 3. Enable SSL/TLS
```env
# PostgreSQL with SSL
DATABASE_URL=postgresql://reviews_user:password@host:5432/aub_reviews?sslmode=require
```

### 4. Database Backups
```bash
# Backup
pg_dump aub_reviews > backup.sql

# Restore
psql aub_reviews < backup.sql
```

## Troubleshooting

### "Connection refused"
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify connection string in `.env`
- Check firewall rules

### "FATAL: role reviews_user does not exist"
```bash
# Create user
psql -U postgres -c "CREATE USER reviews_user WITH PASSWORD 'password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE aub_reviews TO reviews_user;"
```

### "database aub_reviews does not exist"
```bash
psql -U postgres -c "CREATE DATABASE aub_reviews;"
```

### Username Generation Issues
- Check `app.models.user` module loads correctly
- Verify random seed in production
- System regenerates on collision automatically

## Next Steps

- [ ] Add Courses table
- [ ] Add Reviews table
- [ ] Add ratings/ratings table
- [ ] Implement database migrations (Alembic)
- [ ] Set up automated backups
- [ ] Add audit logging for sensitive queries
- [ ] Implement GDPR compliance (user data export/delete)
