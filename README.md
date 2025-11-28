# Smart Bookmark Manager - Backend

A FastAPI-based backend for managing bookmarks, users, and tags with PostgreSQL database.

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### Running with Docker (Recommended)

1. Clone the repository
2. Run the application:
```bash
docker-compose up --build
```

The services will be available at:
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **PgAdmin**: http://localhost:8080 (admin@admin.com / password)

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up PostgreSQL database and update DATABASE_URL in `app/database.py`

3. Run the application:
```bash
uvicorn app.main:app --reload
```

### Running Tests

```bash
pytest
```

## Architecture Decisions

### Database Choice: PostgreSQL
- **Relational data**: Users, bookmarks, and tags have clear relationships
- **ACID compliance**: Ensures data consistency for bookmark management
- **Scalability**: Supports complex queries and indexing for large bookmark collections
- **JSON support**: Future-ready for metadata storage

### Project Structure
```
app/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response models
├── database.py          # Database configuration
└── routers/             # API endpoint modules
    ├── users.py         # User management endpoints
    ├── bookmarks.py     # Bookmark CRUD operations
    └── tags.py          # Tag management endpoints
tests/                   # Unit tests
```

### Key Design Decisions
- **Modular router structure**: Separates concerns and enables easy maintenance
- **Pydantic validation**: Ensures type safety and automatic API documentation
- **SQLAlchemy ORM**: Provides database abstraction and relationship management
- **Many-to-many relationship**: Bookmarks can have multiple tags

## API Endpoints

### Users
- `GET /api/users/` - List all users
- `GET /api/users/{id}` - Get user by ID
- `POST /api/users/` - Create new user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

### Bookmarks
- `GET /api/bookmarks/` - List bookmarks (optional user_id filter)
- `GET /api/bookmarks/{id}` - Get bookmark by ID
- `POST /api/bookmarks/` - Create new bookmark
- `PUT /api/bookmarks/{id}` - Update bookmark
- `DELETE /api/bookmarks/{id}` - Delete bookmark

### Tags
- `GET /api/tags/` - List all tags
- `GET /api/tags/{id}` - Get tag by ID
- `POST /api/tags/` - Create new tag
- `PUT /api/tags/{id}` - Update tag
- `DELETE /api/tags/{id}` - Delete tag

## ML Integration Approach

The current implementation provides a solid foundation for ML integration:

1. **Data Collection**: Bookmark URLs, titles, and descriptions provide rich content
2. **Tag Classification**: ML models could auto-suggest tags based on content
3. **Recommendation Engine**: User behavior patterns could drive bookmark recommendations
4. **Content Analysis**: Natural language processing for automatic categorization

Future ML endpoints would include:
- `/api/bookmarks/{id}/suggest-tags` - Auto-tag suggestions
- `/api/users/{id}/recommendations` - Personalized bookmark recommendations

## Production Roadmap

### Phase 1: Security & Authentication
- JWT-based authentication
- User sessions and refresh tokens
- Rate limiting and input sanitization
- HTTPS enforcement

### Phase 2: Advanced Features
- Full-text search across bookmarks
- Bookmark collections/folders
- Import/export functionality
- Real-time notifications

### Phase 3: ML Integration
- Content-based tag suggestions
- Duplicate bookmark detection
- Smart bookmark organization
- Usage analytics and insights

### Phase 4: Scalability
- Database optimization and indexing
- Caching layer (Redis)
- Microservices architecture
- Load balancing

## Honesty Declaration

I confirm that this submission is my own work. I have:
- [x] Not copied code from existing solutions or other candidates
- [x] Used AI assistants only for syntax help and debugging specific errors
- [x] Not received human help during the assignment period
- [x] Built the core logic and architecture myself
- [x] Cited any references used for specific solutions

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and Object-Relational Mapping
- **PostgreSQL**: Advanced open-source relational database
- **Pydantic**: Data validation and parsing using Python type annotations
- **Pytest**: Testing framework for Python
- **Docker**: Containerization for consistent deployment