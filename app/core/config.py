from dotenv import load_dotenv
load_dotenv()

import os

ENTRA_TENANT_ID = os.getenv("ENTRA_TENANT_ID")
ENTRA_CLIENT_ID = os.getenv("ENTRA_CLIENT_ID")
ENTRA_CLIENT_SECRET = os.getenv("ENTRA_CLIENT_SECRET")
ENTRA_REDIRECT_URI = os.getenv("ENTRA_REDIRECT_URI")
ENTRA_AUTHORITY = os.getenv("ENTRA_AUTHORITY")
SESSION_SECRET = os.getenv("SESSION_SECRET")
