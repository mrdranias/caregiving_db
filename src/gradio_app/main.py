import gradio as gr
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from forms.patient_identity_gradio_ui import build_patient_identity_ui
from forms.patient_history_gradio_ui import build_patient_history_ui
from forms.adl import build_adl_ui
from forms.iadl import build_iadl_ui
from forms.risk_gradio_ui import risk_ui
from forms.recommendations_gradio_ui import create_recommendations_ui
from forms.prapare import build_prapare_ui

from forms.social_risk_gradio_ui import social_risk_ui

import requests
import os

def build_forms_menu():
    with gr.Blocks() as menu:
        gr.Markdown("# 🗂️ **Patient Intake Data Entry**")
        # Shared state for patient_id and all form data
        patient_id_state = gr.State("")
        form_data_state = gr.State({})

        # Patient ID control and buttons
        with gr.Row():
            patient_id_box = gr.Textbox(label="Patient ID", interactive=True)
            new_client_btn = gr.Button("New Client")
            load_client_btn = gr.Button("Load Client")

        choice = gr.Radio(
            ["Patient Identity", "Patient History", "ADL", "IADL", "PRAPARE Assessment", "Risk Management", "Social Risk Management", "Service Recommendations"],
            label="Select a Form",
            value="Patient Identity"
        )

        # Define form containers
        with gr.Group(visible=True) as identity_ui:
            build_patient_identity_ui(patient_id_state, form_data_state)
        with gr.Group(visible=False) as history_ui:
            build_patient_history_ui(patient_id_state, form_data_state)
        with gr.Group(visible=False) as adl_ui:
            build_adl_ui(patient_id_state, form_data_state)
        with gr.Group(visible=False) as iadl_ui:
            build_iadl_ui(patient_id_state, form_data_state)
        with gr.Group(visible=False) as prapare_ui_group:
            build_prapare_ui(patient_id_state, form_data_state)
        with gr.Group(visible=False) as risk_ui_group:
            risk_ui(patient_id_state, form_data_state)
        with gr.Group(visible=False) as social_risk_ui_group:
            social_risk_ui(patient_id_state, form_data_state)

        with gr.Group(visible=False) as recommendations_ui_group:
            create_recommendations_ui(patient_id_state)
        
        # UI switching logic
        def switch_ui(sel):
            return (
                gr.update(visible=(sel == "Patient Identity")),
                gr.update(visible=(sel == "Patient History")),
                gr.update(visible=(sel == "ADL")),
                gr.update(visible=(sel == "IADL")),
                gr.update(visible=(sel == "PRAPARE Assessment")),
                gr.update(visible=(sel == "Risk Management")),
                gr.update(visible=(sel == "Social Risk Management")),
                gr.update(visible=(sel == "Service Recommendations")),
            )
        choice.change(
            switch_ui,
            inputs=choice,
            outputs=[identity_ui, history_ui, adl_ui, iadl_ui, prapare_ui_group, risk_ui_group, social_risk_ui_group, recommendations_ui_group]
        )

        # New Client logic: clear state and all form fields
        def new_client():
            return "", {}, ""
        new_client_btn.click(
            new_client,
            inputs=[],
            outputs=[patient_id_box, form_data_state, patient_id_state]
        )

        # Load Client logic: fetch all data from backend and populate states
        def load_client(patient_id):
            api_url = os.getenv("API_URL", "http://localhost:8000")
            result = {"patient_id": patient_id}
            # Fetch patient
            try:
                resp = requests.get(f"{api_url}/patients/{patient_id}")
                if resp.ok:
                    result["identity"] = resp.json()
            except Exception:
                pass
            # Fetch history
            try:
                resp = requests.get(f"{api_url}/history/by_patient/{patient_id}")
                if resp.ok:
                    result["history"] = resp.json()
            except Exception:
                pass
            # Fetch ADL
            try:
                resp = requests.get(f"{api_url}/adl/by_patient/{patient_id}")
                if resp.ok:
                    result["adl"] = resp.json()
            except Exception:
                pass
            # Fetch IADL
            try:
                resp = requests.get(f"{api_url}/iadl/by_patient/{patient_id}")
                if resp.ok:
                    result["iadl"] = resp.json()
            except Exception:
                pass
            return patient_id, result, patient_id
        load_client_btn.click(
            load_client,
            inputs=[patient_id_box],
            outputs=[patient_id_box, form_data_state, patient_id_state]
        )

        # When patient_id_state changes, update the patient_id_box
        def sync_patient_id(pid):
            return pid
        patient_id_state.change(
            sync_patient_id,
            inputs=patient_id_state,
            outputs=patient_id_box
        )
    return menu

if __name__ == "__main__":
    print("Gradio app started!")
    build_forms_menu().launch(server_name="0.0.0.0", server_port=7860, debug=True)
