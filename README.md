# CPI vs division performance (linear regression)

Minimal Python example: pull CPI, compare to division performance with linear regression, and plot.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

**CLI (script only):**
```bash
python cpi_regression.py
```
Uses sample CPI and `division_performance.csv` by default. Saves `cpi_vs_division.png` and prints slope, intercept, and R².

**Web app (Streamlit):**
```bash
streamlit run app.py
```
Opens the app in the browser. Upload a division CSV or use sample data; optional BLS API key in the sidebar for live CPI.

## Host on the web

### Streamlit Community Cloud (step by step)

1. **Put the project on GitHub**
   - If you don’t have a repo yet: [github.com/new](https://github.com/new) → create a new repository (e.g. `linear-regression`), don’t add a README if this folder already has one.
   - In this project folder, run:
     ```bash
     git init
     git add .
     git commit -m "Add CPI vs division Streamlit app"
     git branch -M main
     git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
     git push -u origin main
     ```
     Replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name.

2. **Sign in to Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io).
   - Click **Sign in with GitHub** and authorize Streamlit to see your repos.

3. **Create a new app**
   - Click **New app**.
   - **Repository**: choose the repo you pushed (e.g. `YOUR_USERNAME/linear-regression`).
   - **Branch**: `main` (or the branch you use).
   - **Main file path**: type `app.py` (this is the file Streamlit will run).
   - Click **Deploy**.

4. **Wait for the first build**
   - Streamlit will install dependencies from `requirements.txt` and start the app. The first run can take 1–2 minutes.
   - When it’s ready, you’ll see a URL like `https://your-app-name.streamlit.app`. Open it to use the app.

5. **Optional: use live CPI (BLS API key)**
   - In the Streamlit Cloud dashboard, open your app and go to **Settings** (or the three dots next to the app) → **Secrets**.
   - Add:
     ```
     BLS_API_KEY = "your_bls_api_key_here"
     ```
   - Save. The app will redeploy; in the sidebar, check **Use live CPI (BLS API)** and the app will use this key.

**Troubleshooting:** If the app fails to start, check the logs in the Streamlit Cloud dashboard. Common fixes: ensure `requirements.txt` lists all dependencies and that **Main file path** is exactly `app.py`.

---

Other options (also free tiers):

| Option | Steps |
|--------|--------|
| **Railway** | [railway.app](https://railway.app) → New project → Deploy from GitHub → Set **Start command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` → Add a domain. |
| **Render** | [render.com](https://render.com) → New Web Service → Connect repo → **Build**: `pip install -r requirements.txt` → **Start**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0` → Deploy. |

## Use your own data

1. **Division performance**  
   Use two columns: `date` and `value` (your metric: revenue, volume, margin, etc.).
   - In the **web app**: use **Download template CSV** (empty placeholders) or **Download example CSV** (sample format), then upload your filled file.
   - In the **repo**: `division_performance_template.csv` is a template to fill; `division_performance.csv` is a full example.

2. **Live CPI**  
   Get a free [BLS API key](https://www.bls.gov/developers/home.htm) and call:
   ```python
   cpi = get_cpi_data(api_key="YOUR_BLS_KEY")
   ```
   (Edit `main()` in `cpi_regression.py` to pass `api_key`.)

## What it does

- Loads CPI (sample or BLS) and division performance.
- Merges on date.
- Fits a line: `division ≈ intercept + slope × CPI`.
- Prints the equation and R²; plots scatter + trend line.
