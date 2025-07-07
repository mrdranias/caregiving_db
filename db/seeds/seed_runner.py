"""
Main seed runner that orchestrates all database seeding operations.
This replaces the monolithic seed_codes.py with a modular approach.
"""
import os
import sys
import psycopg2
from typing import Optional

# Add the seeds directory to Python path for imports
sys.path.append(os.path.dirname(__file__))

from reference_data import seed_medical_codes
from lookup_tables import seed_lookup_tables
from classification_data import (
    seed_classification_data, seed_assessment_hazard_mappings, 
    seed_hazard_service_mappings
)
from contractors_resources import (
    seed_contractors_and_costs, seed_community_resources_and_costs
)
from sample_patients import (
    seed_sample_patients, seed_sample_patient_history, 
    seed_sample_adl_data, seed_sample_iadl_data, seed_sample_prapare_data
)

# Database configuration
DB_CONFIG = {
    'dbname': 'care_db',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': 5433
}

class SeedManager:
    """Manages database seeding operations with environment control"""
    
    def __init__(self, environment: str = 'development'):
        self.environment = environment
        self.conn = None
        self.cur = None
        
    def connect(self):
        """Connect to the database"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.cur = self.conn.cursor()
            print(f"Connected to database successfully")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
            
    def disconnect(self):
        """Close database connection"""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed")
        
    def seed_reference_data(self):
        """Seed all reference data (always needed)"""
        print("\n=== SEEDING REFERENCE DATA ===")
        
        try:
            # Medical codes (dx, tx, rx, sx)
            seed_medical_codes(self.cur)
            
            # Lookup tables (severity, frequency, services)
            seed_lookup_tables(self.cur)
            
            # Classification system (hazards, services, mappings)
            seed_classification_data(self.cur)  # Now includes all hazards + SDOH mitigations
            seed_assessment_hazard_mappings(self.cur)  # All assessment-to-hazard mappings
            seed_hazard_service_mappings(self.cur)
            
            # Contractors, services, and cost data
            seed_contractors_and_costs(self.cur)  # Clinical service providers and costs
            seed_community_resources_and_costs(self.cur)  # Social service resources and costs
            
            self.conn.commit()
            print("✅ Reference data seeded successfully")
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error seeding reference data: {e}")
            raise
    
    def seed_sample_data(self):
        """Seed sample/test data (development/test only)"""
        print("\n=== SEEDING SAMPLE DATA ===")
        
        if self.environment not in ['development', 'test']:
            print(f"⚠️  Skipping sample data for environment: {self.environment}")
            return
            
        try:
            # Create sample patients
            patient_ids = seed_sample_patients(self.cur)
            
            # Create sample assessments and history
            seed_sample_patient_history(self.cur, patient_ids)
            seed_sample_adl_data(self.cur, patient_ids)
            seed_sample_iadl_data(self.cur, patient_ids)
            seed_sample_prapare_data(self.cur, patient_ids)
            
            self.conn.commit()
            print("✅ Sample data seeded successfully")
            
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Error seeding sample data: {e}")
            raise
    
    def seed_all(self):
        """Seed all data according to environment"""
        print(f"\n🌱 Starting database seeding for environment: {self.environment}")
        
        try:
            self.connect()
            
            # Always seed reference data
            self.seed_reference_data()
            
            # Conditionally seed sample data
            self.seed_sample_data()
            
            print(f"\n🎉 Database seeding completed successfully!")
            
        except Exception as e:
            print(f"\n💥 Database seeding failed: {e}")
            raise
        finally:
            self.disconnect()

def main():
    """Main entry point"""
    # Get environment from command line or default to development
    environment = sys.argv[1] if len(sys.argv) > 1 else 'development'
    
    # Validate environment
    valid_environments = ['development', 'test', 'production']
    if environment not in valid_environments:
        print(f"❌ Invalid environment: {environment}")
        print(f"Valid options: {', '.join(valid_environments)}")
        sys.exit(1)
    
    # Run seeding
    seeder = SeedManager(environment=environment)
    seeder.seed_all()

if __name__ == "__main__":
    main()
