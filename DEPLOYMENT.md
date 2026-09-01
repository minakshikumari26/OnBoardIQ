# OnBoardIQ — Deployment Guide

This guide walks through deploying OnBoardIQ to free-tier cloud services so you have a live URL to share.

**Stack:**
- **Postgres** → [Neon](https://neon.tech) (free tier, no card required)
- **Backend (FastAPI)** → [Render](https://render.com) (free tier)
- **UI (Streamlit)** → [Streamlit Community Cloud](https://streamlit.io/cloud) (free)

Total setup time: **~30 minutes**.

---

## 1. Provision Postgres on Neon

1. Sign up at [neon.tech](https://neon.tech) using GitHub.
2. Create a new project — pick any region close to you.
3. From the dashboard, copy the connection string. It looks like:
   ```
   postgresql://user:password@ep-abc-123.us-east-2.aws.neon.tech/neondb
   ```
4. Extract these fields for later:
   - `DB_HOST` → the `ep-abc-123.us-east-2.aws.neon.tech` part
   - `DB_USER`, `DB_PASSWORD`, `DB_NAME` → from the URL
   - `DB_PORT` → `5432`

5. In Neon's SQL Editor, run the schema:
   ```sql
   -- Paste the contents of backend/db/schema.sql
   ```

---

## 2. Deploy the backend on Render

1. Push your code to a GitHub repo (if not already).
2. Sign up at [render.com](https://render.com) using GitHub.
3. Click **New → Web Service** and connect your repo.
4. Configure:
   - **Environment**: Docker
   - **Dockerfile Path**: `Dockerfile`
   - **Instance Type**: Free
5. Under **Environment Variables**, add:
   ```
   DB_HOST       = <from Neon>
   DB_NAME       = <from Neon>
   DB_USER       = <from Neon>
   DB_PASSWORD   = <from Neon>
   DB_PORT       = 5432
   GROQ_API_KEY  = <your Groq key>
   ```
6. Click **Create Web Service**. First build takes ~5 minutes.
7. Once deployed, note the URL (e.g. `https://onboardiq-backend.onrender.com`).

Test it: `curl https://onboardiq-backend.onrender.com/` should return
```
{"message": "OnBoardIQ API running"}
```

---

## 3. Deploy the UI on Streamlit Community Cloud

1. Sign up at [streamlit.io/cloud](https://streamlit.io/cloud) using GitHub.
2. Click **New app** → pick your repo → set:
   - **Main file path**: `ui/app.py`
3. Under **Advanced settings → Secrets**, add:
   ```toml
   API_URL = "https://onboardiq-backend.onrender.com"
   ```
4. Deploy. First build takes ~2 minutes.
5. Your app is live at `https://<your-app-name>.streamlit.app`.

---

## 4. Verify end-to-end

1. Open your Streamlit URL.
2. Fill out the onboarding form with a valid PAN and upload any test image containing text.
3. Submit. You should see:
   - Decision banner (Approved / Rejected / Needs Review)
   - Agent status chips (KYC, Document, Compliance, Risk)
   - AI-generated explanation (if `GROQ_API_KEY` was set)
4. Navigate to the Admin Dashboard page — the new application should appear.

---

## Free tier limitations to know

| Service | Free tier limit | Impact |
|---|---|---|
| Render (backend) | 750 hrs/month, sleeps after 15 min inactivity | Cold start takes ~30s |
| Neon (Postgres) | 0.5 GB storage | Plenty for a demo |
| Streamlit Cloud | 1 GB RAM, 1 CPU | Fine for this app |
| Groq | Free tier is generous but rate-limited | If you hit limits, the pipeline degrades to no-LLM mode |

---

## Troubleshooting

**Backend cold-starts are slow on Render free tier.** First request after 15 min inactivity takes ~30s. Second and subsequent requests are fast. Consider [UptimeRobot](https://uptimerobot.com/) to ping every 10 min if you want it always warm.

**UI can't reach backend.** Check that `API_URL` in Streamlit secrets matches your Render URL exactly (with `https://`, no trailing slash).

**"Tesseract not found" in Render logs.** The `Dockerfile` installs `tesseract-ocr` via apt. If missing, confirm Render is using Docker (not their default Python builder).

**Groq rate limit hit.** The pipeline still works — the `explain` node just returns an empty string. Users see the decision without the AI-generated message.
