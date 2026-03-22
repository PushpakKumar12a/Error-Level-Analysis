# ELA Image Inspector 🔍

A browser-based forensic tool that uses **Error Level Analysis (ELA)** to detect potential image tampering. Upload any image and get an instant visual heatmap, confidence score, and verdict — no command-line expertise required.

---

## 🧠 What Is Error Level Analysis?

When a JPEG image is saved, compression introduces a predictable level of "error" across the entire image. If a region has been edited and re-saved — or pasted from a different source — it will have a different compression error level than the surrounding pixels.

ELA exploits this by recompressing an image at a known quality level and measuring the difference between the recompressed version and the original, pixel by pixel. Regions that stand out in the resulting difference map (appearing brighter or more detailed) may indicate manipulation.

> ⚠️ **Important:** ELA is a forensic aid, not a definitive verdict. Results should be interpreted alongside other analysis.

---

## ✨ Features

- 🖱️ **Drag-and-drop upload** — or click to browse
- 🎛️ **Interactive controls** — adjust JPEG quality and amplification in real time
- 🔀 **Side-by-side comparison** — toggle between the original image and the ELA heatmap
- 📊 **Detailed statistics** — max difference, average difference, and percentage of suspicious pixels
- 🏷️ **Automatic verdict** — `Likely Authentic`, `Possibly Tampered`, or `Likely Tampered` with a confidence score

---

## 📁 Project Structure

```
ela-inspector/
├── app.py               # Flask app and /analyze route
├── ela_engine.py        # Core ELA logic and verdict computation
├── requirements.txt     # Python dependencies
├── templates/
│   └── index.html       # Main UI page
└── static/
    ├── style.css        # App styles
    └── app.js           # Frontend fetch and UI logic
```

---

## 📋 Requirements

- Python 3.10 or newer
- pip

---

## ⚙️ Installation

```bash
# Create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the App

```bash
python app.py
```

Then open your browser to:

```
http://127.0.0.1:5000
```

---

## ⚙️ How It Works

### 🖥️ Frontend

`templates/index.html` renders the upload interface and result panel. `static/app.js` handles the file upload via `fetch()`, sends it to the backend with the chosen quality and amplification values, and updates the UI with the returned heatmap and statistics.

### 🐍 Backend

`app.py` exposes two routes: `GET /` serves the UI, and `POST /analyze` accepts the image and parameters and delegates processing to `ela_engine.py`.

`ela_engine.py` runs the following pipeline:

1. 🖼️ Opens the uploaded image with Pillow and converts it to RGB
2. 🗜️ Recompresses the image as JPEG at the requested quality level
3. 🔢 Computes the per-pixel absolute difference between the original and recompressed image
4. 🔆 Amplifies the differences by the requested factor to make subtle variations visible
5. 🎨 Builds a PNG heatmap from the amplified difference map
6. 📈 Calculates summary statistics and determines a verdict with a confidence score
7. 📤 Returns everything as JSON

---

## 📡 API Reference

### `GET /`

Returns the main web interface.

---

### `POST /analyze`

**Request** — `multipart/form-data`

| Field | Type | Default | Description |
|---|---|---|---|
| `image` | file | — | The image to analyze (JPEG, PNG, etc.) |
| `quality` | integer | `75` | JPEG recompression quality (1–95) |
| `amplification` | integer | `15` | Difference amplification factor |

**Response** — `application/json`

| Field | Type | Description |
|---|---|---|
| `elaDataUrl` | string | Base64-encoded PNG of the ELA heatmap |
| `maxDifference` | number | Maximum per-pixel difference detected |
| `avgDifference` | number | Average per-pixel difference across the image |
| `suspiciousRegions` | number | Percentage of pixels above the suspicious threshold |
| `verdict` | string | `likely_authentic`, `possibly_tampered`, or `likely_tampered` |
| `confidenceScore` | number | Confidence percentage (0–100) |

**Example response:**

```json
{
  "elaDataUrl": "data:image/png;base64,iVBORw0KGgo...",
  "maxDifference": 42.7,
  "avgDifference": 3.1,
  "suspiciousRegions": 12.4,
  "verdict": "possibly_tampered",
  "confidenceScore": 61
}
```

---

## 🎛️ Tuning Tips

**Quality** controls how aggressively the image is recompressed before comparison. Lower values produce stronger compression, which can reveal more subtle edits but also increase false positives on heavily compressed originals. The default of `75` works well for most images.

**Amplification** scales the brightness of difference values in the output heatmap. A higher value makes small differences easier to see but can make a clean image look suspicious. Start at `15` and increase only if the heatmap looks uniformly flat.

---

## ⚠️ Limitations

- 🔁 ELA is most reliable on images that have been saved as JPEG exactly once. Images that have been re-saved, screenshotted, or converted multiple times will have elevated error levels throughout, making tampered regions harder to isolate.
- 🖼️ PNG and losslessly-encoded images are converted to JPEG before analysis, which introduces a compression baseline that affects results.
- ❓ ELA cannot determine *what* was edited — only *where* compression artifacts differ from the expected baseline.
