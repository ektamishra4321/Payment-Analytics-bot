# Razorpay Analytics Bot — Setup Guide

Daily morning summary of your Razorpay account sent to Microsoft Teams at 9 AM IST.
Covers: Collections, Failed Payments, Refunds, Settlements.

---

## What you need before starting

| Item | Where to get it |
|------|----------------|
| Razorpay API Key ID | Razorpay Dashboard → Settings → API Keys |
| Razorpay API Key Secret | Same place — copy it immediately, shown only once |
| Microsoft Teams Incoming Webhook URL | Teams channel → Connectors → Incoming Webhook |
| Python 3.10+ installed | python.org |
| Heroku or Railway account (for deployment) | heroku.com or railway.app |

---

## Step 1 — Get your Razorpay API Keys

1. Log in to dashboard.razorpay.com
2. Go to **Settings → API Keys**
3. Click **Generate Test Key** (use Test mode first to verify the bot)
4. Copy the **Key ID** (starts with `rzp_test_...`) and **Key Secret**
5. Keep these safe — treat them like passwords

> When ready for live data, generate a **Live Key** the same way.

---

## Step 2 — Create Microsoft Teams Incoming Webhook

1. Open Microsoft Teams
2. Go to the **channel** where you want the daily summary
3. Click the **three dots (...)** next to the channel name → **Connectors**
4. Search for **"Incoming Webhook"** → click **Configure**
5. Give it a name like `Razorpay Bot` and upload a logo if you like
6. Click **Create** → **Copy** the webhook URL shown
7. Save that URL — it looks like: `https://xyz.webhook.office.com/webhookb2/...`

---

## Step 3 — Set up the project locally

```bash
# Create a folder
mkdir razorpay-analytics-bot
cd razorpay-analytics-bot

# Copy all 4 project files into this folder:
# razorpay_analytics_bot.py
# requirements.txt
# Procfile
# runtime.txt

# Create a virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Step 4 — Set environment variables

**On your local machine (Mac/Linux):**
```bash
export RAZORPAY_KEY_ID="rzp_test_XXXXXXXXXXXXXXXX"
export RAZORPAY_KEY_SECRET="XXXXXXXXXXXXXXXXXXXXXXXX"
export TEAMS_WEBHOOK_URL="https://xyz.webhook.office.com/webhookb2/..."
```

**On Windows:**
```cmd
set RAZORPAY_KEY_ID=rzp_test_XXXXXXXXXXXXXXXX
set RAZORPAY_KEY_SECRET=XXXXXXXXXXXXXXXXXXXXXXXX
set TEAMS_WEBHOOK_URL=https://xyz.webhook.office.com/webhookb2/...
```

---

## Step 5 — Test it locally

Open `razorpay_analytics_bot.py` and find this line near the bottom:

```python
# Uncomment below to test immediately without waiting for schedule:
# job()
```

Remove the `#` before `job()` so it reads:
```python
job()
```

Then run:
```bash
python razorpay_analytics_bot.py
```

You should see output like:
```
Razorpay Analytics Bot — 24 Apr 2025 09:00 IST
==================================================
  Fetching collections...
  Fetching failed payments...
  Fetching refunds...
  Fetching settlements...
Sending to Microsoft Teams...
  Sent successfully at 09:00:12 IST

Summary:
  Collections : ₹1,24,500.00 (47 txns)
  Failures    : 3 (6.0% rate)
  Refunds     : ₹2,200.00 (2 refunds)
  Settlement  : Last ₹98,000.00 on 23 Apr 2025
```

Check your Teams channel — the card should appear within seconds.

Once confirmed, put `# job()` back (re-comment it) before deploying.

---

## Step 6 — Deploy to Railway (recommended — free tier available)

1. Go to **railway.app** and sign up with GitHub
2. Click **New Project → Deploy from GitHub repo**
3. Push your project folder to a GitHub repository first:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/razorpay-bot.git
   git push -u origin main
   ```
4. Railway will auto-detect the `Procfile` and deploy
5. Go to **Variables** tab in Railway → add your 3 environment variables:
   - `RAZORPAY_KEY_ID`
   - `RAZORPAY_KEY_SECRET`
   - `TEAMS_WEBHOOK_URL`
6. Click **Deploy** — the bot is now live and will run every day at 9 AM IST

---

## Step 7 — Switch to Live mode

When you're satisfied with test data:
1. Go to Razorpay Dashboard → Settings → API Keys → **Generate Live Key**
2. Update `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` in Railway variables
3. Redeploy — now pulling real payment data

---

## Customisation options

| What to change | Where in the code |
|---------------|------------------|
| Send time (default 9 AM) | `scheduler.add_job(job, "cron", hour=9, minute=0)` |
| Number of payments fetched | `"count": 100` in each fetch function |
| Failure rate alert threshold | `if failures["failure_rate"] > 10` (currently 10%) |
| Add Telegram alongside Teams | Copy `send_to_telegram()` from your old bot |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `401 Unauthorized` from Razorpay | Wrong API key or secret — double-check |
| Teams card not appearing | Webhook URL expired or wrong — regenerate in Teams |
| All metrics show 0 | You're in Test mode with no test transactions — create one in Razorpay test dashboard |
| `KeyError` on settlements | Your Razorpay plan may not include settlement recon API — comment out `fetch_settlements()` |
