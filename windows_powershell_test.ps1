# Windows PowerShell Authentication Testing Script
# Run this script in PowerShell to test the complete authentication flow

$BASE_URL = "http://localhost:8000"
$EMAIL = "test$(Get-Date -Format 'yyyyMMddHHmmss')@example.com"
$PASSWORD = "SecurePassword123!"

Write-Host "=== Testing Authentication Flow ===" -ForegroundColor Green
Write-Host "Email: $EMAIL" -ForegroundColor Yellow
Write-Host ""

# 1. Register
Write-Host "1. Registering new user..." -ForegroundColor Cyan
try {
    $body = @{
        email = $EMAIL
        password = $PASSWORD
        first_name = "Test"
        last_name = "User"
        password_confirm = $PASSWORD
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/register/" -Method POST -ContentType "application/json" -Body $body
    $response | ConvertTo-Json -Depth 10 | Write-Host
    
    $TOKEN = $response.token
    Write-Host "Token: $TOKEN" -ForegroundColor Yellow
} catch {
    Write-Host "Registration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 2. Login
Write-Host "2. Logging in..." -ForegroundColor Cyan
try {
    $body = @{
        email = $EMAIL
        password = $PASSWORD
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/login/" -Method POST -ContentType "application/json" -Body $body -SessionVariable session
    $response | ConvertTo-Json -Depth 10 | Write-Host
    
    $TOKEN = $response.token
    Write-Host "New Token: $TOKEN" -ForegroundColor Yellow
} catch {
    Write-Host "Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
Write-Host ""

# 3. Test authenticated health check
Write-Host "3. Testing authenticated health check..." -ForegroundColor Cyan
try {
    $headers = @{
        "Authorization" = "Token $TOKEN"
    }
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/health/" -Method GET -Headers $headers
    $response | ConvertTo-Json -Depth 10 | Write-Host
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 4. Test unauthorized access
Write-Host "4. Testing unauthorized access..." -ForegroundColor Cyan
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/health/" -Method GET
    Write-Host "Unexpected success - should have failed!" -ForegroundColor Red
} catch {
    Write-Host "Expected error: $($_.Exception.Message)" -ForegroundColor Green
}
Write-Host ""

# 5. Logout
Write-Host "5. Logging out..." -ForegroundColor Cyan
try {
    $headers = @{
        "Authorization" = "Token $TOKEN"
    }
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/logout/" -Method POST -Headers $headers
    $response | ConvertTo-Json -Depth 10 | Write-Host
} catch {
    Write-Host "Logout failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 6. Verify token is invalidated
Write-Host "6. Verifying token is invalidated..." -ForegroundColor Cyan
try {
    $headers = @{
        "Authorization" = "Token $TOKEN"
    }
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/health/" -Method GET -Headers $headers
    Write-Host "Unexpected success - token should be invalid!" -ForegroundColor Red
} catch {
    Write-Host "Expected error: $($_.Exception.Message)" -ForegroundColor Green
}
Write-Host ""

Write-Host "=== Authentication Flow Test Complete ===" -ForegroundColor Green
