# Rhythm Game Project - Claude Instructions

## Project Overview
A rhythm game where players hit directional notes (up, down, left, right) that spawn from screen edges and move toward a subdivided circle in the center. Players must hit notes when they reach the circle's corresponding section. Backend focus with server-side data persistence.

## Tech Stack
- **Game Engine**: Godot
- **Backend**: Python with FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 (async)
- **Migration Tool**: Alembic
- **Connection Pooling**: asyncpg via SQLAlchemy
- **Validation**: Pydantic v2
- **Authentication**: JWT tokens (for future expansion)

## Game Mechanics

### Core Gameplay
- Central circle divided into 4 sections: Up, Down, Left, Right
- Small square notes spawn at screen edges
- Notes move toward center at constant speed
- Player must press corresponding key (arrow keys/WASD) when note reaches the circle
- Hit timing determines score (Perfect/Good/Bad/Miss)

### Shields System
- Players start with 0 shields (configurable)
- Shields absorb missed notes without penalty
- Shields can be purchased in shop with earned funds
- Each shield = 1 miss forgiveness and is consumed when activated during a run

## Menus Required

1. **Login Screen**
  - Username and password entry
  - Login
  - Register

2. **Home Screen**
  - Start Game
  - Leaderboard
  - Shop
  - Logout
  - Quit

3. **Song Selection Screen**
  - Display available tracks
  - Select song before starting
  - Back to home screen

4. **Pause Menu** (during gameplay)
  - Resume
  - Restart
  - Main Menu
  - Quit

5. **Leaderboard Menu**
  - Display top scores (username + score)
  - Back to main menu

6. **Shop Menu**
  - Display current account funds
  - Purchase shields (price per shield)
  - Display current shield count
  - Back to main menu

7. **Game Over Screen**
  - Retry current song
  - Continue to song selection

8. **Quit Menu**
  - Confirmation dialog before exiting

## Server Architecture

### Project Structure
```
rhythm/
├── scenes/
│   ├── login.tscn
│   ├── main_menu.tscn           # Home screen after login
│   ├── music_select.tscn
│   ├── game.tscn
│   ├── leaderboard.tscn
│   ├── shop.tscn
│   ├── pause_menu.tscn
│   └── quit_dialog.tscn
├── scripts/
│   ├── autoloads/
│   ├── game/
│   ├── network/
│   └── ui/
└── assets/

backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Environment config & settings
│   ├── database.py             # Database connection & session management
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── score.py
│   │   └── purchase.py
│   ├── schemas/                # Pydantic models (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── score.py
│   │   └── shop.py
│   ├── api/                    # Route handlers (endpoints)
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── scores.py
│   │   ├── shop.py
│   │   └── leaderboard.py
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── score_service.py
│   │   └── shop_service.py
│   └── utils/                  # Helper functions
│       ├── __init__.py
│       ├── security.py         # Password hashing, token generation
│       └── exceptions.py       # Custom exceptions
├── alembic/                    # Database migrations
│   ├── versions/
│   └── env.py
├── tests/
├── alembic.ini
├── requirements.txt
└── .env                        # Environment variables
```

### Architecture Layers

#### 1. Database Layer (`database.py`)
**Purpose**: Manage PostgreSQL connections and sessions

**Key Components**:
- **Async Engine**: SQLAlchemy async engine with connection pooling
  - Pool size: 20 connections
  - Max overflow: 10 additional connections
  - Pool pre-ping: Verify connections before use
  - Pool recycle: Reset connections after 1 hour
- **Session Factory**: Creates database sessions for each request
- **Dependency Injection**: `get_db()` provides sessions to route handlers
  - Auto-commits on success
  - Auto-rolls back on error
  - Always closes session properly
- **Base Class**: Declarative base for all ORM models

**Connection String Format**:
```
postgresql+asyncpg://username:password@host:port/database_name
```

**Session Management Pattern**:
- Each API request gets a fresh database session
- Session is injected as dependency into route handlers
- Automatic transaction management (commit/rollback)
- Connection pooling handles concurrent requests efficiently
- Sessions are always closed, even if errors occur

#### 2. Models Layer (`models/`)
**Purpose**: Define database tables using SQLAlchemy ORM

**Tables**:

**Users** (`models/user.py`):
- `id` (String/UUID, Primary Key)
- `username` (String, Unique, Indexed)
- `password_hash` (String)
- `account_funds` (Numeric/Decimal)
- `shields_owned` (Integer)
- `created_at` (DateTime)
- Relationships: one-to-many with Scores and Purchases

**Scores** (`models/score.py`):
- `id` (String/UUID, Primary Key)
- `user_id` (Foreign Key → Users, cascade delete)
- `score` (Integer, Indexed descending for leaderboard)
- `achieved_at` (DateTime, Indexed)
- Relationship: many-to-one with User

**Purchases** (`models/purchase.py`):
- `id` (String/UUID, Primary Key)
- `user_id` (Foreign Key → Users, cascade delete)
- `item_type` (String) - e.g., "shield"
- `quantity` (Integer)
- `cost` (Numeric/Decimal)
- `purchased_at` (DateTime)
- Relationship: many-to-one with User

**Key Design Decisions**:
- UUIDs for all primary keys (better for distributed systems)
- Cascade deletes on foreign keys (maintain referential integrity)
- Indexes on frequently queried fields (username, score, timestamps)
- Decimal type for currency (avoid floating-point errors)
- Relationships use `back_populates` for bidirectional access

#### 3. Schemas Layer (`schemas/`)
**Purpose**: Pydantic models for request/response validation

**User Schemas** (`schemas/user.py`):
- `UserCreate`: username, password (for registration)
- `UserLogin`: username, password (for authentication)
- `UserResponse`: id, username, account_funds, shields_owned (no password!)
- `UserUpdate`: Optional fields for updating profile

**Score Schemas** (`schemas/score.py`):
- `ScoreCreate`: user_id, score, funds_earned
- `ScoreResponse`: id, user_id, score, achieved_at
- `LeaderboardEntry`: username, score (for leaderboard display)

**Shop Schemas** (`schemas/shop.py`):
- `ShopItem`: item_type, price, description
- `PurchaseRequest`: user_id, item_type, quantity
- `PurchaseResponse`: success, new_balance, new_shield_count

**Why Separate Schemas from Models**:
- Security: Don't expose password hashes in responses
- Validation: Enforce data rules before hitting database
- Flexibility: API contract independent from database structure
- Documentation: Auto-generates OpenAPI/Swagger docs

#### 4. Services Layer (`services/`)
**Purpose**: Business logic and database operations (keeps routes thin)

**UserService** (`services/user_service.py`):
- `create_user()`: Register new user with hashed password
- `authenticate_user()`: Verify credentials
- `get_user_by_id()`: Retrieve user data
- `update_funds()`: Add/subtract funds (with validation)
- `update_shields()`: Add/subtract shields (with validation)

**ScoreService** (`services/score_service.py`):
- `submit_score()`: Create score record AND update user funds atomically
- `get_leaderboard()`: Fetch top N scores with usernames (JOIN query)
- `get_user_best_score()`: Get user's personal best
- `get_user_score_history()`: List all scores for a user

**ShopService** (`services/shop_service.py`):
- `purchase_shields()`: 
  - Validate funds availability
  - Deduct cost from account
  - Add shields to inventory
  - Record purchase transaction
  - All in one database transaction (atomic)
- `get_shop_items()`: Return available items and prices
- `get_purchase_history()`: User's transaction history

**Service Layer Benefits**:
- Reusable business logic (use in multiple endpoints)
- Testable in isolation from HTTP layer
- Database queries encapsulated in one place
- Transaction management centralized
- Easy to add caching or additional logic later

#### 5. API Layer (`api/`)
**Purpose**: HTTP route handlers (thin wrappers around services)

**Pattern for All Endpoints**:
```python
# Pseudo-code pattern
@router.post("/endpoint")
async def endpoint_handler(
    request_data: Schema,           # Pydantic validates input
    db: AsyncSession = Depends(get_db)  # Inject database session
):
    service = SomeService(db)       # Create service with session
    result = await service.method(request_data)  # Call business logic
    return ResponseSchema(**result)  # Return validated response
```

**Users Routes** (`api/users.py`):
- `POST /users/register` - Create new account
- `POST /users/login` - Authenticate and return user data
- `GET /users/{user_id}` - Get user profile

**Scores Routes** (`api/scores.py`):
- `POST /scores` - Submit score after gameplay
  - Body: `{user_id, score, funds_earned}`
  - Atomically updates funds and creates score record

**Leaderboard Routes** (`api/leaderboard.py`):
- `GET /leaderboard?limit=10` - Get top scores

**Shop Routes** (`api/shop.py`):
- `GET /shop/items` - List available items
- `POST /shop/purchase` - Buy shields
  - Body: `{user_id, item_type, quantity}`
  - Validates funds, processes transaction

#### 6. Configuration Layer (`config.py`)
**Purpose**: Centralized settings management

**Settings Categories**:
- **Database**: Connection URL
- **Server**: Host, port, debug mode
- **Security**: Secret key, JWT algorithm, token expiration
- **Game Balance**: Shield prices, reward amounts

**Environment Variables** (`.env` file):
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/rhythm_game
SECRET_KEY=generate-with-openssl-rand-hex-32
DEBUG=True
SHIELD_PRICE=100
PERFECT_HIT_FUNDS=15
GOOD_HIT_FUNDS=10
```

**Benefits**:
- Easy to change settings without code changes
- Different configs for dev/staging/production
- Sensitive data (passwords, keys) not in code
- Type-safe access to settings via Pydantic

#### 7. Utilities Layer (`utils/`)
**Purpose**: Shared helper functions

**security.py**:
- `hash_password()`: Bcrypt password hashing
- `verify_password()`: Check password against hash
- `create_access_token()`: Generate JWT tokens (future)
- `verify_token()`: Validate JWT tokens (future)

**exceptions.py**:
- `UserAlreadyExistsError`: Username taken
- `InvalidCredentialsError`: Wrong password
- `InsufficientFundsError`: Can't afford purchase
- `UserNotFoundError`: User ID doesn't exist

**Custom exceptions allow**:
- Meaningful error messages
- Consistent error handling
- Different HTTP status codes per error type

### Database Transaction Management

**Atomic Operations**:
All multi-step operations are wrapped in transactions:

1. **Score Submission**:
   - Create Score record
   - Update User.account_funds
   - Both succeed or both fail (no partial updates)

2. **Shield Purchase**:
   - Check User.account_funds >= cost
   - Subtract cost from User.account_funds
   - Add to User.shields_owned
   - Create Purchase record
   - All or nothing

**How Transactions Work**:
- `get_db()` dependency provides session
- Session auto-commits on successful endpoint completion
- Session auto-rolls back if any exception occurs
- No manual transaction management needed in services

**Concurrency Handling**:
- Connection pool handles multiple simultaneous requests
- PostgreSQL row-level locking prevents race conditions
- Optimistic concurrency (could add version columns if needed)

### Database Migration Strategy

**Alembic for Schema Changes**:
```bash
# Create migration after model changes
alembic revision --autogenerate -m "add shield system"

# Apply migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

**Migration Best Practices**:
- Never edit models and database directly
- Always create migration scripts
- Test migrations on dev database first
- Keep migrations in version control
- Can deploy schema changes before code changes

### Error Handling Strategy

**Three Levels of Error Handling**:

1. **Validation Errors** (Pydantic):
   - Caught automatically by FastAPI
   - Return 422 Unprocessable Entity
   - Example: Missing required field, wrong data type

2. **Business Logic Errors** (Custom Exceptions):
   - Raised by services
   - Caught by exception handlers in main.py
   - Return appropriate status codes (400, 401, 404, etc.)
   - Example: Insufficient funds, user not found

3. **Database Errors** (SQLAlchemy):
   - Connection failures, constraint violations
   - Automatically trigger rollback
   - Return 500 Internal Server Error
   - Log for debugging

**Example Error Response**:
```json
{
  "detail": "Insufficient funds. Need 300, have 150"
}
```

### Security Considerations

**Current Implementation**:
- Password hashing with bcrypt (cost factor 12+)
- No plaintext passwords stored
- SQL injection prevention (SQLAlchemy parameterized queries)
- Input validation (Pydantic schemas)

**Future Enhancements**:
- JWT token authentication
- Rate limiting on endpoints
- HTTPS only in production
- CORS configuration for Godot client
- Refresh tokens for persistent login

### Performance Optimization

**Database Level**:
- Connection pooling (reuse connections)
- Indexes on queried columns
- LIMIT clauses on large queries
- SELECT only needed columns

**Application Level**:
- Async operations (non-blocking I/O)
- Efficient JOIN queries for leaderboard
- Caching frequent queries (future)
- Pagination for long lists

**Monitoring Points**:
- Slow query log in PostgreSQL
- Connection pool utilization
- API endpoint response times
- Error rates per endpoint

## API Endpoints Reference

### User Management

**Register New User**
```
POST /users/register
Body: {
  "username": "player123",
  "password": "secure_password"
}
Response: {
  "id": "uuid-string",
  "username": "player123",
  "account_funds": 0.0,
  "shields_owned": 0
}
```

**Login**
```
POST /users/login
Body: {
  "username": "player123",
  "password": "secure_password"
}
Response: {
  "id": "uuid-string",
  "username": "player123",
  "account_funds": 150.50,
  "shields_owned": 3
}
```

**Get User Profile**
```
GET /users/{user_id}
Response: {
  "id": "uuid-string",
  "username": "player123",
  "account_funds": 150.50,
  "shields_owned": 3,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Gameplay

**Submit Score**
```
POST /scores
Body: {
  "user_id": "uuid-string",
  "score": 1250,
  "funds_earned": 45.50
}
Response: {
  "id": "score-uuid",
  "user_id": "uuid-string",
  "score": 1250,
  "achieved_at": "2024-01-15T11:00:00Z"
}
Note: Funds are automatically added to user account
```

**Get Leaderboard**
```
GET /leaderboard?limit=10
Response: [
  {"username": "player1", "score": 5000},
  {"username": "player2", "score": 4800},
  ...
]
```

**Get User Best Score**
```
GET /users/{user_id}/best-score
Response: {
  "best_score": 5000
}
```

### Shop

**Get Shop Items**
```
GET /shop/items
Response: [
  {
    "item_type": "shield",
    "price": 100,
    "description": "Protects against one missed note"
  }
]
```

**Purchase Shields**
```
POST /shop/purchase
Body: {
  "user_id": "uuid-string",
  "item_type": "shield",
  "quantity": 3
}
Response: {
  "success": true,
  "new_balance": 50.50,
  "new_shield_count": 6,
  "purchase_id": "purchase-uuid"
}
Errors:
- 400: Insufficient funds
- 404: User not found
```

## Godot Integration

### HTTP Request Pattern

**Example: Submit Score from Godot**
```gdscript
func submit_score(user_id: String, score: int, funds: float):
    var http = HTTPRequest.new()
    add_child(http)
    http.request_completed.connect(_on_score_submitted)
    
    var url = "http://localhost:8000/scores"
    var headers = ["Content-Type: application/json"]
    var body = JSON.stringify({
        "user_id": user_id,
        "score": score,
        "funds_earned": funds
    })
    
    http.request(url, headers, HTTPClient.METHOD_POST, body)

func _on_score_submitted(result, response_code, headers, body):
    if response_code == 200:
        var json = JSON.parse_string(body.get_string_from_utf8())
        print("Score submitted successfully!")
    else:
        print("Error submitting score: ", response_code)
```

### State Management in Godot

**Store User Session**:
- After login, store user_id and username locally
- Use autoload singleton for global access
- Refresh user data periodically to show updated funds/shields

**Game Flow**:
1. Login page → Home screen → Song selection
2. Song selection → Start Game → Use user_id for gameplay
3. End Game → Retry or return to song selection
4. Shop → Fetch user data → Purchase → Update local state
5. Leaderboard → Fetch and display

## Implementation Priorities

### Phase 1: Backend Foundation
1. Set up FastAPI project structure
2. Configure PostgreSQL database
3. Create SQLAlchemy models (User, Score, Purchase)
4. Set up Alembic for migrations
5. Implement database.py with connection pooling
6. Create Pydantic schemas

**Deliverable**: Database running with tables created

### Phase 2: Core Services
1. Implement UserService (register, login, get_user)
2. Implement ScoreService (submit, leaderboard)
3. Implement ShopService (purchase shields)
4. Add password hashing in utils/security.py
5. Add custom exceptions

**Deliverable**: Business logic complete and testable

### Phase 3: API Endpoints
1. Create user endpoints (register, login, profile)
2. Create score endpoints (submit, leaderboard)
3. Create shop endpoints (items, purchase)
4. Add error handlers in main.py
5. Test all endpoints with Postman/curl

**Deliverable**: Fully functional REST API

### Phase 4: Godot Core Gameplay
1. Create basic game scene with center circle
2. Implement note spawning system
3. Add input detection (arrow keys/WASD)
4. Implement hit detection timing
5. Add scoring logic
6. Test with placeholder assets

**Deliverable**: Playable game loop (local, no backend)

### Phase 5: Integration
1. Add HTTP client to Godot (HTTPRequest nodes)
2. Create UserSession autoload singleton
3. Connect login/register to backend
4. Connect gameplay to score submission
5. Implement leaderboard fetching and display
6. Test full loop: login → play → submit → leaderboard

**Deliverable**: Game communicates with backend

### Phase 6: Shop & Shields
1. Implement shop UI in Godot
2. Connect to shop endpoints
3. Add shield purchase functionality
4. Implement shield consumption in gameplay
5. Test: earn funds → buy shields → use in game

**Deliverable**: Full economy system working

### Phase 7: Menus & Polish
1. Create all menu UIs (main, pause, leaderboard, shop, quit)
2. Add menu navigation and state management
3. Implement pause functionality
4. Add basic visual feedback (particles, score pop-ups)
5. Replace placeholder assets with AI-generated art

**Deliverable**: Complete game ready for submission

## Testing Strategy

### Backend Testing
**Unit Tests** (pytest):
- Test each service method in isolation
- Mock database sessions
- Test error cases (insufficient funds, user not found, etc.)

**Integration Tests**:
- Test API endpoints with real database
- Use test database (separate from dev/prod)
- Test transaction rollback scenarios

**Load Testing** (locust or similar):
- Simulate many concurrent users
- Test connection pool under load
- Identify bottlenecks

### Godot Testing
**Manual Testing**:
- Test each menu flow
- Test gameplay timing accuracy
- Test error handling (network errors)
- Test edge cases (0 funds, 0 shields)

**User Acceptance**:
- Have classmates/friends play
- Gather feedback on difficulty
- Adjust shield prices and rewards

## Data Seeding for Development

**Create Sample Users**:
```sql
INSERT INTO users (id, username, password_hash, account_funds, shields_owned)
VALUES 
  ('test-user-1', 'alice', '<hashed>', 500.0, 5),
  ('test-user-2', 'bob', '<hashed>', 200.0, 2);
```

**Create Sample Scores**:
```sql
INSERT INTO scores (id, user_id, score)
VALUES
  ('score-1', 'test-user-1', 5000),
  ('score-2', 'test-user-2', 4800);
```

## Scoring System Design

**Hit Timing Windows**:
- **Perfect**: ±50ms from target = 100 points + 15 funds
- **Good**: ±100ms from target = 50 points + 10 funds
- **Bad**: ±150ms from target = 10 points + 5 funds
- **Miss**: Outside window or no input = 0 points, 0 funds
  - If shields > 0: consume shield, continue
  - If shields = 0: game over

**Combo System** (optional enhancement):
- Consecutive perfect hits increase multiplier
- Multiplier applies to both points and funds
- Miss breaks combo

**Funds Earning Formula**:
```
total_funds = (perfect_hits * 15) + (good_hits * 10) + (bad_hits * 5)
            = funds for this game session
            = added to user.account_funds on score submission
```

## Shop Economy Balance

**Initial Prices**:
- 1 Shield = 100 funds
- (Can add more items later)

**Expected Earnings**:
- Average player: ~150-300 funds per game
- Good player: ~400-600 funds per game
- Expert player: ~700+ funds per game

**Shield Value**:
- Each shield = 1 extra mistake forgiven
- Player should earn 1-3 shields per game session
- Balance keeps players engaged without being too grindy

**Adjustment Recommendations**:
- If players always have too many shields: increase price or decrease rewards
- If players never buy shields: decrease price or increase rewards
- Monitor via purchase_history table

## Future Enhancements (Post-MVP)

### Gameplay
- Multiple difficulty levels (faster notes, more lanes)
- Different note patterns/rhythms synced to music
- Special notes (hold notes, double notes)
- Visual themes/skins
- Multiple songs to choose from

### Backend
- JWT authentication with refresh tokens
- User profile customization (avatars, colors)
- Friend system and friend leaderboards
- Daily challenges with bonus rewards
- Achievement system
- Admin dashboard for monitoring

### Shop Expansion
- Cosmetic items (note skins, circle themes)
- Power-ups (score multipliers, slow-mo)
- Premium currency (optional)

### Analytics
- Track average score per user
- Monitor most difficult timing windows
- A/B test different reward amounts
- Track shield usage patterns

## Deployment Considerations

### Development Environment
- Run locally: PostgreSQL on localhost:5432
- FastAPI dev server: `uvicorn app.main:app --reload`
- Godot: Export to desktop for testing

### Production Environment (Future)
- **Database**: Hosted PostgreSQL (AWS RDS, DigitalOcean, etc.)
- **Backend**: Docker container on cloud VM
- **Reverse Proxy**: Nginx for HTTPS
- **Domain**: Point to backend IP
- **Godot**: Update API URL to production domain

### Environment Variables
**Development** (.env):
```
DATABASE_URL=postgresql+asyncpg://dev_user:dev_pass@localhost:5432/rhythm_dev
DEBUG=True
```

**Production**:
```
DATABASE_URL=postgresql+asyncpg://prod_user:secure_pass@prod-db.host:5432/rhythm_prod
DEBUG=False
SECRET_KEY=<strong-random-key>
```

## Assets Needed (AI Generation Prompts)

### Temporary Assets (for prototyping)
- Use colored rectangles/circles in Godot
- No AI generation needed initially

### Final Assets (AI-generated)

**Notes** (4 variations):
- "Simple geometric square icon, flat design, red color, game sprite"
- "Simple geometric square icon, flat design, blue color, game sprite"
- "Simple geometric square icon, flat design, green color, game sprite"
- "Simple geometric square icon, flat design, yellow color, game sprite"

**Center Circle**:
- "Circular target divided into 4 quadrants, minimalist game UI, flat design, glowing edges"

**Background**:
- "Abstract geometric background pattern, dark theme, music rhythm game aesthetic"

**UI Elements**:
- "Modern game UI button, flat design, rounded corners"
- "Score counter display, digital aesthetic, glowing numbers"

**Effects**:
- "Particle explosion effect, colorful sparkles, game VFX sprite sheet"
- "Success hit indicator, glowing ring animation, game feedback"

## Troubleshooting Guide

### Common Backend Issues

**Database Connection Failed**:
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify DATABASE_URL in .env
- Check firewall rules
- Test connection: `psql -U username -d database_name`

**Migration Errors**:
- Rollback: `alembic downgrade -1`
- Delete alembic_version table if stuck
- Recreate database and migrate from scratch

**Session/Transaction Errors**:
- Check get_db() dependency is used in routes
- Verify services receive db session
- Check for uncommitted transactions

### Common Godot Issues

**HTTP Request Failed**:
- Check backend is running on correct port
- Verify URL in Godot code
- Check CORS settings in FastAPI (add middleware)
- Test endpoint with Postman first

**JSON Parsing Errors**:
- Verify response body is valid JSON
- Check Content-Type header
- Print raw response for debugging

**Timing Issues**:
- Adjust hit windows in game settings
- Add visual indicators for hit zones
- Test on different frame rates

## Success Criteria

### Minimum Viable Product (MVP)
- ✅ User can register and login
- ✅ User can play game with 4-directional notes
- ✅ Score is calculated and submitted to server
- ✅ Leaderboard displays top 10 scores
- ✅ User can buy shields with earned funds
- ✅ Shields protect against missed notes
- ✅ All menus functional

### Technical Requirements
- ✅ Backend uses proper service layer architecture
- ✅ Database uses transactions for atomic operations
- ✅ API returns appropriate status codes and error messages
- ✅ Connection pooling configured
- ✅ Passwords hashed, never stored plaintext
- ✅ Input validation on all endpoints

### Presentation Requirements
- Demonstrate full gameplay loop
- Show leaderboard with multiple users
- Show shop purchase working
- Explain backend architecture (diagram helpful)
- Discuss database design decisions
- Highlight transaction safety

## Questions to Address During Development

1. **Authentication**: For school project, simple username/password is fine. Add JWT tokens only if time permits.

2. **User Sessions**: Store user_id locally in Godot after login. No persistent sessions needed (login each time for now).

3. **Offline Mode**: Always-online is fine for school project. Could add offline practice mode later.

4. **Shield Limits**: No max shield count for now. Could add cap (e.g., 10 shields max) to balance economy.

5. **Score Validation**: Trust client for now. In production, validate gameplay server-side or use anti-cheat.

6. **Multiple Games**: One game mode, one difficulty for MVP. Add variations if time permits.

## Notes for Claude Code

When implementing this project:

1. **Start with backend structure**: Create all folders and __init__.py files first
2. **Database first**: Get PostgreSQL connected and models working before API
3. **Test incrementally**: Test each service method before moving to routes
4. **Use Alembic**: Don't manually create tables, use migrations from start
5. **Environment config**: Set up .env file early, never hardcode credentials
6. **Error handling**: Add try-except blocks and meaningful error messages
7. **Type hints**: Use Python type hints everywhere for better IDE support
8. **Async/await**: Remember to use async functions and await database calls
9. **Session management**: Always use get_db() dependency, never create sessions manually
10. **Testing**: Write at least basic tests for services before connecting to Godot

## Final Notes

**Backend Focus**: This project emphasizes proper server architecture, database design, and API implementation. The Godot game is functional but simple by design.

**Learning Objectives**:
- Understand layered architecture (models, services, routes)
- Practice async Python with SQLAlchemy
- Implement RESTful API design
- Manage database transactions and connections
- Handle errors gracefully
- Integrate game client with backend server

**Time Estimate**:
- Backend: 15-20 hours
- Godot: 10-15 hours
- Integration & Testing: 5-10 hours
- Total: 30-45 hours

Good luck with your project!
