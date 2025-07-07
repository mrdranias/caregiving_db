"""
Lookup tables for standardized values used across the system.
These are relatively stable reference values.
"""
import psycopg2

def seed_lookup_tables(cur):
    """Seed severity levels, frequency levels, and other lookup tables"""
    
    # Severity levels with QALY weights
    severity_levels = [
        ("0", "None", 0, 1.0, "No discomfort/impact"),
        ("1", "Mild", 1, 0.9, "Mild discomfort, does not interfere with activities"),
        ("2", "Moderate", 2, 0.7, "Noticeable, some interference with activities"),
        ("3", "Severe", 3, 0.5, "Severe, substantial interference, distress"),
        ("4", "Extreme", 4, 0.2, "Extreme, disabling, prevents activities, constant"),
    ]
    cur.executemany("INSERT INTO severity_levels (severity_code, label, ordinal, utility_weight, description) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", severity_levels)
    print(f"Seeded {len(severity_levels)} severity levels")

    # Frequency levels
    frequency_levels = [
        ("0", "Not at all", 0, "Does not occur"),
        ("1", "Monthly", 1, "Occurs at least once per month"),
        ("2", "Weekly", 2, "Occurs at least once per week"),
        ("3", "Daily", 3, "Occurs at least once per day"),
        ("4", "Hourly", 4, "Occurs every hour or more frequently"),
        ("5", "Constant", 5, "Always present"),
    ]
    cur.executemany("INSERT INTO frequency_levels (frequency_code, label, ordinal, description) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", frequency_levels)
    print(f"Seeded {len(frequency_levels)} frequency levels")

    # Caregiver services (HCPCS/CPT codes)
    caregiver_services = [
        ("T1019", "Personal care services", "Personal care aide services per 15 minutes", 45.00, "Personal Care"),
        ("T1020", "Personal care services", "Personal care services per hour", 180.00, "Personal Care"),
        ("G0156", "Services of home health aide", "Services of home health aide in home health or hospice settings", 50.00, "Home Health"),
        ("99509", "Home visit for assistance with activities of daily living", "Home visit for assistance with ADL and personal care", 75.00, "Home Health"),
        ("S5125", "Attendant care services", "Attendant care services per hour", 25.00, "Personal Care"),
        ("S5126", "Attendant care services", "Attendant care services per diem", 200.00, "Personal Care"),
        ("T2025", "Waiver services", "Waiver services per 15 minutes", 15.00, "Waiver Services"),
        ("T1027", "Family training and counseling", "Family training and counseling for child development per 15 minutes", 60.00, "Training"),
        ("97535", "Self-care management training", "Self-care/home management training per 15 minutes", 45.00, "Rehabilitation"),
        ("99401", "Preventive medicine counseling", "Preventive medicine counseling individual approximately 15 minutes", 50.00, "Counseling"),
        ("99402", "Preventive medicine counseling", "Preventive medicine counseling individual approximately 30 minutes", 90.00, "Counseling"),
        ("96116", "Neurobehavioral status exam", "Neurobehavioral status exam per hour", 120.00, "Assessment"),
        ("90834", "Psychotherapy", "Psychotherapy 45 minutes", 150.00, "Mental Health"),
        ("90837", "Psychotherapy", "Psychotherapy 60 minutes", 200.00, "Mental Health"),
        ("90901", "Biofeedback training", "Biofeedback training by any modality", 100.00, "Therapy"),
        ("97110", "Therapeutic exercises", "Therapeutic exercises to develop strength and endurance", 55.00, "Physical Therapy"),
        ("97116", "Gait training", "Gait training (includes stair climbing)", 55.00, "Physical Therapy"),
        ("97530", "Therapeutic activities", "Therapeutic activities direct patient contact", 55.00, "Occupational Therapy"),
        ("97535", "Self-care training", "Self-care/home management training", 55.00, "Occupational Therapy"),
        ("T1021", "Home health aide services", "Home health aide or certified nurse assistant per hour", 40.00, "Home Health")
    ]
    
    for service in caregiver_services:
        cur.execute("""
            INSERT INTO caregiver_services (service_code, service_name, description, typical_cost, category)
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, service)
    print(f"Seeded {len(caregiver_services)} caregiver services")
