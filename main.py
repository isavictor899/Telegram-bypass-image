"""
Telegram View-Once Media Interceptor
-------------------------------------
Intercepts view-once photos/videos, saves them locally,
and forwards them to your Saved Messages.

Setup:
  1. Get API_ID and API_HASH from https://my.telegram.org
  2. Copy .env.example to .env and fill in your credentials
  3. pip install -r requirements.txt
  4. python main.py  (first run will ask for your phone number + OTP)
"""

import os
import asyncio
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import (
    MessageMediaPhoto,
    MessageMediaDocument,
)

load_dotenv()

API_ID   = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

SAVE_DIR = Path("saved_media")
SAVE_DIR.mkdir(exist_ok=True)

# Session file is stored locally so you only log in once
client = TelegramClient("viewonce_session", API_ID, API_HASH)


def is_view_once(media) -> bool:
    """Return True if the media has a TTL (i.e. it's view-once)."""
    return bool(getattr(media, "ttl_seconds", None))


def get_extension(media) -> str:
    if isinstance(media, MessageMediaPhoto):
        return ".jpg"
    if isinstance(media, MessageMediaDocument):
        mime = getattr(media.document, "mime_type", "")
        mime_map = {
            "video/mp4":       ".mp4",
            "video/quicktime": ".mov",
            "image/jpeg":      ".jpg",
            "image/png":       ".png",
            "image/gif":       ".gif",
        }
        return mime_map.get(mime, ".bin")
    return ".bin"


@client.on(events.NewMessage)
async def on_message(event):
    msg = event.message

    # Only care about messages with view-once media
    if not msg.media or not is_view_once(msg.media):
        return

    # Who sent it?
    sender = await event.get_sender()
    sender_name = getattr(sender, "first_name", "") or getattr(sender, "username", "unknown")
    chat = await event.get_chat()
    chat_title = getattr(chat, "title", None) or getattr(chat, "first_name", "DM")

    print(f"\n[!] View-once media detected")
    print(f"    From : {sender_name}")
    print(f"    Chat : {chat_title}")

    # 1. Save locally
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = get_extension(msg.media)
    filename = SAVE_DIR / f"{timestamp}_{sender_name}{ext}"

    saved_path = await client.download_media(msg.media, file=str(filename))
    print(f"    Saved: {saved_path}")

    # 2. Forward to Saved Messages (send as file so it has no TTL)
    caption = (
        f"📸 View-once from **{sender_name}**\n"
        f"💬 Chat: {chat_title}\n"
        f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await client.send_file(
        "me",                   # "me" = your own Saved Messages
        saved_path,
        caption=caption,
        force_document=False,   # send as photo/video, not raw file
    )
    print(f"    Forwarded to Saved Messages ✓")


async def main():
    print("=" * 45)
    print("  Telegram View-Once Interceptor")
    print("=" * 45)
    await client.start()
    me = await client.get_me()
    print(f"\n[✓] Logged in as: {me.first_name} (@{me.username})")
    print(f"[*] Saving media to: {SAVE_DIR.resolve()}")
    print(f"[*] Listening for view-once media...\n")
    print("    Press Ctrl+C to stop.\n")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
