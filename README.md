# 📚 Bookshop.org Social Media Automator

Post book recommendations to **Instagram**, **Bluesky**, and **TikTok** from your
Bookshop.org affiliate shop — with auto-generated BookTok-style slide images.

---

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Copy the env template and fill in your credentials
cp .env.example .env
# edit .env with your API keys

# 3. Add your books to books.csv (or edit the sample data)

# 4. Preview a post without publishing
python main.py --dry-run

# 5. Post for real
python main.py
```

---

## Usage

```
python main.py [options]

Options:
  --mode {random,curated,seasonal,new}   How to pick the book (default: random)
  --genre GENRE                          Filter by genre
  --book ISBN                            Post a specific book by ISBN
  --platforms {bluesky,instagram,tiktok,all} [...]
                                         Which platforms (default: all)
  --dry-run                              Preview without posting
  --no-mark                              Don't update last_posted in books.csv
```

### Examples

```bash
# Post a random book to all platforms
python main.py

# Post a curated pick — sci-fi only
python main.py --mode curated --genre sci-fi

# Post seasonally appropriate book (uses current month)
python main.py --mode seasonal

# Post recently added books you haven't promoted yet
python main.py --mode new

# Post a specific book by ISBN
python main.py --book 9780765389220

# Bluesky only
python main.py --platforms bluesky

# Preview everything before committing
python main.py --dry-run
```

---

## books.csv Reference

| Column | Description |
|--------|-------------|
| `title` | Book title |
| `author` | Author name |
| `isbn` | 13-digit ISBN |
| `genre` | `mystery`, `thriller`, `sci-fi`, `horror`, `literary`, `romance` |
| `blurb` | 1-2 sentence description (keep under 150 chars for best results) |
| `cover_url` | Direct image URL — leave blank to auto-fetch from Open Library |
| `affiliate_url` | Full Bookshop.org URL — leave blank to auto-build from ISBN |
| `curated` | `true` if this is a hand-picked featured book |
| `added_date` | `YYYY-MM-DD` when you added it |
| `seasonal_tags` | Space-separated: `spring summer fall winter halloween holiday` |
| `last_posted` | Auto-filled by script — don't edit manually |

---

## Platform Setup

### Bluesky (easiest)
1. Go to **Settings → Privacy and Security → App Passwords**
2. Create a new App Password (name it something like "book-bot")
3. Add to `.env`:
   ```
   BLUESKY_HANDLE=yourhandle.bsky.social
   BLUESKY_PASSWORD=xxxx-xxxx-xxxx-xxxx
   ```

---

### Instagram

Instagram's Graph API requires more setup, but it's free.

**One-time setup:**
1. Convert your Instagram account to **Business** or **Creator** (free, in app settings)
2. Link it to a **Facebook Page** (you can create a page just for this)
3. Go to [developers.facebook.com](https://developers.facebook.com)
4. Create an app → choose **Business** type
5. Add the **Instagram Graph API** product to your app
6. In **Graph API Explorer**, select your app and generate a User Access Token
   with scopes: `instagram_basic`, `instagram_content_publish`, `pages_read_engagement`
7. Exchange for a long-lived token (valid 60 days):
   ```
   GET https://graph.facebook.com/v18.0/oauth/access_token
     ?grant_type=fb_exchange_token
     &client_id=YOUR_APP_ID
     &client_secret=YOUR_APP_SECRET
     &fb_exchange_token=YOUR_SHORT_TOKEN
   ```
8. Get your Instagram User ID:
   ```
   GET https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_TOKEN
   ```
   Then: `GET https://graph.facebook.com/v18.0/{page_id}?fields=instagram_business_account&access_token=...`

**Imgur (for image hosting):**
Instagram requires a public URL — we use Imgur as a free intermediary.
1. Go to [api.imgur.com/oauth2/addclient](https://api.imgur.com/oauth2/addclient)
2. Choose **"Anonymous usage without user authorization"**
3. Copy the **Client ID** to your `.env`

Add to `.env`:
```
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_USER_ID=...
IMGUR_CLIENT_ID=...
```

**Token refresh** (do this every ~50 days):
```bash
curl "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=CURRENT_TOKEN"
```

---

### TikTok (most involved — takes a few days for app review)

TikTok requires an approved developer app to use the Content Posting API.

1. Go to [developers.tiktok.com](https://developers.tiktok.com) → **Manage Apps**
2. Create an app, fill in details (use your Bookshop affiliate site as the URL)
3. Under **Products**, add **Content Posting API**
4. Request these scopes: `video.upload`, `video.publish`
5. Submit for review — TikTok typically approves in 1-3 business days
6. Once approved, run the OAuth 2.0 flow to get your access token:

```
# Authorization URL (paste in browser while logged into TikTok):
https://www.tiktok.com/v2/auth/authorize/
  ?client_key=YOUR_CLIENT_KEY
  &scope=video.upload,video.publish
  &response_type=code
  &redirect_uri=YOUR_REDIRECT_URI
  &state=random_string
```

Then exchange the code for a token:
```bash
curl -X POST "https://open.tiktokapis.com/v2/oauth/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_key=...&client_secret=...&code=...&grant_type=authorization_code&redirect_uri=..."
```

The response includes `access_token` (valid 24 hours) and `refresh_token` (valid 365 days).

Add to `.env`:
```
TIKTOK_ACCESS_TOKEN=...
```

**Refreshing your TikTok token:**
```bash
curl -X POST "https://open.tiktokapis.com/v2/oauth/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_key=...&client_secret=...&grant_type=refresh_token&refresh_token=YOUR_REFRESH_TOKEN"
```

---

## Fonts (optional but recommended)

The image generator works without custom fonts, but looks much better with them.
Download free fonts and put the `.ttf` files in the `fonts/` folder:

- **Inter** (recommended): [fonts.google.com/specimen/Inter](https://fonts.google.com/specimen/Inter)
  - Save as `fonts/Inter-Regular.ttf` and `fonts/Inter-Bold.ttf`

---

## Automating with cron

Post automatically (e.g., every Tuesday and Friday at 10am):

```bash
# Edit your crontab
crontab -e

# Add this line (adjust path):
0 10 * * 2,5 cd /path/to/bookshop-automator && python main.py --mode curated >> logs/post.log 2>&1
```

---

## Bookshop.org Affiliate ID

Your affiliate ID is the short code in your store URL or affiliate links.
For example, if your link is `https://bookshop.org/a/abc123/9780765389220`,
your affiliate ID is `abc123`.

Set it in `.env` as `BOOKSHOP_AFFILIATE_ID=abc123`.

If you leave `affiliate_url` blank in `books.csv`, the script will auto-build
links in the format `https://bookshop.org/a/{your_id}/{isbn}`.
