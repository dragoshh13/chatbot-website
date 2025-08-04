from flask import Blueprint, request, jsonify
import anthropic
import os
import pdfplumber
import docx
import logging
import re
from datetime import datetime

chatbot_bp = Blueprint('chatbot', __name__)

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('chatbot')

# Cartella documenti
DOCUMENTS_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)), 'documents')

# Informazioni strutturate (modifica qui per aggiungere/aggiornare i tuoi dati)
STRUCTURED_DATA = {
    "competences": [
        "Sviluppo web full-stack (Python, JavaScript)",
        "Machine learning e data analysis",
        "Ottimizzazione SEO e content strategy",
        "Grafica avanzata (Photoshop, Illustrator)",
        "Video editing professionale (Premiere Pro, After Effects)"
    ],
    "strengths": [
        "Problem solving creativo",
        "Adattabilità a nuovi contesti lavorativi",
        "Precisione e attenzione ai dettagli",
        "Capacità di lavorare sotto pressione",
        "Comunicazione efficace in team multiculturali"
    ],
    "contact": {
        "email": "dragos.baicu@example.com",
        "phone": "+39 123 4567890",
        "linkedin": "https://linkedin.com/in/dragosbaicu"
    },
    "portfolio": {
        "photoshop": [
            {"title": "Progetto Brand Identity", "url": "https://portfolio.com/brand-identity", "skills": ["grafica", "branding"]},
            {"title": "Manipolazione Fotografica", "url": "https://portfolio.com/photo-manipulation", "skills": ["fotoritocco", "compositing"]}
        ],
        "video": [
            {"title": "Video Corporate", "url": "https://portfolio.com/corporate-video", "skills": ["montaggio", "color grading"]},
            {"title": "Animazione Promozionale", "url": "https://portfolio.com/promo-animation", "skills": ["motion graphics", "after effects"]}
        ],
        "projects": [
            {"title": "E-commerce Platform", "url": "https://github.com/dragoshh/ecommerce", "skills": ["python", "django", "javascript"]},
            {"title": "AI Content Analyzer", "url": "https://github.com/dragoshh/ai-analyzer", "skills": ["machine learning", "nlp"]}
        ]
    },
    "articles": [
        {"title": "Innovazioni nel Web Design Moderno", "url": "https://blog.com/web-design-innovations"},
        {"title": "L'Impatto dell'AI sul Digital Marketing", "url": "https://blog.com/ai-digital-marketing"}
    ]
}

# FIX 1: Migliorato il prompt per formattazione elenchi
SYSTEM_PROMPT = """
Sei Dragoș Baicu, un professionista IT e creativo digitale. Rispondi in modo conciso e mirato alle domande dei recruiter.

# Istruzioni fondamentali
1. **Formattazione elenchi**:
   - Usa SEMPRE '-' per gli elenchi puntati (non '*' o altri caratteri)
   - Allinea tutti gli elementi a sinistra senza rientri
   - Massimo 5 punti per elenco

2. **Risposte focalizzate**: 
   - Massimo 2-3 frasi per domande semplici
   - Differenzia chiaramente tra competenze tecniche e punti di forza personali

3. **Tono e stile**:
   - Domande tecniche: tono professionale e diretto
   - Domande personali: tono più caldo e personale
   - Evita ripetizioni e informazioni ridondanti

# Linee guida per tipologie di domande

## Competenze tecniche (es: "Quali linguaggi conosci?")
- Formatta a punti SEMPRE così:
- **Nome competenza** (esperienza): breve descrizione
- Esempio: 
- **Python** (5 anni): Sviluppo backend e analisi dati
- **JavaScript** (4 anni): Sviluppo frontend e applicazioni web

## Punti di forza personali (es: "Quali sono i suoi punti di forza?")
- Massimo 3 punti focali
- Breve esempio concreto per ognuno
- Formatta:
- **Punto di forza**: Esempio concreto
- Esempio:
- **Problem solving**: Risolto X problema in Y progetto

## Suggerimento portfolio
- Solo se pertinente alla domanda
- Formatta come: 
  "Potrebbe vedere [titolo progetto](link) per un esempio concreto di [competenza]"
"""

def read_pdf(file_path):
    """Legge file PDF"""
    try:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    except Exception as e:
        logger.error(f"Errore lettura PDF: {e}")
        return ""

def read_docx(file_path):
    """Legge file DOCX"""
    try:
        doc = docx.Document(file_path)
        return "\n".join(para.text for para in doc.paragraphs if para.text)
    except Exception as e:
        logger.error(f"Errore lettura DOCX: {e}")
        return ""

def read_txt(file_path):
    """Legge file TXT"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Errore lettura TXT: {e}")
        return ""

def load_documents():
    """Carica tutti i documenti"""
    if not os.path.exists(DOCUMENTS_FOLDER):
        return ""
    
    content = []
    for file in os.listdir(DOCUMENTS_FOLDER):
        path = os.path.join(DOCUMENTS_FOLDER, file)
        if file.endswith('.pdf'):
            content.append(f"### {file}\n{read_pdf(path)}")
        elif file.endswith('.docx'):
            content.append(f"### {file}\n{read_docx(path)}")
        elif file.endswith('.txt'):
            content.append(f"### {file}\n{read_txt(path)}")
    
    return "\n\n".join(content)

def should_include_contact(question):
    """Determina se includere i contatti nella risposta"""
    contact_keywords = [
        'contatt', 'chiam', 'telefon', 'email', 'mail', 
        'colloquio', 'incont', 'parlare', 'discutere'
    ]
    return any(kw in question.lower() for kw in contact_keywords)

def get_relevant_portfolio_items(question, max_items=2):
    """Trova elementi del portfolio pertinenti alla domanda"""
    relevant = []
    question_lower = question.lower()
    
    # Cerca in tutte le categorie
    for category in ['photoshop', 'video', 'projects']:
        for item in STRUCTURED_DATA['portfolio'].get(category, []):
            # Cerca match nelle skills o nel titolo
            if any(skill in question_lower for skill in item.get('skills', [])) or \
               any(kw in item['title'].lower() for kw in question_lower.split()):
                relevant.append(item)
                if len(relevant) >= max_items:
                    return relevant
    
    return relevant

# FIX 2: Migliorata formattazione portfolio
def format_portfolio_suggestion(items):
    """Formatta la presentazione degli elementi del portfolio"""
    if not items:
        return ""
    
    suggestion = "\n\n**Potrebbe essere utile vedere:**"
    for item in items:
        suggestion += f"\n- [{item['title']}]({item['url']})"
    
    return suggestion

# FIX 3: Migliorata formattazione contatti
def format_contact_info():
    """Formatta le informazioni di contatto"""
    contact = STRUCTURED_DATA['contact']
    return (
        f"\n\n**Contatti:**\n"
        f"- Email: {contact['email']}\n"
        f"- Telefono: {contact['phone']}\n"
        f"- [LinkedIn]({contact['linkedin']})"
    )

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    """Endpoint per il chatbot"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Domanda mancante'}), 400
        
        # Carica documenti e prepara contesto
        cv_content = load_documents()
        
        # Costruisci prompt avanzato
        prompt_parts = [
            f"DOMANDA RECRUITER: {question}",
            f"\n### CONTESTO PROFESSIONALE\n{cv_content}"
        ]
        
        # Aggiungi elementi pertinenti
        portfolio_items = get_relevant_portfolio_items(question)
        if portfolio_items:
            prompt_parts.append(f"\n### PORTFOLIO PERTINENTE")
            for item in portfolio_items:
                prompt_parts.append(f"- {item['title']}: Dimostra {', '.join(item.get('skills', []))}")
        
        # Costruisci prompt finale
        user_prompt = "\n".join(prompt_parts)
        
        # Inizializza client Claude
        api_key = os.getenv('CLAUDE_API_KEY')
        if not api_key:
            return jsonify({'error': 'API key non configurata'}), 500
            
        client = anthropic.Anthropic(api_key=api_key)
        
        # Richiedi risposta
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}]
        )
        
        # Estrai e processa la risposta
        bot_response = response.content[0].text
        
        # FIX 4: Correzione formattazione elenchi
        # Sostituisce eventuali punti elenco diversi con '-'
        bot_response = re.sub(r'(\*|\+|\d+\.)\s+', '- ', bot_response)
        
        # Aggiungi elementi contestuali se pertinenti
        if should_include_contact(question):
            bot_response += format_contact_info()
        
        if portfolio_items:
            bot_response += format_portfolio_suggestion(portfolio_items)
        
        # Pulizia finale della risposta
        bot_response = re.sub(r'\n{3,}', '\n\n', bot_response).strip()
        
        return jsonify({'response': bot_response})
        
    except Exception as e:
        logger.exception(f"Errore nel chatbot: {e}")
        return jsonify({'error': 'Errore interno del server'}), 500

@chatbot_bp.route('/preset-questions', methods=['GET'])
def get_preset_questions():
    """Domande preimpostate differenziate"""
    return jsonify({
        'technical': [
            "Quali linguaggi di programmazione padroneggia?",
            "Può descrivere un progetto tecnico complesso?",
            "Quali framework ha utilizzato?",
            "Esperienza con database SQL/NoSQL?",
            "Ha lavorato con tecnologie cloud?"
        ],
        'strengths': [
            "Quali sono i suoi punti di forza professionali?",
            "Come gestisce situazioni stressanti?",
            "Esempi di problem solving creativo?",
            "Come lavora in team multiculturali?",
            "Qual è il suo approccio agli obiettivi?"
        ],
        'experience': [
            "Esperienza più rilevante?",
            "Progetto di cui è più orgoglioso?",
            "Ha gestito progetti cross-funzionali?",
            "Maggiori risultati conseguiti?",
            "Casi di ottimizzazione processi?"
        ],
        'portfolio': [
            "Può mostrare esempi di progetti?",
            "Esempi di lavoro grafico?",
            "Video dimostrativi delle sue capacità?",
            "Progetti open source?",
            "Portfolio creativo?"
        ]
    })

@chatbot_bp.route('/documents', methods=['GET'])
def list_documents():
    """Lista documenti disponibili"""
    if not os.path.exists(DOCUMENTS_FOLDER):
        return jsonify([])
    
    documents = []
    for file in os.listdir(DOCUMENTS_FOLDER):
        path = os.path.join(DOCUMENTS_FOLDER, file)
        if os.path.isfile(path):
            documents.append({
                'name': file,
                'size': os.path.getsize(path),
                'modified': datetime.fromtimestamp(os.path.getmtime(path)).isoformat()
            })
    
    return jsonify(documents)
