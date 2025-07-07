import gradio as gr

import requests
import os
import json

def build_patient_identity_ui(patient_id_state, form_data_state):

    def submit_patient(name, dob, gender, phone, email):
        data = {
            "name": name,
            "dob": dob if dob else None,
            "gender": gender,
            "phone": phone,
            "email": email
        }
        api_url = os.getenv("API_URL", "http://localhost:8000")
        if not api_url.endswith("/patients/create"):
            api_url = api_url.rstrip("/") + "/patients/create"
        try:
            resp = requests.post(api_url, json=data)
            if resp.ok:
                result = resp.json()
                patient_id = result.get("patient_id", "")
                # Update states
                return result, patient_id, {"identity": {**data, "patient_id": patient_id}}, patient_id
            else:
                try:
                    return {"status": "error", "error": resp.json()}, "", {}, ""
                except Exception:
                    return {"status": "error", "error": resp.text}, "", {}, ""
        except Exception as e:
            return {"status": "error", "error": str(e)}, "", {}, ""

    def populate_fields(form_data, patient_id):
        identity = form_data.get("identity", {}) if form_data else {}
        if identity.get("patient_id") != patient_id:
            return "", "", "", "", ""
        return (
            identity.get("name", ""),
            identity.get("dob", ""),
            identity.get("gender", ""),
            identity.get("phone", ""),
            identity.get("email", "")
        )

    with gr.Blocks() as form:
        gr.Markdown("## Patient Identity")
        name = gr.Textbox(label="Name")
        dob = gr.Textbox(label="Date of Birth (YYYY-MM-DD)")
        gender = gr.Radio(["Male", "Female", "Other"], label="Gender")
        phone = gr.Textbox(label="Phone")
        email = gr.Textbox(label="Email")
        submit = gr.Button("Submit")
        output = gr.JSON(label="Patient Creation Result")
        # Submit updates output, patient_id_state, form_data_state, and patient_id_state again
        submit.click(
            submit_patient,
            inputs=[name, dob, gender, phone, email],
            outputs=[output, patient_id_state, form_data_state, patient_id_state]
        )
        # On patient_id_state or form_data_state change, populate fields
        def on_state_change(pid, form_data):
            return populate_fields(form_data, pid)
        patient_id_state.change(
            on_state_change,
            inputs=[patient_id_state, form_data_state],
            outputs=[name, dob, gender, phone, email]
        )
        form_data_state.change(
            on_state_change,
            inputs=[patient_id_state, form_data_state],
            outputs=[name, dob, gender, phone, email]
        )
    return form
