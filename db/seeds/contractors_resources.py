"""
Contractors, costs, community resources, and resource costs seeding.
Comprehensive seeding for both clinical and social service providers.
"""
import uuid
import psycopg2


def seed_contractors_and_costs(cur):
    """Seed contractors and their service costs with frequency"""
    
    # --- Seed Contractors ---
    print("Seeding contractors...")
    contractors = [
        ("Four Seasons Home Health", '{"phone": "828-555-0101", "email": "contact@fourseasons.care", "address": "1234 Patton Ave, Asheville, NC 28806"}', "Home health aide services, personal care assistance, Medicare certified"),
        ("Asheville Home Health", '{"phone": "828-555-0102", "email": "info@ashevillehomehealth.com", "address": "567 Biltmore Ave, Asheville, NC 28801"}', "Licensed nursing, physical therapy, skilled home health, Medicare/Medicaid certified"),
        ("Bayada Home Health Care", '{"phone": "828-555-0103", "email": "services@bayada.com", "address": "890 Tunnel Rd, Asheville, NC 28805"}', "Home health care, nursing services, companion care, 24/7 availability"),
        ("Home Instead Senior Care", '{"phone": "828-555-0104", "email": "care@homeinstead.com", "address": "321 Haywood St, Asheville, NC 28801"}', "Senior care services, companion care, personal care, Alzheimer's care"),
        ("Visiting Angels", '{"phone": "828-555-0105", "email": "angels@visitingangels.org", "address": "445 Merrimon Ave, Asheville, NC 28804"}', "Senior home care, companion services, personal care, respite care"),
        ("Comfort Keepers", '{"phone": "828-555-0106", "email": "comfort@comfortkeepers.com", "address": "678 Long Shoals Rd, Arden, NC 28704"}', "In-home senior care, companion care, personal care, safety monitoring")
    ]
    
    for name, contact_info, qualifications in contractors:
        cur.execute("""
            INSERT INTO contractors (name, contact_info, qualifications) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (name, contact_info, qualifications))
    
    print(f"Seeded {len(contractors)} contractors")
    
    # --- Seed Sample Services ---
    print("Seeding sample services...")
    sample_services = [
        ("Personal Care Assistant", "Health Aide", "2 hours daily", "Basic personal care and hygiene assistance"),
        ("Home Health Aide", "Health Aide", "4 hours daily", "Health monitoring and basic medical support"),
        ("Skilled Nursing", "Nursing", "1 visit weekly", "Licensed nursing assessment and care"),
        ("Companion Care", "Companion", "8 hours daily", "Social interaction and light housekeeping"),
        ("Physical Therapy", "Therapy", "2 sessions weekly", "Physical rehabilitation services"),
        ("Occupational Therapy", "Therapy", "1 session weekly", "Daily living skills therapy"),
        ("Speech Therapy", "Therapy", "1 session weekly", "Communication and swallowing therapy"),
        ("Respite Care", "Respite", "4 hours weekly", "Temporary relief for family caregivers"),
        ("Medication Management", "Nursing", "1 visit weekly", "Medication administration and monitoring"),
        ("Transportation Services", "Transport", "2 trips weekly", "Medical appointment transportation")
    ]
    
    service_ids = []
    for service_name, service_category, default_frequency, description in sample_services:
        service_id = str(uuid.uuid4())
        service_ids.append(service_id)
        cur.execute("""
            INSERT INTO services (service_id, service_name, service_category, default_frequency, description) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (service_id, service_name, service_category, default_frequency, description))
    
    print(f"Seeded {len(sample_services)} services")
    
    # Get contractor and service IDs for cost mapping
    cur.execute("SELECT contractor_id, name FROM contractors")
    contractor_map = {name: contractor_id for contractor_id, name in cur.fetchall()}
    
    cur.execute("SELECT service_id, service_name FROM services")
    service_map = {name: service_id for service_id, name in cur.fetchall()}
    
    # --- Seed Contractor Service Costs (with weekly frequency) ---
    print("Seeding contractor service costs...")
    costs_data = [
        # Personal Care Assistant - multiple frequencies
        (contractor_map["Four Seasons Home Health"], service_map["Personal Care Assistant"], 35.00, "hourly", 7, "Medicare/Private"),  # Daily
        (contractor_map["Four Seasons Home Health"], service_map["Personal Care Assistant"], 32.00, "hourly", 14, "Medicare/Private"), # Twice daily
        (contractor_map["Asheville Home Health"], service_map["Personal Care Assistant"], 38.00, "hourly", 7, "Medicare/Private"),
        (contractor_map["Bayada Home Health Care"], service_map["Personal Care Assistant"], 30.00, "hourly", 7, "Medicare/Private"),
        (contractor_map["Home Instead Senior Care"], service_map["Personal Care Assistant"], 28.00, "hourly", 7, "Private Pay"),
        
        # Home Health Aide - multiple frequencies  
        (contractor_map["Four Seasons Home Health"], service_map["Home Health Aide"], 42.00, "hourly", 7, "Medicare/Insurance"),
        (contractor_map["Asheville Home Health"], service_map["Home Health Aide"], 45.00, "hourly", 7, "Medicare/Insurance"),
        (contractor_map["Bayada Home Health Care"], service_map["Home Health Aide"], 38.00, "hourly", 7, "Medicare/Insurance"),
        (contractor_map["Home Instead Senior Care"], service_map["Home Health Aide"], 35.00, "hourly", 7, "Private Pay"),
        
        # Skilled Nursing - weekly visits
        (contractor_map["Asheville Home Health"], service_map["Skilled Nursing"], 180.00, "per visit", 1, "Medicare/Insurance"),
        (contractor_map["Four Seasons Home Health"], service_map["Skilled Nursing"], 165.00, "per visit", 1, "Medicare/Insurance"),
        (contractor_map["Bayada Home Health Care"], service_map["Skilled Nursing"], 170.00, "per visit", 1, "Medicare/Insurance"),
        
        # Companion Care - flexible frequencies
        (contractor_map["Home Instead Senior Care"], service_map["Companion Care"], 25.00, "hourly", 7, "Private Pay"),
        (contractor_map["Visiting Angels"], service_map["Companion Care"], 28.00, "hourly", 7, "Private Pay"),
        (contractor_map["Comfort Keepers"], service_map["Companion Care"], 26.00, "hourly", 7, "Private Pay"),
        
        # Physical Therapy - 2x weekly
        (contractor_map["Asheville Home Health"], service_map["Physical Therapy"], 125.00, "per session", 2, "Medicare/Insurance"),
        (contractor_map["Four Seasons Home Health"], service_map["Physical Therapy"], 115.00, "per session", 2, "Medicare/Insurance"),
        
        # Occupational Therapy - 1x weekly
        (contractor_map["Asheville Home Health"], service_map["Occupational Therapy"], 120.00, "per session", 1, "Medicare/Insurance"),
        (contractor_map["Four Seasons Home Health"], service_map["Occupational Therapy"], 110.00, "per session", 1, "Medicare/Insurance"),
        
        # Speech Therapy - 1x weekly  
        (contractor_map["Asheville Home Health"], service_map["Speech Therapy"], 130.00, "per session", 1, "Medicare/Insurance"),
        
        # Respite Care - flexible
        (contractor_map["Visiting Angels"], service_map["Respite Care"], 22.00, "hourly", 1, "Private Pay"),
        (contractor_map["Comfort Keepers"], service_map["Respite Care"], 24.00, "hourly", 1, "Private Pay"),
        
        # Medication Management - weekly
        (contractor_map["Asheville Home Health"], service_map["Medication Management"], 85.00, "per visit", 1, "Medicare/Insurance"),
        (contractor_map["Bayada Home Health Care"], service_map["Medication Management"], 75.00, "per visit", 1, "Medicare/Insurance"),
        
        # Transportation Services - 2x weekly
        (contractor_map["Four Seasons Home Health"], service_map["Transportation Services"], 45.00, "per trip", 2, "Medicare/Private"),
        (contractor_map["Home Instead Senior Care"], service_map["Transportation Services"], 40.00, "per trip", 2, "Private Pay")
    ]
    
    for contractor_id, service_id, amount, billing_cycle, weekly_freq, payer in costs_data:
        cost_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO costs (cost_id, contractor_id, service_id, amount, billing_cycle, weekly_frequency, payer) 
            VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (cost_id, contractor_id, service_id, amount, billing_cycle, weekly_freq, payer))
    
    print(f"Seeded {len(costs_data)} contractor service costs")


def seed_community_resources_and_costs(cur):
    """Seed comprehensive community resources and their costs"""
    
    print("Seeding community resources...")
    
    # --- Comprehensive Community Resources ---
    community_resources = [
        # Food Resources
        {
            'subclass_id': 'food_pantry',
            'name': 'Mountain Community Food Pantry',
            'description': 'Emergency food assistance for families in need',
            'address': '145 Main Street',
            'city': 'Asheville',
            'zip_code': '28801',
            'phone': '(828) 555-FOOD',
            'website': 'https://mountainfoodpantry.org',
            'cost_info': 'Free with income verification',
            'hours': '{"monday": "9-12", "wednesday": "1-4", "friday": "9-12"}',
            'appointment_required': False
        },
        {
            'subclass_id': 'mobile_pantry',
            'name': 'MANNA Mobile Market',
            'description': 'Mobile food pantry serving rural communities',
            'address': 'Various locations',
            'city': 'Western NC',
            'zip_code': '28801',
            'phone': '(828) 555-MANNA',
            'website': 'https://mannafoodbank.org/mobile',
            'cost_info': 'Free, no documentation required',
            'hours': '{"schedule": "Rotating weekly schedule"}',
            'appointment_required': False
        },
        {
            'subclass_id': 'senior_meals',
            'name': 'Meals on Wheels WNC',
            'description': 'Home-delivered meals for seniors and disabled adults',
            'address': '789 Elderly Lane',
            'city': 'Asheville',
            'zip_code': '28804',
            'phone': '(828) 555-MEALS',
            'website': 'https://mealsonwheelswnc.org',
            'cost_info': 'Suggested donation $3-5 per meal',
            'hours': '{"delivery": "Monday-Friday 11-1"}',
            'appointment_required': True
        },
        
        # Housing Resources
        {
            'subclass_id': 'housing_emergency',
            'name': 'Homeward Bound Emergency Shelter',
            'description': 'Emergency housing for individuals and families',
            'address': '123 Shelter Street',
            'city': 'Asheville',
            'zip_code': '28801',
            'phone': '(828) 555-HOME',
            'website': 'https://homewardboundnc.org',
            'cost_info': 'Free emergency shelter, 30-day limit',
            'hours': '{"intake": "24/7"}',
            'appointment_required': False
        },
        {
            'subclass_id': 'utility_assistance',
            'name': 'LIHEAP Energy Assistance Program',
            'description': 'Low Income Home Energy Assistance Program',
            'address': '40 Coxe Avenue',
            'city': 'Asheville',
            'zip_code': '28801',
            'phone': '(828) 555-HEAT',
            'website': 'https://ncdhhs.gov/liheap',
            'cost_info': 'Free for income-qualified households',
            'hours': '{"office": "Monday-Friday 8-5"}',
            'appointment_required': True
        },
        
        # Transportation Resources
        {
            'subclass_id': 'medical_transport',
            'name': 'Mountain Mobility Medical Transport',
            'description': 'Non-emergency medical transportation for seniors',
            'address': '200 Healthcare Drive',
            'city': 'Asheville',
            'zip_code': '28803',
            'phone': '(828) 555-RIDE',
            'website': 'https://mountainmobility.org',
            'cost_info': '$25 one-way, Medicare may cover',
            'hours': '{"service": "Monday-Friday 7-17"}',
            'appointment_required': True
        },
        
        # Health Resources
        {
            'subclass_id': 'primary_care',
            'name': 'Mountain Community Health Partnership',
            'description': 'Sliding scale primary healthcare',
            'address': '123 Health Plaza',
            'city': 'Asheville',
            'zip_code': '28801',
            'phone': '(828) 555-HLTH',
            'website': 'https://mchp.org',
            'cost_info': 'Sliding fee scale based on income',
            'hours': '{"clinic": "Monday-Friday 8-17"}',
            'appointment_required': True
        },
        
        # Social Support Resources
        {
            'subclass_id': 'case_management',
            'name': 'Council on Aging Case Management',
            'description': 'Comprehensive case management for seniors',
            'address': '29 Ravenscroft Drive',
            'city': 'Asheville',
            'zip_code': '28801',
            'phone': '(828) 555-CASE',
            'website': 'https://coabc.org',
            'cost_info': 'Free for income-qualified seniors',
            'hours': '{"office": "Monday-Friday 8:30-17"}',
            'appointment_required': True
        },
        
        # Legal Resources
        {
            'subclass_id': 'legal_aid',
            'name': 'Pisgah Legal Services',
            'description': 'Free legal assistance for low-income residents',
            'address': '148 Coxe Avenue',
            'city': 'Asheville',
            'zip_code': '28801',
            'phone': '(828) 555-LEGAL',
            'website': 'https://pisgahlegal.org',
            'cost_info': 'Free for income-qualified clients',
            'hours': '{"office": "Monday-Friday 9-17"}',
            'appointment_required': True
        }
    ]
    
    # Insert community resources
    resource_ids = []
    for resource in community_resources:
        resource_id = str(uuid.uuid4())
        resource_ids.append((resource_id, resource['subclass_id']))
        cur.execute("""
            INSERT INTO community_resources (
                resource_id, resource_subclass_id, name, description, address, city, 
                zip_code, phone, website, cost_info, operating_hours, appointment_required
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (
            resource_id, resource['subclass_id'], resource['name'], resource['description'],
            resource['address'], resource['city'], resource['zip_code'], resource['phone'],
            resource['website'], resource['cost_info'], resource['hours'], resource['appointment_required']
        ))
    
    print(f"Seeded {len(community_resources)} community resources")
    
    # --- Seed Resource Costs ---
    print("Seeding resource costs...")
    resource_costs = [
        # Food resource costs
        (resource_ids[0][0], 'weekly_visit', 0.00, 'free', 1, 'Income verification required', 'Free'),
        (resource_ids[1][0], 'weekly_visit', 0.00, 'free', 1, 'No documentation required', 'Free'),
        (resource_ids[2][0], 'per_meal', 4.00, 'per meal', 5, 'Age 60+ or disabled', 'Suggested donation'),
        
        # Housing resource costs
        (resource_ids[3][0], 'emergency', 0.00, 'free', 1, '30-day limit, intake assessment', 'Free'),
        (resource_ids[4][0], 'annual', 300.00, 'annual', 1, 'Income at or below 150% FPL', 'LIHEAP'),
        
        # Transportation costs
        (resource_ids[5][0], 'per_trip', 25.00, 'per trip', 2, 'Medical necessity', 'Medicare/Private'),
        
        # Health resource costs
        (resource_ids[6][0], 'per_visit', 45.00, 'per visit', 1, 'Sliding scale based on income', 'Self-pay/Insurance'),
        
        # Social support costs
        (resource_ids[7][0], 'monthly', 0.00, 'free', 4, 'Age 60+, income qualified', 'Free'),
        
        # Legal resource costs
        (resource_ids[8][0], 'per_case', 0.00, 'free', 1, '125% of Federal Poverty Level', 'Free')
    ]
    
    for resource_id, service_type, amount, billing_cycle, weekly_freq, eligibility, payer in resource_costs:
        cost_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO resource_costs (
                resource_cost_id, resource_id, service_type, amount, billing_cycle, 
                weekly_frequency, eligibility_requirements, payer
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (cost_id, resource_id, service_type, amount, billing_cycle, weekly_freq, eligibility, payer))
    
    print(f"Seeded {len(resource_costs)} resource costs")
