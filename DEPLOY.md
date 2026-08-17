# Deploying the Webhook (app.py) — Step by Step

This puts the backend code on a real server so Retell can send it call
data. I've already written and tested the code (`app.py`) — this guide is
just the human-only account/deployment steps.

You'll need two free accounts: **GitHub** (to hold the code) and
**Render** (to run it). Both are free for what you need here.

---

### 1. Create a GitHub account (if you don't have one)
- Go to github.com, sign up (free)

### 2. Create a new repository and upload the code
- Click the "+" in the top right → "New repository"
- Name it `hashtag-dispatch` (or anything you like), keep it Public or
  Private (either works), don't add a README (we already have files)
- Click "Create repository"
- On the next page, click **"uploading an existing file"**
- Drag in every file and folder from the `hashtag-dispatch` folder I gave
  you (app.py, requirements.txt, Procfile, the `core/` and
  `integrations/` folders — everything except `SETUP_CHECKLIST.md`,
  `CALL_SCRIPT.md`, and `demo.py`, which aren't needed for deployment but
  don't hurt anything if included)
- Commit the upload (there's a button at the bottom, default message is fine)

### 3. Create a Render account
- Go to render.com, sign up (free tier is enough for this)
- You can sign up directly with your GitHub account, which makes step 4 easier

### 4. Create a new Web Service on Render
- From the Render dashboard, click **"New +"** → **"Web Service"**
- Connect your GitHub account if prompted, then select the
  `hashtag-dispatch` repository you just created
- Render should auto-detect it's a Python app. Confirm these settings:
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `gunicorn app:app`
  - **Instance Type:** Free
- Click **"Create Web Service"**

### 5. Add environment variables (your Twilio credentials)
- Once the service exists, go to its **"Environment"** tab
- Add these (values from your Twilio account — the same ones from
  `integrations/twilio_client.py`'s comments):
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `TWILIO_PHONE_NUMBER` (the 620 number: +16203250515)
  - `OWNER_PHONE` (your own phone number, for escalation alerts)
- Save — this will trigger a redeploy automatically

### 6. Get your live webhook URL
- Once deployed (a few minutes), Render shows a URL at the top of the
  service page, something like:
  `https://hashtag-dispatch.onrender.com`
- Visit `https://hashtag-dispatch.onrender.com/health` in your browser —
  you should see `{"status": "ok", "service": "hashtag-dispatch"}`.
  If you see that, it's live.

### 7. Put the webhook URL into Retell
- In Retell's agent settings, go to **Webhook Settings** (you saw this
  section earlier when checking Post-Call Data Extraction)
- Set the **Agent Level Webhook URL** to:
  `https://hashtag-dispatch.onrender.com/webhook`
- Save

### 8. Test it for real
- Call (620) 325-0515 again
- After the call ends, check Render's **"Logs"** tab for your service —
  you should see the same kind of output you saw in testing (job
  created, technician assigned, SMS lines logged)
- Note: the free Render tier "sleeps" after 15 minutes of no traffic and
  takes ~30-60 seconds to wake up on the next request — fine for a pilot,
  but worth knowing so a test call right after a quiet period might have
  a delay before the webhook fires. Paid tiers ($7/mo) eliminate this if
  it becomes an issue.

---

## One important gap once this is live

Right now `integrations/twilio_client.py` is written but
`core/notifications.py` still just *prints* what it would send instead of
actually calling it. Once your Twilio credentials are in Render's
environment variables, send me a message and I'll make that one small
code change (swapping the placeholder `_send()` function to actually call
`send_sms()`) so texts really go out. That's a 2-minute fix I can do
immediately once you confirm the deployment is live.
