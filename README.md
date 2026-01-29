# 🎓 SmartQuiz — Quiz IA Adaptatif

SmartQuiz est une application web interactive qui génère des QCM personnalisés grâce à l’IA (Groq API) et adapte la difficulté selon vos réponses. Elle propose une expérience moderne, sécurisée, et pédagogique, avec export des résultats et attestation PDF.
Link demo: https://quiz-generator-agent.streamlit.app/

Capture de l'application:

![quiz exemple](assets/question%20exemple%20quiz.png)

---

## 🚀 Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/VOTRE-UTILISATEUR/VOTRE-DEPOT.git
   cd VOTRE-DEPOT
   ```
2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```
3. **Lancer l’application**
   ```bash
   streamlit run main.py
   ```

---

## 🧑‍💻 Fonctionnalités principales
![Bienvenue](assets/Bienvenue%20quiz.png)
- **Quiz IA adaptatif** : questions générées par l’IA, difficulté ajustée selon vos réponses (niveau Beginner, Intermediate, Advanced)
- **Paramètres administrateur** : personnalisez le modèle, la température, le nombre de tokens, et la clé Groq API (saisie sécurisée, non stockée)
- **Sécurité** : chaque utilisateur entre sa propre clé API, jamais stockée
- **Timer automatique** : le quiz s’arrête à la fin du temps imparti
- **Export des résultats** : téléchargez vos réponses et corrections au format JSON
- **Correction détaillée** : chaque réponse utilisateur est comparée à la bonne réponse, avec indication visuelle (✅/❌)
- **Attestation PDF** : générez un certificat de réussite à la fin du quiz
- **Accueil et réinitialisation** : retour rapide à l’accueil, possibilité de réinitialiser le quiz ou le cache
- **Aucune répétition** : gestion avancée du cache pour éviter les doublons de questions

---

## 📝 Utilisation
![Utilisation et configuration](assets/configuration%20quiz.png)
1. **Accueil** : Entrez votre nom, le sujet, le niveau de départ, le nombre de questions (5-100) et la durée (1-180 min).
2. **Quiz** : Répondez aux questions générées par l’IA avant la fin du temps.
3. **Fin du quiz** :
   - Visualisez votre score et votre niveau de maîtrise.
   - Téléchargez votre attestation PDF.
   - Exportez toutes vos réponses et corrections.
   - Revenez à l’accueil pour recommencer.

---

## 🗝️ Clé API Groq

- Obtenez une clé sur [https://console.groq.com/keys](https://console.groq.com/keys)
- Entrez-la dans l’interface (champ masqué) à chaque session.
- **Ne partagez jamais votre clé API.**

---

## 🗂️ Structure des fichiers

- `main.py` : interface utilisateur Streamlit, logique principale
- `quiz_generator.py` : génération des questions via Groq API, gestion des paramètres admin
- `question_cache.py` : gestion du cache des questions et des réponses utilisateur
- `learner_model.py` : suivi de la progression et du niveau de maîtrise
- `attestation.py` : génération du certificat PDF
- `models.py` : schémas de données (questions)
- `questions_cache.json` : cache des questions et réponses (exportable)
- `learner_profile.json` : historique de progression utilisateur

---

## 📦 Export et correction
![Fin quiz image](assets/fin%20quiz.png)
![verifier reponses image](assets/verifier%20reponses.png)
- À la fin du quiz, cliquez sur **Exporter mes réponses** pour télécharger un fichier JSON contenant :
  - Toutes les questions posées
  - Vos réponses
  - Les bonnes réponses
  - Un indicateur si votre réponse était correcte ou non

---

## 🛠️ Personnalisation avancée

- Accédez à l’expandeur “Admin” pour :
  - Modifier le prompt IA
  - Changer le modèle Groq (ex : llama-3.1-8b-instant)
  - Régler la température et le nombre de tokens
  - Saisir votre clé API de façon sécurisée

---

## ❓ FAQ

- **Ma clé API est-elle stockée ?**  
  Non, elle n’est jamais enregistrée sur le disque.
- **Puis-je exporter mes résultats ?**  
  Oui, via le bouton “Exporter mes réponses” à la fin du quiz.
- **Comment réinitialiser le quiz ?**  
  Utilisez le bouton “Accueil” ou “Réinitialiser”.

---

## 📄 Licence

Projet open-source sous licence MIT.

---



