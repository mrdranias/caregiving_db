import gradio as gr
import requests
import os

def social_risk_ui(patient_id_state, form_data_state):
    """Social Risk Management UI - 20 predefined social risk rows"""
    return build_social_risk_ui(patient_id_state, form_data_state)

def build_social_risk_ui(patient_id_state, form_data_state):
    with gr.Group():
        gr.Markdown("## Social Risk Management")
        gr.Markdown("Rate the severity and likelihood for each social hazard identified from PRAPARE assessment. Risk Score = Severity × Likelihood")
        
        # Add helpful descriptions
        with gr.Accordion("📋 Social Risk Rating Guide", open=False):
            gr.Markdown("""
            **Severity Scale (0-5):**
            • 0 = None • 1 = Minimal • 2 = Mild • 3 = Moderate • 4 = Severe • 5 = Critical
            
            **Likelihood Scale (0-6):**
            • 0 = Never • 1 = Rarely • 2 = Sometimes • 3 = Often • 4 = Very Often • 5 = Always
            
            **Social Risk Types:**
            • Housing, Transportation, Food Security, Financial Strain, Social Isolation, Health Access, Safety
            
            **Risk Score:** Higher scores indicate greater need for social intervention
            """)
        
        # Auto-generate button
        auto_btn = gr.Button("Auto-Generate Social Risks", variant="primary")
        
        # Status message
        status = gr.Markdown("", visible=False)
        
        # Create 20 static social risk input rows
        social_risk_inputs = []
        for i in range(20):
            with gr.Row():
                # Hidden social_risk_id field
                social_risk_id = gr.Textbox(visible=False)
                
                # Social hazard description (wider, more informative)
                social_hazard = gr.Textbox(
                    label=f"Social Hazard {i+1}", 
                    interactive=False,
                    scale=3
                )
                
                # Severity input
                severity = gr.Number(
                    label="Severity (0-5)", 
                    value=1, 
                    minimum=0, 

                    scale=1
                )
                
                # Likelihood input
                likelihood = gr.Number(
                    label="Likelihood (0-6)", 
                    value=1, 
                    minimum=0, 
                    scale=1
                )
                
                # Risk score (computed)
                risk_score = gr.Number(
                    label="Risk Score", 
                    interactive=False,
                    scale=1
                )
                
                # Notes field
                notes = gr.Textbox(
                    label="Notes", 
                    placeholder="Expert notes...",
                    scale=2
                )
            
            social_risk_inputs.append([social_risk_id, social_hazard, severity, likelihood, risk_score, notes])
        
        # Save button
        save_btn = gr.Button("Save All Social Risks", variant="secondary")
        
        def auto_generate_social_risks(patient_id):
            """Auto-generate social risks from PRAPARE assessment"""
            try:
                if not patient_id:
                    empty_values = []
                    for row in social_risk_inputs:
                        empty_values.extend(["", "", None, None, None, ""])
                    return "❌ No patient selected", {}, *empty_values
                
                api_url = os.getenv("API_URL", "http://localhost:8000")
                resp = requests.post(f"{api_url}/social_risk/auto_generate/{patient_id}")
                
                if resp.ok:
                    result = resp.json()
                    status_msg = f"✅ Generated {result['created']} new social risks, updated {result['updated']} existing ones from {result['total_hazards']} social hazards"
                    
                    # Fetch updated social risks
                    resp2 = requests.get(f"{api_url}/social_risk/by_patient/{patient_id}")
                    if resp2.ok:
                        risks_data = resp2.json()
                        social_risks = risks_data.get("social_risks", [])
                        
                        # Populate the form fields
                        outputs = []
                        for i in range(20):
                            if i < len(social_risks):
                                risk = social_risks[i]
                                # Truncate description to 50 characters to prevent UI overflow
                                description = risk.get('social_hazard_description', '')
                                truncated_desc = description[:47] + '...' if len(description) > 50 else description
                                hazard_display = f"{risk['social_hazard_label']} - {truncated_desc}"
                                
                                outputs.extend([
                                    risk["social_risk_id"],
                                    hazard_display,
                                    risk.get("severity"),
                                    risk.get("likelihood"),
                                    risk.get("risk_score"),
                                    risk.get("notes", "")
                                ])
                            else:
                                outputs.extend(["", "", None, None, None, ""])
                        
                        return (status_msg, {"social_risks": social_risks}) + tuple(outputs)
                    else:
                        empty_values = []
                        for row in social_risk_inputs:
                            empty_values.extend(["", "", None, None, None, ""])
                        return f"⚠️ Generated risks but failed to fetch: {resp2.text}", {}, *empty_values
                else:
                    empty_values = []
                    for row in social_risk_inputs:
                        empty_values.extend(["", "", None, None, None, ""])
                    return f"❌ Error: {resp.text}", {}, *empty_values
            except Exception as e:
                empty_values = []
                for row in social_risk_inputs:
                    empty_values.extend(["", "", None, None, None, ""])
                return f"❌ Error: {str(e)}", {}, *empty_values
        
        def save_all_social_risks(patient_id, *args):
            """Save all social risk ratings"""
            try:
                if not patient_id:
                    return "❌ No patient selected", {}
                
                api_url = os.getenv("API_URL", "http://localhost:8000")
                saved_count = 0
                
                # Process each row (6 fields per row)
                for i in range(0, len(args), 6):
                    social_risk_id = args[i]
                    social_hazard = args[i+1]
                    severity = args[i+2]
                    likelihood = args[i+3]
                    risk_score = args[i+4]
                    notes = args[i+5]
                    
                    # Skip empty rows
                    if not social_risk_id or not social_hazard:
                        continue
                    
                    # Calculate risk score if both severity and likelihood are provided
                    if severity is not None and likelihood is not None:
                        computed_risk_score = severity * likelihood
                    else:
                        computed_risk_score = risk_score
                    
                    # Update the social risk
                    update_data = {
                        "severity": severity,
                        "likelihood": likelihood,
                        "risk_score": computed_risk_score,
                        "notes": notes or ""
                    }
                    
                    resp = requests.post(f"{api_url}/social_risk/update/{social_risk_id}", json=update_data)
                    if resp.ok:
                        saved_count += 1
                    else:
                        print(f"Failed to save social risk {social_risk_id}: {resp.text}")
                
                return f"✅ Saved {saved_count} social risk assessments", {"social_risks_saved": saved_count}
            except Exception as e:
                return f"❌ Error saving: {str(e)}", {}
        
        def compute_risk_score(severity, likelihood):
            """Automatically compute risk score when severity or likelihood changes"""
            if severity is not None and likelihood is not None:
                return severity * likelihood
            return None
        
        def populate_social_risk_fields(patient_id, form_data):
            """Populate social risk fields from existing data"""
            try:
                if not patient_id:
                    empty_values = []
                    for row in social_risk_inputs:
                        empty_values.extend(["", "", None, None, None, ""])
                    return tuple(empty_values)
                
                api_url = os.getenv("API_URL", "http://localhost:8000")
                resp = requests.get(f"{api_url}/social_risk/by_patient/{patient_id}")
                
                if resp.ok:
                    risks_data = resp.json()
                    social_risks = risks_data.get("social_risks", [])
                    
                    outputs = []
                    for i in range(20):
                        if i < len(social_risks):
                            risk = social_risks[i]
                            outputs.extend([
                                risk["social_risk_id"],
                                f"{risk['social_hazard_label']} - {risk.get('social_hazard_description', '')}",
                                risk.get("severity"),
                                risk.get("likelihood"),
                                risk.get("risk_score"),
                                risk.get("notes", "")
                            ])
                        else:
                            outputs.extend(["", "", None, None, None, ""])
                    
                    return tuple(outputs)
                else:
                    empty_values = []
                    for row in social_risk_inputs:
                        empty_values.extend(["", "", None, None, None, ""])
                    return tuple(empty_values)
            except Exception:
                empty_values = []
                for row in social_risk_inputs:
                    empty_values.extend(["", "", None, None, None, ""])
                return tuple(empty_values)
        
        # Auto-compute risk scores when severity or likelihood changes
        for i, (social_risk_id, social_hazard, severity, likelihood, risk_score, notes) in enumerate(social_risk_inputs):
            def make_compute_fn(risk_score_field):
                def compute_fn(sev, like):
                    return compute_risk_score(sev, like)
                return compute_fn
            
            severity.change(
                make_compute_fn(risk_score),
                inputs=[severity, likelihood],
                outputs=[risk_score]
            )
            likelihood.change(
                make_compute_fn(risk_score),
                inputs=[severity, likelihood],
                outputs=[risk_score]
            )
        
        # Event handlers
        auto_btn.click(
            auto_generate_social_risks,
            inputs=[patient_id_state],
            outputs=[status] + [form_data_state] + [item for row in social_risk_inputs for item in row]
        )
        
        save_btn.click(
            save_all_social_risks,
            inputs=[patient_id_state] + [item for row in social_risk_inputs for item in row],
            outputs=[status, form_data_state]
        )
        
        # Populate fields when patient changes
        patient_id_state.change(
            populate_social_risk_fields,
            inputs=[patient_id_state, form_data_state],
            outputs=[item for row in social_risk_inputs for item in row]
        )
        
        form_data_state.change(
            populate_social_risk_fields,
            inputs=[patient_id_state, form_data_state],
            outputs=[item for row in social_risk_inputs for item in row]
        )
        
        # Show status when it's updated
        status.change(
            lambda msg: gr.update(visible=bool(msg)),
            inputs=[status],
            outputs=[status]
        )
