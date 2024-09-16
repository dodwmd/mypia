#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Load environment variables from .env file
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '#' | awk '/=/ {print $1}')
fi

# Database configuration
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${DB_NAME:-"mypia"}
DB_USER=${DB_USER:-"mypia"}
DB_PASSWORD=${DB_PASSWORD:-"password"}

# Flyway configuration
FLYWAY_URL="jdbc:postgresql://${DB_HOST}:${DB_PORT}/${DB_NAME}"
FLYWAY_USER=$DB_USER
FLYWAY_PASSWORD=$DB_PASSWORD
FLYWAY_LOCATIONS="filesystem:sql"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to run Flyway commands
run_flyway() {
    flyway -url="$FLYWAY_URL" -user="$FLYWAY_USER" -password="$FLYWAY_PASSWORD" -locations="$FLYWAY_LOCATIONS" -baselineOnMigrate=true -validateMigrationNaming=true "$@"
}

# Run Flyway migrations
echo -e "${GREEN}Running database migrations...${NC}"
run_flyway migrate

echo -e "${GREEN}Development setup completed successfully!${NC}"
