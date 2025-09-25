#!/bin/bash

# Medical History App Setup Script
# This script sets up the development environment for the Medical History Application

set -e

echo "🏥 Medical History App Setup"
echo "=========================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js (v16 or higher) first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL is not installed. Please install PostgreSQL first."
    echo "   On Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "   On macOS: brew install postgresql"
    echo "   On Windows: Download from https://www.postgresql.org/download/"
    exit 1
fi

echo "✅ PostgreSQL is installed"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
npm install

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd client
npm install
cd ..

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads logs

# Set up environment file
if [ ! -f .env ]; then
    echo "⚙️  Setting up environment configuration..."
    cp .env.example .env
    echo "✅ Environment file created. Please edit .env with your configuration."
else
    echo "✅ Environment file already exists"
fi

# Database setup
echo "🗄️  Setting up database..."

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "⚠️  PostgreSQL is not running. Please start PostgreSQL and run this script again."
    echo "   On Ubuntu/Debian: sudo systemctl start postgresql"
    echo "   On macOS: brew services start postgresql"
    exit 1
fi

# Create database and user
echo "Creating database and user..."
sudo -u postgres psql -c "CREATE DATABASE medical_history_db;" 2>/dev/null || echo "Database already exists"
sudo -u postgres psql -c "CREATE USER medical_user WITH PASSWORD 'secure_password_here';" 2>/dev/null || echo "User already exists"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE medical_history_db TO medical_user;" 2>/dev/null || echo "Privileges already granted"

echo "✅ Database setup complete"

# Run database migration
echo "🔄 Running database migration..."
npm run migrate

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start the development server: npm run dev"
echo "3. Open http://localhost:3000 in your browser"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: Admin123!"
echo ""
echo "⚠️  IMPORTANT: Change the default admin password after first login!"
echo ""
echo "For production deployment, see README.md for detailed instructions."