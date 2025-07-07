import gradio as gr
import requests
import json
from typing import List, Dict, Any, Optional

def create_recommendations_ui(patient_id_state: gr.State):
    """Create Service Recommendations UI with risk dashboard and hazard-to-service mapping"""
    
    with gr.Column():
        gr.Markdown("## 🎯 Service Recommendations & Care Plan")
        gr.Markdown("Comprehensive risk assessment and personalized service recommendations")
        
        # Risk Dashboard Section
        with gr.Accordion("📊 Risk Summary Dashboard", open=True):
            with gr.Row():
                # Risk Score Cards
                with gr.Column(scale=1):
                    clinical_risk_display = gr.Number(
                        label="Clinical Risk", 
                        value=0, 
                        interactive=False,
                        info="ADL/IADL functional risks"
                    )
                
                with gr.Column(scale=1):
                    social_risk_display = gr.Number(
                        label="Social Risk", 
                        value=0, 
                        interactive=False,
                        info="PRAPARE social determinants"
                    )
                
                with gr.Column(scale=1):
                    composite_risk_display = gr.Number(
                        label="Composite Risk", 
                        value=0, 
                        interactive=False,
                        info="Combined risk score"
                    )
                
                with gr.Column(scale=1):
                    urgency_display = gr.Textbox(
                        label="Urgency Level",
                        value="Low",
                        interactive=False,
                        info="Priority for intervention"
                    )
            
            with gr.Row():
                risk_amplification = gr.Number(
                    label="Risk Amplification Factor",
                    value=1.0,
                    interactive=False,
                    info="How social factors compound clinical risks"
                )
                
                total_hazards = gr.Number(
                    label="Total Active Hazards",
                    value=0,
                    interactive=False,
                    info="Clinical + social hazards identified"
                )
        
        # Control Buttons
        with gr.Row():
            refresh_dashboard_btn = gr.Button("🔄 Refresh Risk Dashboard", variant="secondary")
            load_btn = gr.Button("⚡ Load Service Recommendations", variant="primary")
        
        # Status message
        status_msg = gr.Markdown("", visible=False)
        
        # Clinical Risk Recommendations Section
        gr.Markdown("## 🏥 Clinical Risk Recommendations")
        clinical_rows = []
        for i in range(25):  # 25 clinical recommendations
            with gr.Row(visible=False) as row:
                # Hazard info (readonly)
                hazard_text = gr.Textbox(
                    label=f"Clinical Hazard {i+1}",
                    interactive=False,
                    scale=2
                )
                
                # Risk score (readonly)
                risk_score = gr.Number(
                    label="Risk Score",
                    interactive=False,
                    scale=1
                )
                
                # Service info (readonly)
                service_text = gr.Textbox(
                    label="Recommended Service",
                    interactive=False,
                    scale=2
                )
                
                # Parent service class (readonly)
                parent_class = gr.Textbox(
                    label="Service Category",
                    interactive=False,
                    scale=1
                )
                
                # Frequency (editable)
                frequency = gr.Textbox(
                    label="Frequency",
                    value="1",
                    placeholder="e.g., 2x weekly",
                    scale=1
                )
                
                # Cost estimate (editable)
                cost = gr.Number(
                    label="Cost ($)",
                    placeholder="Est. cost",
                    scale=1
                )
                
                # Contractor selection (editable)
                contractor = gr.Dropdown(
                    label="Contractor",
                    choices=[],  # Will be populated with contractors
                    scale=2
                )
                
                # Include in report checkbox (editable)
                selected = gr.Checkbox(
                    label="Include in Report",
                    value=True,  # Default to selected
                    scale=1
                )
                
                clinical_rows.append([
                    row, hazard_text, risk_score, service_text,
                    parent_class, frequency, cost, contractor, selected
                ])
        
        # Social Risk Recommendations Section  
        gr.Markdown("## 🏘️ Social Risk Recommendations (SDOH)")
        social_rows = []
        for i in range(25):  # 25 social recommendations
            with gr.Row(visible=False) as row:
                # Hazard info (readonly)
                hazard_text = gr.Textbox(
                    label=f"Social Hazard {i+1}",
                    interactive=False,
                    scale=2
                )
                
                # Risk score (readonly)
                risk_score = gr.Number(
                    label="Risk Score",
                    interactive=False,
                    scale=1
                )
                
                # Service info (readonly)
                service_text = gr.Textbox(
                    label="Recommended Service",
                    interactive=False,
                    scale=2
                )
                
                # Parent service class (readonly)
                parent_class = gr.Textbox(
                    label="Service Category",
                    interactive=False,
                    scale=1
                )
                
                # Frequency (editable)
                frequency = gr.Textbox(
                    label="Frequency",
                    value="1",
                    placeholder="e.g., weekly",
                    scale=1
                )
                
                # Cost estimate (editable)
                cost = gr.Number(
                    label="Cost ($)",
                    placeholder="Est. cost",
                    scale=1
                )
                
                # Community resource selection (editable)
                community_resource = gr.Dropdown(
                    label="Community Resource",
                    choices=[],  # Will be populated with community_resources
                    scale=2
                )
                
                # Include in report checkbox (editable)
                selected = gr.Checkbox(
                    label="Include in Report",
                    value=True,  # Default to selected
                    scale=1
                )
                
                social_rows.append([
                    row, hazard_text, risk_score, service_text,
                    parent_class, frequency, cost, community_resource, selected
                ])
        
        # Combine all rows for compatibility
        recommendation_rows = clinical_rows + social_rows
        
        # Save button
        save_btn = gr.Button("Save All Recommendations", variant="secondary")
        
        # Generate report button and download link
        with gr.Row():
            report_btn = gr.Button("Generate Report", variant="secondary")
            # Download link removed due to Docker container file path issues

    # Functions
    def refresh_dashboard(patient_id):
        """Refresh risk dashboard with real data from backend"""
        if not patient_id:
            return (
                gr.update(value=0),
                gr.update(value=0),
                gr.update(value=0),
                gr.update(value="Low"),
                gr.update(value=1.0),
                gr.update(value=0),
                gr.update(value="Please select a patient first", visible=True)
            )
        
        api_url = "http://care_fastapi:8000"
        clinical_risk = 0
        clinical_hazards = 0
        
        try:
            # Fetch clinical risks
            resp = requests.get(f"{api_url}/risk/by_patient/{patient_id}")
            if resp.ok:
                clinical_data = resp.json()
                print(f"DEBUG: Clinical risks response: {clinical_data}")
                
                # Handle list of clinical risks
                if isinstance(clinical_data, list):
                    clinical_risks = [r for r in clinical_data if r.get('risk_score', 0) > 0]
                    if clinical_risks:
                        clinical_risk = sum(r.get('risk_score', 0) for r in clinical_risks) / len(clinical_risks)
                        clinical_hazards = len(clinical_risks)
                    else:
                        clinical_risk = 0
                        clinical_hazards = len(clinical_data)
                # Handle object with risks array
                else:
                    clinical_risks = clinical_data.get('risks', [])
                    if clinical_risks:
                        clinical_risk = sum(r.get('risk_score', 0) for r in clinical_risks) / len(clinical_risks) if clinical_risks else 0
                    clinical_hazards = len(clinical_risks)
                print(f"DEBUG: Calculated clinical_risk={clinical_risk}, hazards={clinical_hazards}")
            elif resp.status_code == 404:
                # No clinical risks found - try auto-generation
                print(f"DEBUG: No clinical risks found, attempting auto-generation...")
                gen_resp = requests.post(f"{api_url}/risk/auto_generate/{patient_id}")
                if gen_resp.ok:
                    print(f"DEBUG: Auto-generated clinical risks successfully")
                    # Retry fetching after generation
                    resp = requests.get(f"{api_url}/risk/by_patient/{patient_id}")
                    if resp.ok:
                        clinical_data = resp.json()
                        if isinstance(clinical_data, list):
                            clinical_risks = [r for r in clinical_data if r.get('risk_score', 0) > 0]
                            if clinical_risks:
                                clinical_risk = sum(r.get('risk_score', 0) for r in clinical_risks) / len(clinical_risks)
                            clinical_hazards = len(clinical_data)
        except Exception as e:
            print(f"DEBUG: Clinical risk fetch error: {e}")
            
        # Fetch social risks (PRAPARE)
        social_risk = 0
        social_hazards = 0
        try:
            resp = requests.get(f"{api_url}/social_risk/by_patient/{patient_id}")
            if resp.ok:
                social_data = resp.json()
                print(f"DEBUG: Social risks response: {social_data}")
                
                # Handle API response format: {"social_risks": [...], "total": count}
                if isinstance(social_data, dict) and 'social_risks' in social_data:
                    social_risks_list = social_data.get('social_risks', [])
                    social_risks = [r for r in social_risks_list if r.get('risk_score', 0) > 0]
                    if social_risks:
                        social_risk = sum(r.get('risk_score', 0) for r in social_risks) / len(social_risks)
                        social_hazards = len(social_risks)
                    else:
                        social_risk = 0
                        social_hazards = len(social_risks_list)
                # Handle legacy list format
                elif isinstance(social_data, list):
                    social_risks = [r for r in social_data if r.get('risk_score', 0) > 0]
                    if social_risks:
                        social_risk = sum(r.get('risk_score', 0) for r in social_risks) / len(social_risks)
                        social_hazards = len(social_risks)
                # Handle object with composite score
                else:
                    social_risk = social_data.get('composite_score', 0)
                    social_hazards = len(social_data.get('hazards', []))
                
                print(f"DEBUG: Calculated social_risk={social_risk}, hazards={social_hazards}")
            elif resp.status_code == 404:
                # No social risks found - try auto-generation
                print(f"DEBUG: No social risks found, attempting auto-generation...")
                gen_resp = requests.post(f"{api_url}/social_risk/auto_generate/{patient_id}")
                if gen_resp.ok:
                    print(f"DEBUG: Auto-generated social risks successfully")
                    # Retry fetching after generation
                    resp = requests.get(f"{api_url}/social_risk/by_patient/{patient_id}")
                    if resp.ok:
                        social_data = resp.json()
                        if isinstance(social_data, dict) and 'social_risks' in social_data:
                            social_risks_list = social_data.get('social_risks', [])
                            social_risks = [r for r in social_risks_list if r.get('risk_score', 0) > 0]
                            if social_risks:
                                social_risk = sum(r.get('risk_score', 0) for r in social_risks) / len(social_risks)
                            social_hazards = len(social_risks_list)
                        elif isinstance(social_data, list):
                            social_risks = [r for r in social_data if r.get('risk_score', 0) > 0]
                            if social_risks:
                                social_risk = sum(r.get('risk_score', 0) for r in social_risks) / len(social_risks)
                            social_hazards = len(social_data)
        except Exception as e:
            print(f"DEBUG: Social risk fetch error: {e}")
        
        # Calculate composite risk and urgency
        total_hazards_count = clinical_hazards + social_hazards
        
        # Risk amplification: social factors compound clinical risks
        amplification_factor = 1.0 + (social_risk / 100)  # 1.0 to 2.0 range
        composite_risk = (clinical_risk * amplification_factor + social_risk) / 2
        
        # Determine urgency level
        if composite_risk >= 80:
            urgency = "Critical"
        elif composite_risk >= 60:
            urgency = "High"
        elif composite_risk >= 40:
            urgency = "Moderate"
        else:
            urgency = "Low"
        
        return (
            gr.update(value=round(clinical_risk, 1)),
            gr.update(value=round(social_risk, 1)),
            gr.update(value=round(composite_risk, 1)),
            gr.update(value=urgency),
            gr.update(value=round(amplification_factor, 2)),
            gr.update(value=total_hazards_count),
            gr.update(value=f"✅ Risk dashboard updated - {total_hazards_count} hazards identified", visible=True)
        )
    
    def load_recommendations(patient_id):
        """Load recommendations from backend and populate static rows"""
        if not patient_id:
            # Return 450 hidden components (50 rows × 9 components) + 1 status message
            return [gr.update(visible=False)] * 450 + [gr.update(value="Please select a patient first", visible=True)]
        
        try:
            # Load contractors for clinical risks
            contractors_response = requests.get("http://care_fastapi:8000/contractors")
            contractors = []
            if contractors_response.status_code == 200:
                contractor_data = contractors_response.json()
                contractors = [c["name"] for c in contractor_data.get("contractors", [])]
            
            # Load community resources for social risks
            community_response = requests.get("http://care_fastapi:8000/community_resources")
            community_resources = []
            if community_response.status_code == 200:
                community_data = community_response.json()
                community_resources = [r["name"] for r in community_data.get("resources", [])]
            
            # Load recommendations
            response = requests.get(f"http://care_fastapi:8000/recommendations/by_patient/{patient_id}")
            
            if response.status_code != 200:
                return [gr.update(visible=False)] * 450 + [gr.update(value=f"Error loading recommendations: {response.text}", visible=True)]
            
            data = response.json()
            service_categories = data.get("service_categories", [])
            
            # Separate clinical and social services
            clinical_services = []
            social_services = []
            
            for category in service_categories:
                for service in category.get("services", []):
                    for hazard in service.get("linked_hazards", []):
                        # Determine hazard type with better detection logic
                        hazard_type = hazard.get("hazard_type", hazard.get("type", ""))
                        
                        # Enhanced type detection for social hazards
                        if not hazard_type:
                            # Check hazard code patterns for social indicators
                            hazard_code = hazard.get('hazard_code', '')
                            if any(social_indicator in hazard_code.lower() for social_indicator in 
                                   ['social', 'housing', 'food', 'transport', 'employment', 'education', 'community']):
                                hazard_type = "social"
                            else:
                                hazard_type = "clinical"
                        
                        service_item = {
                            "hazard": f"{hazard.get('hazard_code', '')} - {hazard.get('hazard_item', '')}".strip(' -'),
                            "risk_score": hazard.get("risk_score", 0),
                            "service": service.get("service_subclass_label", ""),
                            "parent_class": category.get("service_class_label", ""),
                            "priority": service.get("priority", ""),
                            "hazard_type": hazard_type
                        }
                        
                        print(f"DEBUG: Hazard {hazard.get('hazard_code', '')} classified as: {hazard_type}")
                        
                        # Segregate by hazard type
                        if hazard_type == "social":
                            social_services.append(service_item)
                        else:
                            clinical_services.append(service_item)
            
            # Update UI components
            updates = []
            
            # Update clinical risk rows (first 25 rows)
            for i in range(25):
                if i < len(clinical_services):
                    service = clinical_services[i]
                    updates.extend([
                        gr.update(visible=True),  # row
                        gr.update(value=service["hazard"]),  # hazard_text
                        gr.update(value=service["risk_score"]),  # risk_score
                        gr.update(value=service["service"]),  # service_text
                        gr.update(value=service["parent_class"]),  # parent_class
                        gr.update(value=""),  # frequency (blank)
                        gr.update(value=None),  # cost (blank)
                        gr.update(choices=contractors, value=None),  # contractor dropdown
                        gr.update(value=True)  # checkbox (selected by default)
                    ])
                else:
                    # Hide unused clinical rows
                    updates.extend([
                        gr.update(visible=False),  # row
                        gr.update(value=""),  # hazard_text
                        gr.update(value=0),  # risk_score
                        gr.update(value=""),  # service_text
                        gr.update(value=""),  # parent_class
                        gr.update(value=""),  # frequency
                        gr.update(value=None),  # cost
                        gr.update(choices=contractors, value=None),  # contractor dropdown
                        gr.update(value=False)  # checkbox (unchecked for hidden rows)
                    ])
            
            # Update social risk rows (next 25 rows)
            for i in range(25):
                if i < len(social_services):
                    service = social_services[i]
                    updates.extend([
                        gr.update(visible=True),  # row
                        gr.update(value=service["hazard"]),  # hazard_text
                        gr.update(value=service["risk_score"]),  # risk_score
                        gr.update(value=service["service"]),  # service_text
                        gr.update(value=service["parent_class"]),  # parent_class
                        gr.update(value=""),  # frequency (blank)
                        gr.update(value=None),  # cost (blank)
                        gr.update(choices=community_resources, value=None),  # community resource dropdown
                        gr.update(value=True)  # checkbox (selected by default)
                    ])
                else:
                    # Hide unused social rows
                    updates.extend([
                        gr.update(visible=False),  # row
                        gr.update(value=""),  # hazard_text
                        gr.update(value=0),  # risk_score
                        gr.update(value=""),  # service_text
                        gr.update(value=""),  # parent_class
                        gr.update(value=""),  # frequency
                        gr.update(value=None),  # cost
                        gr.update(choices=community_resources, value=None),  # community resource dropdown
                        gr.update(value=False)  # checkbox (unchecked for hidden rows)
                    ])
            
            # Add status message
            total_services = len(clinical_services) + len(social_services)
            updates.append(gr.update(
                value=f"✅ Loaded {len(clinical_services)} clinical + {len(social_services)} social recommendations ({total_services} total)",
                visible=True
            ))
            
            return updates
            
        except Exception as e:
            return [gr.update(visible=False)] * 450 + [gr.update(value=f"Error: {str(e)}", visible=True)]

    def save_recommendations(*args):
        """Save recommendation settings (frequency, cost, contractor)"""
        patient_id = args[0]
        if not patient_id:
            return gr.update(value="Please select a patient first", visible=True)
        
        # Extract data from args (patient_id + 8 fields per row * 50 rows = 401 args)
        # Clinical rows: 25 rows with 8 fields each (hazard, risk_score, service, parent_class, frequency, cost, contractor, selected)
        # Social rows: 25 rows with 8 fields each (hazard, risk_score, service, parent_class, frequency, cost, community_resource, selected)
        saved_count = 0
        recommendations = []
        
        try:
            # Process all 50 rows (25 clinical + 25 social)
            for i in range(50):
                start_idx = 1 + (i * 8)  # Skip patient_id, then 8 fields per row
                if start_idx + 7 < len(args):
                    hazard = args[start_idx]
                    risk_score = args[start_idx + 1] 
                    service = args[start_idx + 2]
                    parent_class = args[start_idx + 3]
                    frequency = args[start_idx + 4]
                    cost = args[start_idx + 5]
                    provider = args[start_idx + 6]  # contractor (clinical) or community_resource (social)
                    selected = args[start_idx + 7]  # checkbox value
                    
                    # Only save if row has data and user inputs
                    if hazard and service and (frequency or cost or provider):
                        recommendation = {
                            "patient_id": patient_id,
                            "hazard_code": hazard,
                            "service_description": service,
                            "service_category": parent_class,
                            "frequency": frequency or "",
                            "estimated_cost": float(cost) if cost else 0.0,
                            "provider": provider or "",
                            "priority": "Medium",  # Default priority
                            "notes": "",
                            "selected": bool(selected)  # Include checkbox value
                        }
                        recommendations.append(recommendation)
                        saved_count += 1
            
            # Call backend API to save recommendations
            if recommendations:
                api_url = "http://care_fastapi:8000"
                response = requests.post(f"{api_url}/recommendations/save", json={
                    "patient_id": patient_id,
                    "recommendations": recommendations
                })
                
                if response.ok:
                    return gr.update(value=f"✅ Saved {saved_count} recommendations successfully", visible=True)
                else:
                    return gr.update(value=f"❌ Error saving recommendations: {response.text}", visible=True)
            else:
                return gr.update(value="⚠️ No recommendations to save (fill in frequency, cost, or provider)", visible=True)
                
        except Exception as e:
            print(f"Error in save_recommendations: {e}")
            return gr.update(value=f"❌ Error: {str(e)}", visible=True)

    def generate_report(patient_id):
        """Generate comprehensive recommendations report"""
        if not patient_id:
            return gr.update(value="Please select a patient first", visible=True)
        
        try:
            response = requests.post(f"http://care_fastapi:8000/recommendations/generate_report/{patient_id}")
            
            if response.status_code == 200:
                return gr.update(value="✅ Report generated successfully! Report content saved to database.", visible=True)
            else:
                return gr.update(value=f"Error generating report: {response.text}", visible=True)
                
        except Exception as e:
            return gr.update(value=f"Error: {str(e)}", visible=True)

    # Wire up event handlers
    load_btn.click(
        fn=load_recommendations,
        inputs=[patient_id_state],
        outputs=[
            # For each row: row, hazard_text, risk_score, service_text, parent_class, frequency, cost, contractor
            *[comp for row in recommendation_rows for comp in row],
            status_msg
        ]
    )
    
    save_btn.click(
        fn=save_recommendations,
        inputs=[
            patient_id_state,
            *[comp for row in recommendation_rows for comp in row[1:]]  # Skip the first element (row component)
        ],
        outputs=[status_msg]
    )
    
    report_btn.click(
        fn=generate_report,
        inputs=[patient_id_state],
        outputs=[status_msg]
    )
    
    # Wire up refresh dashboard button
    refresh_dashboard_btn.click(
        fn=refresh_dashboard,
        inputs=[patient_id_state],
        outputs=[
            clinical_risk_display,
            social_risk_display, 
            composite_risk_display,
            urgency_display,
            risk_amplification,
            total_hazards,
            status_msg
        ]
    )
