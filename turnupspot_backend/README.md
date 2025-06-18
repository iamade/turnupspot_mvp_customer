# TurnUp Spot Backend API

A comprehensive FastAPI backend for the TurnUp Spot platform - Events, Sports, and Vendor Management.

## Features

- **User Management**: Registration, authentication, profiles
- **Sport Groups**: Create and manage sports groups, team formation, game scheduling
- **Events**: Event creation, registration, attendee management
- **Vendors**: Vendor profiles, service listings, business management
- **Games**: Live game management, scoring, player check-ins
- **Chat**: Real-time messaging for groups and events
- **Authentication**: JWT-based authentication with role-based access control
- **File Upload**: Support for images and documents
- **Real-time Features**: WebSocket support for live updates

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **PostgreSQL**: Primary database
- **Redis**: Caching and session management
- **Alembic**: Database migration tool
- **JWT**: JSON Web Tokens for authentication
- **WebSockets**: Real-time communication
- **Pytest**: Testing framework

## Project Structure

```
turnupspot_backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   └── main.py
├── alembic/
├── tests/
├── requirements.txt
└── README.md
```

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis (optional, for caching)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd turnupspot_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   # Create database
   createdb turnupspot_db
   
   # Run migrations
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/turnupspot_db

# JWT
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis (optional)
REDIS_URL=redis://localhost:6379

# AWS S3 (for file uploads)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_BUCKET_NAME=turnupspot-uploads

# Stripe (for payments)
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key

# SendGrid (for emails)
SENDGRID_API_KEY=your-sendgrid-api-key
FROM_EMAIL=noreply@turnupspot.com
```

## API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/{user_id}` - Get user by ID

### Sport Groups
- `POST /api/v1/sport-groups/` - Create sport group
- `GET /api/v1/sport-groups/` - Get all sport groups
- `GET /api/v1/sport-groups/{group_id}` - Get sport group by ID
- `PUT /api/v1/sport-groups/{group_id}` - Update sport group
- `POST /api/v1/sport-groups/{group_id}/join` - Join sport group
- `POST /api/v1/sport-groups/{group_id}/leave` - Leave sport group
- `GET /api/v1/sport-groups/{group_id}/members` - Get group members

### Events
- `POST /api/v1/events/` - Create event
- `GET /api/v1/events/` - Get all events
- `GET /api/v1/events/{event_id}` - Get event by ID
- `PUT /api/v1/events/{event_id}` - Update event
- `POST /api/v1/events/{event_id}/register` - Register for event
- `POST /api/v1/events/{event_id}/unregister` - Unregister from event

### Vendors
- `POST /api/v1/vendors/` - Create vendor profile
- `GET /api/v1/vendors/` - Get all vendors
- `GET /api/v1/vendors/me` - Get my vendor profile
- `PUT /api/v1/vendors/me` - Update my vendor profile
- `POST /api/v1/vendors/me/services` - Create vendor service

### Games
- `POST /api/v1/games/` - Create game
- `GET /api/v1/games/sport-group/{group_id}` - Get group games
- `GET /api/v1/games/{game_id}` - Get game by ID
- `POST /api/v1/games/{game_id}/timer` - Update game timer
- `POST /api/v1/games/{game_id}/score` - Update team score

### Chat
- `GET /api/v1/chat/rooms/{room_id}` - Get chat room
- `GET /api/v1/chat/rooms/{room_id}/messages` - Get chat messages
- `POST /api/v1/chat/rooms/{room_id}/messages` - Send message
- `WS /api/v1/chat/ws/{room_id}` - WebSocket connection

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migrations
alembic downgrade -1
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py
```

## Development

### Code Style

The project follows PEP 8 style guidelines. Use tools like `black` and `flake8` for formatting:

```bash
# Format code
black app/

# Check style
flake8 app/
```

### Adding New Features

1. Create models in `app/models/`
2. Create schemas in `app/schemas/`
3. Create API endpoints in `app/api/v1/endpoints/`
4. Add tests in `tests/`
5. Create database migration with Alembic

## Deployment

### Docker

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

- Use environment variables for all configuration
- Set up proper logging
- Use a production WSGI server like Gunicorn
- Set up database connection pooling
- Configure CORS properly
- Set up monitoring and health checks
- Use HTTPS in production

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License.