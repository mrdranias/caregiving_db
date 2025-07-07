"""
PRAPARE Questionnaire Administration UI
FHIR SDOH Clinical Care IG v2.3.0 - PRAPARE Questionnaire
Follows ADL/IADL form pattern with patient_id_state integration
"""

import gradio as gr
import requests
import json
import os
from datetime import date
from typing import Dict, Any, Optional, List

# Get API URL from environment
API_URL = os.getenv("API_URL", "http://localhost:8000")

def build_prapare_ui(patient_id_state, form_data_state):
    """Build the PRAPARE questionnaire form interface - follows ADL/IADL pattern"""
    
    def submit_prapare(patient_id, *args):
        """Submit PRAPARE form data to backend"""
        try:
            # Parse form data
            form_data = parse_prapare_form_data(args)
            form_data["patient_id"] = patient_id
            
            # Submit to API
            api_url = f"{API_URL}/prapare/submit"
            resp = requests.post(api_url, json=form_data)
            
            if resp.ok:
                result = resp.json()
                # Format success message for display
                success_msg = f"✅ PRAPARE Assessment Saved Successfully\n" \
                             f"Total Score: {result.get('total_score', 'N/A')}\n" \
                             f"Risk Level: {result.get('risk_level', 'N/A').title()}\n" \
                             f"Z-Codes: {', '.join(result.get('z_codes', []))}" if result.get('z_codes') else "Z-Codes: None"
                return success_msg, {"prapare": form_data}
            else:
                try:
                    error_detail = resp.json()
                    error_msg = f"❌ Error: {error_detail.get('detail', 'Unknown error')}"
                    return error_msg, {}
                except Exception:
                    return f"❌ Error: {resp.text}", {}
        except Exception as e:
            return f"❌ Error: {str(e)}", {}
    
    def populate_fields(patient_id, form_data):
        """Populate form fields from existing data"""
        try:
            if not patient_id:
                # Return default values for all fields when no patient ID is provided
                return [
                    "",  # patient_id_display
                    None,  # ethnicity
                    False,  # race_asian
                    False,  # race_native_hawaiian
                    False,  # race_pacific_islander
                    False,  # race_black
                    False,  # race_white
                    False,  # race_american_indian
                    False,  # race_other
                    False,  # race_no_answer
                    None,   # farm_work
                    None,   # military_service
                    None,   # primary_language
                    None,   # housing_situation
                    1,      # household_size
                    None,   # housing_worry
                    None,   # education_level
                    None,   # employment_status
                    None,   # primary_insurance
                    None,   # annual_income
                    False,  # unmet_food
                    False,  # unmet_clothing
                    False,  # unmet_utilities
                    False,  # unmet_childcare
                    False,  # unmet_healthcare
                    False,  # unmet_phone
                    False,  # unmet_other
                    False,  # unmet_no_answer
                    None,   # transportation_barrier
                    None,   # social_contact
                    None,   # stress_level
                    None,   # incarceration_history
                    None,   # feel_safe
                    None,   # domestic_violence
                    None,   # food_worry
                    None,   # food_didnt_last
                    None,   # need_food_help
                    ""      # notes
                ]
            
            # Try to get existing PRAPARE data
            api_url = f"{API_URL}/prapare/by_patient/{patient_id}"
            resp = requests.get(api_url)
            
            if resp.ok and resp.status_code != 404:
                data = resp.json()
                # Get form data (36 values for form inputs only)
                form_data = populate_form_from_data(data)
                return form_data if form_data else [None] * 36
            else:
                # Return default values if no data exists for the patient (36 form field values only)
                return [
                    None,  # ethnicity
                    False,  # race_american_indian
                    False,  # race_asian
                    False,  # race_black
                    False,  # race_native_hawaiian
                    False,  # race_pacific_islander
                    False,  # race_white
                    False,  # race_other
                    False,  # race_no_answer
                    None,   # farm_work
                    None,   # military_service
                    None,   # primary_language
                    None,   # housing_situation
                    1,      # household_size
                    None,   # housing_worry
                    None,   # education_level
                    None,   # employment_status
                    None,   # primary_insurance
                    None,   # annual_income
                    False,  # unmet_food
                    False,  # unmet_clothing
                    False,  # unmet_utilities
                    False,  # unmet_childcare
                    False,  # unmet_healthcare
                    False,  # unmet_phone
                    False,  # unmet_other
                    False,  # unmet_no_answer
                    None,   # transportation_barrier
                    None,   # social_contact
                    None,   # stress_level
                    None,   # incarceration_history
                    None,   # feel_safe
                    None,   # domestic_violence
                    None,   # food_worry
                    None,   # food_didnt_last
                    None    # need_food_help
                ]
        except Exception as e:
            print(f"Error populating PRAPARE fields: {str(e)}")
            # Return default values on error (36 form field values only)
            return [
                None,  # ethnicity
                False,  # race_american_indian
                False,  # race_asian
                False,  # race_black
                False,  # race_native_hawaiian
                False,  # race_pacific_islander
                False,  # race_white
                False,  # race_other
                False,  # race_no_answer
                None,   # farm_work
                None,   # military_service
                None,   # primary_language
                None,   # housing_situation
                1,      # household_size
                None,   # housing_worry
                None,   # education_level
                None,   # employment_status
                None,   # primary_insurance
                None,   # annual_income
                False,  # unmet_food
                False,  # unmet_clothing
                False,  # unmet_utilities
                False,  # unmet_childcare
                False,  # unmet_healthcare
                False,  # unmet_phone
                False,  # unmet_other
                False,  # unmet_no_answer
                None,   # transportation_barrier
                None,   # social_contact
                None,   # stress_level
                None,   # incarceration_history
                None,   # feel_safe
                None,   # domestic_violence
                None,   # food_worry
                None,   # food_didnt_last
                None    # need_food_help
            ]
    
    gr.Markdown("# PRAPARE Social Determinants Assessment")
    gr.Markdown("**Protocol for Responding to and Assessing Patients' Assets, Risks, and Experiences**")
    gr.Markdown("*Based on HL7 FHIR US Core PRAPARE Questionnaire*")
    
    # Patient ID display (read-only, synced with main UI)
    patient_id_display = gr.Textbox(
        label="Patient ID", 
        value="", 
        interactive=False,
        visible=True
    )
    
    # 1. Personal Characteristics
    with gr.Group():
        gr.Markdown("## 1. Personal Characteristics")
        
        # Question 1: Hispanic or Latino (LOINC: 32624-9)
        ethnicity = gr.Radio(
            label="1. Are you Hispanic or Latino?",
            choices=[
                "Yes",  # 1
                "No",   # 0
                "I choose not to answer"  # 3 (2=Unknown not used in UI)
            ],
            value=None
        )
        
        # Question 2: Race (multiple choice) - LOINC: 32624-9
        with gr.Column():
            gr.Markdown("**2. Which race(s) are you? (Check all that apply)**")
            race_american_indian = gr.Checkbox(label="American Indian or Alaska Native", value=False)
            race_asian = gr.Checkbox(label="Asian", value=False)
            race_black = gr.Checkbox(label="Black or African American", value=False)
            race_native_hawaiian = gr.Checkbox(label="Native Hawaiian", value=False)
            race_pacific_islander = gr.Checkbox(label="Other Pacific Islander", value=False)
            race_white = gr.Checkbox(label="White", value=False)
            race_other = gr.Checkbox(label="Other race", value=False)
            race_no_answer = gr.Checkbox(label="I choose not to answer", value=False)
        
        # Question 3: Farm work (LOINC: 63504-5)
        farm_work = gr.Radio(
            label="3. In the past 2 years, has seasonal or migrant farm work been your or your family's main source of income?",
            choices=[
                "Yes",  # 1
                "No",   # 0
                "I choose not to answer"  # 2
            ],
            value=None
        )
        
        # Question 4: Military service (LOINC: 63504-5)
        military_service = gr.Radio(
            label="4. Have you ever served on active duty in the U.S. Armed Forces, military Reserves, or National Guard?",
            choices=[
                "No",  # 0
                "Yes",  # 1
                "I choose not to answer"  # 2
            ],
            value=None
        )
        
        # Question 5: Primary language (LOINC: 63504-5)
        primary_language = gr.Radio(
            label="5. What language do you feel most comfortable speaking with a doctor or nurse?",
            choices=[
                "English",  # 0
                "Language other than English",  # 1
                "I choose not to answer"  # 2
            ],
            value=None
        )
    
    # 2. Family & Home
    with gr.Group():
        gr.Markdown("## 2. Family & Home")
        
        # Question 6: Housing situation (LOINC: 71802-3)
        housing_situation = gr.Radio(
            label="6. What is your housing situation today?",
            choices=[
                "I do not have housing (staying with others, in a hotel, in a shelter, living outside on the street, on a beach, in a car, or in a park)",  # 0
                "I am in temporary or emergency housing (including shelters, hotels, transitional housing, or treatment programs)",  # 1
                "I have stable housing (own or rent)",  # 2
                "I choose not to answer"  # 3
            ],
            value=None
        )
        
        # Question 7: Household size (LOINC: 63504-5)
        household_size = gr.Number(
            label="7. Including yourself, how many people live in your home?",
            minimum=1,
            maximum=50,
            step=1,
            value=None
        )
        
        # Question 8: Housing worry (LOINC: 93027-1)
        housing_worry = gr.Radio(
            label="8. How worried are you about losing your housing?",
            choices=[
                "Not at all worried",  # 0
                "Slightly worried",    # 1
                "Worried",            # 2
                "I choose not to answer"  # 3
            ],
            value=None
        )
        

    # 3. Money & Resources
    with gr.Group():
        gr.Markdown("## 3. Money & Resources (LOINC: 63504-5)")
        
        # Question 9: Education level (LOINC: 63504-5)
        education_level = gr.Radio(
            label="9. What is the highest grade or year of school you have completed?",
            choices=[
                "Less than high school",  # 0
                "High school graduate/GED or equivalent",  # 1
                "Some college or technical school (no degree)",  # 2
                "I choose not to answer"  # 3
            ],
            value=None
        )
        
        # Question 10: Employment status
        employment_status = gr.Radio(
            label="10. Which of the following best describes your current work situation?",
            choices=[
                "Unemployed",  # 0
                "Employed part-time (less than 35 hours/week)",  # 1
                "Employed full-time (35+ hours/week)",  # 2
                "Retired, student, or homemaker",  # 3
                "I choose not to answer"  # 4
            ],
            value=None
        )
        
        # Question 11: Primary insurance (single selection)
        primary_insurance = gr.Radio(
            label="11. What is your main source of health insurance coverage?",
            choices=[
                "No insurance of any type",  # 0
                "Medicaid",  # 1
                "Medicare",  # 2
                "CHIP (Children's Health Insurance Program)",  # 3
                "Private insurance (through employer or purchased)",  # 4
                "Veterans/military health care (including TRICARE)",  # 5
                "Other public insurance (not Medicare)",  # 6
                "I choose not to answer"  # 7
            ],
            value=None
        )
        
        # Question 12: Annual income (LOINC: 63504-5)
        annual_income = gr.Radio(
            label="12. What was your total household income in the past year? (before taxes and deductions)",
            choices=[
                "Less than $10,000",  # 0
                "$10,000 to $24,999",  # 1
                "$25,000 to $49,999",  # 2
                "$50,000 to $74,999",  # 3
                "$75,000 or more",  # 4
                "I don't know",  # 5
                "I choose not to answer"  # 6
            ],
            value=None
        )
        
    # 4. Material Security
    with gr.Group():
        gr.Markdown("## 4. Material Security")
        
        # Question 13: Unmet needs (LOINC: 93030-5)
        with gr.Group():
            gr.Markdown("**13. In the past year, have you or family members been unable to get any of the following when really needed?** (Check all that apply)")
            with gr.Row():
                unmet_food = gr.Checkbox(label="Food", info="Unable to get food when needed")
                unmet_clothing = gr.Checkbox(label="Clothing", info="Unable to get clothing when needed")
                unmet_utilities = gr.Checkbox(label="Utilities", info="Unable to pay for utilities when needed")
            with gr.Row():
                unmet_childcare = gr.Checkbox(label="Child care", info="Unable to get child care when needed")
                unmet_healthcare = gr.Checkbox(label="Medicine/Health care", info="Unable to get medicine or healthcare when needed")
                unmet_phone = gr.Checkbox(label="Phone")
                unmet_other = gr.Checkbox(label="Other")
            unmet_no_answer = gr.Checkbox(label="I choose not to answer")
        
        # Question 14: Transportation barriers (LOINC: 93039-6)
        transportation_barrier = gr.Radio(
            label="14. Has lack of transportation kept you from any of the following?",
            choices=[
                "No, I have not had transportation problems",  # 0
                "Yes, I've missed medical appointments",       # 1
                "Yes, I've missed non-medical appointments",   # 2
                "I am unable to respond"                       # 3
            ],
            value=None
        )
    
    # 5. Social & Emotional Health (LOINC: 63504-5)
    with gr.Group():
        gr.Markdown("## 5. Social & Emotional Health")
        
        # Question 15: Social contact (LOINC: 63504-5)
        social_contact = gr.Radio(
            label="15. How often do you see or talk to people you care about and feel close to? (For example, talking to friends, family, or co-workers on the phone, through email or social media, or in person)",
            choices=[
                "Daily",  # 0
                "3 to 5 times per week",  # 1
                "1 to 2 times per week",  # 2
                "Less than once per week",  # 3
                "I choose not to answer"  # 4
            ],
            value=None
        )
        
        # Question 16: Stress level (LOINC: 63504-5)
        stress_level = gr.Radio(
            label="16. In the past 12 months, how would you rate your usual level of stress?",
            choices=[
                "None",  # 0
                "A little",  # 1
                "Some",  # 2
                "A lot",  # 3
                "Extremely",  # 4
                "I don't know",  # 5
                "I choose not to answer"  # 6
            ],
            value=None
        )

    # 6. Safety
    with gr.Group():
        gr.Markdown("## 6. Safety")
        # Question 17 : Incarceration history
        incarceration_history = gr.Radio(
            label ="17. In the past 12 months, have you or a family member been incarcerated?",
            choices=[
                "Yes",  # 1
                "No",  # 0
                "I choose not to answer"  # -1
            ],
            value=None
        )
        # Question 18 : Feel safe
        feel_safe = gr.Radio(
            label ="18. In the past 12 months, how often have you or a family member felt unsafe or threatened?",
            choices=[
                "Never",  # 1
                "Sometimes",  # 2
                "Often",  # 3
                "I choose not to answer"  # 4
            ],
            value=None
        )
        # Question 19 : Domestic violence
        domestic_violence = gr.Radio(
            label ="19. In the past 12 months, have you or a family member experienced domestic violence?",
            choices=[
                "Yes",  # 1
                "No",  # 0
                "I choose not to answer"  # -1
            ],
            value=None
        )
        

    # 7. Food Security (Additional Questions)
    with gr.Group():    
        gr.Markdown("## 7. Food Security (Additional Questions)")
        
        # Question 20: Food worry (ACORN)
        food_worry = gr.Radio(
            label="20. Within the past 12 months, you worried whether your food would run out before you got money to buy more.",
            choices=["Often true", "Sometimes true", "Never true", "I choose not to answer"],
            value=None
        )
        
        # Question 21: Food didn't last (ACORN)
        food_didnt_last = gr.Radio(
            label="21. Within the past 12 months, the food you bought just didn't last and you didn't have money to get more.",
            choices=["Often true", "Sometimes true", "Never true", "I choose not to answer"],
            value=None
        )
        
        # Question 22: Need help with food (ACORN)
        need_food_help = gr.Radio(
            label="22. Do you need help getting food for this week?",
            choices=["Yes", "No", "I choose not to answer"],
            value=None
        )
    
    # Form submission
    with gr.Row():
        submit_btn = gr.Button("Submit PRAPARE Assessment", variant="primary")
        submit_result = gr.HTML()
    
    # Collect all form inputs - MUST MATCH THE ORDER IN populate_fields
    form_inputs = [
        # Personal Characteristics (1-5)
        ethnicity,  # 1. Hispanic/Latino
        race_american_indian,  # 2. Race: American Indian
        race_asian,  # 2. Race: Asian
        race_black,  # 2. Race: Black
        race_native_hawaiian,  # 2. Race: Native Hawaiian
        race_pacific_islander,  # 2. Race: Pacific Islander
        race_white,  # 2. Race: White
        race_other,  # 2. Race: Other
        race_no_answer,  # 2. Race: No answer
        farm_work,  # 3. Farm work
        military_service,  # 4. Military service
        primary_language,  # 5. Primary language
        # Family & Home (6-8)
        housing_situation,  # 6. Housing situation
        household_size,  # 7. Household size
        housing_worry,  # 8. Housing worry
        # Money & Resources (9-12)
        education_level,  # 9. Education level
        employment_status,  # 10. Employment status
        primary_insurance,  # 11. Primary insurance
        annual_income,  # 12. Annual income
        # Material Security (13-14)
        unmet_food,  # 13. Unmet needs: Food
        unmet_clothing,  # 13. Unmet needs: Clothing
        unmet_utilities,  # 13. Unmet needs: Utilities
        unmet_childcare,  # 13. Unmet needs: Childcare
        unmet_healthcare,  # 13. Unmet needs: Healthcare
        unmet_phone,  # 13. Unmet needs: Phone
        unmet_other,  # 13. Unmet needs: Other
        unmet_no_answer,  # 13. Unmet needs: No answer
        transportation_barrier,  # 14. Transportation barrier
        # Social & Emotional Health (15-16)
        social_contact,  # 15. Social contact
        stress_level,  # 16. Stress level
        # Safety (17-19)
        incarceration_history,  # 17. Incarceration history
        feel_safe,  # 18. Feel safe
        domestic_violence,  # 19. Domestic violence
        # Food Security (20-22)
        food_worry,  # 20. Food worry
        food_didnt_last,  # 21. Food didn't last
        need_food_help  # 22. Need food help
    ]
    
    # Set up form interactions
    def submit_prapare(
        patient_id,
        # Personal Characteristics (1-5)
        ethnicity, race_american_indian, race_asian, race_black, race_native_hawaiian, race_pacific_islander,
        race_white, race_other, race_no_answer, farm_work, military_service, primary_language,
        # Family & Home (6-8)
        housing_situation, household_size, housing_worry,
        # Money & Resources (9-12)
        education_level, employment_status, primary_insurance, annual_income,
        # Material Security (13-14)
        unmet_food, unmet_clothing, unmet_utilities, unmet_childcare, unmet_healthcare, unmet_phone, 
        unmet_other, unmet_no_answer, transportation_barrier,
        # Social & Emotional Health (15-16)
        social_contact, stress_level,
        # Safety (17-19)
        incarceration_history, feel_safe, domestic_violence,
        # Food Security (20-22)
        food_worry, food_didnt_last, need_food_help
    ):
        """
        Submit PRAPARE form data to the backend
        Handles the new PRAPARE form structure with 23 questions
        """
        import requests
        import json
        from datetime import datetime
        import os
        
        # Get API URL from environment or use default
        api_url = os.getenv("API_URL", "http://localhost:8000")
        endpoint = f"{api_url}/prapare/submit"
        
        # Prepare the data payload
        data = {
            "patient_id": str(patient_id),
            "date_completed": datetime.now().strftime("%Y-%m-%d"),
            "created_at": datetime.now().isoformat(),
            
            # 1. Personal Characteristics (1-5)
            "hispanic": 1 if ethnicity == "Yes" else (0 if ethnicity == "No" else -1),
            "race_asian": 1 if race_asian else 0,
            "race_native_hawaiian": 1 if race_native_hawaiian else 0,
            "race_pacific_islander": 1 if race_pacific_islander else 0,
            "race_black": 1 if race_black else 0,
            "race_white": 1 if race_white else 0,
            "race_american_indian": 1 if race_american_indian else 0,
            "race_other": 1 if race_other else 0,
            "race_no_answer": 1 if race_no_answer else 0,
            "farm_work": 1 if farm_work == "Yes" else (0 if farm_work == "No" else -1),
            "military_service": 1 if military_service == "Yes" else (0 if military_service == "No" else -1),
            "primary_language": {
                "English": 1,
                "Language other than English": 0,
                "I choose not to answer": 2
            }.get(primary_language, 2),
            
            # 2. Family & Home (6-8) - LOINC: 71802-3, 93027-1
            "household_size": int(household_size) if household_size and str(household_size).isdigit() else None,
            "housing_situation": {
                "I do not have housing (staying with others, in a hotel, in a shelter, living outside on the street, on a beach, in a car, or in a park)": 0,
                "I am in temporary or emergency housing (including shelters, hotels, transitional housing, or treatment programs)": 1,
                "I have stable housing (own or rent)": 2,
                "I choose not to answer": 3
            }.get(housing_situation, -1),
            "housing_worry": {
                "Not at all worried": 0,
                "Slightly worried": 1,
                "Worried": 2,
                "I choose not to answer": 3
            }.get(housing_worry, -1),
            
            # 3. Money & Resources (9-12) - LOINC: 63504-5
            "education_level": {
                "Less than high school": 0,
                "High school graduate/GED or equivalent": 1,
                "Some college or technical school (no degree)": 2,
                "Associate's degree or technical certificate": 3,
                "Bachelor's degree": 4,
                "Graduate or professional degree": 5,
                "I don't know": 6,
                "I choose not to answer": 7
            }.get(education_level, -1),
            "employment_status": {
                "Unemployed": 0,
                "Employed part-time (less than 35 hours/week)": 1,
                "Employed full-time (35+ hours/week)": 2,
                "Retired, student, or homemaker": 3,
                "I choose not to answer": 4
            }.get(employment_status, 4),
            "primary_insurance": {
                "No insurance of any type": 0,
                "Medicaid": 1,
                "Medicare": 2,
                "CHIP (Children's Health Insurance Program)": 3,
                "Private insurance (through employer or purchased)": 4,
                "Veterans/military health care (including TRICARE)": 5,
                "Other public insurance (not Medicare)": 6,
                "I choose not to answer": 7
            }.get(primary_insurance, -1),
            "annual_income": {
                "Less than $10,000": 0,
                "$10,000 to $24,999": 1,
                "$25,000 to $49,999": 2,
                "$50,000 to $74,999": 3,
                "$75,000 or more": 4,
                "I don't know": 5,
                "I choose not to answer": 6
            }.get(annual_income, 6),
            
            # Unmet needs (all individual boolean fields)
            "unmet_food": 1 if unmet_food else 0,
            "unmet_clothing": 1 if unmet_clothing else 0,
            "unmet_utilities": 1 if unmet_utilities else 0,
            "unmet_childcare": 1 if unmet_childcare else 0,
            "unmet_healthcare": 1 if unmet_healthcare else 0,
            "unmet_phone": 1 if unmet_phone else 0,
            "unmet_other": 1 if unmet_other else 0,
            "unmet_no_answer": 1 if unmet_no_answer else 0,
            "transportation_barrier": {
                "Yes, it has kept me from medical appointments or from getting my medications": 0,
                "Yes, it has kept me from non-medical meetings, appointments, work, or from getting things needed for daily living": 1,
                "No": 2,
                "I choose not to answer": 3
            }.get(transportation_barrier, 3),
            
            # 5. Social & Emotional Health (15-16)
            "social_contact": {
                "Daily": 4,
                "3 to 5 times per week": 3,
                "1 to 2 times per week": 2,
                "Less than once per week": 1,
                "I choose not to answer": -1
            }.get(social_contact, -1),
            "stress_level": {
                "Not at all": 0,
                "A little bit": 1,
                "Somewhat": 2,
                "Quite a bit": 3,
                "Very much": 4,
                "Extremely": 5,
                "I choose not to answer": 6
            }.get(stress_level, 6),
            
            # 6. Safety (17-19)
            "incarceration_history": 1 if incarceration_history == "Yes" else (0 if incarceration_history == "No" else -1),
            "feel_safe": {
                "Yes": 1,
                "No": 0,
                "Unsure": 2,
                "I choose not to answer": 3
            }.get(feel_safe, 3),
            "domestic_violence": 1 if domestic_violence == "Yes" else (0 if domestic_violence == "No" else -1),
            
            # 7. Food Security (20-22)
            "food_worry": {
                "Often true": 2,
                "Sometimes true": 1,
                "Never true": 0,
                "Don't know/refused": 3,
                "I choose not to answer": 4
            }.get(food_worry, 4),
            "food_didnt_last": {
                "Often true": 2,
                "Sometimes true": 1,
                "Never true": 0,
                "Don't know/refused": 3,
                "I choose not to answer": 4
            }.get(food_didnt_last, 4),
            "need_food_help": 1 if need_food_help == "Yes" else (0 if need_food_help == "No" else -1),
            
            # Metadata
            "assessed_by": "Gradio UI",
            "notes": "Submitted via Gradio interface"
        }
        
        try:
            # Send POST request to the backend
            response = requests.post(
                endpoint,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                # Update form data state with the submitted data
                form_data = {
                    "form_type": "prapare",
                    "data": data,
                    "timestamp": datetime.now().isoformat(),
                    "status": "submitted"
                }
                
                return "PRAPARE form submitted successfully!", form_data
            else:
                error_msg = f"Error submitting PRAPARE form: {response.status_code} - {response.text}"
                print(error_msg)
                return error_msg, None
                
        except Exception as e:
            error_msg = f"Exception submitting PRAPARE form: {str(e)}"
            print(error_msg)
            return error_msg, None
    
    submit_btn.click(
        submit_prapare,
        inputs=[patient_id_state] + form_inputs,
        outputs=[submit_result, form_data_state]
    )
    
    # Populate fields when patient changes
    patient_id_state.change(
        populate_fields,
        inputs=[patient_id_state, form_data_state],
        outputs=form_inputs
    )
    
    # Update patient ID display when state changes
    patient_id_state.change(
        lambda x: x,
        inputs=[patient_id_state],
        outputs=[patient_id_display]
    )
    
    # Insurance is handled by primary_insurance radio button
    
    # Convert radio button values to integers
    hispanic = 1 if ethnicity == "Yes" else (0 if ethnicity == "No" else -1)
    primary_lang = 1 if primary_language == "English" else (0 if primary_language == "Language other than English" else -1)
    housing = 1 if housing_situation == "I have housing" else (0 if housing_situation == "I do not have housing (staying with others, in a hotel, in a shelter, living outside on the street, on a beach, in a car, or in a park)" else -1)
    housing_worry_val = 1 if housing_worry == "Yes" else (0 if housing_worry == "No" else -1)
    transport_val = 1 if transportation_barrier == "Yes" else (0 if transportation_barrier == "No" else -1)
    
    # Map education level
    edu_map = {
        "Less than high school": 1,
        "High school diploma or GED": 2,
        "More than high school": 3
    }
    edu_level = edu_map.get(education_level, -1)
    
    # Map employment status
    emp_map = {
        "Unemployed": 0,
        "Part-time or temporary work": 1,
        "Full-time work": 2,
        "Otherwise unemployed but not seeking work (ex: student, retired, disabled, unpaid primary care giver)": 3
    }
    emp_status = emp_map.get(employment_status, -1)
    
    # Map social contact
    social_map = {
        "5 or more times a week": 4,
        "3 to 5 times a week": 3,
        "1 or 2 times a week": 2,
        "Less than once a week": 1
    }
    social_contact_val = social_map.get(social_contact, -1)
    
    # Map stress level
    stress_map = {
        "Not at all": 1,
        "A little bit": 2,
        "Somewhat": 3,
        "Quite a bit": 4,
        "Very much": 5
    }
    stress_lvl = stress_map.get(stress_level, -1)
    
    # Set default values for required fields that don't have UI components yet
    feel_safe = -1  # 1=Yes, 0=No, -1=No answer
    domestic_violence = -1  # 1=Yes, 0=No, -1=No answer
    
    # Unmet needs are handled by individual fields below
    
    return {
        # Basic Demographics
        "hispanic": hispanic,
        "race_asian": 1 if race_asian else 0,
        "race_native_hawaiian": 1 if race_native_hawaiian else 0,
        "race_pacific_islander": 1 if race_pacific_islander else 0,
        "race_black": 1 if race_black else 0,
        "race_white": 1 if race_white else 0,
        "race_american_indian": 1 if race_american_indian else 0,
        "race_other": 1 if race_other else 0,
        "race_no_answer": 1 if race_no_answer else 0,
        
        # Work/Service
        "farm_work": 1 if farm_work == "Yes" else (0 if farm_work == "No" else -1),
        "military_service": 1 if military_service == "Yes" else (0 if military_service == "No" else -1),
        
        # Social/Cultural
        "primary_language": primary_lang,
        
        # Housing
        "housing_situation": housing,
        "housing_worry": housing_worry_val,
        
        # Food Security
        "food_worry": {
            "Often true": 3,
            "Sometimes true": 2,
            "Never true": 1,
            "I choose not to answer": -1
        }.get(food_worry, -1),
        "food_didnt_last": {
            "Often true": 3,
            "Sometimes true": 2,
            "Never true": 1,
            "I choose not to answer": -1
        }.get(food_didnt_last, -1),
        
        # Transportation
        "transportation_barrier": transport_val,
        
        # Education and Employment
        "education_level": edu_level,
        "employment_status": emp_status,
        
        # Social Support
        "social_contact": social_contact_val,
        "stress_level": stress_lvl,
        
        # FHIR/PRAPARE specific
        # Unmet needs (all individual boolean fields)
        "feel_safe": feel_safe,  # 1=Yes, 0=No, -1=No answer
        "domestic_violence": domestic_violence,  # 1=Yes, 0=No, -1=No answer
        
        # Other fields
        "annual_pretax_income": None,
        "notes": None
    }
def map_int_to_radio(value, choices, default=None):
    """Map integer value to radio button choice"""
    if value is None or value == -1:
        return default or choices[-1]  # Default to last choice (usually 'I choose not to answer')
    if value == 1 and len(choices) > 0:
        return choices[0]  # First choice is usually 'Yes' or similar
    if value == 0 and len(choices) > 1:
        return choices[1]  # Second choice is usually 'No' or similar
    return default or choices[-1]  # Fallback to last choice

def map_education_level(level):
    """Map integer education level to string"""
    edu_map = {
        0: "Less than high school",
        1: "High school graduate/GED or equivalent",
        2: "Some college or technical school (no degree)",
        3: "I choose not to answer"
    }
    return edu_map.get(level, "I choose not to answer")

def map_employment_status(status):
    """Map integer employment status to string"""
    emp_map = {
        0: "Unemployed",
        1: "Employed part-time (less than 35 hours/week)",
        2: "Employed full-time (35+ hours/week)",
        3: "Retired, student, or homemaker",
        4: "I choose not to answer"
    }
    return emp_map.get(status, "I choose not to answer")

def populate_form_from_data(data):
    """Populate form fields from existing PRAPARE data"""
    try:
        # Map integer values back to form strings
        hispanic = "Yes" if data.get("hispanic") == 1 else ("No" if data.get("hispanic") == 0 else "I choose not to answer")
        
        # Race checkboxes (already boolean in data)
        race_asian = bool(data.get("race_asian", False))
        race_native_hawaiian = bool(data.get("race_native_hawaiian", False))
        race_pacific_islander = bool(data.get("race_pacific_islander", False))
        race_black = bool(data.get("race_black", False))
        race_white = bool(data.get("race_white", False))
        race_american_indian = bool(data.get("race_american_indian", False))
        race_other = bool(data.get("race_other", False))
        race_no_answer = bool(data.get("race_no_answer", False))
        
        # Farm work
        farm_work = "Yes" if data.get("farm_work") == 1 else ("No" if data.get("farm_work") == 0 else "I choose not to answer")
        
        # Military service
        military = "Yes" if data.get("military_service") == 1 else ("No" if data.get("military_service") == 0 else "I choose not to answer")
        
        # Primary language
        primary_lang = "English" if data.get("primary_language") == 1 else ("Language other than English" if data.get("primary_language") == 0 else "I choose not to answer")
        
        # Housing situation
        housing_map = {
            0: "I do not have housing (staying with others, in a hotel, in a shelter, living outside on the street, on a beach, in a car, or in a park)",
            1: "I am in temporary or emergency housing (including shelters, hotels, transitional housing, or treatment programs)",
            2: "I have stable housing (own or rent)",
            3: "I choose not to answer"
        }
        housing_situation = data.get("housing_situation")
        housing = housing_map.get(housing_situation, "I choose not to answer") if housing_situation is not None else "I choose not to answer"
        
        # Household size - ensure it's an integer
        try:
            household_size = int(data.get("household_size", 1))
        except (TypeError, ValueError):
            household_size = 1
            
        # Housing worry
        housing_worry_map = {
            0: "Not at all worried",
            1: "Slightly worried",
            2: "Worried",
            3: "I choose not to answer"
        }
        housing_worry = housing_worry_map.get(data.get("housing_worry", 3), "I choose not to answer")
        
        # Education level - ensure we handle None case
        education_level = data.get("education_level")
        if education_level is not None:
            education = map_education_level(education_level)
        else:
            education = "I choose not to answer"
            
        # Employment status - ensure we handle None case
        employment_status = data.get("employment_status")
        if employment_status is not None:
            employment = map_employment_status(employment_status)
        else:
            employment = "I choose not to answer"
        
        # Primary insurance
        insurance_map = {
            0: "No insurance of any type",
            1: "Medicaid",
            2: "Medicare",
            3: "CHIP (Children's Health Insurance Program)",
            4: "Private insurance (through employer or purchased)",
            5: "Veterans/military health care (including TRICARE)",
            6: "Other public insurance (not Medicare)",
            7: "I choose not to answer"
        }
        primary_insurance = insurance_map.get(data.get("primary_insurance", 7), "I choose not to answer")
        
        # Annual income
        income_map = {
            0: "Less than $10,000",
            1: "$10,000 to $24,999",
            2: "$25,000 to $49,999",
            3: "$50,000 to $74,999",
            4: "$75,000 or more",
            5: "I don't know",
            6: "I choose not to answer"
        }
        annual_income = income_map.get(data.get("annual_income", 6), "I choose not to answer")
        
        # Unmet needs (boolean fields)
        unmet_food = bool(data.get("unmet_food", False))
        unmet_clothing = bool(data.get("unmet_clothing", False))
        unmet_utilities = bool(data.get("unmet_utilities", False))
        unmet_childcare = bool(data.get("unmet_childcare", False))
        unmet_healthcare = bool(data.get("unmet_healthcare", False))
        unmet_phone = bool(data.get("unmet_phone", False))
        unmet_other = bool(data.get("unmet_other", False))
        unmet_no_answer = bool(data.get("unmet_no_answer", False))
        
        # Transportation barrier
        transport_map = {
            0: "No, I have not had transportation problems",
            1: "Yes, I've missed medical appointments",
            2: "Yes, I've missed non-medical appointments",
            3: "I am unable to respond"
        }
        transport = transport_map.get(data.get("transportation_barrier", 3), "I am unable to respond")
        
        # Social contact
        social_contact_map = {
            0: "Daily",
            1: "3 to 5 times per week",
            2: "1 to 2 times per week",
            3: "Less than once per week",
            4: "I choose not to answer"
        }
        social_contact = social_contact_map.get(data.get("social_contact", 4), "I choose not to answer")
        
        # Stress level
        stress_map = {
            0: "None",
            1: "A little",
            2: "Some",
            3: "A lot",
            4: "Extremely",
            5: "I don't know",
            6: "I choose not to answer"
        }
        stress_level = stress_map.get(data.get("stress_level", 6), "I choose not to answer")
        
        # Incarceration history
        incarceration_map = {
            1: "Yes",
            0: "No",
            2: "I choose not to answer"
        }
        incarceration_history = incarceration_map.get(data.get("incarceration_history", 2), "I choose not to answer")
        
        # Feel safe
        feel_safe_map = {
            1: "Never",
            2: "Sometimes",
            3: "Often",
            4: "I choose not to answer"
        }
        feel_safe = feel_safe_map.get(data.get("feel_safe", 4), "I choose not to answer")
        
        # Domestic violence
        domestic_violence_map = {
            1: "Yes",
            0: "No",
            2: "I choose not to answer"
        }
        domestic_violence = domestic_violence_map.get(data.get("domestic_violence", 2), "I choose not to answer")
        
        # Food security
        food_map = {
            0: "Never true",
            1: "Sometimes true",
            2: "Often true",
            3: "I don't know",
            4: "I choose not to answer"
        }
        food_worry = food_map.get(data.get("food_worry", 4), "I choose not to answer")
        food_didnt_last = food_map.get(data.get("food_didnt_last", 4), "I choose not to answer")
        
        # Need food help
        need_food_help_map = {
            1: "Yes",
            0: "No",
            2: "I choose not to answer"
        }
        need_food_help = need_food_help_map.get(data.get("need_food_help", 2), "I choose not to answer")
        
        # Notes
        notes = data.get("notes", "")
        
        # Return values in the exact order expected by the UI components (36 total form fields)
        return [
            hispanic,  # ethnicity
            race_american_indian,  # race_american_indian
            race_asian,  # race_asian
            race_black,  # race_black
            race_native_hawaiian,  # race_native_hawaiian
            race_pacific_islander,  # race_pacific_islander
            race_white,  # race_white
            race_other,  # race_other
            race_no_answer,  # race_no_answer
            farm_work,  # farm_work
            military,  # military_service
            primary_lang,  # primary_language
            housing,  # housing_situation
            household_size,  # household_size
            housing_worry,  # housing_worry
            education,  # education_level
            employment,  # employment_status
            primary_insurance,  # primary_insurance
            annual_income,  # annual_income
            unmet_food,  # unmet_food
            unmet_clothing,  # unmet_clothing
            unmet_utilities,  # unmet_utilities
            unmet_childcare,  # unmet_childcare
            unmet_healthcare,  # unmet_healthcare
            unmet_phone,  # unmet_phone
            unmet_other,  # unmet_other
            unmet_no_answer,  # unmet_no_answer
            transport,  # transportation_barrier
            social_contact,  # social_contact
            stress_level,  # stress_level
            incarceration_history,  # incarceration_history
            feel_safe,  # feel_safe
            domestic_violence,  # domestic_violence
            food_worry,  # food_worry
            food_didnt_last,  # food_didnt_last
            need_food_help  # need_food_help
        ]
    except Exception as e:
        print(f"Error populating form: {str(e)}")
        # Return a list of Nones with the correct length on error (36 form fields only)
        return [None] * 36
