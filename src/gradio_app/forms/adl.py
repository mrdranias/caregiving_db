import gradio as gr
import os
import requests
from datetime import datetime

adl_instructions = """
**ADL Administration Instructions:**\n
- Ask the respondent each question as written.\n- For each item, select the score that best describes the individual's ability.\n- If unsure, use the best estimate based on observation or collateral information.
"""
adl_options = {
    "Bowels": [(2, "Continent"), (1, "Occasional accident (once/week)"), (0, "Incontinent or needs enemata")],
    "Bladder": [(2, "Continent (over 7 days)"), (1, "Occasional accident (max. once per 24 hrs)"), (0, "Incontinent or catheterized, unable to manage")],
    "Grooming": [(1, "Independent face/hair/teeth/shaving (implements provided)"), (0, "Needs help with personal care")],
    "Toilet use": [(2, "Independent (on and off, dressing, wiping)"), (1, "Needs some help, but can do something alone"), (0, "Dependent")],
    "Feeding": [(2, "Independent (food provided within reach)"), (1, "Needs help cutting, spreading butter, etc."), (0, "Unable")],
    "Transfers": [(3, "Independent"), (2, "Minor help (verbal or physical)"), (1, "Major help (one or two people, physical, can sit)"), (0, "Unable – no sitting balance")],
    "Mobility": [(3, "Independent (may use any aid, e.g., stick)"), (2, "Walks with help of one person (verbal or physical)"), (1, "Wheelchair independent, including corners, etc."), (0, "Immobile")],
    "Dressing": [(2, "Independent (including buttons, zips, laces, etc.)"), (1, "Needs help, but can do about half unaided"), (0, "Dependent")],
    "Stairs": [(2, "Independent up and down"), (1, "Needs help (verbal, physical, carrying aid)"), (0, "Unable")],
    "Bathing": [(1, "Independent (or in shower)"), (0, "Dependent")],
}

adl_questions = list(adl_options.keys())


def build_adl_ui(patient_id_state, form_data_state):
    def submit_adl(patient_id, date_completed, *args):
        try:
            responses = {q.lower().replace(' ', '_'): int(a.split(':')[0]) for q, a in zip(adl_questions, args)}
            data = {
                "patient_id": patient_id,
                "date_completed": date_completed,
                **responses,
                "answers": responses
            }
            api_url = os.getenv("API_URL", "http://localhost:8000")
            if not api_url.endswith("/adl/submit"):
                api_url = api_url.rstrip("/") + "/adl/submit"
            resp = requests.post(api_url, json=data)
            if resp.ok:
                result = resp.json()
                if result.get("was_update"):
                    result["warning"] = "⚠️ Existing ADL record for this date was overwritten."
                return result, {"adl": data}
            else:
                try:
                    return {"status": "error", "error": resp.json()}, {}
                except Exception:
                    return {"status": "error", "error": resp.text}, {}
        except Exception as e:
            return {"status": "error", "error": str(e)}, {}

    def populate_fields(form_data, patient_id):
        if not isinstance(form_data, dict) or form_data is None:
            return datetime.now().strftime('%Y-%m-%d'), *[f"{adl_options[q][0][0]}: {adl_options[q][0][1]}" for q in adl_questions]
        adl = form_data.get("adl")
        if not isinstance(adl, dict) or adl is None:
            return datetime.now().strftime('%Y-%m-%d'), *[f"{adl_options[q][0][0]}: {adl_options[q][0][1]}" for q in adl_questions]
        if adl.get("patient_id") != patient_id:
            return datetime.now().strftime('%Y-%m-%d'), *[f"{adl_options[q][0][0]}: {adl_options[q][0][1]}" for q in adl_questions]
        vals = []
        for q in adl_questions:
            val = adl.get(q.lower().replace(' ', '_'), None)
            opts = [f"{score}: {desc}" for score, desc in adl_options[q]]
            if val is not None:
                # Find label
                found = next((o for o in opts if o.startswith(str(val))), opts[0])
                vals.append(found)
            else:
                vals.append(opts[0])
        return adl.get("date_completed", datetime.now().strftime('%Y-%m-%d')), *vals

    with gr.Blocks() as form:
        gr.Markdown("## ADL Questionnaire")
        gr.Markdown(adl_instructions)
        date_completed = gr.Textbox(label="Date Completed (YYYY-MM-DD)", value=datetime.now().strftime('%Y-%m-%d'))
        dropdowns = [
            gr.Dropdown(
                [f"{score}: {desc}" for score, desc in adl_options[q]],
                label=q,
                value=f"{adl_options[q][0][0]}: {adl_options[q][0][1]}"
            ) for q in adl_questions
        ]
        submit = gr.Button("Submit")
        output = gr.JSON(label="Submission Preview")
        submit.click(
            submit_adl,
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
