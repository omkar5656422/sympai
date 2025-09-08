from flask import Flask, render_template, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

DATA_FILE = "data.csv"
STORY_FILE = "story.txt"

# --- Load story text ---
if os.path.exists(STORY_FILE):
    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story_text = f.read()
else:
    story_text = ""

# --- Load CSV symptom data ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    
    # 🩹 FIX 1: This parameter handles inconsistent columns and skips bad lines
    df = pd.read_csv(DATA_FILE, on_bad_lines='skip')
    df.columns = df.columns.str.strip().str.lower()
    symptom_data = {}
    
    # 🩹 FIX 2: This line fills empty cells in the 'symptom' column
    df["symptom"] = df["symptom"].fillna('')
    
    for _, row in df.iterrows():
        symptom = str(row["symptom"]).lower().strip()
        conditions = [c.strip() for c in str(row["conditions"]).split(",") if c.strip()]
        symptom_data[symptom] = conditions
    return symptom_data

# --- Save new symptom-condition mapping ---
def save_new_mapping(symptom, condition):
    symptom = symptom.strip().lower()
    condition = condition.strip().lower()
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, on_bad_lines='skip')
        df.columns = df.columns.str.strip().str.lower()
    else:
        df = pd.DataFrame(columns=["symptom", "conditions"])

    existing_symptoms = df["symptom"].str.lower().str.strip().tolist()
    if symptom in existing_symptoms:
        idx = df[df["symptom"].str.lower().str.strip() == symptom].index[0]
        existing_conditions = set(str(df.at[idx, "conditions"]).split(","))
        existing_conditions.add(condition)
        df.at[idx, "conditions"] = ",".join(existing_conditions)
    else:
        new_row = pd.DataFrame({"symptom": [symptom], "conditions": [condition]})
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

# --- Load CSV data ---
symptom_data = load_data()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global symptom_data
    user_input = request.json.get("message", "").lower().strip()
    response = []

    # 1️⃣ Check CSV
    for symptom, conditions in symptom_data.items():
        if symptom in user_input:
            response.extend(conditions)

    # 2️⃣ Check story text
    if not response and story_text:
        sentences = story_text.split(".")
        for sentence in sentences:
            if all(word in sentence.lower() for word in user_input.split()):
                response.append(sentence.strip())

    # 3️⃣ Auto-learn unknown
    if not response:
        words = [w.strip() for w in user_input.split() if w.isalpha()]
        if words:
            save_new_mapping(words[0], "unknown")
            symptom_data = load_data()
            response.append("unknown")

    reply_text = "🤖 I’m not sure. Please consult a doctor." if not response else ", ".join(set(response))
    return jsonify({"reply": reply_text})

if __name__ == "__main__":
    app.run(port=5000, debug=True)