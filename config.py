import os

# ====================================================
# IMPORTANT: Set these as Environment Variables on Railway!
# Do NOT hardcode tokens here — this file is git-ignored.
# ====================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "6420210658"))
ABA_QR_URL = "payment_qr.jpg"          # local path (or set as env var if needed)
WELCOME_IMAGE_URL = "image copy.png"   # local path (or set as env var if needed)
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/your_channel")
