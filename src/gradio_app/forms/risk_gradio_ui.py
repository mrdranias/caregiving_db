import gradio as gr
import requests
import os

def risk_ui(patient_id_state, form_data_state):
    """Static Risk Management UI - 20 predefined risk rows"""
    return build_risk_ui(patient_id_state, form_data_state)

def build_risk_ui(patient_id_state, form_data_state):
    with gr.Group():
        gr.Markdown("## Risk Management")
        gr.Markdown("Rate the severity and likelihood for each hazard. Risk Score = Severity × Likelihood")
        
        # Add helpful descriptions
        with gr.Accordion("📋 Rating Guide", open=False):
            gr.Markdown("""
            **Severity Scale (0-5):**
            • 0 = None • 1 = Minimal • 2 = Mild • 3 = Moderate • 4 = Severe • 5 = Complete
            
            **Likelihood Scale (0-6):**
            • 0 = Not at all • 1 = Monthly • 2 = Weekly • 3 = Daily • 4 = Hourly • 5 = Constant
            
            **Risk Score:** Higher scores indicate greater need for intervention
            """)
        
        # Auto-generate button
        auto_btn = gr.Button("Auto-Generate Risks", variant="primary")
        
        # Status message
        status = gr.Markdown("", visible=False)
        
        # Create 20 static risk input rows
        risk_inputs = []
        for i in range(20):
            with gr.Row():
                # Hidden risk_id field
                risk_id = gr.Textbox(visible=False)
                
                # Hazard description (wider, more informative)
                hazard = gr.Textbox(
                    label=f"Hazard {i+1}", 
                    interactive=False,
                    scale=3
                )
                
                # Severity input
                severity = gr.Number(
                    label="Severity (0-5)", 
                    value=1, 
                    minimum=0, 

                    step=1,
                    scale=1,
                    info="0=None, 3=Severe, 5=Deadly"
                )
                
                # Likelihood input
                likelihood = gr.Number(
                    label="Likelihood (0-6)", 
                    value=1, 
                    minimum=0, 
                    scale=1,
                    info="0=Not at all, 3=Daily, 5=Constant"
                )
                
                # Risk score (auto-calculated)
                risk_score = gr.Number(
                    label="Risk Score", 
                    interactive=False,
                    scale=1,
                    info="Severity × Likelihood"
                )
                
                # Notes field (compact)
                notes = gr.Textbox(
                    label="Notes", 
                    placeholder="Optional notes...",
                    max_lines=1,
                    scale=2
                )
            
            # Store references to all components for this row
            risk_inputs.append({
                'risk_id': risk_id,
                'hazard': hazard,
                'severity': severity,
                'likelihood': likelihood,
                'risk_score': risk_score,
                'notes': notes
            })
            
            # Auto-calculate risk score when severity or likelihood changes
            def make_calculator(sev_input, lik_input, score_output):
                def calculate(sev, lik):
                    if sev is not None and lik is not None:
                        return sev * lik
                    return None
                
                sev_input.change(calculate, [sev_input, lik_input], [score_output])
                lik_input.change(calculate, [sev_input, lik_input], [score_output])
            
            make_calculator(severity, likelihood, risk_score)
        
        # Save button
        save_btn = gr.Button("Save All Ratings", variant="secondary")
        
        def populate_risks(patient_id):
            """Fetch patient hazards and populate the static rows with any existing risk ratings"""
            if not patient_id:
                risk_ids = [""] * 20
                hazards = [""] * 20
                severities = [None] * 20
                likelihoods = [None] * 20
                risk_scores = [None] * 20
                notes_list = [""] * 20
                status = "No patient selected"
                return (*risk_ids, *hazards, *severities, *likelihoods, *risk_scores, *notes_list, status)
            
            api_url = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
            try:
                # First, get all patient hazards
                hazards_resp = requests.get(f"{api_url}/hazards/by_patient/{patient_id}")
                if not hazards_resp.ok:
                    risk_ids = [""] * 20
                    hazards = [""] * 20
                    severities = [None] * 20
                    likelihoods = [None] * 20
                    risk_scores = [None] * 20
                    notes_list = [""] * 20
                    status = f"❌ Error loading hazards: {hazards_resp.status_code}"
                    return (*risk_ids, *hazards, *severities, *likelihoods, *risk_scores, *notes_list, status)
                
                patient_hazards = hazards_resp.json().get("hazards", [])
                
                # Then, get any existing risk ratings
                risks_resp = requests.get(f"{api_url}/risk/by_patient/{patient_id}")
                existing_risks = {}
                if risks_resp.ok:
                    try:
                        risk_data = risks_resp.json()
                        # Handle different possible response structures
                        if isinstance(risk_data, dict) and "risks" in risk_data:
                            risks_list = risk_data["risks"]
                        elif isinstance(risk_data, list):
                            risks_list = risk_data
                        else:
                            risks_list = []
                        
                        for risk in risks_list:
                            if isinstance(risk, dict) and "hazard_code" in risk:
                                existing_risks[risk["hazard_code"]] = risk
                    except (ValueError, KeyError, TypeError) as e:
                        print(f"Error parsing risk data: {e}")
                        # Continue with empty existing_risks
                
                # Prepare display data
                risk_ids = [""] * 20
                hazards = [""] * 20
                severities = [None] * 20
                likelihoods = [None] * 20
                risk_scores = [None] * 20
                notes_list = [""] * 20
                
                # Store hazard codes globally for save operations
                global current_hazard_codes
                current_hazard_codes = [""] * 20
                
                # Fill in hazard information and any existing ratings
                for i, hazard in enumerate(patient_hazards[:20]):
                    # Extract hazard code - use subclass_id first, then class_id as fallback
                    hazard_code = hazard.get("hazard_subclass_id") or hazard.get("hazard_class_id", "")
                    
                    # Extract hazard description - use item first, then code as fallback, then type
                    hazard_desc = hazard.get("item") or hazard.get("code") or hazard.get("type", "Unknown")
                    
                    # Create concise hazard display (max ~60 chars)
                    if len(hazard_desc) > 50:
                        display_text = f"{hazard_code}: {hazard_desc[:45]}..."
                    else:
                        display_text = f"{hazard_code}: {hazard_desc}"
                    
                    hazards[i] = display_text
                    current_hazard_codes[i] = hazard_code
                    
                    # Pre-fill existing risk data if available
                    if hazard_code in existing_risks:
                        risk = existing_risks[hazard_code]
                        risk_ids[i] = risk.get("risk_id", "")
                        severities[i] = risk.get("severity")
                        likelihoods[i] = risk.get("likelihood") 
                        if severities[i] and likelihoods[i]:
                            risk_scores[i] = round(severities[i] * likelihoods[i], 1)
                        notes_list[i] = risk.get("notes", "")
                
                status = f"✅ Loaded {len(patient_hazards)} hazards for assessment"
                return (*risk_ids, *hazards, *severities, *likelihoods, *risk_scores, *notes_list, status)
                
            except Exception as e:
                risk_ids = [""] * 20
                hazards = [""] * 20
                severities = [None] * 20
                likelihoods = [None] * 20
                risk_scores = [None] * 20
                notes_list = [""] * 20
                status = f"❌ Error: {str(e)}"
                return (*risk_ids, *hazards, *severities, *likelihoods, *risk_scores, *notes_list, status)
        
        def auto_generate_risks(patient_id):
            """Auto-generate risks and refresh display"""
            if not patient_id:
                risk_ids = [""] * 20
                hazards = [""] * 20
                severities = [None] * 20
                likelihoods = [None] * 20
                risk_scores = [None] * 20
                notes_list = [""] * 20
                status = "No patient selected"
                return (*risk_ids, *hazards, *severities, *likelihoods, *risk_scores, *notes_list, status)
            
            api_url = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
            try:
                resp = requests.post(f"{api_url}/risk/auto_generate/{patient_id}")
                if resp.ok:
                    # Fetch the newly generated risks
                    return populate_risks(patient_id)
                else:
                    risk_ids = [""] * 20
                    hazards = [""] * 20
                    severities = [None] * 20
                    likelihoods = [None] * 20
                    risk_scores = [None] * 20
                    notes_list = [""] * 20
                    status = f"Error: {resp.status_code}"
                    return (*risk_ids, *hazards, *severities, *likelihoods, *risk_scores, *notes_list, status)
            except Exception as e:
                risk_ids = [""] * 20
                hazards = [""] * 20
                severities = [None] * 20
                likelihoods = [None] * 20
                risk_scores = [None] * 20
                notes_list = [""] * 20
                status = f"Exception: {e}"
                return (*risk_ids, *hazards, *severities, *likelihoods, *risk_scores, *notes_list, status)
        
        def save_all_ratings(patient_id, *all_inputs):
            """Save all non-empty risk ratings"""
            if not patient_id:
                return "No patient selected"
            
            # Parse inputs: risk_ids, hazards, severities, likelihoods, risk_scores, notes
            risk_ids = all_inputs[0:20]
            hazards = all_inputs[20:40]
            severities = all_inputs[40:60]
            likelihoods = all_inputs[60:80]
            risk_scores = all_inputs[80:100]
            notes_list = all_inputs[100:120]
            
            api_url = os.getenv("API_URL", "http://localhost:8000").rstrip("/")
            saved_count = 0
            
            for i in range(20):
                risk_id = risk_ids[i]
                severity = severities[i]
                likelihood = likelihoods[i]
                risk_score = risk_scores[i]
                notes = notes_list[i]
                
                # Skip empty rows (only if no risk_id AND no ratings entered)
                if not risk_id and (severity is None and likelihood is None):
                    continue
                
                # Debug logging
                print(f"Processing row {i}: risk_id={risk_id}, severity={severity}, likelihood={likelihood}, hazard_code={current_hazard_codes[i] if i < len(current_hazard_codes) else 'N/A'}")
                
                try:
                    payload = {
                        "severity": float(severity) if severity is not None else None,
                        "likelihood": float(likelihood) if likelihood is not None else None,
                        "risk_score": float(risk_score) if risk_score is not None else None,
                        "notes": str(notes) if notes else ""
                    }
                    
                    if risk_id:
                        print(f"Updating existing risk {risk_id}")
                        resp = requests.post(f"{api_url}/risk/update/{risk_id}", json=payload)
                        
                        if resp.ok:
                            saved_count += 1
                            print(f"Successfully saved risk {risk_id}")
                        else:
                            print(f"Failed to save risk {risk_id}: {resp.status_code} - {resp.text}")
                    else:
                        # No risk_id means auto-generate wasn't run first
                        print(f"Skipping row {i}: No risk_id available. Please run Auto-Generate Risks first.")
                        continue
                except Exception as e:
                    print(f"Error saving risk {risk_id}: {e}")
            
            return f"Saved {saved_count} risks to database"
        
        # Collect all inputs for the save function
        all_risk_ids = [row['risk_id'] for row in risk_inputs]
        all_hazards = [row['hazard'] for row in risk_inputs]
        all_severities = [row['severity'] for row in risk_inputs]
        all_likelihoods = [row['likelihood'] for row in risk_inputs]
        all_risk_scores = [row['risk_score'] for row in risk_inputs]
        all_notes = [row['notes'] for row in risk_inputs]
        
        # Auto-generate button
        auto_btn.click(
            auto_generate_risks,
            inputs=[patient_id_state],
            outputs=all_risk_ids + all_hazards + all_severities + all_likelihoods + all_risk_scores + all_notes + [status]
        ).then(
            lambda msg: gr.update(visible=True),
            inputs=[status],
            outputs=[status]
        )
        
        # Save button
        save_btn.click(
            save_all_ratings,
            inputs=[patient_id_state] + all_risk_ids + all_hazards + all_severities + all_likelihoods + all_risk_scores + all_notes,
            outputs=[status]
        ).then(
            lambda msg: gr.update(visible=True),
            inputs=[status],
            outputs=[status]
        )
        
        # Auto-refresh when patient changes
        patient_id_state.change(
            populate_risks,
            inputs=[patient_id_state],
            outputs=all_risk_ids + all_hazards + all_severities + all_likelihoods + all_risk_scores + all_notes + [status]
        ).then(
            lambda msg: gr.update(visible=True),
            inputs=[status],
            outputs=[status]
        )
