# 🚓 Smart FIR Filing System

An AI-powered web application designed to streamline the FIR filing process for police departments and citizens. It uses NLP and machine learning to analyze incident descriptions, extract key metadata, and auto-suggest appropriate legal sections under the Bharatiya Nyaya Sanhita (BNS).

---

## ✨ Features

- 🔍 **AI-Suggested Legal Sections**  
  Automatically suggests relevant sections and acts based on incident description.

- 🧠 **Metadata Extraction with NLP**  
  Extracts time, date, location, and suspect details from the incident text using spaCy.

- ⚖️ **Bharatiya Nyaya Sanhita (BNS) Integration**  
  Matches incidents with updated legal sections from the BNS.

- 🧾 **FIR Form Autofill (Form IF1 - Section 154 Cr.P.C)**  
  Fills FIR fields using extracted data, aligned with legal FIR format.

- 📊 **Live Section Preview with Confidence Score**  
  Shows suggested laws in real time with AI explanation and confidence level.

- 📄 **PDF Generation**  
  Converts completed FIR form into a downloadable PDF.

---

## 🖥️ Tech Stack

| Component      | Technology                |
|----------------|---------------------------|
| Backend        | Python, Flask             |
| Frontend       | HTML, Bootstrap, JS       |
| NLP            | spaCy, SentenceTransformers |
| Database       | SQLite (`law_sections`, `fir_submissions`) |
| Deployment     | Flask Server              |

