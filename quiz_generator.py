import json
import os
import re
from groq import Groq
from models import Question
from question_cache import QuestionCache

# ==========================================================
# ✅ API Key Check
# ==========================================================

# --- Paramètres dynamiques (admin) ---
import streamlit as st
def get_admin_params():
    if hasattr(st, "session_state") and st.session_state.get("admin_mode", False):
        return {
            "api_key": st.session_state.get("admin_groq_key", os.getenv("GROQ_API_KEY")),
            "model": st.session_state.get("admin_model", "llama-3.1-8b-instant"),
            "temperature": st.session_state.get("admin_temperature", 0.5),
            "max_tokens": st.session_state.get("admin_max_tokens", 600)
        }
    else:
        return {
            "api_key": os.getenv("GROQ_API_KEY"),
            "model": "llama-3.1-8b-instant",
            "temperature": 0.5,
            "max_tokens": 600
        }


question_cache = QuestionCache()



# ==========================================================
# ✅ JSON Extraction (Safe)
# ==========================================================
def extract_json_from_text(text: str) -> dict:
    """
    Extract JSON safely even if model adds extra text.
    """
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError("❌ Aucun JSON détecté dans la réponse du modèle.")

    json_str = text[start:end + 1]

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"❌ JSON invalide: {e}")


# ==========================================================
# ✅ Quality Filter
# ==========================================================
def is_low_quality(data: dict) -> bool:
    """
    Reject weak or trivial AI-generated questions.
    """

    question = data.get("question", "").lower()
    options = data.get("options", [])

    # Too short → usually trivial
    if len(question) < 25:
        return True

    # Generic beginner patterns
    bad_starts = ["what is", "define", "explain"]
    if any(question.startswith(b) for b in bad_starts):
        return True

    # Placeholder options like "Option A"
    if any(opt.lower().startswith("option") for opt in options):
        return True

    return False


# ==========================================================
# ✅ Main Question Generator
# ==========================================================
def generate_question(topic: str, level: str, index: int) -> Question:
    """
    Priority:
    1. Return unused cached question
    2. Generate new high-quality question via API
    3. Cache only validated good questions
    """

    # Step 1: Try cache first
    cached_question = question_cache.get_cached_question(topic, level)
    if cached_question and not question_cache.was_asked_in_session(cached_question):
        return cached_question

    # Step 2: Generate new question
    question = _generate_question_from_api(topic, level, index)

    # Step 3: Cache only good questions
    question_cache.add_question(question)

    return question


# ==========================================================
# ✅ API Generation with Retry + Filtering
# ==========================================================
def _generate_question_from_api(topic: str, level: str, index: int) -> Question:
    """
    Generates exam-quality MCQ from Groq API.
    Retries if weak question is generated.
    """
    # --- PROMPT ADMIN OU PAR DÉFAUT ---
    params = get_admin_params()
    if not params["api_key"]:
        raise ValueError("❌ GROQ_API_KEY n'est pas définie. Merci de la saisir dans les paramètres admin avant de lancer le quiz.")
    client = Groq(api_key=params["api_key"])
    prompt = f"""
Tu es un professeur universitaire expert chargé de rédiger des QCM de niveau examen.

Génère UNE seule question QCM de haute qualité.

Sujet : {topic}
Niveau : {level}

RÈGLES STRICTES :
- La question doit tester la compréhension et le raisonnement, PAS une simple définition.
- Ne génère jamais des questions triviales comme : "Qu'est-ce que Python ?"
- Les mauvaises réponses doivent être plausibles (erreurs fréquentes des étudiants).
- Ne jamais utiliser des options génériques comme "Option A", "Option B".
- La bonne réponse ne doit pas être évidente immédiatement.
- Retourne UNIQUEMENT un JSON valide, sans aucun texte supplémentaire.

Format JSON exact :

{{
    "id": "q_{index}",
    "topic": "{topic}",
    "level": "{level}",
    "question": "Texte de la question en français",
    "options": ["Choix 1", "Choix 2", "Choix 3", "Choix 4"],
    "correct_answer": "Choix 1",
    "type": "MCQ"
}}
"""
    # ✅ Retry up to 5 times if low-quality output appears
    import streamlit as st
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model=params["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=params["temperature"],
                max_tokens=params["max_tokens"]
            )
        except Exception as e:
            st.error(f"❌ Erreur API GROQ : {e}. Vérifiez la clé et le modèle.")
            raise

        if not response.choices or not response.choices[0].message.content:
            continue

        content = response.choices[0].message.content.strip()

        # Extract JSON
        data = extract_json_from_text(content)

        # Required fields validation
        required_fields = ["id", "topic", "level", "question", "options", "correct_answer", "type"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"❌ Champ manquant: {field}")

        # Reject weak questions
        if is_low_quality(data):
            print("⚠️ Question trop faible générée → retry...")
            continue

        # Check correct answer consistency
        if data["correct_answer"] not in data["options"]:
            print("⚠️ La bonne réponse n'est pas dans les options → retry...")
            continue

        # ✅ Return validated question
        return Question(**data)

    # If all retries fail
    raise Exception("❌ Impossible de générer une question de bonne qualité après plusieurs essais.")
