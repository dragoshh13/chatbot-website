# Guida Deployment SiteGround - Chatbot Website

## Passo 1: Preparazione File

### 1.1 File da caricare su SiteGround
Carica tutti questi file e cartelle sul tuo hosting SiteGround:

```
chatbot_website/
├── src/                     # Cartella completa
├── documents/               # Cartella per i tuoi documenti
├── requirements.txt         # Lista dipendenze
├── README.md               # Documentazione
└── DEPLOYMENT_GUIDE.md     # Questa guida
```

### 1.2 Posizione sul server
- Carica i file nella cartella principale del tuo dominio (solitamente `public_html/`)
- Assicurati che la struttura delle cartelle sia mantenuta

## Passo 2: Configurazione Python su SiteGround

### 2.1 Attivazione Python
1. Accedi al **cPanel di SiteGround**
2. Cerca **"Python App"** o **"Python Selector"**
3. Crea una nuova applicazione Python:
   - **Versione Python**: 3.11 o superiore
   - **Cartella applicazione**: `/chatbot_website`
   - **URL**: il tuo dominio principale

### 2.2 Installazione dipendenze
Nel terminale SSH di SiteGround (o tramite interfaccia Python App):
```bash
pip install -r requirements.txt
```

## Passo 3: Configurazione API Key Claude

### 3.1 Impostazione variabile d'ambiente
Nel pannello Python App di SiteGround:
1. Vai alla sezione **"Environment Variables"**
2. Aggiungi una nuova variabile:
   - **Nome**: `CLAUDE_API_KEY`
   - **Valore**: la tua chiave API Claude reale

### 3.2 Verifica API Key
La tua chiave API Claude deve essere ottenuta da:
- Sito web: https://console.anthropic.com/
- Sezione: API Keys

## Passo 4: Configurazione File di Avvio

### 4.1 File startup
SiteGround potrebbe richiedere un file di avvio specifico. Crea `passenger_wsgi.py` nella root:

```python
import sys
import os

# Aggiungi il percorso del progetto
sys.path.insert(0, os.path.dirname(__file__))

# Importa l'applicazione Flask
from src.main import app

# Configura l'applicazione per il deployment
application = app

if __name__ == "__main__":
    application.run()
```

## Passo 5: Gestione Documenti

### 5.1 Caricamento documenti via File Manager
1. Accedi al **File Manager** di SiteGround
2. Naviga alla cartella `chatbot_website/documents/`
3. Carica i tuoi file:
   - CV aggiornato (PDF, DOCX, o TXT)
   - Lettere di presentazione
   - Altri documenti professionali

### 5.2 Formati supportati
- **PDF**: `.pdf` (raccomandato per CV)
- **Word**: `.docx`
- **Testo**: `.txt`

### 5.3 Aggiornamento documenti
Per aggiornare i documenti:
1. Elimina i vecchi file dalla cartella `documents/`
2. Carica i nuovi file
3. Il chatbot leggerà automaticamente i nuovi documenti

## Passo 6: Test e Verifica

### 6.1 Test di funzionamento
1. Visita il tuo sito web
2. Clicca su **"About"** per accedere al chatbot
3. Prova le domande preimpostate
4. Testa l'input manuale

### 6.2 Risoluzione problemi comuni

**Problema**: Errore 500 - Internal Server Error
- **Soluzione**: Controlla che l'API key sia configurata correttamente
- **Verifica**: Controlla i log di errore nel cPanel

**Problema**: Chatbot risponde "Errore interno del server"
- **Soluzione**: Verifica che l'API key Claude sia valida e attiva
- **Verifica**: Controlla il credito disponibile nel tuo account Anthropic

**Problema**: "Nessun documento disponibile"
- **Soluzione**: Verifica che i file siano nella cartella `documents/`
- **Verifica**: Controlla i permessi dei file (devono essere leggibili)

## Passo 7: Manutenzione

### 7.1 Aggiornamento documenti
- Usa il File Manager di SiteGround per sostituire i file nella cartella `documents/`
- Non serve riavviare l'applicazione

### 7.2 Monitoraggio
- Controlla periodicamente i log di accesso nel cPanel
- Verifica il consumo API Claude nel dashboard Anthropic

### 7.3 Backup
- Fai backup regolari della cartella `documents/`
- Salva una copia del codice sorgente

## Passo 8: Personalizzazione Foto Profilo

### 8.1 Aggiungere la tua foto
1. Carica la tua foto nella cartella `src/static/`
2. Rinomina il file in `profile-photo.jpg`
3. La foto apparirà automaticamente nella pagina chatbot

### 8.2 Formato consigliato
- **Formato**: JPG o PNG
- **Dimensioni**: 200x200 pixel (quadrata)
- **Peso**: Massimo 500KB

## Supporto Tecnico

### Contatti SiteGround
- **Chat**: Disponibile 24/7 nel cPanel
- **Ticket**: Sistema di supporto integrato

### Documentazione Claude
- **API Docs**: https://docs.anthropic.com/
- **Console**: https://console.anthropic.com/

---

**Nota importante**: Mantieni sempre segreta la tua API key Claude e non condividerla mai pubblicamente.

