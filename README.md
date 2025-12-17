# Timber BE - Django REST API

A Django REST API backend for the Timber application with user authentication, organizations, and subscription management.

## Features

- **User Authentication**: Email-based registration/login with token authentication
- **Email Verification**: Automatic email verification for new users
- **Password Recovery**: Secure password reset via email tokens
- **Organizations**: Multi-tenant organization management
- **Subscriptions**: Organization subscription tracking
- **API Documentation**: Automatic Swagger/OpenAPI docs (configurable)
- **PostgreSQL Support**: Configurable for local and production (AWS) databases
- **Admin Interface**: Full Django admin setup

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Virtualenv (recommended)

### Installation

1. **Create and activate virtual environment**:
```bash
# Using virtualenvwrapper
mkvirtualenv timber-be
workon timber-be

# Or using standard virtualenv
python -m venv venv
# Windows
venv\Scripts\activate
# Unix/Mac
source venv/bin/activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Setup database**:
```bash
# Create PostgreSQL database
createdb timber_be_dev

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser**:
```bash
python manage.py createsuperuser
# Or use the custom command
python manage.py create_user --superuser --email admin@example.com --username admin
```

6. **Collect static files**:
```bash
python manage.py collectstatic
```

7. **Run development server**:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - User login
- `POST /api/v1/auth/logout/` - User logout
- `GET /api/v1/auth/profile/` - Get user profile
- `PUT /api/v1/auth/profile/update/` - Update user profile
- `POST /api/v1/auth/verify-email/<token>/` - Verify email
- `POST /api/v1/auth/password-reset/request/` - Request password reset
- `POST /api/v1/auth/password-reset/confirm/` - Confirm password reset
- `POST /api/v1/auth/password/change/` - Change password

### Organizations
- `GET /api/v1/organizations/` - List user organizations
- `POST /api/v1/organizations/create/` - Create organization
- `GET /api/v1/organizations/<id>/` - Get organization details
- `PUT /api/v1/organizations/<id>/update/` - Update organization
- `GET /api/v1/organizations/<id>/members/` - List organization members

### Subscriptions
- `GET /api/v1/organizations/subscriptions/` - List subscriptions
- `POST /api/v1/organizations/subscriptions/create/` - Create subscription

### General
- `GET /api/v1/health/` - Health check and API info
- `GET /api/v1/statistics/` - API statistics (authenticated)

### Documentation
- `GET /api/docs/` - Swagger UI (if enabled)
- `GET /api/redoc/` - ReDoc (if enabled)
- `GET /api/schema/` - OpenAPI schema

## Management Commands

### Create User
```bash
# Interactive mode
python manage.py create_user

# With parameters
python manage.py create_user --email user@example.com --username johndoe --password mypassword

# Create superuser
python manage.py create_user --superuser --email admin@example.com --username admin --password adminpassword

# Create staff user
python manage.py create_user --staff --email staff@example.com --username staffuser --password staffpassword
```

## Email Configuration

The project supports multiple free SMTP services for development and testing:

### Option 1: Mailtrap (Recommended for Development)
- **Free tier**: 1000 emails/month
- **Setup**: Sign up at [mailtrap.io](https://mailtrap.io)

**Method A: Token Authentication (Recommended for newer plans)**
```bash
EMAIL_PROVIDER=mailtrap
MAILTRAP_AUTH_METHOD=token
EMAIL_HOST=smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_HOST_USER=api
EMAIL_HOST_PASSWORD=your-mailtrap-api-token
```

**Method B: Username/Password Authentication (Legacy)**
```bash
EMAIL_PROVIDER=mailtrap
MAILTRAP_AUTH_METHOD=password
EMAIL_HOST=smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-mailtrap-username
EMAIL_HOST_PASSWORD=your-mailtrap-password
```

### Option 2: Brevo (Sendinblue)
- **Free tier**: 300 emails/day
- **Setup**: Sign up at [brevo.com](https://www.brevo.com)
- **Configuration**:
```bash
EMAIL_PROVIDER=brevo
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-brevo-email@example.com
EMAIL_HOST_PASSWORD=your-brevo-api-key
```

### Option 3: Gmail
- **Setup**: Use app-specific password
- **Configuration**:
```bash
EMAIL_PROVIDER=gmail
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Development Mode
If no email credentials are provided in development mode, emails will be printed to the console automatically.

## Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `True` |
| `ENV` | Environment (`development`/`production`) | `development` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `DB_NAME` | Database name | `timber_be_dev` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `postgres` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `EMAIL_HOST` | SMTP server | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP port | `587` |
| `EMAIL_USE_TLS` | Use TLS | `True` |
| `EMAIL_HOST_USER` | SMTP username | `""` |
| `EMAIL_HOST_PASSWORD` | SMTP password | `""` |
| `FRONTEND_URL` | Frontend base URL | `http://localhost:3000` |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` |
| `ENABLE_SWAGGER` | Enable Swagger docs | `True` |

## Production Deployment

### AWS PostgreSQL Configuration
For production deployment with AWS RDS:

```bash
# Set environment variables
ENV=production
DB_HOST=your-rds-endpoint.rds.amazonaws.com
DB_NAME=your-production-db
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DEBUG=False
```

### Security Settings
In production, ensure:
- `DEBUG=False`
- Set a strong `SECRET_KEY`
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS
- Set `SESSION_COOKIE_SECURE=True`
- Set `CSRF_COOKIE_SECURE=True`

## Docker Support

The project includes Docker configuration for containerized deployment:

```bash
# Build and run
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
