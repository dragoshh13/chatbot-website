from flask import Blueprint, request, jsonify
import anthropic
import os
import pdfplumber
import docx
import io
from pathlib import Path

chatbot_bp = Blueprint('chatbot', __name__)

# Cartella dove sono salvati i documenti
DOCUMENTS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'documents')

def read_pdf(file_path):
    """Legge file PDF"""
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Errore nella lettura PDF {file_path}: {e}")
        return ""

def read_docx(file_path):
    """Legge file DOCX"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        print(f"Errore nella lettura DOCX {file_path}: {e}")
        return ""

def read_txt(file_path):
    """Legge file TXT"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Errore nella lettura TXT {file_path}: {e}")
        return ""

def load_documents():
    """Carica tutti i documenti dalla cartella documents"""
    documents_content = ""
    
    if not os.path.exists(DOCUMENTS_FOLDER):
        return "Nessun documento disponibile."
    
    for file_name in os.listdir(DOCUMENTS_FOLDER):
        file_path = os.path.join(DOCUMENTS_FOLDER, file_name)
        
        if file_name.lower().endswith('.pdf'):
            content = read_pdf(file_path)
        elif file_name.lower().endswith('.docx'):
            content = read_docx(file_path)
        elif file_name.lower().endswith('.txt'):
            content = read_txt(file_path)
        else:
            continue
            
        if content.strip():
            documents_content += f"\n--- DOCUMENTO: {file_name} ---\n{content}\n"
    
    return documents_content if documents_content.strip() else "Nessun documento leggibile trovato."

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """Endpoint per il chatbot"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Domanda mancante'}), 400
        
        # Carica tutti i documenti
        cv_content = load_documents()
        
        # Crea il prompt per Claude
        prompt = f"""
        Sei un assistente che rappresenta professionalmente Dragoș Baicu.
        Rispondi SOLO a domande sul background professionale usando queste informazioni:
        
        {cv_content}
        
        Se la domanda non riguarda il profilo professionale, rispondi: 
        "Mi dispiace, posso parlare solo del background professionale di Dragoș."
        
        Rispondi in modo professionale e cordiale, come se fossi Dragoș stesso.
        
        Domanda: {question}
        """
        
        # Inizializza client Claude (la chiave API deve essere impostata come variabile d'ambiente)
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key non configurata'}), 500
            
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return jsonify({'response': response.content[0].text})
        
    except Exception as e:
        print(f"Errore nel chatbot: {e}")
        return jsonify({'error': 'Errore interno del server'}), 500

@chatbot_bp.route('/preset-questions', methods=['GET'])
def get_preset_questions():
    """Restituisce le domande preimpostate"""
    questions = [
        "Quali sono le tue competenze principali?",
        "Raccontami della tua esperienza lavorativa",
        "Quali progetti hai realizzato?",
        "Qual è la tua formazione?",
        "Sei disponibile per nuove opportunità?",
        "Che software sai utilizzare?",
        "Quali sono i tuoi punti di forza?"
    ]
    return jsonify({'questions': questions})

@chatbot_bp.route('/documents', methods=['GET'])
def list_documents():
    """Lista i documenti disponibili (per debug)"""
    if not os.path.exists(DOCUMENTS_FOLDER):
        return jsonify({'documents': []})
    
    documents = []
    for file_name in os.listdir(DOCUMENTS_FOLDER):
        file_path = os.path.join(DOCUMENTS_FOLDER, file_name)
        if os.path.isfile(file_path):
            documents.append({
                'name': file_name,
                'size': os.path.getsize(file_path),
                'modified': os.path.getmtime(file_path)
            })
    
    return jsonify({'documents': documents})

