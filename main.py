import streamlit as st
import json
import time
from quiz_generator import generate_question, question_cache
from attestation import generate_attestation
from learner_model import LearnerModel
import os

# =============================
# CONFIG
# =============================
DEFAULT_TOTAL_QUESTIONS = 10
DEFAULT_EXAM_DURATION = 5 * 60  # 5 minutes

st.set_page_config(page_title="SmartQuiz IA", layout="centered")
st.title("SmartQuiz – QCM IA Adaptatif")

# =============================
# INITIALISATION SESSION
# =============================
if "started" not in st.session_state:
    st.session_state.started = False

# =============================
# PARAMÈTRES ADMIN (session_state)
# =============================
if "admin_mode" not in st.session_state:
    st.session_state.admin_mode = True
if "admin_temperature" not in st.session_state:
    st.session_state.admin_temperature = 0.5
if "admin_max_tokens" not in st.session_state:
    st.session_state.admin_max_tokens = 600
if "admin_model" not in st.session_state:
    st.session_state.admin_model = "llama-3.1-8b-instant"
if "admin_groq_key" not in st.session_state:
    st.session_state.admin_groq_key = ""

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "index" not in st.session_state:
    st.session_state.index = 1

if "score" not in st.session_state:
    st.session_state.score = 0

if "question" not in st.session_state:
    st.session_state.question = None

if "nom_apprenant" not in st.session_state:
    st.session_state.nom_apprenant = ""

if "learner_model" not in st.session_state:
    st.session_state.learner_model = LearnerModel()

if "consecutive_correct" not in st.session_state:
    st.session_state.consecutive_correct = 0

if "consecutive_incorrect" not in st.session_state:
    st.session_state.consecutive_incorrect = 0

# =============================
# PAGE QCM (AVANT EXAMEN)
# =============================
if not st.session_state.started:
    st.subheader("📝 Configuration du Quiz")
    st.warning("Important: Pour utiliser le SmartQuiz, vous devez entrer votre propre clé GROQ API dans le champ ci-dessous dans les paramètres admin.")
    st.markdown('[Obtenir une clé GROQ API](https://console.groq.com/keys)', unsafe_allow_html=True)
    
    st.info("""
Bienvenue sur SmartQuiz – QCM IA Adaptatif !

Ce système génère un quiz intelligent dont la difficulté s'adapte automatiquement à vos réponses. Plus vous répondez juste, plus les questions deviennent complexes, et inversement.

1. Remplissez vos informations et choisissez le sujet du quiz.
2. Sélectionnez le niveau de départ (Beginner, Intermediate, Advanced), le nombre de questions (5 à 100) et la durée (1 à 180 minutes).
3. Cliquez sur "Démarrer le quiz" pour commencer.
4. **N'oubliez pas d'entrer votre clé GROQ API dans les paramètres admin ci-dessous avant de commencer, et activer le mode admin**
Vous pouvez obtenir une clé gratuite sur [GROQ Console](https://console.groq.com/keys).
""")

    # =============================
    # INTERFACE ADMIN
    # =============================
    with st.expander("🔒 Paramètres Admin (IA)"):
        st.session_state.admin_mode = st.checkbox("Activer le mode admin", value=st.session_state.admin_mode)
        admin_groq_key = st.text_input("Clé GROQ API", value=st.session_state.admin_groq_key, type="password")
        model_options = [
            "llama-3.1-8b-instant",
            "llama-3-8b",
            "llama-3-70b",
            "mixtral-8x7b",
            "gemma-7b-it",
            "autre (personnalisé)"
        ]
        selected_model = st.selectbox("Choix du modèle", model_options, index=model_options.index(st.session_state.admin_model) if st.session_state.admin_model in model_options else len(model_options)-1)
        if selected_model == "autre (personnalisé)":
            admin_model = st.text_input("Nom du modèle personnalisé", value=st.session_state.admin_model)
        else:
            admin_model = selected_model
        admin_temperature = st.slider("Température", min_value=0.0, max_value=2.0, value=st.session_state.admin_temperature, step=0.01)
        admin_max_tokens = st.number_input("Max tokens", min_value=100, max_value=4096, value=st.session_state.admin_max_tokens, step=1)
        if st.button("✅ Sauvegarder les paramètres"):
            error_msgs = []
            if st.session_state.admin_mode:
                if not admin_groq_key:
                    error_msgs.append("La clé GROQ API est obligatoire en mode admin.")
                if not admin_model:
                    error_msgs.append("Le nom du modèle est obligatoire.")
                if not (0.0 <= admin_temperature <= 2.0):
                    error_msgs.append("La température doit être comprise entre 0.0 et 2.0.")
                if not (100 <= admin_max_tokens <= 4096):
                    error_msgs.append("Max tokens doit être entre 100 et 4096.")
            if error_msgs:
                for msg in error_msgs:
                    st.error(msg)
            else:
                st.session_state.admin_groq_key = admin_groq_key
                st.session_state.admin_model = admin_model
                st.session_state.admin_temperature = admin_temperature
                st.session_state.admin_max_tokens = admin_max_tokens
                st.success("Paramètres admin sauvegardés et pris en compte !")
        st.info("Les paramètres admin seront utilisés pour la génération des questions si le mode admin est activé.")

    # Les boutons de reset sont déplacés à la fin du quiz
        # -------- RÉINITIALISER TOUT --------
        if st.button("🧹 Vider cache et données"):
            question_cache.clear_cache()
            try:
                with open("learner_profile.json", "w", encoding="utf-8") as f:
                    f.write('{"scores": {}}')
            except Exception:
                pass
            st.success("✅ Cache et données réinitialisés !")

    nom_apprenant = st.text_input("👤 Nom et Prénom de l'étudiant")

    topic = st.text_input(
        "📘 Sujet",
        placeholder="Ex: Python Basics, Web Development, Machine Learning, etc."
    )

    level = st.selectbox(
        "🎯 Niveau de départ",
        ["Beginner", "Intermediate", "Advanced"],
        help="Le niveau s'ajustera automatiquement selon votre performance"
    )

    total_questions = st.number_input(
        "🔢 Nombre de questions",
        min_value=5,
        max_value=100,
        value=DEFAULT_TOTAL_QUESTIONS,
        step=1,
        help="Entre 5 et 100 questions"
    )

    exam_minutes = st.number_input(
        "⏰ Durée de l'examen (minutes)",
        min_value=1,
        max_value=180,
        value=DEFAULT_EXAM_DURATION // 60,
        step=1,
        help="Entre 1 et 180 minutes"
    )

    if st.button("🚀 Démarrer l'examen"):
        if nom_apprenant.strip() == "":
            st.warning("⚠️ Veuillez saisir votre nom et prénom")
        elif not topic.strip():
            st.warning("⚠️ Veuillez saisir un sujet")
        else:
            st.session_state.nom_apprenant = nom_apprenant
            st.session_state.topic = topic.strip()
            st.session_state.started = True
            if not st.session_state.start_time:
                st.session_state.start_time = time.time()
            st.session_state.level = level
            st.session_state.consecutive_correct = 0
            st.session_state.consecutive_incorrect = 0
            st.session_state.total_questions = int(total_questions)
            st.session_state.exam_duration = int(exam_minutes) * 60
            question_cache.start_session()
            st.rerun()

# =============================
# MODE EXAMEN
# =============================
if st.session_state.started:
    # Rafraîchissement automatique toutes les secondes pour le timer
    _has_autorefresh = False
    try:
        from streamlit_extras.st_autorefresh import st_autorefresh
        _has_autorefresh = True
    except ModuleNotFoundError:
        pass
    if _has_autorefresh:
        st_autorefresh(interval=1000, limit=None, key="timer_autorefresh")
    else:
        import time as _time
        _time.sleep(1)
        # Compatibilité rerun selon version Streamlit
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        elif hasattr(st, "_rerun"):
            st._rerun()
    total_questions = st.session_state.get("total_questions", DEFAULT_TOTAL_QUESTIONS)
    exam_duration = st.session_state.get("exam_duration", DEFAULT_EXAM_DURATION)
    elapsed = int(time.time() - st.session_state.start_time)
    remaining = exam_duration - elapsed

    # =============================
    # FIN EXAMEN
    # =============================
    if remaining <= 0 or st.session_state.index >= total_questions:
        # Arrêt immédiat du test si le temps est écoulé
        import streamlit as st
        st.error("⏰ Examen terminé")
        st.success(
            f"🏆 Score : {st.session_state.score} / {total_questions}"
        )
        # -------- ATTESTATION PDF --------
        if st.button("📄 Attestation PDF"):
            pdf_path = generate_attestation(
                nom_apprenant=st.session_state.nom_apprenant,
                score=st.session_state.score,
                total=total_questions,
                sujet=st.session_state.topic
            )
            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="⬇️ Télécharger l'attestation",
                    data=f,
                    file_name="attestation_quiz.pdf",
                    mime="application/pdf"
                )
        # -------- ACCUEIL --------
        if st.button("🏠 Accueil"):
            st.session_state.started = False
            st.session_state.start_time = None
            st.session_state.index = 1
            st.session_state.score = 0
            st.session_state.question = None
            st.session_state.nom_apprenant = ""
            st.session_state.total_questions = DEFAULT_TOTAL_QUESTIONS
            st.session_state.exam_duration = DEFAULT_EXAM_DURATION
            st.rerun()
        # -------- EXPORT/VOIR QUESTIONS --------
        with st.expander("📦 Exporter / Voir les questions générées"):
            try:
                with open("questions_cache.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                questions = data.get("questions", [])
                st.write(f"Nombre de questions dans le cache : {len(questions)}")
                for q in questions:
                    st.markdown(f"**Sujet :** {q.get('topic','')} | **Niveau :** {q.get('level','')}")
                    st.markdown(f"**Q :** {q.get('question','')}")
                    st.markdown(f"**Choix :**")
                    for opt in q.get('options', []):
                        if opt == q.get('correct_answer'):
                            st.markdown(f"- ✅ **{opt}**")
                        else:
                            st.markdown(f"- {opt}")
                    user_choice = q.get('user_choice', None)
                    correct_answer = q.get('correct_answer', None)
                    if user_choice is not None:
                        if user_choice == correct_answer:
                            st.markdown(f"**Votre choix :** {user_choice} ✅ <span style='color:green'>(Correct)</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**Votre choix :** {user_choice} ❌ <span style='color:red'>(Faux)</span>", unsafe_allow_html=True)
                            st.markdown(f"**Bonne réponse :** {correct_answer} ✅", unsafe_allow_html=True)
                    st.markdown("---")
                st.download_button("⬇️ Exporter mes réponses", data=json.dumps(data, ensure_ascii=False, indent=2), file_name="questions_cache.json", mime="application/json")
            except Exception as e:
                st.info("Aucune question générée ou cache introuvable.")
        st.stop()

    # =============================
    # TIMER + PROGRESSION
    # =============================
    minutes = remaining // 60
    seconds = remaining % 60

    st.info(f"⏱ Temps restant : {minutes:02d}:{seconds:02d}")
    st.progress(st.session_state.index / total_questions)

    # Afficher le niveau actuel et la maîtrise
    mastery = st.session_state.learner_model.mastery(st.session_state.topic)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📚 Niveau Actuel", st.session_state.level)
    with col2:
        st.metric("🎯 Maîtrise", f"{mastery:.1f}%")

    # =============================
    # QUESTION
    # =============================
    if st.session_state.question is None:
        try:
            st.session_state.question = generate_question(
                st.session_state.topic,
                st.session_state.level,
                st.session_state.index
            )
        except Exception as e:
            st.error(f"❌ Erreur lors de la génération de la question : {e}")
            st.stop()

    q = st.session_state.question
    
    # Mark question as asked in this session
    question_cache.mark_as_asked(q)

    # Affichage de la question et des boutons de navigation
    top_quit_col, top_spacer, top_right = st.columns([1, 6, 1])
    with top_right:
        if st.button("🏠 Accueil", key="top_quit"):
            question_cache.clear_cache()
            st.session_state.started = False
            st.session_state.start_time = None
            st.session_state.index = 1
            st.session_state.score = 0
            st.session_state.question = None
            st.session_state.nom_apprenant = ""
            st.session_state.total_questions = DEFAULT_TOTAL_QUESTIONS
            st.session_state.exam_duration = DEFAULT_EXAM_DURATION
            st.rerun()

    st.subheader(f"Question {st.session_state.index} / {total_questions}")
    st.write(q.question)

    answer = st.radio(
        "Réponse :",
        q.options,
        key=f"exam_q_{st.session_state.index}"
    )

    if st.button("Question Suivante ➡️"):
        # Sauvegarder le choix utilisateur dans le cache
        question_cache.save_user_choice(q, answer)
        is_correct = answer == q.correct_answer
        if is_correct:
            st.session_state.score += 1
            st.session_state.consecutive_correct += 1
            st.session_state.consecutive_incorrect = 0
            st.session_state.learner_model.update(st.session_state.topic, correct=True)
        else:
            st.session_state.consecutive_correct = 0
            st.session_state.consecutive_incorrect += 1
            st.session_state.learner_model.update(st.session_state.topic, correct=False)
        levels = ["Beginner", "Intermediate", "Advanced"]
        current_level_idx = levels.index(st.session_state.level)
        if st.session_state.consecutive_correct >= 3 and current_level_idx < 2:
            st.session_state.level = levels[current_level_idx + 1]
            st.session_state.consecutive_correct = 0
            st.success("⬆️ Niveau +1")
        elif st.session_state.consecutive_incorrect >= 2 and current_level_idx > 0:
            st.session_state.level = levels[current_level_idx - 1]
            st.session_state.consecutive_incorrect = 0
            st.warning("⬇️ Niveau -1")
        st.session_state.index += 1
        st.session_state.question = None
        st.rerun()
