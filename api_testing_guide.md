# API Authentication Testing Guide

This guide provides step-by-step instructions for testing the authentication endpoints using curl commands.

## Prerequisites

- Django development server running on `http://localhost:8000`
- A registered user account (or create one using the register endpoint)

## Base URL
```
BASE_URL="http://localhost:8000"
```

---

## Windows PowerShell Commands

**Note**: Windows PowerShell uses `Invoke-WebRequest` which has different syntax than bash curl. Use these commands for Windows:

### 1. User Registration (Windows)

```powershell
$body = @{
    email = "test@example.com"
    password = "SecurePassword123!"
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register/" -Method POST -ContentType "application/json" -Body $body
$response | ConvertTo-Json -Depth 10
```

### 2. User Login (Windows)

```powershell
$body = @{
    email = "test@example.com"
    password = "SecurePassword123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/login/" -Method POST -ContentType "application/json" -Body $body -SessionVariable session
$response | ConvertTo-Json -Depth 10

# Store token for later use
$token = $response.token
```

### 3. Test Authenticated Health Check (Windows)

```powershell
# Using Token Authentication
$headers = @{
    "Authorization" = "Token $token"
}
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/" -Method GET -Headers $headers
$response | ConvertTo-Json -Depth 10
```

### 4. Test Unauthorized Access (Windows)

```powershell
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health/" -Method GET
} catch {
    $_.Exception.Message
}
```

### 5. User Logout (Windows)

```powershell
$headers = @{
    "Authorization" = "Token $token"
}
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/logout/" -Method POST -Headers $headers
$response | ConvertTo-Json -Depth 10
```

---

## Linux/macOS Bash Commands

### 1. User Registration

Create a new user account:

```bash
curl -X POST "${BASE_URL}/api/v1/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

**Expected Response:**
```json
{
  "user": {
    "id": 1,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "is_email_verified": false,
    "created_at": "2023-12-18T12:00:00Z"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "message": "Registration successful. Please check your email for verification.",
  "email_sent": true
}
```

## 2. User Login

Login with existing credentials:

```bash
curl -X POST "${BASE_URL}/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

**Expected Response:**
```json
{
  "user": {
    "id": 1,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User",
    "is_email_verified": false,
    "created_at": "2023-12-18T12:00:00Z"
  },
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "message": "Login successful"
}
```

## 3. Test Authenticated Health Check

Access the protected health endpoint using token authentication:

```bash
# Using Token Authentication
curl -X GET "${BASE_URL}/api/v1/health/" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json"
```

Or using session cookies:

```bash
# Using Session Authentication
curl -X GET "${BASE_URL}/api/v1/health/" \
  -b cookies.txt \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "status": "healthy",
  "message": "Timber BE API is running",
  "version": "1.0.0",
  "authenticated_user": {
    "id": 1,
    "email": "test@example.com",
    "is_email_verified": false
  },
  "endpoints": {
    "auth": {
      "register": "/api/v1/auth/register/",
      "login": "/api/v1/auth/login/",
      "logout": "/api/v1/auth/logout/",
      "profile": "/api/v1/auth/profile/",
      "verify_email": "/api/v1/auth/verify-email/<token>/",
      "password_reset": "/api/v1/auth/password-reset/request/",
      "password_change": "/api/v1/auth/password/change/"
    },
    "organizations": {
      "list": "/api/v1/organizations/",
      "create": "/api/v1/organizations/create/",
      "detail": "/api/v1/organizations/<id>/",
      "subscriptions": "/api/v1/organizations/subscriptions/"
    },
    "docs": {
      "swagger": "/api/docs/",
      "redoc": "/api/redoc/",
      "schema": "/api/schema/"
    }
  },
  "statistics": {
    "total_users": 1,
    "total_organizations": 0,
    "total_subscriptions": 0
  }
}
```

## 4. Test Unauthorized Access

Try accessing the health endpoint without authentication:

```bash
curl -X GET "${BASE_URL}/api/v1/health/" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

## 5. User Logout

Logout the user (invalidates the token and session):

```bash
# Using Token Authentication
curl -X POST "${BASE_URL}/api/v1/auth/logout/" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json"
```

Or using session cookies:

```bash
# Using Session Authentication
curl -X POST "${BASE_URL}/api/v1/auth/logout/" \
  -b cookies.txt \
  -c cookies.txt \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "message": "Logout successful"
}
```

## 6. Verify Token is Invalidated

Try using the token after logout:

```bash
curl -X GET "${BASE_URL}/api/v1/health/" \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b" \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "detail": "Invalid token."
}
```

## 7. Get User Profile

Access the protected profile endpoint:

```bash
curl -X GET "${BASE_URL}/api/v1/auth/profile/" \
  -H "Authorization: Token YOUR_NEW_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

## 8. Change Password

Change user password while authenticated:

```bash
curl -X POST "${BASE_URL}/api/v1/auth/password/change/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePassword123!",
    "new_password": "NewSecurePassword456!"
  }'
```

## Testing Script

Here's a complete bash script for testing the entire authentication flow:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"
EMAIL="test$(date +%s)@example.com"
PASSWORD="SecurePassword123!"

echo "=== Testing Authentication Flow ==="
echo "Email: $EMAIL"
echo ""

# 1. Register
echo "1. Registering new user..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\", \"first_name\": \"Test\", \"last_name\": \"User\"}")

echo "$REGISTER_RESPONSE" | jq .

TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.token')
echo "Token: $TOKEN"
echo ""

# 2. Login
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/auth/login/" \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

echo "$LOGIN_RESPONSE" | jq .
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token')
echo ""

# 3. Test authenticated health check
echo "3. Testing authenticated health check..."
HEALTH_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/v1/health/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json")

echo "$HEALTH_RESPONSE" | jq .
echo ""

# 4. Test unauthorized access
echo "4. Testing unauthorized access..."
UNAUTH_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/v1/health/" \
  -H "Content-Type: application/json")

echo "$UNAUTH_RESPONSE" | jq .
echo ""

# 5. Logout
echo "5. Logging out..."
LOGOUT_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/auth/logout/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json")

echo "$LOGOUT_RESPONSE" | jq .
echo ""

# 6. Verify token is invalidated
echo "6. Verifying token is invalidated..."
INVALID_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/v1/health/" \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json")

echo "$INVALID_RESPONSE" | jq .
echo ""

echo "=== Authentication Flow Test Complete ==="
```

## Important Notes

1. **Token vs Session Authentication**: The API supports both token-based and session-based authentication. Token authentication is ideal for APIs, while session authentication works well for web applications.

2. **CSRF Protection**: For session-based authentication with POST/PUT/DELETE requests, you may need to include CSRF tokens. The current configuration allows API requests without CSRF when using proper authentication headers.

3. **Token Storage**: Store tokens securely on the client side. Tokens are invalidated on logout.

4. **Session Duration**: Sessions are configured to last 24 hours (86400 seconds) as per `SESSION_COOKIE_AGE` setting.

5. **Testing with Postman/Insomnia**: You can also use these API testing tools with the same endpoints and request bodies.

## Troubleshooting

- **401 Unauthorized**: Check that your token is correct and not expired
- **403 Forbidden**: Ensure the user has the required permissions
- **400 Bad Request**: Verify the request body format and required fields
- **CSRF Token Missing**: Add `X-CSRFToken` header for session-based requests
