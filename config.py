
import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ABA_QR_URL = "payment_qr.jpg"
WELCOME_IMAGE_URL = "image copy.png"
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/your_channel")
_admin_ids_env = os.getenv("ADMIN_IDS", "")
if _admin_ids_env:
    ADMIN_IDS = [int(x.strip()) for x in _admin_ids_env.split(",") if x.strip()]
else:
    ADMIN_IDS = [ADMIN_ID]

# Ensure main ADMIN_ID is always in the list
if ADMIN_ID not in ADMIN_IDS:
    ADMIN_IDS.insert(0, ADMIN_ID)
