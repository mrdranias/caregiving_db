"""
Classification data for hazard/service mapping system.
This includes hazard classes, service classes, and their mappings.
"""
import psycopg2
import uuid

def seed_classification_data(cur):
    """Seed hazard classes, service classes, and mapping tables"""
    
    # Hazard classes (parent categories)
    hazard_classes = [
        ("ADL_HEAVY", "Heavy ADL Deficits", "Significant impairments in basic activities of daily living requiring substantial assistance"),
        ("ADL_LIGHT", "Light ADL Deficits", "Mild to moderate impairments in basic activities of daily living"),
        ("IADL_VEHICLE", "Vehicle-Dependent IADL", "Instrumental ADL deficits requiring vehicle transportation"),
        ("IADL_NONVEHICLE", "Non-Vehicle IADL", "Instrumental ADL deficits not requiring vehicle transportation"),
        ("SX_LIFE_THREATENING", "Life-Threatening Symptoms", "Medical symptoms that pose immediate risk to life"),
        ("SX_DISABLING", "Disabling Symptoms", "Medical symptoms that significantly impair function"),
        ("DX_MOOD_BEHAVIORAL", "Mood/Behavioral Disorders", "Mental health and behavioral conditions"),
        ("DX_CHRONIC_DISEASE", "Chronic Disease Management", "Ongoing management of chronic medical conditions"),
        ("COG", "Cognitive Impairment", "Cognitive or memory difficulties"),
        ("MOB", "Mobility/Falls Risk", "Mobility limitations or fall risk"),
        ("MED", "Medical Complexity", "Multiple or complex medical conditions"),        
    ]
    
    for hc in hazard_classes:
        cur.execute("""
            INSERT INTO hazard_classes (class_id, label, description)
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, hc)
    print(f"Seeded {len(hazard_classes)} hazard classes")

    # Hazard subclasses (specific items)
    hazard_subclasses = [
        # ADL Heavy
        ("BATH_SHOWER", "ADL_HEAVY", "Bathing/Showering", "Difficulty with bathing or showering safely"),
        ("TOILET_USE", "ADL_HEAVY", "Toilet Use", "Difficulty using toilet or managing incontinence"),
        ("TRANSFER", "ADL_HEAVY", "Transferring", "Difficulty moving between bed, chair, wheelchair"),
        ("MOBILITY", "ADL_HEAVY", "Walking/Mobility", "Difficulty walking or moving around"),
        
        # ADL Light  
        ("DRESSING", "ADL_LIGHT", "Dressing", "Difficulty putting on or taking off clothes"),
        ("GROOMING", "ADL_LIGHT", "Personal Hygiene", "Difficulty with grooming, oral care"),
        ("EATING", "ADL_LIGHT", "Eating", "Difficulty feeding self or swallowing"),
        
        # IADL Vehicle
        ("TRANSPORTATION", "IADL_VEHICLE", "Transportation", "Unable to drive or use public transport"),
        ("SHOPPING", "IADL_VEHICLE", "Shopping", "Difficulty getting to stores for necessities"),
        ("MEDICAL_TRANSPORT", "IADL_VEHICLE", "Medical Appointments", "Difficulty getting to medical appointments"),
        
        # IADL Non-Vehicle
        ("HOUSEKEEPING", "IADL_NONVEHICLE", "Housekeeping", "Difficulty maintaining home cleanliness"),
        ("MEAL_PREP", "IADL_NONVEHICLE", "Meal Preparation", "Difficulty preparing nutritious meals"),
        ("MEDICATION_MGT", "IADL_NONVEHICLE", "Medication Management", "Difficulty managing medication regimen"),
        ("FINANCE_MGT", "IADL_NONVEHICLE", "Financial Management", "Difficulty managing finances, bills"),

        # Cognitive
        ("COG_MEM", "COG", "Memory loss", "Memory impairment"),
        ("COG_DEC", "COG", "Decision-making difficulty", "Difficulty making decisions"),
        # Mobility
        ("MOB_WALK", "MOB", "Walking difficulty", "Difficulty walking"),
        ("MOB_FALL", "MOB", "Frequent falls", "History of falls"),
        # Symptom - Life Threatening
        ("SYM_PAIN_ACUTE", "SX_LIFE_THREATENING", "Acute severe pain", "Severe, life-threatening pain"),
        ("SYM_DYSPNEA", "SX_LIFE_THREATENING", "Acute dyspnea", "Acute shortness of breath"),

        # Mood/Behavioral
        ("MOOD_DEP", "DX_MOOD_BEHAVIORAL", "Depression", "Depressive symptoms"),
        ("MOOD_DISINH", "DX_MOOD_BEHAVIORAL", "Disinhibition", "Behavioral disinhibition"),
        # Medical
        ("MED_POLY", "MED", "Polypharmacy", "Many medications"),
        ("MED_MULTI", "MED", "Multiple conditions", "Multiple chronic illnesses"),
        ("MED_CARDIO", "MED", "Cardiovascular condition", "Heart and blood vessel disease"),
        ("MED_ENDO", "MED", "Endocrine condition", "Hormone and metabolic disorders"),
        ("MED_NEURO", "MED", "Neurological condition", "Brain and nervous system disorders"),
        ("MED_RESP", "MED", "Respiratory condition", "Lung and breathing disorders"),
        ("MED_RENAL", "MED", "Kidney condition", "Kidney and urinary disorders"),
        ("MED_GI", "MED", "Gastrointestinal condition", "Digestive system disorders"),
        ("MED_MUSCULO", "MED", "Musculoskeletal condition", "Bone, muscle, and joint disorders"),

        # Life-threatening symptoms
        ("CHEST_PAIN", "SX_LIFE_THREATENING", "Chest Pain", "Cardiac-related chest pain or discomfort"),
        ("BREATHING_DIFF", "SX_LIFE_THREATENING", "Difficulty Breathing", "Severe respiratory distress"),
        ("STROKE_SYMPTOMS", "SX_LIFE_THREATENING", "Stroke Symptoms", "Signs of cerebrovascular accident"),
        
        # Disabling symptoms
        ("CHRONIC_PAIN", "SX_DISABLING", "Chronic Pain", "Persistent pain affecting function"),
        ("FATIGUE", "SX_DISABLING", "Severe Fatigue", "Exhaustion limiting daily activities"),
        ("DIZZINESS", "SX_DISABLING", "Dizziness/Falls", "Balance problems increasing fall risk"),
        
        # Mood/Behavioral
        ("DEPRESSION", "DX_MOOD_BEHAVIORAL", "Depression", "Major depressive symptoms"),
        ("ANXIETY", "DX_MOOD_BEHAVIORAL", "Anxiety", "Anxiety disorders affecting function"),
        ("DEMENTIA", "DX_MOOD_BEHAVIORAL", "Dementia/Cognitive", "Cognitive impairment or dementia"),
        
        # Chronic Disease
        ("DIABETES", "DX_CHRONIC_DISEASE", "Diabetes Management", "Type 2 diabetes requiring monitoring"),
        ("HYPERTENSION", "DX_CHRONIC_DISEASE", "Hypertension", "High blood pressure management"),
        ("HEART_DISEASE", "DX_CHRONIC_DISEASE", "Heart Disease", "Cardiovascular disease management"),
        
        # ADL Hazard Subclasses
        ("ADL_BOWELS_DEP", "ADL_HEAVY", "Bowel Incontinence", "Complete loss of bowel control"),
        ("ADL_BOWELS_PART", "ADL_LIGHT", "Bowel Issues", "Occasional bowel accidents"),
        ("ADL_BLADDER_DEP", "ADL_HEAVY", "Bladder Incontinence", "Complete loss of bladder control"),
        ("ADL_BLADDER_PART", "ADL_LIGHT", "Bladder Issues", "Occasional bladder accidents"),
        ("ADL_GROOM_DEP", "ADL_LIGHT", "Grooming Dependency", "Unable to perform grooming tasks"),
        ("ADL_TOILET_DEP", "ADL_LIGHT", "Toilet Dependency", "Unable to use toilet independently"),
        ("ADL_TOILET_PART", "ADL_LIGHT", "Toilet Assistance", "Needs some help with toilet use"),
        ("ADL_FEED_DEP", "ADL_LIGHT", "Feeding Dependency", "Unable to feed self"),
        ("ADL_FEED_PART", "ADL_LIGHT", "Feeding Assistance", "Needs help with feeding"),
        ("ADL_TRANSF_DEP", "ADL_HEAVY", "Transfer Dependency", "Unable to transfer independently"),
        ("ADL_TRANSF_PART", "ADL_LIGHT", "Transfer Assistance", "Needs help with transfers"),
        ("ADL_MOBILITY_DEP", "ADL_HEAVY", "Mobility Dependency", "Unable to move independently"),
        ("ADL_MOBILITY_PART", "ADL_LIGHT", "Mobility Assistance", "Needs mobility assistance"),
        ("ADL_DRESS_DEP", "ADL_LIGHT", "Dressing Dependency", "Unable to dress independently"),
        ("ADL_DRESS_PART", "ADL_LIGHT", "Dressing Assistance", "Needs help with dressing"),
        ("ADL_STAIRS_DEP", "ADL_LIGHT", "Stair Dependency", "Unable to use stairs"),
        ("ADL_STAIRS_PART", "ADL_LIGHT", "Stair Assistance", "Needs help with stairs"),
        ("ADL_BATH_DEP", "ADL_LIGHT", "Bathing Dependency", "Unable to bathe independently"),
        
        # IADL Hazard Subclasses
        ("IADL_PHONE_DEP", "IADL_NONVEHICLE", "Phone Dependency", "Unable to use telephone"),
        ("IADL_SHOP_VEH", "IADL_VEHICLE", "Shopping Dependency", "Unable to shop independently"),
        ("IADL_COOK_DEP", "IADL_NONVEHICLE", "Cooking Dependency", "Unable to prepare food"),
        ("IADL_CLEAN_DEP", "IADL_NONVEHICLE", "Housekeeping Dependency", "Unable to maintain house"),
        ("IADL_LAUNDRY_DEP", "IADL_NONVEHICLE", "Laundry Dependency", "Unable to do laundry"),
        ("IADL_TRANS_VEH", "IADL_VEHICLE", "Transportation Dependency", "Unable to use transportation"),
        ("IADL_MED_DEP", "IADL_NONVEHICLE", "Medication Dependency", "Unable to manage medications"),
        ("IADL_FIN_DEP", "IADL_NONVEHICLE", "Financial Dependency", "Unable to manage finances")
    ]
    
    for hs in hazard_subclasses:
        cur.execute("""
            INSERT INTO hazard_subclasses (subclass_id, parent_class_id, label, description)
            VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (hs[0], hs[1], hs[2], hs[3]))
    print(f"Seeded {len(hazard_subclasses)} hazard subclasses")

    # Service classes (parent categories) - from seed_codes.py
    service_classes = [
        ("SVC_HEAVY_PC", "Heavy Personal Care", "Intensive ADL support: bedbound, heavy lifting"),
        ("SVC_LIGHT_PC", "Light Personal Care", "Routine ADL support: feeding, dressing, grooming"),
        ("SVC_VEHICLE_HS", "Vehicle Home Support", "IADL support requiring vehicle: transportation, shopping"),
        ("SVC_NONVEHICLE_HS", "Non-Vehicle Home Support", "IADL support: cooking, cleaning, medication, finances"),
        ("SVC_COG_SUP", "Cognitive Supervision", "Supervision for cognitive impairment"),
        ("SVC_MOB_TH", "Mobility Therapy", "Therapy for mobility/falls"),
        ("SVC_SYM_LIFE", "Symptom Management (Life-Threatening)", "Management of acute/life-threatening symptoms"),
        ("SVC_SYM_DISAB", "Symptom Management (Disabling)", "Management of chronic/disabling symptoms"),
        ("SVC_MOOD", "Mood/Behavioral Support", "Support for mood/behavioral disorders"),
        ("SVC_MED_MGMT", "Medical Management", "Complex medical management"),
        ("SVC_SOC_SUP", "Social/Environmental Support", "Support for social/environmental risks")
    ]
    
    for sc in service_classes:
        cur.execute("""
            INSERT INTO service_classes (class_id, label, description)
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, sc)
    print(f"Seeded {len(service_classes)} service classes")

    # Service subclasses (specific services) - from seed_codes.py
    service_subclasses = [
        # Heavy Personal Care
        ("SVC_BED", "SVC_HEAVY_PC", "Bed mobility assistance", "Assist with bed mobility"),
        ("SVC_TRAN", "SVC_HEAVY_PC", "Transfer assistance", "Assist with transfers"),
        ("SVC_BATH_HEAVY", "SVC_HEAVY_PC", "Total assist bathing", "Total assist bathing (bedbound)"),
        ("SVC_TOIL", "SVC_HEAVY_PC", "Incontinence", "Incontinence assist"),
        ("SVC_MOB", "SVC_HEAVY_PC", "Mobility assistance", "Heavy mobility assistance"),
        ("SVC_STAIR", "SVC_HEAVY_PC", "Stair assistance", "Assistance with stairs"),
        ("SVC_BATH", "SVC_HEAVY_PC", "Bathing assistance", "Heavy bathing assistance"),
        
        # Light Personal Care
        ("SVC_FEED", "SVC_LIGHT_PC", "Feeding assistance", "Assist with feeding"),
        ("SVC_DRESS", "SVC_LIGHT_PC", "Dressing assistance", "Assist with dressing"),
        ("SVC_GROOM", "SVC_LIGHT_PC", "Grooming assistance", "Assist with grooming"),
        ("SVC_TOIL_LIGHT", "SVC_LIGHT_PC", "Toileting assistance (ambulatory)", "Toileting assist, ambulatory"),
        
        # Vehicle Home Support
        ("SVC_TRANS", "SVC_VEHICLE_HS", "Transportation", "Transportation support"),
        ("SVC_SHOP", "SVC_VEHICLE_HS", "Shopping support", "Shopping/errands support"),
        ("SVC_ERRANDS", "SVC_VEHICLE_HS", "Errands support", "General errands support"),
        ("SVC_APPT", "SVC_VEHICLE_HS", "Appointment transport", "Medical appointment transport"),
        
        # Non-Vehicle Home Support
        ("SVC_PHONE", "SVC_NONVEHICLE_HS", "Phone assistance", "Help with phone calls"),
        ("SVC_HOUSE", "SVC_NONVEHICLE_HS", "Housekeeping", "Light housekeeping"),
        ("SVC_LAUND", "SVC_NONVEHICLE_HS", "Laundry", "Laundry assistance"),
        ("SVC_MEAL", "SVC_NONVEHICLE_HS", "Meal preparation", "Assist with meal prep"),
        ("SVC_MED", "SVC_NONVEHICLE_HS", "Medication reminders", "Medication reminders"),
        ("SVC_FIN", "SVC_NONVEHICLE_HS", "Financial management", "Assist with finances"),
        
        # Cognitive Supervision
        ("SVC_COG_STIM", "SVC_COG_SUP", "Cognitive stimulation", "Cognitive stimulation activities"),
        ("SVC_COG_GUID", "SVC_COG_SUP", "Cognitive guidance", "Guidance for cognitive tasks"),
        ("SVC_MEM", "SVC_COG_SUP", "Memory supervision", "Supervision for memory loss"),
        ("SVC_DEC", "SVC_COG_SUP", "Decision-making support", "Support for decision-making"),
        
        # Mobility Therapy
        ("SVC_MOB_AIDE", "SVC_MOB_TH", "Mobility aide", "Mobility assistance and training"),
        ("SVC_FALL_PREV", "SVC_MOB_TH", "Fall prevention", "Fall prevention training"),
        ("SVC_WALK", "SVC_MOB_TH", "Gait training", "Therapy for walking/mobility"),
        ("SVC_FALL", "SVC_MOB_TH", "Fall prevention", "Fall prevention"),
        
        # Symptom Management (Life-Threatening)
        ("SVC_EMERG", "SVC_SYM_LIFE", "Emergency response", "Emergency medical response"),
        ("SVC_RESP", "SVC_SYM_LIFE", "Respiratory support", "Respiratory emergency support"),
        ("SVC_PAIN_ACUTE", "SVC_SYM_LIFE", "Acute pain management", "Management of acute severe pain"),
        ("SVC_DYSPNEA", "SVC_SYM_LIFE", "Acute dyspnea management", "Management of acute dyspnea"),
        
        # Symptom Management (Disabling)
        ("SVC_PAIN", "SVC_SYM_DISAB", "Pain management", "Chronic pain management"),
        ("SVC_ENERGY", "SVC_SYM_DISAB", "Energy management", "Fatigue management"),
        ("SVC_PAIN_CHRONIC", "SVC_SYM_DISAB", "Chronic pain management", "Management of chronic pain"),
        ("SVC_FATIG", "SVC_SYM_DISAB", "Fatigue management", "Management of severe fatigue"),
        
        # Mood/Behavioral Support
        ("SVC_COUNSEL", "SVC_MOOD", "Counseling", "Mental health counseling"),
        ("SVC_BEHAV", "SVC_MOOD", "Behavioral support", "Behavioral intervention support"),
        ("SVC_DEP", "SVC_MOOD", "Depression support", "Support for depression"),
        ("SVC_DISINH", "SVC_MOOD", "Disinhibition support", "Support for disinhibition"),
        
        # Medical Management
        ("SVC_MED_REV", "SVC_MED_MGMT", "Medication review", "Comprehensive medication review"),
        ("SVC_POLY", "SVC_MED_MGMT", "Polypharmacy management", "Management of polypharmacy"),
        ("SVC_MULTI", "SVC_MED_MGMT", "Multi-condition care", "Care for multiple conditions"),
        ("SVC_CARDIO", "SVC_MED_MGMT", "Cardiovascular management", "Management of cardiovascular conditions"),
        ("SVC_ENDO", "SVC_MED_MGMT", "Endocrine management", "Management of endocrine conditions"),
        ("SVC_NEURO", "SVC_MED_MGMT", "Neurological management", "Management of neurological conditions"),
        ("SVC_RESP", "SVC_MED_MGMT", "Respiratory management", "Management of respiratory conditions"),
        ("SVC_RENAL", "SVC_MED_MGMT", "Kidney management", "Management of kidney conditions"),
        ("SVC_GI", "SVC_MED_MGMT", "Gastrointestinal management", "Management of gastrointestinal conditions"),
        ("SVC_MUSCULO", "SVC_MED_MGMT", "Musculoskeletal management", "Management of musculoskeletal conditions"),
        
        # Social/Environmental Support
        ("SVC_UNSAFE", "SVC_SOC_SUP", "Home safety assessment", "Assessment for home safety"),
        ("SVC_ISOL", "SVC_SOC_SUP", "Social support", "Support for isolation/loneliness")
    ]
    
    for ss in service_subclasses:
        cur.execute("""
            INSERT INTO service_subclasses (subclass_id, parent_class_id, label, description)
            VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (ss[0], ss[1], ss[2], ss[3]))
    print(f"Seeded {len(service_subclasses)} service subclasses")
    
    # --- Social Hazard Classes (SDOH-related hazards) ---
    social_hazard_classes = [
        ('HIGH_NEED_HOUSING', 'High Need Housing', 'Critical housing instability requiring immediate intervention'),
        ('LOW_NEED_HOUSING', 'Low Need Housing', 'Housing concerns that need monitoring and support'),
        ('HIGH_NEED_FOOD', 'High Need Food', 'Severe food insecurity requiring emergency assistance'),
        ('LOW_NEED_FOOD', 'Low Need Food', 'Food insecurity that needs ongoing support'),
        ('HIGH_NEED_TRANSPORTATION', 'High Need Transportation', 'Critical transportation barriers affecting health and safety'),
        ('LOW_NEED_TRANSPORTATION', 'Low Need Transportation', 'Transportation challenges that limit access'),
        ('HIGH_NEED_SOCIAL', 'High Need Social', 'Severe social isolation requiring intensive intervention'),
        ('LOW_NEED_SOCIAL', 'Low Need Social', 'Social connections that need strengthening'),
        ('HIGH_NEED_HEALTH', 'High Need Health', 'Critical health access barriers requiring immediate attention'),
        ('LOW_NEED_HEALTH', 'Low Need Health', 'Health access issues that need ongoing support'),
        ('HIGH_NEED_EMPLOYMENT', 'High Need Employment', 'Unemployment crisis requiring comprehensive support'),
        ('LOW_NEED_EMPLOYMENT', 'Low Need Employment', 'Employment challenges that need skills development'),
        ('HIGH_NEED_EDUCATION', 'High Need Education', 'Critical education barriers affecting basic functioning'),
        ('LOW_NEED_EDUCATION', 'Low Need Education', 'Education gaps that need skills training'),
        ('HIGH_NEED_SAFETY', 'High Need Safety', 'Immediate safety threats requiring crisis intervention'),
        ('LOW_NEED_SAFETY', 'Low Need Safety', 'Safety concerns that need ongoing monitoring'),
        ('HIGH_NEED_FINANCE', 'High Need Finance', 'Financial crisis requiring emergency assistance'),
        ('LOW_NEED_FINANCE', 'Low Need Finance', 'Financial challenges that need planning support'),
        ('HIGH_NEED_INSURANCE', 'High Need Insurance', 'Critical insurance barriers affecting health access'),
        ('LOW_NEED_INSURANCE', 'Low Need Insurance', 'Insurance issues that need navigation support'),
        ('HIGH_NEED_UNMET_NEEDS', 'High Need Unmet Needs', 'Critical unmet basic needs requiring immediate help'),
        ('LOW_NEED_UNMET_NEEDS', 'Low Need Unmet Needs', 'Unmet needs that require ongoing assistance')
    ]
    
    for class_id, label, description in social_hazard_classes:
        cur.execute("""
            INSERT INTO social_hazards (class_id, label, description) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (class_id, label, description))
    print(f"Seeded {len(social_hazard_classes)} social hazard classes")
    
    # --- Social Hazard Subclasses ---
    social_hazard_subclasses = [
        # Housing Subclasses
        ('EVICTION', 'Eviction Risk', 'HIGH_NEED_HOUSING', 'Imminent risk of eviction'),
        ('HOMELESS', 'Homelessness', 'HIGH_NEED_HOUSING', 'Currently homeless or at immediate risk'),
        ('OVERCROWDING', 'Severe Overcrowding', 'HIGH_NEED_HOUSING', 'Living in severely overcrowded conditions'),
        ('HOUSING', 'Housing Instability', 'LOW_NEED_HOUSING', 'General housing concerns or instability'),
        
        # Food Subclasses
        ('CHRONIC_FOOD', 'Chronic Food Insecurity', 'HIGH_NEED_FOOD', 'Long-term inability to access adequate food'),
        ('ACUTE_FOOD', 'Acute Food Crisis', 'HIGH_NEED_FOOD', 'Immediate food emergency'),
        ('FOOD', 'Food Insecurity', 'LOW_NEED_FOOD', 'Ongoing food access challenges'),
        
        # Transportation Subclasses
        ('MEDICAL_TRANSPORT', 'Medical Transport Barrier', 'HIGH_NEED_TRANSPORTATION', 'Cannot access medical care due to transportation'),
        ('GENERAL_TRANSPORT', 'General Transport Barrier', 'LOW_NEED_TRANSPORTATION', 'Limited transportation affecting daily activities'),
        
        # Social Subclasses
        ('SOCIAL_ISOLATION', 'Severe Social Isolation', 'HIGH_NEED_SOCIAL', 'Complete lack of social connections'),
        ('LINGUISTIC_ISOLATION', 'Linguistic Isolation', 'HIGH_NEED_SOCIAL', 'Language barriers preventing social connection'),
        ('CULTURAL_ISOLATION', 'Cultural Isolation', 'LOW_NEED_SOCIAL', 'Lack of cultural community connections'),
        ('SOCIAL', 'Social Support Needs', 'LOW_NEED_SOCIAL', 'General social support needs'),
        
        # Health Subclasses
        ('MEDICATION', 'Medication Access Crisis', 'HIGH_NEED_HEALTH', 'Cannot afford or access needed medications'),
        ('NO_HEALTH_INSURANCE', 'No Health Insurance', 'HIGH_NEED_INSURANCE', 'Completely uninsured'),
        ('HIGH_COPAY', 'High Copay Burden', 'LOW_NEED_INSURANCE', 'Insurance copays too high'),
        ('NOT_PREFERRED_INSURANCE', 'Not Preferred Insurance', 'LOW_NEED_INSURANCE', 'Insurance not accepted by preferred providers'),
        ('HIGH_STRESS', 'High Stress Level', 'HIGH_NEED_HEALTH', 'Severe stress affecting health and functioning'),
        ('MEDIUM_STRESS', 'Medium Stress Level', 'LOW_NEED_HEALTH', 'Moderate stress needing support'),
        
        # Employment Subclasses
        ('UNEMPLOYED', 'Long-term Unemployment', 'HIGH_NEED_EMPLOYMENT', 'Extended period without employment'),
        ('UNDEREMPLOYED', 'Underemployment', 'LOW_NEED_EMPLOYMENT', 'Insufficient hours or wages'),
        
        # Education Subclasses
        ('LITERACY', 'Critical Literacy Barrier', 'HIGH_NEED_EDUCATION', 'Severe literacy problems affecting daily functioning'),
        ('SKILLS', 'Critical Skills Gap', 'LOW_NEED_EDUCATION', 'Lack of job-relevant skills'),
        
        # Safety Subclasses
        ('DOMESTIC_VIOLENCE', 'Domestic Violence', 'HIGH_NEED_SAFETY', 'Current or recent domestic violence'),
        ('UNSAFE', 'Feel Unsafe', 'HIGH_NEED_SAFETY', 'Feel unsafe in current environment'),
        ('FEEL_UNSAFE', 'Sometimes Feel Unsafe', 'LOW_NEED_SAFETY', 'Occasional safety concerns'),
        ('JAILTIME', 'Incarceration History', 'LOW_NEED_SAFETY', 'Recent incarceration affecting reintegration'),
        
        # Finance Subclasses
        ('NO_INCOME', 'No Income', 'HIGH_NEED_FINANCE', 'No current source of income'),
        ('NO_SAVINGS', 'No Savings', 'LOW_NEED_FINANCE', 'Unable to save money'),
        ('SEASONAL_WORK', 'Seasonal Work Only', 'LOW_NEED_EMPLOYMENT', 'Only seasonal employment available'),
        
        # Unmet Needs Subclasses
        ('CLOTHING', 'Clothing Needs', 'LOW_NEED_UNMET_NEEDS', 'Lack adequate clothing'),
        ('UTILITIES', 'Utility Needs', 'HIGH_NEED_UNMET_NEEDS', 'Unable to pay for utilities'),
        ('CHILD_CARE', 'Child Care Needs', 'LOW_NEED_UNMET_NEEDS', 'Lack child care services'),
        ('PHONE', 'Phone Needs', 'LOW_NEED_UNMET_NEEDS', 'Lack access to phone'),
        ('OTHER', 'Other Needs', 'LOW_NEED_UNMET_NEEDS', 'Lack access to other resources')
    ]
    
    for subclass_id, label, parent_class_id, description in social_hazard_subclasses:
        cur.execute("""
            INSERT INTO social_hazards_subclasses (subclass_id, label, parent_class_id, description) 
            VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (subclass_id, label, parent_class_id, description))
    print(f"Seeded {len(social_hazard_subclasses)} social hazard subclasses")
    
    # --- SDOH Mitigation Classes (Resource/Service Classes for Social Risks) ---
    sdoh_mitigation_classes = [
        ('housing', 'Housing Services', 'Emergency and supportive housing services'),
        ('food_bank', 'Food Services', 'Food assistance and nutrition programs'),
        ('transport', 'Transportation', 'Transportation assistance and mobility services'),
        ('social', 'Social Services', 'Case management and social support services'),
        ('health', 'Health Services', 'Healthcare access and support services'),
        ('employment', 'Employment Services', 'Job training and employment assistance'),
        ('education', 'Education Services', 'Educational and skills training programs'),
        ('legal', 'Legal Services', 'Legal aid and advocacy services'),
        ('safety', 'Safety Services', 'Safety and crisis intervention services')
    ]
    
    for class_id, label, description in sdoh_mitigation_classes:
        cur.execute("""
            INSERT INTO sdoh_mitigations (class_id, label, description) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (class_id, label, description))
    print(f"Seeded {len(sdoh_mitigation_classes)} SDOH mitigation classes")
    
    # --- SDOH Mitigation Subclasses ---
    sdoh_mitigation_subclasses = [
        # Housing Subclasses
        ('housing_emergency', 'Emergency Housing', 'housing', 'Immediate temporary housing assistance'),
        ('rent_assistance', 'Rent Assistance', 'housing', 'Help with rent payments and housing costs'),
        ('housing_repair', 'Housing Repair', 'housing', 'Home repair and maintenance assistance'),
        ('utility_assistance', 'Utility Assistance', 'housing', 'Help with utility bills and energy costs'),
        
        # Food Bank Subclasses
        ('food_pantry', 'Food Pantry', 'food_bank', 'Regular food distribution programs'),
        ('food_vouchers', 'Food Vouchers', 'food_bank', 'Vouchers for grocery purchases'),
        ('mobile_pantry', 'Mobile Food Pantry', 'food_bank', 'Mobile food distribution services'),
        ('senior_meals', 'Senior Meal Programs', 'food_bank', 'Meal programs specifically for seniors'),
        
        # Transport Subclasses
        ('medical_transport', 'Medical Transportation', 'transport', 'Transportation to medical appointments'),
        ('volunteer_drivers', 'Volunteer Driver Programs', 'transport', 'Volunteer-based transportation services'),
        ('public_transit', 'Public Transit Assistance', 'transport', 'Help with public transportation access'),
        ('vehicle_repair', 'Vehicle Repair Assistance', 'transport', 'Help with vehicle maintenance and repair'),
        
        # Social Subclasses
        ('case_management', 'Case Management', 'social', 'Comprehensive case management services'),
        ('visiting_program', 'Friendly Visiting', 'social', 'Regular social visits and companionship'),
        ('senior_center', 'Senior Center Programs', 'social', 'Senior center activities and services'),
        ('support_groups', 'Support Groups', 'social', 'Peer support and group counseling'),
        
        # Health Subclasses
        ('primary_care', 'Primary Care Access', 'health', 'Access to primary healthcare services'),
        ('mobile_clinic', 'Mobile Health Clinic', 'health', 'Mobile healthcare services for rural areas'),
        ('mental_health', 'Mental Health Services', 'health', 'Counseling and psychiatric services'),
        ('pharmacy_assistance', 'Prescription Assistance', 'health', 'Help with medication costs'),
        
        # Employment Subclasses
        ('job_training', 'Job Training Programs', 'employment', 'Skills training and workforce development'),
        ('employment_placement', 'Employment Placement', 'employment', 'Job search assistance and placement services'),
        
        # Education Subclasses
        ('adult_education', 'Adult Education', 'education', 'GED preparation and adult literacy programs'),
        ('computer_training', 'Computer Training', 'education', 'Basic computer and internet skills training'),
        
        # Legal Subclasses
        ('legal_aid', 'Legal Aid', 'legal', 'Free legal assistance for low-income individuals'),
        ('benefits_advocacy', 'Benefits Advocacy', 'legal', 'Help applying for government benefits'),
        
        # Safety Subclasses
        ('emergency_services', 'Safety Services', 'safety', 'Crisis intervention and safety services'),
    ]
    
    for subclass_id, label, parent_class_id, description in sdoh_mitigation_subclasses:
        cur.execute("""
            INSERT INTO sdoh_mitigation_subclasses (subclass_id, label, parent_class_id, description) 
            VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (subclass_id, label, parent_class_id, description))
    print(f"Seeded {len(sdoh_mitigation_subclasses)} SDOH mitigation subclasses")
    
    # --- SDOH Mitigation Mappings (Social Hazard → Service Mappings) ---
    sdoh_mitigation_mappings = [
        # === HOUSING HAZARDS === #
        # Eviction Risk → Multiple housing interventions
        ('EVICTION', 'housing_emergency', 'housing'),
        ('EVICTION', 'rent_assistance', 'housing'),
        ('EVICTION', 'legal_aid', 'legal'),
        ('EVICTION', 'benefits_advocacy', 'legal'),
        
        # Homelessness → Emergency housing + support services
        ('HOMELESS', 'housing_emergency', 'housing'),
        ('HOMELESS', 'case_management', 'social'),
        ('HOMELESS', 'benefits_advocacy', 'legal'),
        ('HOMELESS', 'mental_health', 'health'),
        
        # Severe Overcrowding → Housing assistance + utilities
        ('OVERCROWDING', 'rent_assistance', 'housing'),
        ('OVERCROWDING', 'housing_repair', 'housing'),
        ('OVERCROWDING', 'utility_assistance', 'housing'),
        
        # General Housing Instability → Housing support
        ('HOUSING', 'rent_assistance', 'housing'),
        ('HOUSING', 'utility_assistance', 'housing'),
        
        # === FOOD HAZARDS === #
        # Chronic Food Insecurity → Multiple food resources
        ('CHRONIC_FOOD', 'food_pantry', 'food_bank'),
        ('CHRONIC_FOOD', 'food_vouchers', 'food_bank'),
        ('CHRONIC_FOOD', 'senior_meals', 'food_bank'),
        ('CHRONIC_FOOD', 'benefits_advocacy', 'legal'),
        
        # Acute Food Crisis → Emergency food + advocacy
        ('ACUTE_FOOD', 'food_pantry', 'food_bank'),
        ('ACUTE_FOOD', 'mobile_pantry', 'food_bank'),
        ('ACUTE_FOOD', 'benefits_advocacy', 'legal'),
        
        # General Food Insecurity → Food assistance
        ('FOOD', 'food_pantry', 'food_bank'),
        ('FOOD', 'senior_meals', 'food_bank'),
        
        # === TRANSPORTATION HAZARDS === #
        # Medical Transport Barrier → Medical transport options
        ('MEDICAL_TRANSPORT', 'medical_transport', 'transport'),
        ('MEDICAL_TRANSPORT', 'volunteer_drivers', 'transport'),
        ('MEDICAL_TRANSPORT', 'public_transit', 'transport'),
        
        # General Transport Barrier → Multiple transport options
        ('GENERAL_TRANSPORT', 'volunteer_drivers', 'transport'),
        ('GENERAL_TRANSPORT', 'public_transit', 'transport'),
        ('GENERAL_TRANSPORT', 'vehicle_repair', 'transport'),
        
        # === SOCIAL HAZARDS === #
        # Severe Social Isolation → Multiple social interventions
        ('SOCIAL_ISOLATION', 'visiting_program', 'social'),
        ('SOCIAL_ISOLATION', 'senior_center', 'social'),
        ('SOCIAL_ISOLATION', 'support_groups', 'social'),
        ('SOCIAL_ISOLATION', 'case_management', 'social'),
        
        # Linguistic Isolation → Language-appropriate services
        ('LINGUISTIC_ISOLATION', 'senior_center', 'social'),
        ('LINGUISTIC_ISOLATION', 'case_management', 'social'),
        ('LINGUISTIC_ISOLATION', 'primary_care', 'health'),
        
        # Cultural Isolation → Community connection services
        ('CULTURAL_ISOLATION', 'senior_center', 'social'),
        ('CULTURAL_ISOLATION', 'support_groups', 'social'),
        
        # General Social Support → Basic social services
        ('SOCIAL', 'senior_center', 'social'),
        ('SOCIAL', 'support_groups', 'social'),
        
        # === HEALTH HAZARDS === #
        # Medication Access Crisis → Prescription assistance + care
        ('MEDICATION', 'pharmacy_assistance', 'health'),
        ('MEDICATION', 'primary_care', 'health'),
        ('MEDICATION', 'benefits_advocacy', 'legal'),
        
        # Health Insurance Crisis → Healthcare access + advocacy
        ('NO_HEALTH_INSURANCE', 'primary_care', 'health'),
        ('NO_HEALTH_INSURANCE', 'mobile_clinic', 'health'),
        ('NO_HEALTH_INSURANCE', 'benefits_advocacy', 'legal'),
        
        # High Copay → Alternative care options
        ('HIGH_COPAY', 'primary_care', 'health'),
        ('HIGH_COPAY', 'mobile_clinic', 'health'),
        
        # Not Preferred Insurance → Care navigation
        ('NOT_PREFERRED_INSURANCE', 'case_management', 'social'),
        ('NOT_PREFERRED_INSURANCE', 'primary_care', 'health'),
        
        # High Stress → Mental health services
        ('HIGH_STRESS', 'mental_health', 'health'),
        ('HIGH_STRESS', 'support_groups', 'social'),
        ('HIGH_STRESS', 'case_management', 'social'),
        
        # Medium Stress → Support services
        ('MEDIUM_STRESS', 'support_groups', 'social'),
        ('MEDIUM_STRESS', 'senior_center', 'social'),
        
        # === EMPLOYMENT HAZARDS === #
        # Long-term Unemployment → Comprehensive employment support
        ('UNEMPLOYED', 'employment_placement', 'employment'),
        ('UNEMPLOYED', 'job_training', 'employment'),
        ('UNEMPLOYED', 'benefits_advocacy', 'legal'),
        ('UNEMPLOYED', 'case_management', 'social'),
        
        # Underemployment → Skills enhancement
        ('UNDEREMPLOYED', 'job_training', 'employment'),
        ('UNDEREMPLOYED', 'adult_education', 'education'),
        ('UNDEREMPLOYED', 'computer_training', 'education'),
        
        # === EDUCATION HAZARDS === #
        # Critical Literacy Barrier → Education + employment support
        ('LITERACY', 'adult_education', 'education'),
        ('LITERACY', 'computer_training', 'education'),
        ('LITERACY', 'employment_placement', 'employment'),
        
        # Critical Skills Gap → Skills training
        ('SKILLS', 'computer_training', 'education'),
        ('SKILLS', 'job_training', 'employment'),
        ('SKILLS', 'adult_education', 'education'),
        
        # === SAFETY HAZARDS === #
        # Domestic Violence → Safety + support services
        ('DOMESTIC_VIOLENCE', 'emergency_services', 'safety'),
        ('DOMESTIC_VIOLENCE', 'case_management', 'social'),
        ('DOMESTIC_VIOLENCE', 'legal_aid', 'legal'),
        ('DOMESTIC_VIOLENCE', 'mental_health', 'health'),
        
        # Feel Unsafe → Safety assessment + support
        ('UNSAFE', 'emergency_services', 'safety'),
        ('UNSAFE', 'case_management', 'social'),
        ('UNSAFE', 'legal_aid', 'legal'),
        
        # Sometimes Feel Unsafe → Community safety resources
        ('FEEL_UNSAFE', 'case_management', 'social'),
        ('FEEL_UNSAFE', 'support_groups', 'social'), 
                
        # Incarceration History → Reentry support services
        ('JAILTIME', 'case_management', 'social'),
        ('JAILTIME', 'employment_placement', 'employment'),
        ('JAILTIME', 'legal_aid', 'legal'),
        ('JAILTIME', 'benefits_advocacy', 'legal'),
        
        # === FINANCE HAZARDS === #
        # No Income → Comprehensive financial assistance
        ('NO_INCOME', 'benefits_advocacy', 'legal'),
        ('NO_INCOME', 'case_management', 'social'),
        ('NO_INCOME', 'employment_placement', 'employment'),
        ('NO_INCOME', 'food_pantry', 'food_bank'),
        
        # No Savings → Financial planning + assistance
        ('NO_SAVINGS', 'benefits_advocacy', 'legal'),
        ('NO_SAVINGS', 'case_management', 'social'),
        
        # Seasonal Work → Employment stability support
        ('SEASONAL_WORK', 'employment_placement', 'employment'),
        ('SEASONAL_WORK', 'job_training', 'employment'),
        ('SEASONAL_WORK', 'benefits_advocacy', 'legal'),
        
        # === UNMET NEEDS HAZARDS === #
        # Clothing Needs → Basic needs assistance
        ('CLOTHING', 'case_management', 'social'),
        ('CLOTHING', 'benefits_advocacy', 'legal'),
        
        # Utility Needs → Utility assistance
        ('UTILITIES', 'utility_assistance', 'housing'),
        ('UTILITIES', 'benefits_advocacy', 'legal')
    ]
    
    for social_hazard_subclass_id, mitigation_subclass_id, mitigation_class_id in sdoh_mitigation_mappings:
        cur.execute("""
            INSERT INTO sdoh_mitigation_map (social_hazard_subclass_id, mitigation_subclass_id, mitigation_class_id) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (social_hazard_subclass_id, mitigation_subclass_id, mitigation_class_id))
    print(f"Seeded {len(sdoh_mitigation_mappings)} SDOH mitigation mappings")
 

def seed_assessment_hazard_mappings(cur):
    """Seed mappings between assessment scores/codes and hazards"""
    
    # --- ADL Item to Hazard Mapping (Barthel Index) ---
    adl_item_hazard_map = [
        ("bowels", 0, 0, "ADL_BOWELS_DEP", "ADL_HEAVY"),        # Incontinent
        ("bowels", 1, 1, "ADL_BOWELS_PART", "ADL_LIGHT"),       # Occasional accident
        ("bladder", 0, 0, "ADL_BLADDER_DEP", "ADL_HEAVY"),
        ("bladder", 1, 1, "ADL_BLADDER_PART", "ADL_LIGHT"),
        ("grooming", 0, 0, "ADL_GROOM_DEP", "ADL_LIGHT"),
        ("toilet_use", 0, 0, "ADL_TOILET_DEP", "ADL_LIGHT"),
        ("toilet_use", 1, 1, "ADL_TOILET_PART", "ADL_LIGHT"),
        ("feeding", 0, 0, "ADL_FEED_DEP", "ADL_LIGHT"),
        ("feeding", 1, 1, "ADL_FEED_PART", "ADL_LIGHT"),
        ("transfers", 0, 0, "ADL_TRANSF_DEP", "ADL_HEAVY"),
        ("transfers", 1, 2, "ADL_TRANSF_PART", "ADL_LIGHT"),
        ("mobility", 0, 0, "ADL_MOBILITY_DEP", "ADL_HEAVY"),
        ("mobility", 1, 2, "ADL_MOBILITY_PART", "ADL_LIGHT"),
        ("dressing", 0, 0, "ADL_DRESS_DEP", "ADL_LIGHT"),
        ("dressing", 1, 1, "ADL_DRESS_PART", "ADL_LIGHT"),
        ("stairs", 0, 0, "ADL_STAIRS_DEP", "ADL_LIGHT"),
        ("stairs", 1, 1, "ADL_STAIRS_PART", "ADL_LIGHT"),
        ("bathing", 0, 0, "ADL_BATH_DEP", "ADL_LIGHT"),
    ]
    
    for adl_item, score_min, score_max, hazard_subclass_id, hazard_class_id in adl_item_hazard_map:
        cur.execute("""
            INSERT INTO adl_item_hazard_map (adl_item, score_min, score_max, hazard_subclass_id, hazard_class_id) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (adl_item, score_min, score_max, hazard_subclass_id, hazard_class_id))
    print(f"Seeded {len(adl_item_hazard_map)} ADL item hazard mappings")
    
    # --- IADL Item to Hazard Mapping (Lawton IADL) ---
    iadl_item_hazard_map = [
        ("telephone", 0, 0, "IADL_PHONE_DEP", "IADL_NONVEHICLE"),
        ("shopping", 0, 0, "IADL_SHOP_VEH", "IADL_VEHICLE"),
        ("food_preparation", 0, 0, "IADL_COOK_DEP", "IADL_NONVEHICLE"),
        ("housekeeping", 0, 0, "IADL_CLEAN_DEP", "IADL_NONVEHICLE"),
        ("laundry", 0, 0, "IADL_LAUNDRY_DEP", "IADL_NONVEHICLE"),
        ("transportation", 0, 0, "IADL_TRANS_VEH", "IADL_VEHICLE"),
        ("medication", 0, 0, "IADL_MED_DEP", "IADL_NONVEHICLE"),
        ("finances", 0, 0, "IADL_FIN_DEP", "IADL_NONVEHICLE"),
    ]
    
    for iadl_item, score_min, score_max, hazard_subclass_id, hazard_class_id in iadl_item_hazard_map:
        cur.execute("""
            INSERT INTO iadl_item_hazard_map (iadl_item, score_min, score_max, hazard_subclass_id, hazard_class_id) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (iadl_item, score_min, score_max, hazard_subclass_id, hazard_class_id))
    print(f"Seeded {len(iadl_item_hazard_map)} IADL item hazard mappings")
    
    # --- Symptom Code to Hazard Mapping ---
    sx_code_hazard_map = [
        ("R52", "CHRONIC_PAIN", "SX_DISABLING"),   # Chronic pain (chronic/disabling)
        ("R06.0", "SYM_DYSPNEA", "SX_LIFE_THREATENING"),      # Dyspnea (life-threatening)
        ("R53.83", "FATIGUE", "SX_DISABLING"),      # Fatigue (chronic/disabling)
        ("R26.9", "MOB_WALK", "MOB"),              # Gait abnormality (child + parent)
        ("R41.3", "COG_MEM", "COG"),               # Memory loss (child + parent)
    ]
    
    for sx_code, hazard_subclass_id, hazard_class_id in sx_code_hazard_map:
        cur.execute("""
            INSERT INTO sx_code_hazard_map (sx_code, hazard_subclass_id, hazard_class_id) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (sx_code, hazard_subclass_id, hazard_class_id))
    print(f"Seeded {len(sx_code_hazard_map)} symptom code hazard mappings")
    
    # --- Diagnosis Code to Hazard Mapping ---
    dx_code_hazard_map = [
        ("G30.9", "COG_MEM", "COG"),          # Alzheimer's (child + parent)
        ("F03.90", "COG_MEM", "COG"),         # Dementia (child + parent)
        ("I69.351", "MOB_WALK", "MOB"),       # Hemiplegia (child + parent)
        ("M81.0", "MOB_WALK", "MOB"),         # Osteoporosis (child + parent)
        ("E11.9", "MED_ENDO", "MED"),         # Type 2 Diabetes (endocrine subclass)
        ("F32.9", "MOOD_DEP", "DX_MOOD_BEHAVIORAL"),        # Depression (child + parent)
        ("I10", "MED_CARDIO", "MED"),         # Essential Hypertension (cardiovascular subclass)
    ]
    
    for dx_code, hazard_subclass_id, hazard_class_id in dx_code_hazard_map:
        cur.execute("""
            INSERT INTO dx_code_hazard_map (dx_code, hazard_subclass_id, hazard_class_id) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (dx_code, hazard_subclass_id, hazard_class_id))
    print(f"Seeded {len(dx_code_hazard_map)} diagnosis code hazard mappings")
    
    # --- Prescription Code to Hazard Mapping ---
    rx_code_hazard_map = [
        ("RX011", "CHRONIC_PAIN", "SX_DISABLING"),   # Gabapentin for chronic pain (child + parent)
        ("RX013", "MOOD_DEP", "DX_MOOD_BEHAVIORAL"),           # Sertraline for depression (child + parent)
        ("RX004", None, "MED"),                    # Metformin (diabetes, parent only)
    ]
    
    for rx_code, hazard_subclass_id, hazard_class_id in rx_code_hazard_map:
        cur.execute("""
            INSERT INTO rx_code_hazard_map (rx_code, hazard_subclass_id, hazard_class_id) 
            VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
        """, (rx_code, hazard_subclass_id, hazard_class_id))
    print(f"Seeded {len(rx_code_hazard_map)} prescription code hazard mappings")
    
    # --- PRAPARE Item to Social Hazard Mapping ---
    # Format: (field_name, score_min, score_max, social_hazard_subclass_id, social_hazard_class_id)
    prapare_item_hazard_map = [
        # Demographics & Culture (0=No, 1=Yes, 2=Unknown, 3=Decline)
        ("hispanic", 1, 1, "CULTURAL_ISOLATION", "LOW_NEED_SOCIAL"),  # Hispanic/Latino = Yes
        ("race_asian", 1, 1, "CULTURAL_ISOLATION", "LOW_NEED_SOCIAL"),  # Asian = True
        ("race_native_hawaiian", 1, 1, "CULTURAL_ISOLATION", "LOW_NEED_SOCIAL"),  # Native Hawaiian = True
        ("race_pacific_islander", 1, 1, "CULTURAL_ISOLATION", "LOW_NEED_SOCIAL"),  # Pacific Islander = True
        ("race_black", 1, 1, "CULTURAL_ISOLATION", "LOW_NEED_SOCIAL"),  # Black = True
        ("race_american_indian", 1, 1, "CULTURAL_ISOLATION", "LOW_NEED_SOCIAL"),  # American Indian = True
        
        # Work & Language (0=No, 1=Yes, 2=Decline)
        ("military_service", 1, 1, "CULTURAL_ISOLATION", "LOW_NEED_SOCIAL"),  # Military service = Yes
        ("farm_work", 1, 1, "SEASONAL_WORK", "LOW_NEED_FINANCE"),  # Farm work = Yes
        ("primary_language", 0, 0, "LINGUISTIC_ISOLATION", "HIGH_NEED_SOCIAL"),  # Language other than English
        
        # Housing (0=No housing, 1=Temporary, 2=Have housing, 3=Decline)
        ("housing_situation", 0, 0, "HOMELESS", "HIGH_NEED_HOUSING"),  # Do not have housing
        ("housing_situation", 1, 1, "EVICTION", "HIGH_NEED_HOUSING"),  # Temporary housing
        ("housing_worry", 2, 2, "OVERCROWDING", "LOW_NEED_HOUSING"),  # Worried about housing
        ("housing_worry", 1, 1, "OVERCROWDING", "LOW_NEED_HOUSING"),  # Slightly worried
        
        # Insurance (0=None, 1=Medicaid, 2=Medicare, 3=CHIP, 4=Private, 5=VA, 6=Other, 7=No Answer)
        ("primary_insurance", 0, 0, "NO_HEALTH_INSURANCE", "HIGH_NEED_INSURANCE"),  # No insurance
        ("primary_insurance", 1, 1, "NOT_PREFERRED_INSURANCE", "LOW_NEED_INSURANCE"),  # Medicaid
        ("primary_insurance", 3, 3, "HIGH_COPAY", "LOW_NEED_INSURANCE"),  # CHIP
        
        # Income (0=<$10k, 1=$10-25k, 2=$25-50k, 3=$50-75k, 4=$75k+, 5=Unknown, 6=Decline)
        ("annual_income", 0, 0, "NO_INCOME", "HIGH_NEED_FINANCE"),  # <$10,000
        ("annual_income", 1, 1, "NO_SAVINGS", "LOW_NEED_FINANCE"),  # $10,000-24,999
        
        # Education (0=<HS, 1=HS/GED, 2=Some college, 3=Associate, 4=Bachelor, 5=Graduate, 6=Unknown, 7=Decline)
        ("education_level", 0, 0, "LITERACY", "HIGH_NEED_EDUCATION"),  # Less than high school
        ("education_level", 1, 2, "SKILLS", "LOW_NEED_EDUCATION"),  # HS/GED or some college
        
        # Employment (0=Unemployed, 1=Part-Time, 2=Full-Time, 3=Retired/Student, 4=Decline)
        ("employment_status", 0, 0, "UNEMPLOYED", "HIGH_NEED_EMPLOYMENT"),  # Unemployed
        ("employment_status", 1, 1, "UNDEREMPLOYED", "LOW_NEED_EMPLOYMENT"),  # Part-time
        
        # Transportation (0=No, 1=Yes medical, 2=Yes non-medical, 3=Unable to respond)
        ("transportation_barrier", 1, 1, "MEDICAL_TRANSPORT", "HIGH_NEED_TRANSPORTATION"),  # Medical appointments
        ("transportation_barrier", 2, 2, "GENERAL_TRANSPORT", "LOW_NEED_TRANSPORTATION"),  # Non-medical
        
        # Individual Unmet Needs (Boolean fields - True = need exists)
        ("unmet_food", 1, 1, "CHRONIC_FOOD", "HIGH_NEED_UNMET_NEEDS"),  # Food need
        ("unmet_clothing", 1, 1, "CLOTHING", "LOW_NEED_UNMET_NEEDS"),  # Clothing need
        ("unmet_utilities", 1, 1, "UTILITIES", "LOW_NEED_UNMET_NEEDS"),  # Utilities need
        ("unmet_childcare", 1, 1, "CHILD_CARE", "LOW_NEED_UNMET_NEEDS"),  # Childcare need
        ("unmet_healthcare", 1, 1, "MEDICATION", "HIGH_NEED_UNMET_NEEDS"),  # Healthcare need
        ("unmet_phone", 1, 1, "PHONE", "LOW_NEED_UNMET_NEEDS"),  # Phone need
        ("unmet_other", 1, 1, "OTHER", "LOW_NEED_UNMET_NEEDS"),  # Other needs
        
        # Social Contact (0=Daily, 1=3-5/week, 2=1-2/week, 3=<1/week, 4=Decline)
        ("social_contact", 3, 3, "SOCIAL_ISOLATION", "HIGH_NEED_SOCIAL"),  # Less than once per week
        ("social_contact", 2, 2, "SOCIAL", "LOW_NEED_SOCIAL"),  # 1-2 per week
        
        # Stress Level (0=None, 1=Little, 2=Some, 3=A lot, 4=Extremely, 5=Unknown, 6=Decline)
        ("stress_level", 4, 4, "HIGH_STRESS", "HIGH_NEED_HEALTH"),  # Extremely stressed
        ("stress_level", 3, 3, "MEDIUM_STRESS", "LOW_NEED_HEALTH"),  # A lot of stress
        
        # Safety (0=No, 1=Sometimes, 2=Yes, 3=Decline) for feel_safe
        ("feel_safe", 0, 0, "UNSAFE", "HIGH_NEED_SAFETY"),  # Do not feel safe
        ("feel_safe", 1, 1, "FEEL_UNSAFE", "LOW_NEED_SAFETY"),  # Sometimes feel safe
        
        # Domestic Violence & Incarceration (0=No, 1=Yes, 2=Decline)
        ("domestic_violence", 1, 1, "DOMESTIC_VIOLENCE", "HIGH_NEED_SAFETY"),  # Yes to domestic violence
        ("incarceration_history", 1, 1, "JAILTIME", "LOW_NEED_SAFETY"),  # Yes to incarceration
        
        # ACORN Food Security (0=Never, 1=Sometimes, 2=Often, 3=Unknown, 4=Decline)
        ("food_worry", 2, 2, "CHRONIC_FOOD", "HIGH_NEED_FOOD"),  # Often worried about food
        ("food_worry", 1, 1, "ACUTE_FOOD", "LOW_NEED_FOOD"),  # Sometimes worried
        ("food_didnt_last", 2, 2, "CHRONIC_FOOD", "HIGH_NEED_FOOD"),  # Food often didn't last
        ("food_didnt_last", 1, 1, "ACUTE_FOOD", "LOW_NEED_FOOD"),  # Food sometimes didn't last
        ("need_food_help", 1, 1, "CHRONIC_FOOD", "HIGH_NEED_FOOD"),  # Need food help
        
        # Household Size Risk (1-20 people)
        ("household_size", 7, 20, "OVERCROWDING", "LOW_NEED_HOUSING")  # Large household (7+ people)
    ]
    
    for prapare_item, score_min, score_max, social_hazard_subclass_id, social_hazard_class_id in prapare_item_hazard_map:
        cur.execute("""
            INSERT INTO prapare_item_hazard_map (prapare_item, score_min, score_max, social_hazard_subclass_id, social_hazard_class_id) 
            VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (prapare_item, score_min, score_max, social_hazard_subclass_id, social_hazard_class_id))
    print(f"Seeded {len(prapare_item_hazard_map)} PRAPARE item hazard mappings")



def seed_hazard_service_mappings(cur):
    """Seed mappings between hazards and appropriate services using direct ID-based mappings"""
    
    # --- Hazard to Service Subclass Mappings (from seed_codes.py) ---
    hazard_service_map = [
        # --- Granular Barthel ADL subclasses ---
        # Bowels
        ("ADL_BOWELS_DEP", "SVC_TOIL", "SVC_HEAVY_PC"),
        ("ADL_BOWELS_PART", "SVC_TOIL", "SVC_HEAVY_PC"),
        # Bladder
        ("ADL_BLADDER_DEP", "SVC_TOIL", "SVC_HEAVY_PC"),
        ("ADL_BLADDER_PART", "SVC_TOIL", "SVC_HEAVY_PC"),
        # Grooming
        ("ADL_GROOM_DEP", "SVC_GROOM", "SVC_LIGHT_PC"),
        # Toilet Use
        ("ADL_TOILET_DEP", "SVC_TOIL_LIGHT", "SVC_LIGHT_PC"),
        ("ADL_TOILET_PART", "SVC_TOIL_LIGHT", "SVC_LIGHT_PC"),
        # Feeding
        ("ADL_FEED_DEP", "SVC_FEED", "SVC_LIGHT_PC"),
        ("ADL_FEED_PART", "SVC_FEED", "SVC_LIGHT_PC"),
        # Transfers
        ("ADL_TRANSF_DEP", "SVC_TRAN", "SVC_HEAVY_PC"),
        ("ADL_TRANSF_PART", "SVC_TRAN", "SVC_HEAVY_PC"),
        # Mobility
        ("ADL_MOBILITY_DEP", "SVC_MOB", "SVC_HEAVY_PC"),
        ("ADL_MOBILITY_PART", "SVC_MOB", "SVC_HEAVY_PC"),
        # Stairs
        ("ADL_STAIRS_DEP", "SVC_STAIR", "SVC_HEAVY_PC"),
        ("ADL_STAIRS_PART", "SVC_STAIR", "SVC_HEAVY_PC"),
        # Dressing
        ("ADL_DRESS_DEP", "SVC_DRESS", "SVC_LIGHT_PC"),
        ("ADL_DRESS_PART", "SVC_DRESS", "SVC_LIGHT_PC"),
        # Bathing
        ("ADL_BATH_DEP", "SVC_BATH", "SVC_HEAVY_PC"),
        
        # --- Granular IADL mappings ---
        # Vehicle-dependent
        ("IADL_SHOP_VEH", "SVC_SHOP", "SVC_VEHICLE_HS"),
        ("IADL_TRANS_VEH", "SVC_TRANS", "SVC_VEHICLE_HS"),
        # Non-vehicle
        ("IADL_PHONE_DEP", "SVC_PHONE", "SVC_NONVEHICLE_HS"),
        ("IADL_LAUNDRY_DEP", "SVC_LAUND", "SVC_NONVEHICLE_HS"),
        ("MEAL_PREP", "SVC_MEAL", "SVC_NONVEHICLE_HS"),
        ("IADL_MED_DEP", "SVC_MED", "SVC_NONVEHICLE_HS"),
        ("IADL_FIN_DEP", "SVC_FIN", "SVC_NONVEHICLE_HS"),
        
        # --- New hazard categories ---
        # Cognitive
        ("COG_MEM", "SVC_COG_STIM", "SVC_COG_SUP"),
        ("COG_DEC", "SVC_COG_GUID", "SVC_COG_SUP"),
        # Mobility
        ("MOB_WALK", "SVC_MOB_AIDE", "SVC_MOB_TH"),
        ("MOB_FALL", "SVC_FALL_PREV", "SVC_MOB_TH"),
        # Symptoms - Life Threatening
        ("SYM_PAIN_ACUTE", "SVC_EMERG", "SVC_SYM_LIFE"),
        ("SYM_DYSPNEA", "SVC_RESP", "SVC_SYM_LIFE"),
        # Symptoms - Disabling
        ("CHRONIC_PAIN", "SVC_PAIN", "SVC_SYM_DISAB"),
        ("FATIGUE", "SVC_ENERGY", "SVC_SYM_DISAB"),
        # Mood/Behavioral
        ("MOOD_DEP", "SVC_COUNSEL", "SVC_MOOD"),
        ("MOOD_DISINH", "SVC_BEHAV", "SVC_MOOD"),
        # Medical
        ("MED_POLY", "SVC_MED_REV", "SVC_MED_MGMT"),
        ("MED_MULTI", "SVC_MULTI", "SVC_MED_MGMT"),
        ("MED_CARDIO", "SVC_CARDIO", "SVC_MED_MGMT"),
        ("MED_ENDO", "SVC_ENDO", "SVC_MED_MGMT"),
        ("MED_NEURO", "SVC_NEURO", "SVC_MED_MGMT"),
        ("MED_RESP", "SVC_RESP", "SVC_MED_MGMT"),
        ("MED_RENAL", "SVC_RENAL", "SVC_MED_MGMT"),
        ("MED_GI", "SVC_GI", "SVC_MED_MGMT"),
        ("MED_MUSCULO", "SVC_MUSCULO", "SVC_MED_MGMT"),

    ]
    
    cur.executemany("INSERT INTO hazard_service_map (hazard_subclass_id, service_subclass_id, parent_service_class_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", hazard_service_map)
    print(f"Seeded {len(hazard_service_map)} hazard-service mappings")
    
    # --- Parent Hazard to Service Class Mappings ---
    parent_hazard_service_map = [
        ("ADL_HEAVY", "SVC_HEAVY_PC"),
        ("ADL_LIGHT", "SVC_LIGHT_PC"),
        ("IADL_VEHICLE", "SVC_VEHICLE_HS"),
        ("IADL_NONVEHICLE", "SVC_NONVEHICLE_HS"),
        ("COG", "SVC_COG_SUP"),
        ("MOB", "SVC_MOB_TH"),
        ("SX_LIFE_THREATENING", "SVC_SYM_LIFE"),
        ("SX_DISABLING", "SVC_SYM_DISAB"),
        ("DX_MOOD_BEHAVIORAL", "SVC_MOOD"),
        ("MED", "SVC_MED_MGMT"),
    ]
    
    cur.executemany("INSERT INTO parent_hazard_service_map (hazard_class_id, service_class_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", parent_hazard_service_map)
    print(f"Seeded {len(parent_hazard_service_map)} parent hazard-service mappings")
