#!/usr/bin/env python
"""
Simplified setup script for Medical History Recording Application.
This script initializes the database using SQLite, creates superuser, and loads sample data.
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_history.settings')
    django.setup()

def create_database():
    """Create database tables."""
    print("Creating database tables...")
    execute_from_command_line(['manage.py', 'makemigrations', '--verbosity=2'])
    execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
    print("✓ Database tables created successfully")

def create_superuser():
    """Create superuser if it doesn't exist."""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        print("Creating superuser...")
        
        # Create superuser
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='System',
            last_name='Administrator',
            role='admin',
            is_verified=True
        )
        
        print("✓ Superuser created: username='admin', password='admin123'")
    else:
        print("✓ Superuser already exists")

def main():
    """Main setup function."""
    print("Setting up Medical History Recording Application (SQLite version)...")
    print("=" * 50)
    
    setup_django()
    create_database()
    create_superuser()
    
    print("=" * 50)
    print("✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Access the admin interface: http://localhost:8000/admin/")
    print("3. Access the dashboard: http://localhost:8000/")
    print("\nDefault login credentials:")
    print("- Admin: username='admin', password='admin123'")

if __name__ == '__main__':
    main()