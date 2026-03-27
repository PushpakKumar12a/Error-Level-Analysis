import io
import base64
from PIL import Image, ImageChops, ImageEnhance

def perform_ela(img_data, quality = 75, amplification = 15):

    if isinstance(img_data, bytes):
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
    else:
        img = img_data.convert("RGB")

    # Recompress image
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality)
    buf.seek(0)
    rec_img = Image.open(buf).convert("RGB")

    diff = ImageChops.difference(img, rec_img)

    enhancer = ImageEnhance.Brightness(diff)
    ela_img = enhancer.enhance(amplification)

    # Convert to pixel data for metrics
    diff_px = ela_img.load()
    width, height = ela_img.size

    max_diff = 0
    total_diff = 0
    bad_px = 0
    px_count = width * height
    threshold = 40

    for y in range(height):
        for x in range(width):
            r, g, b = diff_px[x, y]
            px_diff = (r + g + b) / 3

            max_diff = max(max_diff, px_diff)
            total_diff += px_diff

            if px_diff > threshold:
                bad_px += 1

    avg_diff = total_diff / px_count
    bad_ratio = bad_px / px_count

    if bad_ratio > 0.15 or avg_diff > 50:
        verdict = "likely_tampered"
        confidence_score = min(95, 60 + bad_ratio * 200)
    elif bad_ratio > 0.05 or avg_diff > 25:
        verdict = "possibly_tampered"
        confidence_score = min(75, 40 + bad_ratio * 150)
    else:
        verdict = "likely_authentic"
        confidence_score = min(90, 70 + (1 - bad_ratio) * 20)

    out_buf = io.BytesIO()
    ela_img.save(out_buf, format="PNG")
    out_b64 = base64.b64encode(out_buf.getvalue()).decode("utf-8")

    return {
        "elaDataUrl": f"data:image/png;base64,{out_b64}",
        "maxDifference": round(max_diff),
        "avgDifference": round(avg_diff, 2),
        "suspiciousRegions": round(bad_ratio * 100),
        "verdict": verdict,
        "confidenceScore": round(confidence_score),
    }