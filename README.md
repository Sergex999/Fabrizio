# Cor Bloom Tracking Assistant

Piccola web app locale che automatizza il flusso di tracking del customer
care di Cor Bloom Jewelry:

L'interfaccia è a due riquadri: a sinistra Amanda incolla la mail del
cliente così com'è, a destra compare il risultato.

1. L'app estrae dal testo incollato il numero d'ordine (pattern `CB12345`)
   e/o l'indirizzo email del cliente.
2. Cerca l'ordine su **Shopify** e recupera nome destinatario e paese di
   destinazione.
3. Cerca il tracking number internazionale su **dianxiaomi** (login
   automatico + ricerca per nome destinatario).
4. Interroga **YunExpress** (yuntrack.com) con quel tracking number e
   recupera il "Last Mile carrier" e il tracking number locale.
5. Cerca l'URL ufficiale del corriere in `app/carriers.json`.
6. Se tutti i dati sono stati trovati, il riquadro destro mostra subito
   l'email finale pronta da copiare. Se un passaggio automatico fallisce,
   mostra invece i campi mancanti in un mini-form **editabile** — il
   flusso non si blocca mai, Amanda completa a mano e genera comunque.

## ⚠️ Nota importante su dianxiaomi e YunExpress

Durante lo sviluppo, sia `dianxiaomi.com` che `yuntrack.com` hanno risposto
con **HTTP 403** quando raggiunti dall'ambiente di sviluppo usato per
scrivere questo tool (probabile blocco anti-bot sull'IP di quella rete).
Per questo motivo:

- I selettori CSS usati in `app/dianxiaomi_client.py` e
  `app/yunexpress_client.py` sono **placeholder basati sulla descrizione
  del flusso**, non verificati contro il DOM reale delle pagine autenticate.
- Al primo utilizzo reale, esegui l'app dalla rete/macchina di Amanda con
  `PLAYWRIGHT_HEADLESS=false` nel file `.env`: si aprirà una finestra del
  browser e potrai vedere dove l'automazione eventualmente fallisce nel
  trovare un campo, per poi correggere il selettore corrispondente nei due
  file sopra.
- Se uno dei due step fallisce (eccezione o elemento non trovato), l'app
  **non si interrompe**: mostra un avviso nella pagina di revisione e
  lascia il campo vuoto perché Amanda lo compili a mano, esattamente come
  nel flusso manuale attuale.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

cp .env.example .env
# poi modifica .env con:
#   SHOPIFY_SHOP_DOMAIN
#   SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET  (da Dev Dashboard > Settings > Credentials,
#     con scope read_orders configurato sull'app)
#   DIANXIAOMI_USERNAME / DIANXIAOMI_PASSWORD
```

L'app ottiene l'Admin API access token in automatico ad ogni avvio tramite il
[client credentials grant](https://shopify.dev/docs/apps/build/authentication-authorization/access-tokens/token-exchange)
di Shopify (`app/shopify_client.py::fetch_access_token`) — le app custom create
dalla Dev Dashboard non mostrano più un token statico da "rivelare" nell'admin
del negozio, quindi bastano Client ID e Client Secret.

## Avvio

```bash
uvicorn app.main:app --reload
```

Apri http://127.0.0.1:8000/

## Creare l'eseguibile per Windows

Per far girare l'app sul PC di Amanda senza installare Python, su una macchina
**Windows** con Python 3.10+ installato:

```
build_exe.bat
```

Lo script crea un ambiente di build isolato (`.venv-build`), installa le
dipendenze e PyInstaller, scarica Chromium dentro il pacchetto playwright
(`PLAYWRIGHT_BROWSERS_PATH=0`, così finisce dentro il pacchetto) e compila
usando `tracking_assistant.spec`.

Risultato: la cartella `dist\CorBloomTrackingAssistant\` (~500 MB, Chromium
incluso). **Va copiata tutta**, non solo il file `.exe`.

Primo avvio sul PC di destinazione:

1. Apri il file `.env` dentro la cartella e inserisci le credenziali Shopify.
2. Lancia una volta `CorBloomTrackingAssistant.exe --setup-session` per il
   login manuale a dianxiaomi (captcha): salva `dianxiaomi_state.json`
   accanto all'eseguibile.
3. Poi basta un doppio clic su `CorBloomTrackingAssistant.exe`: parte il
   server locale e si apre il browser sulla pagina dell'app. La finestra nera
   del terminale va lasciata aperta finché l'app è in uso.

La build **deve** essere fatta su Windows: PyInstaller non fa
cross-compilazione, quindi un `.exe` non si può produrre da Linux o macOS.

## Test

I test coprono la logica pura (generazione email, mapping corriere →
URL ufficiale), che non dipende da servizi esterni:

```bash
pytest
```

## Aggiungere un nuovo corriere

Aggiungi una riga in `app/carriers.json` con il nome del corriere (minuscolo)
e l'URL ufficiale di tracking, es.:

```json
"parcelforce": "https://www.parcelforce.com"
```

## Struttura

```
build_exe.bat           # build dell'eseguibile Windows
tracking_assistant.spec # configurazione PyInstaller
run_app.py              # avvio dell'app impacchettata (server + browser)
app/
  main.py               # FastAPI: pagine e orchestrazione del flusso
  config.py             # lettura variabili da .env
  paths.py              # percorsi validi sia da sorgente sia da .exe
  shopify_client.py     # ricerca ordine su Shopify Admin API
  dianxiaomi_client.py  # Playwright: login + ricerca tracking per destinatario
  yunexpress_client.py  # Playwright: risoluzione Last Mile carrier
  carriers.py / .json   # mapping corriere -> URL ufficiale di tracking
  email_template.py     # template email esatto richiesto
  templates/            # pagine HTML (form, revisione, risultato)
tests/                  # test su email_template e carriers
```
