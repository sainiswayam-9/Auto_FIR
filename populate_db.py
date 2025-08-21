import pandas as pd
import sqlite3
import os

os.makedirs("data", exist_ok=True)
df = pd.read_csv("dataset.csv")
conn = sqlite3.connect("data/law_sections.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS law_sections (
    code TEXT,
    section TEXT,
    title TEXT,
    description TEXT,
    punishment TEXT,
    keywords TEXT
)
''')

for _, row in df.iterrows():
    cursor.execute("INSERT INTO law_sections VALUES (?, ?, ?, ?, ?, ? )", tuple(row))

conn.commit()
conn.close()
print("Database populated.")
