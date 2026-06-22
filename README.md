# permesso-bologna-monitor

Daily monitor for an already-started permesso di soggiorno procedure. It checks
whether the pickup notice is ready at Questura Bologna and sends the result by
email.

This project does not request a permesso di soggiorno, manage an application,
book appointments, or contact Questura. It only tracks the public pickup-status
page after the procedure has already been started.

The check uses the public Questura Bologna status page:
https://www.questura.bologna.it/node/2

## Local Usage

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m permesso_bologna_monitor
```

Fill `.env` with your data before running the monitor.

## GitHub Actions Secrets

Configure these secrets in `Settings -> Secrets and variables -> Actions`:

| Secret | Required | Description |
|--------|-----------|-------------|
| `QUESTURA_PRACTICE_CODE` | Yes | Practice code, for example `08BO012345` |
| `QUESTURA_BIRTH_DATE` | Yes | Birth date in `dd/mm/yyyy` or `dd-mm-yyyy` format |
| `SMTP_USER` | Yes | Sender email |
| `SMTP_PASSWORD` | Yes | SMTP app password |
| `NOTIFY_EMAIL` | No | Recipient email; defaults to `SMTP_USER` |

The `Permesso Bologna Monitor` workflow runs every day at 09:00
`Europe/Rome` using a timezone-aware GitHub Actions cron schedule. It can also
be run manually from GitHub Actions.

## Result

An email is always sent:

- negative when Questura shows the confirmed "not ready" message;
- unknown for any other response, including a possible ready-for-pickup message,
  because the positive text has not been confirmed yet.

## Italiano

Monitor giornaliero per una pratica di permesso di soggiorno gia avviata.
Verifica se l'avviso per il ritiro e disponibile presso la Questura di Bologna
e invia il risultato via email.

Questo progetto non richiede un permesso di soggiorno, non gestisce una pratica,
non prenota appuntamenti e non contatta la Questura. Serve solo a controllare la
pagina pubblica dello stato di ritiro dopo che la pratica e gia stata avviata.

La verifica usa la pagina pubblica dello stato di ritiro della Questura di
Bologna:
https://www.questura.bologna.it/node/2

### Uso Locale

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m permesso_bologna_monitor
```

Compila `.env` con i tuoi dati prima di eseguire il monitor.

### Secret Di GitHub Actions

Configura questi secret in `Settings -> Secrets and variables -> Actions`:

| Secret | Obbligatorio | Descrizione |
|--------|--------------|-------------|
| `QUESTURA_PRACTICE_CODE` | Si | Codice pratica, per esempio `08BO012345` |
| `QUESTURA_BIRTH_DATE` | Si | Data di nascita nel formato `dd/mm/yyyy` o `dd-mm-yyyy` |
| `SMTP_USER` | Si | Email mittente |
| `SMTP_PASSWORD` | Si | Password applicativa SMTP |
| `NOTIFY_EMAIL` | No | Email destinatario; se assente usa `SMTP_USER` |

Il workflow `Permesso Bologna Monitor` viene eseguito ogni giorno alle 09:00
`Europe/Rome` con uno schedule cron di GitHub Actions con timezone. Puo anche
essere avviato manualmente da GitHub Actions.

### Risultato

Viene sempre inviata una email:

- negativa quando la Questura mostra il messaggio confermato di "non pronto";
- sconosciuta per qualsiasi altra risposta, incluso un possibile messaggio di
  disponibilita al ritiro, perche il testo positivo non e ancora confermato.

## Tests

```bash
python -m unittest discover -s tests -v
```
