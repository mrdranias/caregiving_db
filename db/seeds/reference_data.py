"""
Reference data for medical codes - these are static lookup values
that don't change frequently and are used across the system.
"""
import psycopg2

def seed_medical_codes(cur):
    """Seed medical diagnosis, treatment, and prescription codes"""
    
    # Diagnosis codes (ICD-10)
    dx_codes = [
        ("E11.9", "Type 2 diabetes mellitus without complications"),
        ("I10", "Essential (primary) hypertension"),
        ("E78.5", "Hyperlipidemia, unspecified"),
        ("M81.0", "Age-related osteoporosis"),
        ("I25.10", "Atherosclerotic heart disease of native coronary artery"),
        ("M17.9", "Osteoarthritis of knee, unspecified"),
        ("M19.90", "Osteoarthritis, unspecified site"),
        ("J44.9", "Chronic obstructive pulmonary disease, unspecified"),
        ("N18.9", "Chronic kidney disease, unspecified"),
        ("F32.9", "Major depressive disorder, single episode, unspecified"),
        ("F03.90", "Dementia, unspecified"),
        ("I69.351", "Hemiplegia, unspecified side"),
        ("G30.9", "Alzheimer's disease, unspecified"),
        ("G20", "Parkinson's disease"),
        ("F41.9", "Anxiety disorder, unspecified"),
        ("I48.91", "Atrial fibrillation, unspecified"),
        ("I50.9", "Heart failure, unspecified"),
        ("J45.909", "Unspecified asthma, uncomplicated"),
        ("E03.9", "Hypothyroidism, unspecified"),
        ("N39.0", "Urinary tract infection, site not specified"),
        ("K21.9", "Gastro-esophageal reflux disease without esophagitis"),
        ("M54.5", "Low back pain"),
        ("R51", "Headache"),
        ("I63.9", "Cerebral infarction, unspecified"),
        ("K59.00", "Constipation, unspecified"),
        ("R53.83", "Other fatigue"),
        ("R26.9", "Unspecified abnormalities of gait and mobility")
    ]
    cur.executemany("INSERT INTO dx_codes (code, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", dx_codes)
    print(f"Seeded {len(dx_codes)} diagnosis codes")

    # Treatment codes (CPT)
    tx_codes = [
        ("99213", "Office/outpatient visit, established patient"),
        ("99214", "Office/outpatient visit, est. pt, moderate complexity"),
        ("99396", "Periodic comprehensive preventive medicine, established patient"),
        ("80053", "Comprehensive metabolic panel"),
        ("81002", "Urinalysis, non-automated"),
        ("36415", "Collection of venous blood by venipuncture"),
        ("93000", "Electrocardiogram, routine"),
        ("90471", "Immunization administration"),
        ("90460", "Immunization admin through 18 years"),
        ("97110", "Therapeutic exercises"),
        ("97530", "Therapeutic activities"),
        ("99406", "Smoking cessation counseling"),
        ("96372", "Therapeutic, prophylactic, or diagnostic injection"),
        ("94760", "Pulse oximetry"),
        ("82947", "Glucose; quantitative, blood"),
        ("99395", "Periodic comprehensive preventive medicine, established patient"),
        ("97140", "Manual therapy techniques"),
        ("G0439", "Annual wellness visit, subsequent"),
        ("G0442", "Annual alcohol misuse screening"),
        ("G0444", "Annual depression screening"),
        ("G0446", "Intensive behavioral therapy for cardiovascular disease"),
        ("G0447", "Obesity counseling"),
        ("G0451", "Developmental testing, limited"),
        ("99407", "Smoking cessation counseling, intensive"),
        ("90658", "Influenza virus vaccine")
    ]
    cur.executemany("INSERT INTO tx_codes (code, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", tx_codes)
    print(f"Seeded {len(tx_codes)} treatment codes")

    # Prescription codes
    rx_codes = [
        ("RX001", "Lisinopril"),
        ("RX002", "Levothyroxine"),
        ("RX003", "Atorvastatin"),
        ("RX004", "Metformin"),
        ("RX005", "Amlodipine"),
        ("RX006", "Metoprolol"),
        ("RX007", "Omeprazole"),
        ("RX008", "Albuterol"),
        ("RX009", "Sertraline"),
        ("RX010", "Ibuprofen"),
        ("RX011", "Gabapentin"),
        ("RX012", "Prednisone"),
        ("RX013", "Furosemide"),
        ("RX014", "Warfarin"),
        ("RX015", "Insulin"),
        ("RX016", "Aspirin"),
        ("RX017", "Acetaminophen"),
        ("RX018", "Hydrochlorothiazide"),
        ("RX019", "Clopidogrel"),
        ("RX020", "Pantoprazole"),
        ("RX021", "Donepezil"),
        ("RX022", "Memantine"),
        ("RX023", "Carbidopa-Levodopa"),
        ("RX024", "Rivastigmine"),
        ("RX025", "Tamsulosin")
    ]
    cur.executemany("INSERT INTO rx_codes (code, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", rx_codes)
    print(f"Seeded {len(rx_codes)} prescription codes")

    # Symptom codes (ICD-10 symptom codes)  
    sx_codes = [
        ("R52", "Chronic pain"),
        ("R06.0", "Shortness of breath (Dyspnea)"),
        ("R06.02", "Chest pain"),
        ("R42", "Dizziness"),
        ("R53.83", "Fatigue"),
        ("R11.10", "Nausea"),
        ("R51", "Headache"),
        ("M25.50", "Joint pain"),
        ("M54.9", "Back pain"),
        ("G47.9", "Sleep disturbance"),
        ("R63.0", "Loss of appetite"),
        ("R63.4", "Weight loss"),
        ("R60.9", "Swelling (Edema)"),
        ("R53.1", "Weakness"),
        ("R41.0", "Confusion"),
        ("R41.3", "Memory problems"),
        ("F41.9", "Anxiety"),
        ("F32.9", "Depression"),
        ("R26.9", "Balance problems (Gait abnormality)"),
        ("H53.9", "Visual disturbance"),
        ("H91.90", "Hearing loss"),
        ("K59.00", "Constipation"),
        ("R32", "Urinary incontinence"),
        ("L98.9", "Skin problems"),
        ("R13.10", "Dysphagia (Difficulty swallowing)")
    ]
    cur.executemany("INSERT INTO sx_codes (code, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", sx_codes)
    print(f"Seeded {len(sx_codes)} symptom codes")

    #   ("SX01", "Cough"),
    #   ("SX02", "Fever"),
    #   ("SX03", "Abdominal pain"),
    #   ("SX04", "Sore throat"),
    #    ("SX05", "Rash"),
    #   ("SX06", "Diarrhea"),
    #    ("SX07", "Insomnia"),
    #    ("SX08", "Falls"),
    #    ("SX09", "Numbness"),
