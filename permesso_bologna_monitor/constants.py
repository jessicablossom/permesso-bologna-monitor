DEFAULT_QUESTURA_URL = "https://www.questura.bologna.it/node/2"
DEFAULT_TIMEZONE = "Europe/Rome"

REQUEST_TIMEOUT_SECONDS = 30
SMTP_TIMEOUT_SECONDS = 30
USER_AGENT = "PermessoBolognaMonitor/1.0 (personal use; daily status check)"

QUESTURA_FORM_ID = "qp-verifica-ritiro-form"
FIELD_REGISTERED_MAIL = "codraccomandata"
FIELD_PRACTICE_CODE = "codpratica"
FIELD_BIRTH_DAY = "dng"
FIELD_BIRTH_MONTH = "dnm"
FIELD_BIRTH_YEAR = "dna"
FIELD_SUBMIT = "op"

QUESTURA_SUBMIT_VALUE = "Prenota il ritiro"
QUESTURA_NOT_READY_MESSAGE = (
    "Non e pronto alcun permesso di soggiorno corrispondente ai dati inseriti."
)
QUESTURA_READY_MESSAGES = (
    "Il permesso di soggiorno e pronto per il ritiro",
    "permesso di soggiorno pronto per il ritiro",
    "puoi ritirare il permesso di soggiorno",
)
