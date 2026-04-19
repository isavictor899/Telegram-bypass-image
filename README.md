# TELEGRAM VIEW-ONCE

Intercepts Telegram view-once photos and videos, saves them locally,
and forwards them to your **Saved Messages** — automatically.

## Setup

### 1. Get API credentials
Go to [https://my.telegram.org](https://my.telegram.org) → **API Development Tools**  
Create an app and copy your `API_ID` and `API_HASH`.

### 2. Configure
```bash
cp .env.example .env
# Edit .env with your API_ID and API_HASH
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run
```bash
python main.py
```

On first run you'll be prompted for your **phone number** and the **OTP** sent to Telegram.
After that, a `viewonce_session.session` file is created — you stay logged in automatically.

## How it works

- Connects as your Telegram user account via the official MTProto API (Telethon)
- Listens to all incoming messages
- Detects view-once media by checking `ttl_seconds` on the media object
- Downloads the file before it can expire
- Sends it (without TTL) to your Saved Messages with metadata caption

## Output

Saved files go to `saved_media/` with filenames like:
```
20260419_143022_John.jpg
20260419_143055_Anna.mp4
```

## Notes

- Only works for **your own account** — it only intercepts media sent to you
- The session file (`viewonce_session.session`) keeps you logged in — keep it private
- Add `.env` and `*.session` to `.gitignore` before pushing anywhere
