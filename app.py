from flask import Flask, request, jsonify, send_from_directory, render_template, send_file, redirect, url_for
from utils import summarize_text, extract_keywords, query_laws
import spacy, re
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
nlp = spacy.load("en_core_web_lg")

@app.route('/')
def home():
    return render_template("login.html")

@app.route('/home')
def home_page():
    return render_template("fir_form.html")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    text = data.get("text", "")
    doc = nlp(text)

    # Extract laws
    keywords = extract_keywords(text)
    laws = query_laws(keywords)

    # Initialize
    date, time, location = None, None, None
    suspects = []
    highest_confidence_law = None

    if laws:
        highest_confidence_law = max(laws, key=lambda x: x['score'])

    # Collect location candidates
    location_candidates = []
    for ent in doc.ents:
        if ent.label_ == "DATE" and not date and len(ent.text) > 4:
            if "night" not in ent.text.lower():
                date = ent.text
        elif ent.label_ == "TIME" and not time and re.search(r"\d", ent.text):
            time = ent.text
        elif ent.label_ in ["GPE", "LOC", "FAC"]:
            location_candidates.append(ent.text)
        elif ent.label_ == "PERSON":
            suspects.append(ent.text)

    # Pick longest location or None
    if location_candidates:
        location = max(location_candidates, key=len)

    # Regex fallback for date
    if not date:
        date_match = re.search(
            r"(January|February|March|April|May|June|July|August|September|October|November|December)?\s?\d{1,2}(st|nd|rd|th)?",
            text, re.IGNORECASE)
        if date_match:
            date = date_match.group()

    # Regex fallback for time
    if not time:
        time_match = re.search(r"\b\d{1,2}\s?(AM|PM|am|pm)\b", text)
        if time_match:
            time = time_match.group()

    # Regex fallback for location
    if not location:
        loc_match = re.search(r"(?:at|near|in|opposite)\s+([\w\s,]+)", text, re.IGNORECASE)
        if loc_match:
            location = loc_match.group(1).strip()

    response = {
        "laws": laws,
        "metadata": {
            "date": date,
            "time": time,
            "location": location,
            "suspects": list(set(suspects))
        }
    }
    print("Extracted Metadata:", response["metadata"])
    return jsonify(response)

@app.route('/view_firs/<fir_number>')
def view_fir_detail(fir_number):
    conn = sqlite3.connect('fir.db')
    c = conn.cursor()
    c.execute("SELECT * FROM fir_submissions WHERE fir_number = ?", (fir_number,))
    fir = c.fetchone()
    columns = [description[0] for description in c.description]
    conn.close()

    if fir:
        return render_template('fir_detail.html', fir=dict(zip(columns, fir)))
    else:
        return f"FIR {fir_number} not found.", 404
        
@app.route('/submit_fir', methods=['POST'])
def submit_fir():
    data = request.form

    fir_number = datetime.now().strftime("FIR%Y%m%d%H%M%S")
    timestamp = datetime.now().isoformat()

    # Connect to DB
    conn = sqlite3.connect('fir.db')
    c = conn.cursor()

    c.execute(''' 
        CREATE TABLE IF NOT EXISTS fir_submissions (
            fir_number TEXT PRIMARY KEY,
            timestamp TEXT,
            first_name TEXT,
            middle_name TEXT,
            last_name TEXT,
            phone TEXT,
            address TEXT,
            place TEXT,
            date TEXT,
            time TEXT,
            police_station TEXT,
            suspects TEXT,
            sections TEXT
        )
    ''')

    c.execute('''
        INSERT INTO fir_submissions (
            fir_number, timestamp, first_name, middle_name, last_name, phone,
            address, place, date, time, police_station, suspects, sections
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        fir_number, timestamp, data.get('first_name'), data.get('middle_name'),
        data.get('last_name'), data.get('phone'), data.get('address'),
        data.get('place'), data.get('date'), data.get('time'),
        data.get('police_station'), data.get('suspects'),
        data.get('suggested_laws')  # Make sure you send suggested_laws if you want to store it
    ))

    conn.commit()
    conn.close()


    return redirect(url_for("view_fir_detail", fir_number=fir_number))


@app.route("/view_firs")
def view_firs():
    conn = sqlite3.connect("fir.db")
    c = conn.cursor()
    c.execute("SELECT * FROM fir_submissions ORDER BY timestamp DESC")
    rows = c.fetchall()
    columns = [description[0] for description in c.description]
    conn.close()

    print("FIR count:", len(rows))
    print("Columns:", columns[:5])
    print("Sample FIR:", rows[:1])

    return render_template("view_firs.html", firs=rows, columns=columns)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username == "admin" and password == "admin123":
        return home_page()
    else:
        return render_template("login.html", error="Invalid credentials")

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))  # Render gives us the PORT variable
#     app.run(host="0.0.0.0", port=port)  # Binding to all IPs