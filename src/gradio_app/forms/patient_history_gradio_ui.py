import gradio as gr
import os
import requests

def build_patient_history_ui(patient_id_state, form_data_state):
    def submit_patient_history(patient_id, dx_codes, tx_codes, rx_codes, sx_codes, notes):
        try:
            dx_list = [c.strip() for c in dx_codes.split(',') if c.strip()] if dx_codes else []
            tx_list = [c.strip() for c in tx_codes.split(',') if c.strip()] if tx_codes else []
            rx_list = [c.strip() for c in rx_codes.split(',') if c.strip()] if rx_codes else []
            sx_list = [c.strip() for c in sx_codes.split(',') if c.strip()] if sx_codes else []
            data = {
                "patient_id": patient_id,
                "dx_codes": dx_list,
                "tx_codes": tx_list,
                "rx_codes": rx_list,
                "sx_codes": sx_list,
                "notes": notes,
            }
            api_url = os.getenv("API_URL", "http://localhost:8000")
            if not api_url.endswith("/history/submit"):
                api_url = api_url.rstrip("/") + "/history/submit"
            resp = requests.post(api_url, json=data)
            if resp.ok:
                result = resp.json()
                # Update form_data_state
                return result, {"history": data}
            else:
                try:
                    return {"status": "error", "error": resp.json()}, {}
                except Exception:
                    return {"status": "error", "error": resp.text}, {}
        except Exception as e:
            return {"status": "error", "error": str(e)}, {}

    def fetch_codes(endpoint):
        api_url = os.getenv("API_URL", "http://localhost:8000")
        url = api_url.rstrip("/") + endpoint
        try:
            resp = requests.get(url)
            if resp.ok:
                data = resp.json()
                return [[row['code'], row['description']] for row in data]
            else:
                return []
        except Exception:
            return []

    def populate_fields(form_data, patient_id):
        if not isinstance(form_data, dict) or form_data is None:
            return "", "", "", "", ""
        history = form_data.get("history")
        if not isinstance(history, dict) or history is None:
            return "", "", "", "", ""
        if history.get("patient_id") != patient_id:
            return "", "", "", "", ""
        return (
            ",".join(history.get("dx_codes", [])),
            ",".join(history.get("tx_codes", [])),
            ",".join(history.get("rx_codes", [])),
            ",".join(history.get("sx_codes", [])),
            history.get("notes", "")
        )

    def update_preview(dx_dropdowns, tx_dropdowns, rx_dropdowns, sx_dropdowns):
        dx_codes = [d.strip() for d in dx_dropdowns if d.strip()]
        tx_codes = [t.strip() for t in tx_dropdowns if t.strip()]
        rx_codes = [r.strip() for r in rx_dropdowns if r.strip()]
        sx_codes = [s.strip() for s in sx_dropdowns if s.strip()]
        return ",".join(dx_codes), ",".join(tx_codes), ",".join(rx_codes), ",".join(sx_codes)

    with gr.Blocks() as form:
        gr.Markdown("## Patient History")
        # Fetch top 10 codes for each type
        # Build choices as (label, code) tuples for dropdowns
        def code_label_options(code_rows):
            return [""] + [
                (f"{row[0]} - {row[1][:15].strip()}" if row[1] else row[0], row[0])
                for row in code_rows[:10]
            ]
        code_choices = {
            'dx': code_label_options(fetch_codes("/codes/dx")),
            'tx': code_label_options(fetch_codes("/codes/tx")),
            'rx': code_label_options(fetch_codes("/codes/rx")),
            'sx': code_label_options(fetch_codes("/codes/sx")),
        }

        # Create 4 dropdowns for each code type
        with gr.Row():
            dx_dropdowns = [gr.Dropdown(choices=code_choices['dx'], label=f"Diagnosis Code {i+1}", allow_custom_value=True) for i in range(4)]
        with gr.Row():
            tx_dropdowns = [gr.Dropdown(choices=code_choices['tx'], label=f"Treatment Code {i+1}", allow_custom_value=True) for i in range(4)]
        with gr.Row():
            rx_dropdowns = [gr.Dropdown(choices=code_choices['rx'], label=f"Medication Code {i+1}", allow_custom_value=True) for i in range(4)]
        with gr.Row():
            sx_dropdowns = [gr.Dropdown(choices=code_choices['sx'], label=f"Symptom Code {i+1}", allow_custom_value=True) for i in range(4)]

        # Preview textboxes for each code type
        with gr.Row():
            dx_preview = gr.Textbox(label="Diagnosis Codes to be saved", interactive=False)
            tx_preview = gr.Textbox(label="Treatment Codes to be saved", interactive=False)
        with gr.Row():
            rx_preview = gr.Textbox(label="Medication Codes to be saved", interactive=False)
            sx_preview = gr.Textbox(label="Symptom Codes to be saved", interactive=False)

        notes = gr.Textbox(label="Notes")
        submit = gr.Button("Submit")
        output = gr.JSON(label="Submission Preview")

        # Flatten all dropdowns for preview update
        all_dropdowns = dx_dropdowns + tx_dropdowns + rx_dropdowns + sx_dropdowns
        def update_preview_flat(*dropdown_values):
            dx = [v for v in dropdown_values[0:4] if v]
            tx = [v for v in dropdown_values[4:8] if v]
            rx = [v for v in dropdown_values[8:12] if v]
            sx = [v for v in dropdown_values[12:16] if v]
            return ",".join(dx), ",".join(tx), ",".join(rx), ",".join(sx)
        for dropdown in all_dropdowns:
            dropdown.change(
                update_preview_flat,
                inputs=all_dropdowns,
                outputs=[dx_preview, tx_preview, rx_preview, sx_preview]
            )

        submit.click(
            submit_patient_history,
            inputs=[patient_id_state, dx_preview, tx_preview, rx_preview, sx_preview, notes],
            outputs=[output, form_data_state]
        )
        # On patient_id_state or form_data_state change, populate fields
        def on_state_change(pid, form_data):
            # When no history, reset dropdowns and preview fields
            result = populate_fields(form_data, pid)
            if result == ("", "", "", "", ""):
                # 4 blanks for each dropdown group, 4 preview, 1 notes
                return ["", "", "", ""]*4 + ["", "", "", "", ""]
            return result
        patient_id_state.change(
            on_state_change,
            inputs=[patient_id_state, form_data_state],
            outputs=[dx_preview, tx_preview, rx_preview, sx_preview, notes]
        )
        form_data_state.change(
            on_state_change,
            inputs=[patient_id_state, form_data_state],
            outputs=[dx_preview, tx_preview, rx_preview, sx_preview, notes]
        )
        gr.Markdown("### Diagnosis Codes (First 20)")
        dx_table = gr.Dataframe(
            value=fetch_codes("/codes/dx"),
            headers=["Code", "Description"],
            interactive=False,
            visible=True
        )
        gr.Markdown("### Treatment Codes (First 20)")
        tx_table = gr.Dataframe(
            value=fetch_codes("/codes/tx"),
            headers=["Code", "Description"],
            interactive=False,
            visible=True
        )
        gr.Markdown("### Medication Codes (First 20)")
        rx_table = gr.Dataframe(
            value=fetch_codes("/codes/rx"),
            headers=["Code", "Description"],
            interactive=False,
            visible=True
        )
        gr.Markdown("### Symptom Codes (First 20)")
        sx_table = gr.Dataframe(
            value=fetch_codes("/codes/sx"),
            headers=["Code", "Description"],
            interactive=False,
            visible=True
        )
    return form
