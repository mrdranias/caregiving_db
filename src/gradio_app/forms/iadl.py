import gradio as gr
import requests
import os
from datetime import datetime

IADL_INFO = {
    "title": "Lawton-Brody Instrumental Activities of Daily Living (IADL)",
    "instructions": "Assess the individual's ability to perform instrumental activities necessary for independent living. Each item is scored as 1 (independent) or 0 (dependent). The total score ranges from 0 (low function, dependent) to 8 (high function, independent).",
    "questions": [
        {"key": "telephone", "text": "Ability to Use Telephone", "options": [1, 0], "explanation": "1 = Operates telephone on own initiative, looks up and dials numbers; 0 = Does not use telephone at all"},
        {"key": "shopping", "text": "Shopping", "options": [1, 0], "explanation": "1 = Takes care of all shopping needs independently; 0 = Completely unable to shop or needs to be accompanied on any shopping trip"},
        {"key": "food_preparation", "text": "Food Preparation", "options": [1, 0], "explanation": "1 = Plans, prepares, and serves adequate meals independently; 0 = Needs to have meals prepared and served"},
        {"key": "housekeeping", "text": "Housekeeping", "options": [1, 0], "explanation": "1 = Maintains house alone with occasional assistance; 0 = Needs help with all home maintenance tasks or does not participate at all"},
        {"key": "laundry", "text": "Laundry", "options": [1, 0], "explanation": "1 = Does personal laundry completely; 0 = All laundry must be done by others"},
        {"key": "transportation", "text": "Mode of Transportation", "options": [1, 0], "explanation": "1 = Travels independently on public transportation or drives own car; 0 = Does not travel at all or needs to be accompanied"},
        {"key": "medication", "text": "Responsibility for Own Medications", "options": [1, 0], "explanation": "1 = Is responsible for taking medication in correct dosages at correct time; 0 = Is not capable of dispensing own medication or only takes if prepared in advance"},
        {"key": "finances", "text": "Ability to Handle Finances", "options": [1, 0], "explanation": "1 = Manages financial matters independently (budgets, pays rent, goes to bank); 0 = Incapable of handling money or needs help with all financial matters"},
    ]
}

def build_iadl_ui(patient_id_state, form_data_state):
    def submit_iadl(patient_id, date_completed, *args):
        try:
            answers = {q["key"]: int(a) for q, a in zip(IADL_INFO["questions"], args)}
            data = {
                "patient_id": patient_id,
                "date_completed": date_completed,
                **answers,
                "answers": answers
            }
            api_url = os.getenv("API_URL", "http://localhost:8000")
            if not api_url.endswith("/iadl/submit"):
                api_url = api_url.rstrip("/") + "/iadl/submit"
            resp = requests.post(api_url, json=data)
            if resp.ok:
                result = resp.json()
                if result.get("was_update"):
                    result["warning"] = "⚠️ Existing IADL record for this date was overwritten."
                return result, {"iadl": data}
            else:
                try:
                    return {"status": "error", "error": resp.json()}, {}
                except Exception:
                    return {"status": "error", "error": resp.text}, {}
        except Exception as e:
            return {"status": "error", "error": str(e)}, {}

    def populate_fields(form_data, patient_id):
        if not isinstance(form_data, dict) or form_data is None:
            return datetime.now().strftime('%Y-%m-%d'), *[str(q["options"][0]) for q in IADL_INFO["questions"]]
        iadl = form_data.get("iadl")
        if not isinstance(iadl, dict) or iadl is None:
            return datetime.now().strftime('%Y-%m-%d'), *[str(q["options"][0]) for q in IADL_INFO["questions"]]
        if iadl.get("patient_id") != patient_id:
            return datetime.now().strftime('%Y-%m-%d'), *[str(q["options"][0]) for q in IADL_INFO["questions"]]
        vals = []
        for q in IADL_INFO["questions"]:
            val = iadl.get(q["key"], None)
            opts = [str(opt) for opt in q["options"]]
            if val is not None and str(val) in opts:
                vals.append(str(val))
            else:
                vals.append(opts[0])
        return iadl.get("date_completed", datetime.now().strftime('%Y-%m-%d')), *vals

    with gr.Blocks() as form:
        gr.Markdown(f"## {IADL_INFO['title']}")
        gr.Markdown(IADL_INFO['instructions'])
        date_completed = gr.Textbox(label="Date Completed (YYYY-MM-DD)", value=datetime.now().strftime('%Y-%m-%d'))
        dropdowns = [
            gr.Dropdown(
                [str(opt) for opt in q["options"]],
                label=q["text"]+" ("+q["explanation"]+")",
                value=str(q["options"][0])
            ) for q in IADL_INFO["questions"]
        ]
        submit = gr.Button("Submit")
        output = gr.JSON(label="Submission Preview")
        submit.click(
            submit_iadl,
            inputs=[patient_id_state, date_completed] + dropdowns,
            outputs=[output, form_data_state]
        )
        # On patient_id_state or form_data_state change, populate fields
        def on_state_change(pid, form_data):
            return populate_fields(form_data, pid)
        patient_id_state.change(
            on_state_change,
            inputs=[patient_id_state, form_data_state],
            outputs=[date_completed] + dropdowns
        )
        form_data_state.change(
            on_state_change,
            inputs=[patient_id_state, form_data_state],
            outputs=[date_completed] + dropdowns
        )
    return form
