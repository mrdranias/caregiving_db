"""
Sample patient data for testing and development.
This data changes frequently and should only be loaded in dev/test environments.
"""
import psycopg2
import uuid
import json
from datetime import datetime, date

def seed_sample_patients(cur):
    """Seed sample patients for testing"""
    
    # Sample patients
    sample_patients = [
        {
            'name': 'Eleanor Rodriguez',
            'dob': date(1938, 3, 15),
            'gender': 'Female',
            'phone': '555-0123',
            'email': 'eleanor.rodriguez@email.com'
        },
        {
            'name': 'Robert Chen',
            'dob': date(1945, 11, 22),
            'gender': 'Male',
            'phone': '555-0124',
            'email': 'robert.chen@email.com'
        },
        {
            'name': 'Margaret Johnson',
            'dob': date(1942, 7, 8),
            'gender': 'Female',
            'phone': '555-0125',
            'email': 'margaret.johnson@email.com'
        }
    ]
    
    patient_ids = []
    for patient in sample_patients:
        patient_id = str(uuid.uuid4())
        patient_ids.append(patient_id)
        cur.execute("""
            INSERT INTO patients (patient_id, name, dob, gender, phone, email)
            VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (patient_id, patient['name'], patient['dob'], 
              patient['gender'], patient['phone'], patient['email']))
    
    print(f"Seeded {len(sample_patients)} sample patients")
    return patient_ids

def seed_sample_patient_history(cur, patient_ids):
    """Seed sample patient medical history"""
    
    # Sample history records
    history_records = [
        {
            'patient_id': patient_ids[0],  # Eleanor
            'dx_codes': ['E11.9', 'I10', 'M81.0'],
            'tx_codes': ['99213', '99214', '80053'],
            'rx_codes': ['RX004', 'RX002', 'RX003'],
            'sx_codes': ['R52', 'R53.83']  # Chronic pain, Fatigue
        },
        {
            'patient_id': patient_ids[1],  # Robert
            'dx_codes': ['G30.9', 'I25.10', 'F41.9'],
            'tx_codes': ['99213', '97110', '90834'],
            'rx_codes': ['RX021', 'RX022', 'RX016'],
            'sx_codes': ['R41.3']  # Memory problems
        },
        {
            'patient_id': patient_ids[2],  # Margaret
            'dx_codes': ['J44.9', 'M17.9', 'F32.9'],
            'tx_codes': ['99214', '97530', '99406'],
            'rx_codes': ['RX008', 'RX009', 'RX010'],
            'sx_codes': ['R06.0', 'M54.9']  # Shortness of breath, Back pain
        }
    ]
    
    for record in history_records:
        history_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO patient_history (
                history_id, patient_id, dx_codes, tx_codes, rx_codes, sx_codes, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING
        """, (
            history_id, record['patient_id'], 
            record['dx_codes'], record['tx_codes'], 
            record['rx_codes'], record['sx_codes'],
            datetime.now()
        ))
    
    print(f"Seeded {len(history_records)} patient history records")

def seed_sample_adl_data(cur, patient_ids):
    """Seed sample ADL assessment data"""
    
    adl_records = [
        {
            # Eleanor - moderate ADL impairment (similar to Alice Smith example)
            'patient_id': patient_ids[0],
            'feeding': 1, 'bathing': 1, 'grooming': 1, 'dressing': 1,
            'bowels': 1, 'bladder': 1, 'toilet_use': 1, 'transfers': 2,
            'mobility': 2, 'stairs': 1,
            'answers': '{"notes": "Needs some help with most ADLs"}'
        },
        {
            # Robert - severe ADL impairment (similar to Bob Jones example)
            'patient_id': patient_ids[1],
            'feeding': 0, 'bathing': 0, 'grooming': 0, 'dressing': 0,
            'bowels': 0, 'bladder': 0, 'toilet_use': 0, 'transfers': 0,
            'mobility': 0, 'stairs': 0,
            'answers': '{"notes": "Needs total assistance with all ADLs"}'
        },
        {
            # Margaret - mild ADL impairment
            'patient_id': patient_ids[2],
            'feeding': 2, 'bathing': 1, 'grooming': 2, 'dressing': 2,
            'bowels': 2, 'bladder': 1, 'toilet_use': 2, 'transfers': 1,
            'mobility': 1, 'stairs': 1,
            'answers': '{"notes": "Independent for most ADLs, minimal help needed"}'
        }
    ]
    
    for record in adl_records:
        cur.execute("""
            INSERT INTO adl_answers (
                patient_id, date_completed, feeding, bathing, grooming, dressing, 
                bowels, bladder, toilet_use, transfers, mobility, stairs, answers
            ) VALUES (%s, CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (patient_id, date_completed) DO NOTHING
        """, (
            record['patient_id'], record['feeding'], record['bathing'], record['grooming'],
            record['dressing'], record['bowels'], record['bladder'], record['toilet_use'],
            record['transfers'], record['mobility'], record['stairs'], record['answers']
        ))
    
    print(f"Seeded {len(adl_records)} ADL assessment records")

def seed_sample_iadl_data(cur, patient_ids):
    """Seed sample IADL assessment data"""
    
    iadl_records = [
        {
            # Eleanor - moderate IADL impairment (similar to Alice Smith example)
            'patient_id': patient_ids[0],
            'telephone': 1, 'shopping': 0, 'food_preparation': 0, 'housekeeping': 1,
            'laundry': 0, 'transportation': 1, 'medication': 1, 'finances': 0,
            'answers': '{"notes": "Some IADL difficulty, especially food prep and finances"}'
        },
        {
            # Robert - severe IADL impairment (similar to Bob Jones example)
            'patient_id': patient_ids[1],
            'telephone': 0, 'shopping': 0, 'food_preparation': 0, 'housekeeping': 0,
            'laundry': 0, 'transportation': 0, 'medication': 0, 'finances': 0,
            'answers': '{"notes": "Dependent for all IADLs"}'
        },
        {
            # Margaret - mild IADL impairment
            'patient_id': patient_ids[2],
            'telephone': 1, 'shopping': 1, 'food_preparation': 1, 'housekeeping': 1,
            'laundry': 1, 'transportation': 0, 'medication': 1, 'finances': 1,
            'answers': '{"notes": "Independent for most IADLs, needs help with transportation"}'
        }
    ]
    
    for record in iadl_records:
        cur.execute("""
            INSERT INTO iadl_answers (
                patient_id, date_completed, telephone, shopping, food_preparation, housekeeping,
                laundry, transportation, medication, finances, answers
            ) VALUES (%s, CURRENT_DATE, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (patient_id, date_completed) DO NOTHING
        """, (
            record['patient_id'], record['telephone'], record['shopping'], record['food_preparation'],
            record['housekeeping'], record['laundry'], record['transportation'],
            record['medication'], record['finances'], record['answers']
        ))
    
    print(f"Seeded {len(iadl_records)} IADL assessment records")

def seed_sample_prapare_data(cur, patient_ids):
    """Seed sample PRAPARE assessment data"""
    
    # Integer-coded PRAPARE responses matching current prapare_answers schema
    prapare_responses = [
        {
            'patient_id': patient_ids[0],
            'hispanic': 1,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'race_white': 1,
            'race_black': 0,
            'race_asian': 0,
            'race_native_hawaiian': 0,
            'race_pacific_islander': 0,
            'race_american_indian': 0,
            'race_other': 0,
            'race_no_answer': 0,
            'farm_work': 0,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'military_service': 0,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'primary_language': 0,  # 0 = English, 1 = Other, 2 = Decline to answer
            'household_size': 3,  # Number of people in household
            'housing_situation': 2,  # 0=No housing, 1=Temporary housing, 2=Have housing, 3=Decline to answer
            'housing_worry': 0,  # 0=Not worried, 1=Slightly worried, 2=Worried, 3=Decline to answer
            'education_level': 2,  # 0=<high school, 1=High school/GED, 2=Some college, 3=Associate, 4=Bachelor, 5=Graduate, 6=Unknown, 7=Decline
            'employment_status': 1,  # 0=Unemployed, 1=Part-time, 2=Full-time, 3=Retired/Student, 4=Decline to answer
            'primary_insurance': 1,  # 0=None, 1=Medicaid, 2=Medicare, 3=CHIP, 4=Private, 5=VA, 6=Other, 7=No Answer
            'annual_income': 2,  # 0=<$10,000, 1=$10,000-24,999, 2=$25,000-49,999, 3=$50,000-74,999, 4=$75,000+, 5=Unknown, 6=Decline to answer
            # Unmet needs - individual boolean fields
            'unmet_food': 1,
            'unmet_clothing': 0,
            'unmet_utilities': 1,
            'unmet_childcare': 0,
            'unmet_healthcare': 0,
            'unmet_phone': 1,
            'unmet_other': 0,
            'unmet_no_answer': 0,
            'transportation_barrier': 0,  # 0=No, 1=Yes (medical), 2=Yes (non-medical), 3=Unable to respond
            'social_contact': 2,  # 0=Daily, 1=3-5 per week, 2=1-2 per week, 3=Less than once per week, 4=Decline to answer
            'stress_level': 2,  # 0=None, 1=A little, 2=Some, 3=A lot, 4=Extremely, 5=Unknown, 6=Decline to answer
            'incarceration_history': 0,  # 0=No, 1=Yes, 2=Decline to answer
            'feel_safe': 2,  # 0=No, 1=Sometimes, 2=Yes, 3=Decline to answer
            'domestic_violence': 0,  # 0=No, 1=Yes, 2=Decline to answer
            # ACORN Food Security
            'food_worry': 1,  # 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
            'food_didnt_last': 1,  # 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
            'need_food_help': 1,  # 0=No, 1=Yes, 2=Unknown, 3=Decline to answer
            'z_codes': ['Z59.1', 'Z59.41', 'Z91.120']
        },
        {
            'patient_id': patient_ids[1],
            'hispanic': 0,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'race_white': 0,
            'race_black': 1,
            'race_asian': 0,
            'race_native_hawaiian': 0,
            'race_pacific_islander': 0,
            'race_american_indian': 0,
            'race_other': 0,
            'race_no_answer': 0,
            'farm_work': 0,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'military_service': 1,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'primary_language': 1,  # 1 = English, 0 = Language other than English, -1 = I choose not to answer
            'household_size': 2,  # Number of people in household
            'housing_situation': 1,  # 1 = I have housing, 0 = I do not have housing, -1 = I choose not to answer
            'housing_worry': 0,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'education_level': 3,  # 1 = Less than high school, 2 = High school diploma/GED, 3 = More than high school, -1 = I choose not to answer
            'employment_status': 2,  # 0=Unemployed, 1=Part-Time, 2=Full-Time, 3=Retired/Student, 4=Decline to answer
            'primary_insurance': 7,  # 0=None, 1=Medicaid, 2=Medicare, 3=CHIP, 4=Private, 5=VA, 6=Other, 7=No Answer
            'annual_income': 3,  # 0=<$10,000, 1=$10,000-24,999, 2=$25,000-49,999, 3=$50,000-74,999, 4=$75,000+, 5=Unknown, 6=Decline to answer
            # Unmet needs - individual boolean fields
            'unmet_food': 0,
            'unmet_clothing': 0,
            'unmet_utilities': 0,
            'unmet_childcare': 0,
            'unmet_healthcare': 0,
            'unmet_phone': 0,
            'unmet_other': 0,
            'unmet_no_answer': 1,
            'transportation_barrier': 0,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'social_contact': 4,  # 1=Less than once a week, 2=1-2 times a week, 3=3-5 times a week, 4=5+ times a week, -1=I choose not to answer
            'stress_level': 2,  # 1=Not at all, 2=A little bit, 3=Somewhat, 4=Quite a bit, 5=Very much, -1=I choose not to answer
            'incarceration_history': 0,  # 0=No, 1=Yes, 2=Decline to answer
            'feel_safe': 1,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'domestic_violence': 0,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            # ACORN Food Security
            'food_worry': 0,  # 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
            'food_didnt_last': 0,  # 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
            'need_food_help': 0,  # 0=No, 1=Yes, 2=Unknown, 3=Decline to answer
            'z_codes': ['Z87.891']
        },
        {
            'patient_id': patient_ids[2],
            'hispanic': -1,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'race_white': 0,
            'race_black': 0,
            'race_asian': 1,
            'race_native_hawaiian': 0,
            'race_pacific_islander': 0,
            'race_american_indian': 0,
            'race_other': 0,
            'race_no_answer': 0,
            'farm_work': -1,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'military_service': 0,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'primary_language': 0,  # 1 = English, 0 = Language other than English, -1 = I choose not to answer
            'household_size': 1,  # Number of people in household
            'housing_situation': 0,  # 1 = I have housing, 0 = I do not have housing, -1 = I choose not to answer
            'housing_worry': 1,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'education_level': 1,  # 1 = Less than high school, 2 = High school diploma/GED, 3 = More than high school, -1 = I choose not to answer
            'employment_status': 0,  # 0=Unemployed, 1=Part-Time, 2=Full-Time, 3=Retired/Student, 4=Decline to answer
            'primary_insurance': 0,  # 0=None, 1=Medicaid, 2=Medicare, 3=CHIP, 4=Private, 5=VA, 6=Other, 7=No Answer
            'annual_income': 0,  # 0=<$10,000, 1=$10,000-24,999, 2=$25,000-49,999, 3=$50,000-74,999, 4=$75,000+, 5=Unknown, 6=Decline to answer
            # Unmet needs - individual boolean fields
            'unmet_food': 1,
            'unmet_clothing': 1,
            'unmet_utilities': 1,
            'unmet_childcare': 0,
            'unmet_healthcare': 1,
            'unmet_phone': 1,
            'unmet_other': 0,
            'unmet_no_answer': 0,
            'transportation_barrier': 1,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'social_contact': 1,  # 1=Less than once a week, 2=1-2 times a week, 3=3-5 times a week, 4=5+ times a week, -1=I choose not to answer
            'stress_level': 5,  # 1=Not at all, 2=A little bit, 3=Somewhat, 4=Quite a bit, 5=Very much, -1=I choose not to answer
            'incarceration_history': 0,  # 0=No, 1=Yes, 2=Decline to answer
            'feel_safe': 0,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            'domestic_violence': -1,  # 1 = Yes, 0 = No, -1 = I choose not to answer
            # ACORN Food Security
            'food_worry': 2,  # 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
            'food_didnt_last': 2,  # 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
            'need_food_help': 1,  # 0=No, 1=Yes, 2=Unknown, 3=Decline to answer
            'z_codes': ['Z59.0', 'Z59.1', 'Z59.41', 'Z91.120', 'Z60.2']
        }
    ]
    
    for record in prapare_responses:
        prapare_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO prapare_answers (
                prapare_id, patient_id, date_completed, assessed_by, notes,
                hispanic, race_white, race_black, race_asian, race_native_hawaiian,
                race_pacific_islander, race_american_indian, race_other, race_no_answer,
                farm_work, military_service, primary_language, household_size, housing_situation,
                housing_worry, education_level, employment_status, primary_insurance,
                annual_income, unmet_food, unmet_clothing, unmet_utilities, unmet_childcare,
                unmet_healthcare, unmet_phone, unmet_other, unmet_no_answer,
                transportation_barrier, social_contact, stress_level, incarceration_history,
                feel_safe, domestic_violence, food_worry, food_didnt_last, need_food_help,
                z_codes, raw_responses
            ) VALUES (
                %s, %s, CURRENT_DATE, 'System', 'Sample data',
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, '{}'::jsonb
            ) ON CONFLICT DO NOTHING
        """, (
            prapare_id, record['patient_id'], record['hispanic'], record['race_white'],
            record['race_black'], record['race_asian'], record['race_native_hawaiian'],
            record['race_pacific_islander'], record['race_american_indian'],
            record['race_other'], record['race_no_answer'], record['farm_work'],
            record['military_service'], record['primary_language'], record['household_size'], record['housing_situation'],
            record['housing_worry'], record['education_level'], record['employment_status'],
            record['primary_insurance'], record['annual_income'], record['unmet_food'],
            record['unmet_clothing'], record['unmet_utilities'], record['unmet_childcare'],
            record['unmet_healthcare'], record['unmet_phone'], record['unmet_other'],
            record['unmet_no_answer'], record['transportation_barrier'], record['social_contact'],
            record['stress_level'], record['incarceration_history'], record['feel_safe'],
            record['domestic_violence'], record['food_worry'], record['food_didnt_last'],
            record['need_food_help'], record['z_codes']
        ))
    
    print(f"Seeded {len(prapare_responses)} PRAPARE assessment records")
