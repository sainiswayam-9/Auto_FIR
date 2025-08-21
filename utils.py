from transformers import pipeline
import spacy
import sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import json

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
nlp = spacy.load("en_core_web_sm")
semantic_model = SentenceTransformer("all-MiniLM-L6-v2")

def summarize_text(text):
    if len(text.split()) < 30:
        return text
    return summarizer(text, max_length=80, min_length=20, do_sample=False)[0]['summary_text']

def extract_keywords(text):
    doc = nlp(text)
    keywords = set()

    # Add noun chunks
    for chunk in doc.noun_chunks:
        keywords.add(chunk.text.lower())

    # Add individual important words (like verbs, nouns, adjectives)
    for token in doc:
        if token.pos_ in ["VERB", "NOUN", "ADJ"]:
            keywords.add(token.lemma_.lower())  # lemma handles "slapped" → "slap"

    return list(keywords)


def load_law_data():
    conn = sqlite3.connect("data/law_sections.db")
    cursor = conn.cursor()
    cursor.execute("SELECT code, section, title, description, punishment, keywords FROM law_sections")
    laws = cursor.fetchall()
    conn.close()
    return laws

LAWS_DATA = load_law_data()
LAW_TEXTS = [f"{title}. {description}. {keywords}" for _, _, title, description, _, keywords in LAWS_DATA]

vectorizer = TfidfVectorizer().fit(LAW_TEXTS)
LAW_VECTORS = vectorizer.transform(LAW_TEXTS)
LAW_EMBEDDINGS = semantic_model.encode(LAW_TEXTS, convert_to_tensor=True)

def extract_keywords(text):
    doc = nlp(text)
    keywords = set()

    for chunk in doc.noun_chunks:
        keywords.add(chunk.text.lower())

    for token in doc:
        if token.pos_ in ["VERB", "NOUN", "ADJ"]:
            keywords.add(token.lemma_.lower())

    return list(keywords)

def query_laws(keywords):
    query_text = " ".join(keywords)
    query_vec = vectorizer.transform([query_text])
    tfidf_similarities = cosine_similarity(query_vec, LAW_VECTORS).flatten()

    query_embedding = semantic_model.encode(query_text, convert_to_tensor=True)
    semantic_similarities = util.pytorch_cos_sim(query_embedding, LAW_EMBEDDINGS)[0].cpu().numpy()

    combined_scores = 0.6 * tfidf_similarities + 0.4 * semantic_similarities
    top_indices = combined_scores.argsort()[::-1][:3]

    top_laws = []
    for i in top_indices:
        score = combined_scores[i]
        if score > 0.2:
            law = LAWS_DATA[i]
            top_laws.append({
                "code": law[0],
                "section": law[1],  
                "title": law[2],
                "description": law[3],
                "punishment": law[4],
                "keywords": law[5],
                "score": round(float(score), 2)
            })
    return top_laws

