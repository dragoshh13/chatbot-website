# Chatbot Website - Dragoș Baicu

Applicazione Flask che integra un chatbot Claude nel sito web personale di Dragoș Baicu.

## Caratteristiche

- **Chatbot AI**: Powered by Claude API per rispondere a domande professionali
- **Design minimalista**: Interfaccia bianco/nero stile social media
- **Responsive**: Ottimizzato per desktop e mobile
- **Gestione documenti**: Legge automaticamente CV e documenti dalla cartella `/documents`
- **Domande preimpostate**: Pulsanti con domande frequenti per i recruiter

## Struttura del Progetto

```
chatbot_website/
├── src/
│   ├── main.py              # Applicazione Flask principale
│   ├── routes/
│   │   ├── chatbot.py       # API endpoints per il chatbot
│   │   └── user.py          # Endpoints utente (template)
│   ├── models/
│   │   └── user.py          # Modelli database (template)
│   └── static/
│       ├── index.html       # Pagina principale (portfolio video)
│       └── about.html       # Pagina chatbot
├── documents/               # Cartella per CV e documenti
│   └── sample_cv.txt        # File di esempio
├── requirements.txt         # Dipendenze Python
└── README.md               # Questa documentazione
```

## Installazione e Setup

### 1. Requisiti
- Python 3.11+
- Chiave API Claude (Anthropic)

### 2. Installazione dipendenze
```bash
pip install -r requirements.txt
```

### 3. Configurazione API Key
Imposta la variabile d'ambiente con la tua chiave API Claude:
```bash
export CLAUDE_API_KEY="your_claude_api_key_here"
```

### 4. Avvio dell'applicazione
```bash
python src/main.py
```

L'applicazione sarà disponibile su `http://localhost:5000`

## Deployment su SiteGround

### Preparazione file
1. Carica tutti i file del progetto sul server SiteGround
2. Installa le dipendenze Python sul server
3. Configura la variabile d'ambiente `CLAUDE_API_KEY`

### Gestione documenti
I documenti (CV, lettere di presentazione, ecc.) vanno caricati nella cartella `/documents` usando:
- **File Manager SiteGround**: Accedi al pannello SiteGround → File Manager
- **FTP/SFTP**: Usa client come FileZilla

Formati supportati:
- PDF (.pdf)
- Word (.docx)
- Testo (.txt)

### Configurazione server
- L'applicazione ascolta su `0.0.0.0:5000` per permettere accesso esterno
- CORS è abilitato per tutte le route
- Non richiede configurazioni specifiche di IP o Host

## API Endpoints

### `/api/chat` (POST)
Invia una domanda al chatbot
```json
{
  "question": "Quali sono le tue competenze?"
}
```

### `/api/preset-questions` (GET)
Ottieni le domande preimpostate
```json
{
  "questions": ["Domanda 1", "Domanda 2", ...]
}
```

### `/api/documents` (GET)
Lista i documenti disponibili (per debug)

## Personalizzazione

### Aggiungere nuove domande preimpostate
Modifica l'array `questions` in `src/routes/chatbot.py`:
```python
questions = [
    "Nuova domanda qui",
    # ... altre domande
]
```

### Modificare il design
Il CSS è contenuto direttamente in `src/static/about.html` per facilità di deployment.

### Aggiungere nuovi formati di documento
Estendi le funzioni di lettura in `src/routes/chatbot.py` per supportare altri formati.

## Sicurezza

- L'API key Claude deve essere mantenuta segreta
- I documenti sono accessibili solo tramite API backend
- Non ci sono endpoint pubblici per il caricamento file (sicurezza)

## Supporto

Per problemi o domande, contatta:
- Email: dragos.baicu1@gmail.com
- LinkedIn: linkedin.com/in/dragos-baicu-486a4a248

