-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Patients
CREATE TABLE patients (
    patient_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT,
    dob DATE,
    gender TEXT,
    phone VARCHAR,
    email VARCHAR
);

-- 2. Patient History
-- Diagnosis Codes Reference Table
CREATE TABLE dx_codes (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

-- Treatment Codes Reference Table
CREATE TABLE tx_codes (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

-- Medication Codes Reference Table
CREATE TABLE rx_codes (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

-- Symptom Codes Reference Table
CREATE TABLE sx_codes (
    code TEXT PRIMARY KEY,
    description TEXT NOT NULL
);

-- Updated Patient History Table
CREATE TABLE patient_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    dx_codes TEXT[],  -- Array of diagnosis codes
    tx_codes TEXT[],  -- Array of treatment codes
    rx_codes TEXT[],  -- Array of medication codes
    sx_codes TEXT[],  -- Array of symptom codes
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);


-- 3. IADL Answers
CREATE TABLE iadl_answers (
    -- existing columns
    -- ...
    -- Add unique constraint for (patient_id, date_completed)
    UNIQUE (patient_id, date_completed),
    iadl_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    date_completed DATE,
    telephone INTEGER,
    shopping INTEGER,
    food_preparation INTEGER,
    housekeeping INTEGER,
    laundry INTEGER,
    transportation INTEGER,
    medication INTEGER,
    finances INTEGER,
    answers JSONB
);

-- 4. ADL Answers
CREATE TABLE adl_answers (
    -- existing columns
    -- ...
    -- Add unique constraint for (patient_id, date_completed)
    UNIQUE (patient_id, date_completed),
    adl_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    date_completed DATE,
    feeding INTEGER,
    bathing INTEGER,
    grooming INTEGER,
    dressing INTEGER,
    bowels INTEGER,
    bladder INTEGER,
    toilet_use INTEGER,
    transfers INTEGER,
    mobility INTEGER,
    stairs INTEGER,
    answers JSONB
);



-- 5. PRAPARE Responses (FHIR US-Core PRAPARE questionnaire answers)
-- Based on HL7 FHIR US-Core PRAPARE Questionnaire (v2.3.0)
-- https://build.fhir.org/ig/HL7/US-Core/Questionnaire-prapare-example.html
CREATE TABLE prapare_answers (
    prapare_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    date_completed DATE DEFAULT CURRENT_DATE,
    
    -- 1. Personal Characteristics (1-5) - LOINC: 93025-5
    hispanic INTEGER, -- 0=No, 1=Yes, 2=Unknown, 3=Decline to answer (LOINC: 32624-9)
    race_asian INTEGER DEFAULT 0,             -- 1=Yes, 0=No (LOINC: 32624-9)
    race_native_hawaiian INTEGER DEFAULT 0,   -- 1=Yes, 0=No (LOINC: 32624-9)
    race_pacific_islander INTEGER DEFAULT 0,  -- 1=Yes, 0=No (LOINC: 32624-9)
    race_black INTEGER DEFAULT 0,             -- 1=Yes, 0=No (LOINC: 32624-9)
    race_white INTEGER DEFAULT 0,             -- 1=Yes, 0=No (LOINC: 32624-9)
    race_american_indian INTEGER DEFAULT 0,   -- 1=Yes, 0=No (LOINC: 32624-9)
    race_other INTEGER DEFAULT 0,             -- 1=Yes, 0=No (LOINC: 32624-9)
    race_no_answer INTEGER DEFAULT 0,         -- 1=Yes, 0=No (LOINC: 32624-9)
    
    -- 2. Employment (6-7)
    farm_work INTEGER,             -- 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)
    military_service INTEGER,       -- 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)
    
    -- 3. Language (8)
    primary_language INTEGER,       -- 0=English, 1=Other, 2=Decline to answer (LOINC: 63504-5)
    
    -- 4. Family & Home (9-11)
    household_size INTEGER,         -- Number of household members (LOINC: 63504-5)
    housing_situation INTEGER,      -- 0=Do not have housing, 1=Temporary housing, 2=Have housing, 3=Decline to answer (LOINC: 71802-3)
    housing_worry INTEGER,          -- 0=Not at all worried, 1=Slightly worried, 2=worried, 3=Decline to answer (LOINC: 93027-1)
    
    -- 5. Money & Resources (12-14)
    education_level INTEGER,        -- 0=Less than high school, 1=High school/GED, 2=Some college, 3=Associate's degree, 4=Bachelor's degree, 5=Graduate degree, 6=Unknown, 7=Decline to answer (LOINC: 63504-5)
    employment_status INTEGER,      -- 0=Unemployed, 1=Part-Time, 2=Full-Time, 3=Retired/Student, 4=Decline to answer (LOINC: 63504-5)
    
    -- 6. Insurance (15)
    primary_insurance INTEGER DEFAULT 0,          --0=None, 1=Medicaid, 2=Medicare, 3=CHIP, 4=Private, 5=VA, 6=Other, 7=No Answer
    
    annual_income INTEGER,           -- 0=<$10,000, 1=$10,000-24,999, 2=$25,000-49,999, 3=$50,000-74,999, 4=$75,000+, 5=Unknown, 6=Decline to answer (LOINC: 63504-5)
    
    -- 6. Material Security (16-17)
    -- Unmet needs (16) - Multi-select (LOINC: 63504-5)
    unmet_food INTEGER DEFAULT 0,           -- 1=Yes, 0=No
    unmet_clothing INTEGER DEFAULT 0,       -- 1=Yes, 0=No
    unmet_utilities INTEGER DEFAULT 0,      -- 1=Yes, 0=No
    unmet_childcare INTEGER DEFAULT 0,      -- 1=Yes, 0=No
    unmet_healthcare INTEGER DEFAULT 0,     -- 1=Yes, 0=No
    unmet_phone INTEGER DEFAULT 0,          -- 1=Yes, 0=No
    unmet_other INTEGER DEFAULT 0,          -- 1=Yes, 0=No
    unmet_no_answer INTEGER DEFAULT 0,      -- 1=Yes, 0=No
    
    -- Transportation (17) - LOINC: 93039-6
    transportation_barrier INTEGER,  -- 0=No, 1=Yes (medical appointments), 2=Yes (non-medical appointments), 3=Unable to respond
    
    -- 7. Social & Emotional Health (18-19)
    social_contact INTEGER,          -- 0=Daily, 1=3 to 5 per week, 2=1-2 per week, 3=Less than once per week, 4=Decline to answer (LOINC: 63504-5)
    stress_level INTEGER,            -- 0=None, 1=A little, 2=Some, 3=A lot, 4=Extremely, 5=Unknown, 6=Decline to answer (LOINC: 63504-5)
    
    -- 8. Safety (20-22)
    incarceration_history INTEGER,   -- 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)
    feel_safe INTEGER,               -- 0=No, 1=Sometimes, 2=Yes, 3=Decline to answer (LOINC: 93035-4)
    domestic_violence INTEGER,       -- 0=No, 1=Yes, 2=Decline to answer (LOINC: 63504-5)
    
    -- 9. ACORN Food Security (23-25) - LOINC: 93037-0, 93038-8, 63504-5
    food_worry INTEGER,              -- 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
    food_didnt_last INTEGER,         -- 0=Never true, 1=Sometimes true, 2=Often true, 3=Unknown, 4=Decline to answer
    need_food_help INTEGER,          -- 0=No, 1=Yes, 2=Unknown, 3=Decline to answer
    
    -- Metadata
    raw_responses JSONB,             -- Raw questionnaire responses (flexible JSON storage)
    z_codes TEXT[],                  -- Generated Z-codes from responses
    created_at TIMESTAMP DEFAULT NOW(),
    assessed_by TEXT,                -- Clinician/assessor ID or name
    notes TEXT,                      -- Free-text notes
    
    -- Ensure only one assessment per patient per day
    UNIQUE(patient_id, date_completed)
);

-- 6. Questionnaire Summary*
CREATE TABLE questionnaire_summary (
    summary_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    iadl_id UUID REFERENCES iadl_answers(iadl_id) ON DELETE SET NULL,
    adl_id UUID REFERENCES adl_answers(adl_id) ON DELETE SET NULL,
    prapare_id UUID REFERENCES prapare_answers(prapare_id) ON DELETE SET NULL,
    adl_score INTEGER,
    adl_frequency INTEGER, -- 1=Daily, 2=Weekly, 3=Monthly, 4=Occasional **for ML
    adl_intensity INTEGER, -- 1=Light, 2=Heavy 0=None **for ML
    iadl_score INTEGER,
    iadl_frequency INTEGER, -- 1=Daily, 2=Weekly, 3=Monthly, 4=Occasional **for ML
    iadl_intensity INTEGER, -- 1=Light, 2=Heavy 0=None**for ML
    housing_stability_score INTEGER,
    food_security_score INTEGER,
    transportation_score INTEGER,
    social_isolation_score INTEGER,
    economic_security_score INTEGER,
    education_employment_score INTEGER,
    total_sdoh_score INTEGER,
    total_score INTEGER,
    date_completed DATE
);
-- 6. Hazards
CREATE TABLE hazards (
    hazard_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    history_id UUID REFERENCES patient_history(history_id) ON DELETE SET NULL,
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    description TEXT,
    hazard_type TEXT,
    severity TEXT,
    weight INTEGER CHECK (weight >=0 AND weight <= 10)
);
-- 7. Risks with ordinal likelihood
CREATE TABLE risks (
    risk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    history_id UUID REFERENCES patient_history(history_id) ON DELETE SET NULL,
    hazard_id UUID REFERENCES hazards(hazard_id) ON DELETE CASCADE,
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    severity FLOAT CHECK (severity >= 0 AND severity <= 10),
    likelihood INTEGER CHECK (likelihood >= 0 AND likelihood <= 6),
    risk_score FLOAT,
    notes TEXT
);

-- 7a. Social Risks (for PRAPARE-based social hazards)
CREATE TABLE social_risks (
    social_risk_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    social_hazard_code VARCHAR(100) NOT NULL,     -- Maps to social_hazards or social_hazards_subclasses
    social_hazard_type VARCHAR(50) NOT NULL,      -- 'class' or 'subclass'
    social_hazard_label VARCHAR(255) NOT NULL,
    social_hazard_description TEXT,
    severity FLOAT CHECK (severity >= 0 AND severity <= 5),
    likelihood INTEGER CHECK (likelihood >= 0 AND likelihood <= 6),
    risk_score FLOAT,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Services (Reference Table)
CREATE TABLE services (
    service_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name TEXT NOT NULL,
    service_category TEXT,
    default_frequency TEXT,
    description TEXT
);

-- 9. Contractors (Reference Table)
CREATE TABLE contractors (
    contractor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    contact_info JSONB,
    qualifications TEXT
);

-- 10. Contractor Service Costs (Reference Table)
CREATE TABLE costs (
    cost_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    contractor_id UUID REFERENCES contractors(contractor_id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(service_id) ON DELETE CASCADE,
    amount NUMERIC(12, 2),
    billing_cycle TEXT,
    weekly_frequency INTEGER DEFAULT 1, -- How many times per week
    payer TEXT,
    UNIQUE(contractor_id, service_id, weekly_frequency)
);



-- 10b. Severity Levels Reference Table
CREATE TABLE severity_levels (
    severity_code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    utility_weight FLOAT NOT NULL,
    description TEXT
);

-- 10c. Frequency Levels Reference Table
CREATE TABLE frequency_levels (
    frequency_code TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    ordinal INTEGER NOT NULL,
    description TEXT
);

-- Hazard/Service/Resource Classification tables are potential targets for ML

-- 11. Hazard/Service Classification Tables 
-- Parent hazard categories
CREATE TABLE hazard_classes (
    class_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

-- Granular hazards (child), FK to parent hazard class
CREATE TABLE hazard_subclasses (
    subclass_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    parent_class_id TEXT REFERENCES hazard_classes(class_id),
    description TEXT
);

-- Parent service categories
CREATE TABLE service_classes (
    class_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    description TEXT
);

-- Granular services (child), FK to parent service class
CREATE TABLE service_subclasses (
    subclass_id TEXT PRIMARY KEY,
    label TEXT NOT NULL,
    parent_class_id TEXT REFERENCES service_classes(class_id),
    description TEXT
);
-- 10d. Caregiver Services Reference Table
CREATE TABLE caregiver_services (
    service_code TEXT PRIMARY KEY,
    service_name TEXT NOT NULL,
    category TEXT,
    description TEXT,
    typical_cost NUMERIC(12, 2)
);

-- 14. Social Hazard Classes (Parent class - follows service_classes pattern)
CREATE TABLE social_hazards (
    class_id TEXT PRIMARY KEY, -- 'High_Need_Food', 'Housing', 'Transport', etc. vs. Low_Need 
    label TEXT NOT NULL,   -- 'Food', 'Housing', 'Transport', 'Social', 'Health', 'Safety', 'Income'
    description TEXT   --social includes language and cultural adaptation, health includes medicines.
);

-- 15. Social Hazard Subclasses (Child class - follows service_subclasses pattern)
-- Detailed subhazards identified by specific PRAPARE questions but can be expanded but must be linked to 
-- social hazard class (e.g. high need housing--> eviction, homelessness,low need housing -->Overcrowding, rent strain;
-- high need food--> chronic food insecurity, low need food -->intermittent food insecurity;
-- high need social --> extreme social isolation, linguistic isolation, low need social--> language barrier
CREATE TABLE social_hazards_subclasses (
    subclass_id TEXT PRIMARY KEY,       -- 'eviction', 'homelessness', 'medical_transport', 'chronic_food_insecurity', 'intermittent_food_insecurity', 'domestic_violence'
    label TEXT NOT NULL,
    parent_class_id TEXT REFERENCES social_hazards(class_id),
    description TEXT
);


-- 14. Social Hazard Mitigation Services Classes (Parent class -social hazard mitigation)
-- we are using an FQIH categorization of services to pair with social hazards. Specifically 
-- whether a service is emergency or enabling (e.g. prevent harm, vs. support welfare).
-- this is the 2 level parent category for services
CREATE TABLE sdoh_mitigations (
    class_id TEXT PRIMARY KEY,  -- 'emergency food', 'emergency housing', 'enabling housing', 'enabling food', etc.
    label TEXT NOT NULL,   
    description TEXT
);

-- 15. Community Resource Subclasses (Child class - follows service_subclasses pattern)
-- A mitigation is any action, intervention, or resource that can reduce the severity or
-- likelihood of a social hazard. general classes emergency/enabling should align with high/low need social hazards.
-- emergency housing (shelters, subsidized housing, legal aid), enabling housing (housing search, rental subsidies)
-- emergency food (SNAP, food delivery), enabling food (food banks, community meals, budgeting classes), 
-- emergency transportation (public transit, ride sharing), enabling transportation (bus passes, ride sharing).
-- enabling social support (community centers, support groups),
-- emergency safety (police, fire, emergency medical services),
-- emergency income (welfare, food stamps, tax assistance)
CREATE TABLE sdoh_mitigation_subclasses (
    subclass_id TEXT PRIMARY KEY,       -- 'food_pantry', 'housing_emergency', 'medical_transport'
    label TEXT NOT NULL,
    parent_class_id TEXT REFERENCES sdoh_mitigations(class_id),
    description TEXT
);



-- 16. Community Resources (Actual resource instances/providers)
CREATE TABLE community_resources (
    resource_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_subclass_id TEXT REFERENCES sdoh_mitigation_subclasses(subclass_id) NOT NULL,
    
    -- Basic Information
    name TEXT NOT NULL,
    description TEXT,
    
    -- Contact Information
    address TEXT,
    city TEXT,
    state TEXT DEFAULT 'NC',
    zip_code TEXT,
    phone TEXT,
    website TEXT,
    email TEXT,
    
    -- Service Details
    services_offered JSONB,
    cost_info TEXT,
    operating_hours JSONB,
    seasonal_availability BOOLEAN DEFAULT FALSE,
    appointment_required BOOLEAN DEFAULT FALSE,
    
    -- Geographic and Access
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    service_area_miles INTEGER DEFAULT 25,
    transportation_provided BOOLEAN DEFAULT FALSE,
    
    -- Administrative
    active BOOLEAN DEFAULT TRUE,
    verified_date DATE,
    capacity_current INTEGER,
    capacity_max INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Community Resource Costs (Reference Table)
CREATE TABLE resource_costs (
    resource_cost_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_id UUID REFERENCES community_resources(resource_id) ON DELETE CASCADE,
    service_type TEXT NOT NULL, -- e.g., 'one_time', 'monthly', 'per_visit'
    amount NUMERIC(12, 2),
    billing_cycle TEXT,
    weekly_frequency INTEGER DEFAULT 1, -- How many times per week if applicable
    eligibility_requirements TEXT,
    payer TEXT,
    UNIQUE(resource_id, service_type, weekly_frequency)
);

-- 13. Mapping tables for source data to hazards
-- ADL item/score to hazard
CREATE TABLE adl_item_hazard_map (
    adl_item TEXT NOT NULL,              -- e.g. 'bathing', 'feeding'
    score_min INTEGER NOT NULL,          -- minimum score for mapping
    score_max INTEGER NOT NULL,          -- maximum score for mapping
    hazard_subclass_id TEXT REFERENCES hazard_subclasses(subclass_id),
    hazard_class_id TEXT REFERENCES hazard_classes(class_id),
    PRIMARY KEY (adl_item, score_min, score_max)
);

-- IADL item/score to hazard
CREATE TABLE iadl_item_hazard_map (
    iadl_item TEXT NOT NULL,             -- e.g. 'shopping', 'housekeeping'
    score_min INTEGER NOT NULL,
    score_max INTEGER NOT NULL,
    hazard_subclass_id TEXT REFERENCES hazard_subclasses(subclass_id),
    hazard_class_id TEXT REFERENCES hazard_classes(class_id),
    PRIMARY KEY (iadl_item, score_min, score_max)
);

-- Symptom code to hazard
CREATE TABLE sx_code_hazard_map (
    sx_code TEXT NOT NULL REFERENCES sx_codes(code),
    hazard_subclass_id TEXT REFERENCES hazard_subclasses(subclass_id),
    hazard_class_id TEXT REFERENCES hazard_classes(class_id),
    PRIMARY KEY (sx_code)
);

-- Diagnosis code to hazard
CREATE TABLE dx_code_hazard_map (
    dx_code TEXT NOT NULL REFERENCES dx_codes(code),
    hazard_subclass_id TEXT REFERENCES hazard_subclasses(subclass_id),
    hazard_class_id TEXT REFERENCES hazard_classes(class_id),
    PRIMARY KEY (dx_code)
);

-- Medication code to hazard (optional, for high-risk meds)
CREATE TABLE rx_code_hazard_map (
    rx_code TEXT NOT NULL REFERENCES rx_codes(code),
    hazard_subclass_id TEXT REFERENCES hazard_subclasses(subclass_id),
    hazard_class_id TEXT REFERENCES hazard_classes(class_id),
    PRIMARY KEY (rx_code)
);

-- Map prapare items to social hazards (employment, education, housing, income, safety, social, health)
CREATE TABLE prapare_item_hazard_map (
    prapare_item TEXT NOT NULL,              -- e.g. food insecurity, housing instability
    score_min INTEGER NOT NULL,          -- minimum score for mapping
    score_max INTEGER NOT NULL,          -- maximum score for mapping
    social_hazard_subclass_id TEXT REFERENCES social_hazards_subclasses(subclass_id),
    social_hazard_class_id TEXT REFERENCES social_hazards(class_id),
    PRIMARY KEY (prapare_item, score_min, score_max)
);

-- 18. SDOH Mitigation Map (Maps PRAPARE responses to community resource types - follows sx_code_hazard_map pattern)
--examples: high need housing, eviction--> emergency housing, legal aid;
-- high need housing, homelessness--> emergency housing, shelter;
-- high need food, chronic food insecurity--> emergency food, SNAP;
-- low need food, intermittent food insecurity--> enabling food, food pantry, community meals
CREATE TABLE sdoh_mitigation_map (
    social_hazard_subclass_id TEXT REFERENCES social_hazards_subclasses(subclass_id),
    mitigation_subclass_id TEXT REFERENCES sdoh_mitigation_subclasses(subclass_id),
    mitigation_class_id TEXT REFERENCES sdoh_mitigations(class_id),
    PRIMARY KEY (social_hazard_subclass_id, mitigation_subclass_id)
);

CREATE TABLE parent_sdoh_mitigation_map (
    social_hazard_class_id TEXT REFERENCES social_hazards(class_id),
    service_class_id TEXT REFERENCES service_classes(class_id),
    mitigation_class_id TEXT REFERENCES sdoh_mitigations(class_id),
    PRIMARY KEY (social_hazard_class_id, mitigation_class_id)
);
-- Mapping: child hazard to (list of) child services and a parent service
CREATE TABLE hazard_service_map (
    hazard_subclass_id TEXT REFERENCES hazard_subclasses(subclass_id),
    service_subclass_id TEXT REFERENCES service_subclasses(subclass_id),
    parent_service_class_id TEXT REFERENCES service_classes(class_id),
    PRIMARY KEY (hazard_subclass_id, service_subclass_id)
);

-- Mapping: parent hazard to parent service (for elucidation of the rule)
CREATE TABLE parent_hazard_service_map (
    hazard_class_id TEXT REFERENCES hazard_classes(class_id),
    service_class_id TEXT REFERENCES service_classes(class_id),
    PRIMARY KEY (hazard_class_id, service_class_id)
);


-- 11. Home Care Plans (Patient-Specific Care Plans)
CREATE TABLE home_care_plan (
    plan_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    risk_id UUID REFERENCES risks(risk_id) ON DELETE CASCADE,
    service_id UUID REFERENCES services(service_id) ON DELETE CASCADE,
    contractor_id UUID REFERENCES contractors(contractor_id) ON DELETE CASCADE,
    cost_id UUID REFERENCES costs(cost_id) ON DELETE CASCADE,
    frequency TEXT,
    custom_cost NUMERIC(12, 2),
    start_date DATE,
    end_date DATE,
    status TEXT DEFAULT 'planned',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- 12. Recommendation Settings (User-entered preferences for recommendations)
CREATE TABLE recommendation_settings (
    rec_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    hazard_code TEXT NOT NULL,
    service_description TEXT NOT NULL,
    service_category TEXT,
    frequency TEXT,
    estimated_cost NUMERIC(12, 2) DEFAULT 0.0,
    provider TEXT,
    priority TEXT DEFAULT 'Medium',
    notes TEXT,
    selected BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(patient_id, hazard_code, service_description)
);

-- 13. Recommendation Report
CREATE TABLE recommendation_report (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(patient_id) ON DELETE CASCADE,
    generated_on DATE DEFAULT CURRENT_DATE,
    risks JSONB,
    services JSONB,
    contractors JSONB,
    costs JSONB,
    content TEXT
);
