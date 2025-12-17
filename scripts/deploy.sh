#!/bin/bash

# Timber BE Deployment Script for DigitalOcean
# This script should be run on the DigitalOcean droplet

set -e

echo "🚀 Starting Timber BE deployment..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root or with sudo"
    exit 1
fi

# Set variables
APP_DIR="/opt/timber-be"
BACKUP_DIR="/opt/timber-be-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Function to backup database
backup_database() {
    echo "📦 Creating database backup..."
    docker-compose exec -T db pg_dump -U $DB_USER $DB_NAME > $BACKUP_DIR/db_backup_$TIMESTAMP.sql
    echo "✅ Database backup created: $BACKUP_DIR/db_backup_$TIMESTAMP.sql"
}

# Function to restore database
restore_database() {
    local backup_file=$1
    echo "🔄 Restoring database from $backup_file..."
    docker-compose exec -T db psql -U $DB_USER -d $DB_NAME < $backup_file
    echo "✅ Database restored successfully"
}

# Function to update application
update_application() {
    echo "🔄 Updating application..."
    
    # Pull latest changes if git repository exists
    if [ -d ".git" ]; then
        git pull origin main
    fi
    
    # Pull latest Docker image
    IMAGE_TAG=${1:-latest}
    docker pull ghcr.io/your-username/timber-be:$IMAGE_TAG
    
    # Update docker-compose.yml with new image tag
    sed -i "s|image: .*|image: ghcr.io/your-username/timber-be:$IMAGE_TAG|" docker-compose.yml
    
    # Stop existing containers
    docker-compose down
    
    # Start new containers
    docker-compose up -d
    
    echo "✅ Application updated successfully"
}

# Function to run migrations
run_migrations() {
    echo "🔄 Running database migrations..."
    docker-compose exec -T web python manage.py migrate
    echo "✅ Migrations completed"
}

# Function to collect static files
collect_static() {
    echo "🔄 Collecting static files..."
    docker-compose exec -T web python manage.py collectstatic --noinput
    echo "✅ Static files collected"
}

# Function to create superuser if needed
create_superuser() {
    echo "🔧 Checking for superuser..."
    if ! docker-compose exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" | grep -q "True"; then
        echo "⚠️ No superuser found. Creating one..."
        echo "Please provide superuser details:"
        docker-compose exec web python manage.py create_user --superuser
    else
        echo "✅ Superuser exists"
    fi
}

# Function to check application health
health_check() {
    echo "🏥 Performing health check..."
    
    # Wait for application to start
    sleep 10
    
    # Check if application is responding
    if curl -f http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
        echo "✅ Application is healthy"
        return 0
    else
        echo "❌ Application health check failed"
        return 1
    fi
}

# Function to cleanup old images
cleanup() {
    echo "🧹 Cleaning up old Docker images..."
    docker image prune -f
    echo "✅ Cleanup completed"
}

# Main deployment function
deploy() {
    local IMAGE_TAG=$1
    
    echo "🚀 Starting deployment with image tag: $IMAGE_TAG"
    
    # Change to application directory
    cd $APP_DIR
    
    # Backup database
    backup_database
    
    # Update application
    update_application $IMAGE_TAG
    
    # Wait for containers to be ready
    sleep 15
    
    # Run migrations
    run_migrations
    
    # Collect static files
    collect_static
    
    # Create superuser if needed
    create_superuser
    
    # Health check
    if health_check; then
        echo "🎉 Deployment completed successfully!"
        cleanup
    else
        echo "❌ Deployment failed. Rolling back..."
        rollback
        exit 1
    fi
}

# Function to rollback to previous version
rollback() {
    echo "🔄 Starting rollback..."
    
    # Get the previous image tag
    PREVIOUS_IMAGE=$(docker images --format "table {{.Repository}}:{{.Tag}}" | grep ghcr.io/your-username/timber-be | tail -n 2 | head -n 1)
    
    if [ -z "$PREVIOUS_IMAGE" ]; then
        echo "❌ No previous image found for rollback"
        exit 1
    fi
    
    echo "🔄 Rolling back to: $PREVIOUS_IMAGE"
    
    # Stop current container
    docker-compose down
    
    # Update docker-compose.yml with previous image
    sed -i "s|image: .*|image: $PREVIOUS_IMAGE|" docker-compose.yml
    
    # Start container with previous image
    docker-compose up -d
    
    # Wait for containers to be ready
    sleep 15
    
    # Health check
    if health_check; then
        echo "✅ Rollback completed successfully!"
    else
        echo "❌ Rollback failed. Please check logs manually."
        exit 1
    fi
}

# Function to show logs
show_logs() {
    echo "📋 Showing application logs..."
    docker-compose logs -f --tail=100 web
}

# Function to show status
show_status() {
    echo "📊 Application Status:"
    docker-compose ps
    
    echo ""
    echo "🏥 Health Check:"
    if curl -f http://localhost:8000/api/v1/health/ > /dev/null 2>&1; then
        echo "✅ Application is healthy"
    else
        echo "❌ Application is not responding"
    fi
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy "${2:-latest}"
        ;;
    "rollback")
        rollback
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "backup")
        backup_database
        ;;
    "restore")
        if [ -z "$2" ]; then
            echo "Usage: $0 restore <backup_file>"
            exit 1
        fi
        restore_database "$2"
        ;;
    "migrate")
        run_migrations
        ;;
    "collectstatic")
        collect_static
        ;;
    "superuser")
        create_superuser
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|logs|status|backup|restore|migrate|collectstatic|superuser}"
        echo ""
        echo "Commands:"
        echo "  deploy [tag]     - Deploy application (default: latest)"
        echo "  rollback         - Rollback to previous version"
        echo "  logs            - Show application logs"
        echo "  status          - Show application status"
        echo "  backup           - Backup database"
        echo "  restore <file>  - Restore database from backup"
        echo "  migrate          - Run database migrations"
        echo "  collectstatic    - Collect static files"
        echo "  superuser        - Create superuser if needed"
        exit 1
        ;;
esac
