import pandas as pd
import os

DATA_FILE = "data.csv"
AIML_FILE = "symptoms.aiml"

# Check if data.csv exists before trying to read it
if not os.path.exists(DATA_FILE):
    print(f"Error: {DATA_FILE} not found! The AIML file cannot be generated.")
else:
    # 🩹 FIX: This parameter handles inconsistent columns and skips bad lines
    df = pd.read_csv(DATA_FILE, on_bad_lines='skip')
    df.columns = df.columns.str.strip().str.lower()

    # 🩹 FIX: Fill missing values with an empty string to prevent errors
    df["symptom"] = df["symptom"].fillna('')

    with open(AIML_FILE, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n<aiml version="2.0">\n')
        
        for _, row in df.iterrows():
            symptom = str(row["symptom"]).strip().upper()
            conditions = [c.strip() for c in str(row["conditions"]).split(",")]
            response = ", ".join(conditions)
            
            f.write("    <category>\n")
            f.write(f"        <pattern>{symptom}</pattern>\n")
            f.write(f"        <template>{response}</template>\n")
            f.write("    </category>\n")
        
        # Default fallback
        f.write("    <category>\n")
        f.write("        <pattern>*</pattern>\n")
        f.write("        <template>🤖 I’m not sure. Please consult a doctor.</template>\n")
        f.write("    </category>\n")

        f.write("</aiml>\n")

    print(f"AIML generated: {AIML_FILE}")