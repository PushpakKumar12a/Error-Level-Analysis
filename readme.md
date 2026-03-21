# Error Level Analysis (ELA) Image Inspector 🔍

This project is a small Flask web app that performs Error Level Analysis on uploaded images and presents the result in the browser.

## What Is ELA? 🧠

Error Level Analysis is a forensic technique for spotting possible image edits by comparing an image against a recompressed version of itself. Because JPEG compression introduces predictable loss, areas that were edited or saved differently can show stronger differences than untouched regions. The result is often displayed as a heatmap-style image where brighter or more detailed areas may deserve closer inspection.

## What ELA Does Here

Error Level Analysis works by recompressing an image at a known JPEG quality and comparing the recompressed version with the original pixels. Areas with larger compression differences can stand out visually and may indicate edits or tampering.

In this project:

1. The user uploads an image from the web UI.
2. The frontend sends the file to the backend at `/analyze`.
3. The backend loads the image with Pillow, converts it to RGB, and recompresses it as JPEG using the selected quality.
4. Each pixel is compared between the original and recompressed image.
5. The differences are amplified to create an ELA heatmap-style image.
6. The backend returns the ELA image as a base64 PNG along with analysis stats.
7. The UI shows the original image, the ELA result, and a verdict such as likely authentic, possibly tampered, or likely tampered.

## Features

- Upload and analyze images in the browser
- Drag-and-drop or click-to-upload interface
- ELA visualization generated on the backend
- Confidence score and suspicious-region summary
- Original vs ELA result toggle

## Project Structure

- [app.py](app.py) - Flask application and API routes
- [ela_engine.py](ela_engine.py) - ELA processing and verdict logic
- [requirements.txt](requirements.txt) - Python dependencies
- [templates/index.html](templates/index.html) - Main HTML page
- [static/style.css](static/style.css) - App styling
- [static/app.js](static/app.js) - Frontend interaction logic

## Requirements

- Python 3.10 or newer
- pip

## Install

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
## Run the App 🚀

Start the Flask server:

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## How It Works

### Frontend

The page in [templates/index.html](templates/index.html) lets the user:

- choose an image
- adjust JPEG quality
- adjust amplification
- run ELA analysis
- switch between the original image and the ELA output

The JavaScript in [static/app.js](static/app.js) sends the file to the backend with `fetch()` and updates the UI with the response.

### Backend

The `/analyze` route in [app.py](app.py) accepts the uploaded file and forwards the image bytes to `perform_ela()` in [ela_engine.py](ela_engine.py).

`perform_ela()` does the following:

- opens the image with Pillow
- recompresses it as JPEG at the requested quality
- calculates per-pixel differences
- amplifies those differences for visibility
- builds a PNG image from the difference map
- computes a simple verdict and confidence score
- returns everything as JSON

## API

### `GET /`

Returns the main web interface.

### `POST /analyze`

Form fields:

- `image` - uploaded image file
- `quality` - JPEG recompression quality, default `75`
- `amplification` - difference amplification factor, default `15`

Response fields:

- `elaDataUrl` - base64 PNG of the ELA image
- `maxDifference` - maximum pixel difference detected
- `avgDifference` - average pixel difference
- `suspiciousRegions` - percentage of pixels above the suspicious threshold
- `verdict` - `likely_authentic`, `possibly_tampered`, or `likely_tampered`
- `confidenceScore` - confidence percentage