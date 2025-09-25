#!/usr/bin/env python
"""
Database setup script for Medical History Recording Application.
This script initializes the database, creates superuser, and loads sample data.
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
    execute_from_command_line(['manage.py', 'makemigrations'])
    execute_from_command_line(['manage.py', 'migrate'])
    print("✓ Database tables created successfully")

def create_superuser():
    """Create superuser if it doesn't exist."""
    from django.contrib.auth import get_user_model
    from accounts.models import Organization
    from core.models import Address
    
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        print("Creating superuser...")
        
        # Create organization address
        address = Address.objects.create(
            street_address_1="123 Medical Center Drive",
            city="Healthcare City",
            state="CA",
            postal_code="90210",
            country="United States"
        )
        
        # Create organization
        organization = Organization.objects.create(
            name="Sample Medical Center",
            organization_type="hospital",
            tax_id="12-3456789",
            npi_number="1234567890",
            address=address,
            email="admin@samplemedical.com"
        )
        
        # Create superuser
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123',
            first_name='System',
            last_name='Administrator',
            role='admin',
            organization=organization,
            is_verified=True
        )
        
        print("✓ Superuser created: username='admin', password='admin123'")
    else:
        print("✓ Superuser already exists")

def load_sample_medical_codes():
    """Load sample medical codes."""
    from core.models import MedicalCode
    
    sample_codes = [
        # ICD-10 codes
        {'code_system': 'icd10', 'code': 'E11.9', 'display_name': 'Type 2 diabetes mellitus without complications'},
        {'code_system': 'icd10', 'code': 'I10', 'display_name': 'Essential hypertension'},
        {'code_system': 'icd10', 'code': 'E78.5', 'display_name': 'Hyperlipidemia'},
        {'code_system': 'icd10', 'code': 'J44.1', 'display_name': 'Chronic obstructive pulmonary disease with acute exacerbation'},
        {'code_system': 'icd10', 'code': 'F32.9', 'display_name': 'Major depressive disorder, single episode, unspecified'},
        
        # CPT codes
        {'code_system': 'cpt', 'code': '99213', 'display_name': 'Office visit, established patient, moderate complexity'},
        {'code_system': 'cpt', 'code': '99214', 'display_name': 'Office visit, established patient, moderate to high complexity'},
        {'code_system': 'cpt', 'code': '99215', 'display_name': 'Office visit, established patient, high complexity'},
        
        # RxNorm codes (sample medications)
        {'code_system': 'rxnorm', 'code': '860975', 'display_name': 'Metformin 500 MG Oral Tablet'},
        {'code_system': 'rxnorm', 'code': '197622', 'display_name': 'Lisinopril 10 MG Oral Tablet'},
        {'code_system': 'rxnorm', 'code': '617310', 'display_name': 'Atorvastatin 20 MG Oral Tablet'},
    ]
    
    created_count = 0
    for code_data in sample_codes:
        code, created = MedicalCode.objects.get_or_create(
            code_system=code_data['code_system'],
            code=code_data['code'],
            defaults={
                'display_name': code_data['display_name'],
                'description': f"Sample {code_data['code_system'].upper()} code"
            }
        )
        if created:
            created_count += 1
    
    print(f"✓ Loaded {created_count} new medical codes")

def create_sample_data():
    """Create sample patients and medical data."""
    from django.contrib.auth import get_user_model
    from accounts.models import Organization
    from patients.models import Patient
    from medical_records.models import MedicalHistory, PastMedicalHistory, Medication, Allergy
    from core.models import Address, DataSource
    from datetime import date, datetime
    
    User = get_user_model()
    
    # Create sample physician
    if not User.objects.filter(username='dr_smith').exists():
        physician = User.objects.create_user(
            username='dr_smith',
            email='dr.smith@example.com',
            password='doctor123',
            first_name='John',
            last_name='Smith',
            role='physician',
            specialty='family_medicine',
            license_number='MD123456',
            npi_number='1234567891',
            is_verified=True
        )
        print("✓ Sample physician created: username='dr_smith', password='doctor123'")
    else:
        physician = User.objects.get(username='dr_smith')
    
    # Create data source
    data_source, created = DataSource.objects.get_or_create(
        source_type='physician_examination',
        defaults={
            'reliability_score': 5,
            'description': 'Sample data for demonstration'
        }
    )
    
    # Create sample patient
    if not Patient.objects.filter(medical_record_number__startswith='SAMPLE').exists():
        # Create patient address
        patient_address = Address.objects.create(
            street_address_1="456 Patient Street",
            city="Patient City",
            state="CA",
            postal_code="90211",
            country="United States"
        )
        
        patient = Patient.objects.create(
            medical_record_number='SAMPLE-001',
            gender='M',
            ethnicity='not_hispanic_latino',
            race='white',
            marital_status='married',
            primary_address=patient_address,
            preferred_language='English',
            primary_physician=physician,
            created_by=physician
        )
        
        # Set encrypted fields
        patient.first_name = 'John'
        patient.last_name = 'Doe'
        patient.date_of_birth = date(1975, 5, 15)
        patient.email = 'john.doe@example.com'
        patient.emergency_contact_name = 'Jane Doe'
        patient.emergency_contact_phone = '555-0123'
        patient.emergency_contact_relationship = 'spouse'
        patient.save()
        
        # Create medical history
        medical_history = MedicalHistory.objects.create(
            patient=patient,
            created_by=physician,
            last_updated_by=physician
        )
        medical_history.chief_complaint = 'Annual physical examination'
        medical_history.history_of_present_illness = 'Patient presents for routine annual physical. No acute complaints.'
        medical_history.save()
        
        # Add past medical history
        past_condition = PastMedicalHistory.objects.create(
            patient=patient,
            condition_type='condition',
            icd10_code=None,
            onset_date=date(2020, 1, 1),
            status='active',
            data_source=data_source,
            created_by=physician
        )
        past_condition.condition_name = 'Hypertension'
        past_condition.description = 'Well-controlled with medication'
        past_condition.save()
        
        # Add medication
        medication = Medication.objects.create(
            patient=patient,
            medication_type='prescription',
            dosage_form='tablet',
            frequency='once_daily',
            route='oral',
            start_date=date(2020, 1, 1),
            status='active',
            data_source=data_source,
            created_by=physician
        )
        medication.medication_name = 'Lisinopril'
        medication.strength = '10mg'
        medication.dosage = '1 tablet'
        medication.indication = 'Hypertension'
        medication.save()
        
        # Add allergy
        allergy = Allergy.objects.create(
            patient=patient,
            allergy_type='drug',
            severity='moderate',
            verified=True,
            data_source=data_source,
            created_by=physician
        )
        allergy.allergen = 'Penicillin'
        allergy.reaction = 'Rash and itching'
        allergy.save()
        
        print("✓ Sample patient created with medical history")
    else:
        print("✓ Sample patient already exists")

def main():
    """Main setup function."""
    print("Setting up Medical History Recording Application...")
    print("=" * 50)
    
    setup_django()
    create_database()
    create_superuser()
    load_sample_medical_codes()
    create_sample_data()
    
    print("=" * 50)
    print("✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the development server: python manage.py runserver")
    print("2. Access the admin interface: http://localhost:8000/admin/")
    print("3. View API documentation: http://localhost:8000/api/docs/")
    print("4. Access the dashboard: http://localhost:8000/")
    print("\nDefault login credentials:")
    print("- Admin: username='admin', password='admin123'")
    print("- Physician: username='dr_smith', password='doctor123'")

if __name__ == '__main__':
    main()