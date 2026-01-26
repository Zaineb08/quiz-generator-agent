from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm
from datetime import datetime
import os

def get_mention(score, total):
    percent = (score / total) * 100
    if percent >= 85:
        return "Très Bien"
    elif percent >= 70:
        return "Bien"
    elif percent >= 50:
        return "Assez Bien"
    else:
        return "Insuffisant"

def generate_attestation(nom_apprenant=None, score=None, total=None, sujet=None, **kwargs):
    file_path = "attestation_quiz.pdf"

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=20,
        spaceAfter=20
    )

    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=12,
        leading=18,
        spaceAfter=15
    )

    footer = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10
    )

    story = []

    # -------- LOGO --------
    logo_path = "assets/logo_universite.png"
    if os.path.exists(logo_path):
        story.append(Image(logo_path, width=4*cm, height=4*cm))
    story.append(Spacer(1, 1*cm))

    # -------- TITLE --------
    story.append(Paragraph("ATTESTATION DE RÉUSSITE", title))
    story.append(Spacer(1, 0.5*cm))

    mention = get_mention(score, total)

    # -------- BODY --------
    story.append(Paragraph(
        f"Cette attestation certifie que :<br/><br/>"
        f"<b>{nom_apprenant}</b><br/><br/>"
        f"a validé avec succès le quiz en mode examen "
        f"(20 questions chronométrées) dans le cadre du projet :<br/>"
        f"<b>Agent Générateur de Quiz Éducatifs basés sur l’IA Agentique</b><br/><br/>"
        f"Sujet : <b>{sujet}</b><br/>"
        f"Score obtenu : <b>{score} / {total}</b><br/>"
        f"Mention : <b>{mention}</b><br/><br/>"
        f"Date : {datetime.now().strftime('%d/%m/%Y')}",
        body
    ))

    story.append(Spacer(1, 2*cm))

    # -------- SIGNATURE --------
    signature_path = "assets/signature.png"
    if os.path.exists(signature_path):
        story.append(Image(signature_path, width=5*cm, height=2*cm))

    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Responsable pédagogique<br/>Master Intelligence Artificielle et Science des Données",
        footer
    ))

    doc.build(story)
    return file_path
