import io
import base64
from PIL import Image


def perform_ela(img_data, quality: int = 75, amplification: int = 15) -> dict:

    if isinstance(img_data, bytes):
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
    else:
        img = img_data.convert("RGB")
    width, height = img.size

    # Re-compress as JPEG at the given quality
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    rec_img = Image.open(buf).convert("RGB")

    # Get pixel data
    img_px = img.load()
    rec_px = rec_img.load()

    # Create ELA output image
    out_img = Image.new("RGB", (width, height))
    out_px = out_img.load()

    max_diff = 0
    total_diff = 0
    bad_px = 0
    px_count = width * height
    threshold = 40  # suspicious threshold after amplification

    for y in range(height):
        for x in range(width):
            r1, g1, b1 = img_px[x, y]
            r2, g2, b2 = rec_px[x, y]

            r_diff = min(255, abs(r1 - r2) * amplification)
            g_diff = min(255, abs(g1 - g2) * amplification)
            b_diff = min(255, abs(b1 - b2) * amplification)

            out_px[x, y] = (r_diff, g_diff, b_diff)

            px_diff = (r_diff + g_diff + b_diff) / 3
            if px_diff > max_diff:
                max_diff = px_diff
            total_diff += px_diff
            if px_diff > threshold:
                bad_px += 1

    avg_diff = total_diff / px_count
    bad_ratio = bad_px / px_count

    # Determine verdict
    if bad_ratio > 0.15 or avg_diff > 50:
        verdict = "likely_tampered"
        confidence_score = min(95, 60 + bad_ratio * 200)
    elif bad_ratio > 0.05 or avg_diff > 25:
        verdict = "possibly_tampered"
        confidence_score = min(75, 40 + bad_ratio * 150)
    else:
        verdict = "likely_authentic"
        confidence_score = min(90, 70 + (1 - bad_ratio) * 20)

    # Convert ELA image to base64 data URL
    out_buf = io.BytesIO()
    out_img.save(out_buf, format="PNG")
    out_b64 = base64.b64encode(out_buf.getvalue()).decode("utf-8")
    out_url = f"data:image/png;base64,{out_b64}"

    return {
        "elaDataUrl": out_url,
        "maxDifference": round(max_diff),
        "avgDifference": round(avg_diff * 100) / 100,
        "suspiciousRegions": round(bad_ratio * 100),
        "verdict": verdict,
        "confidenceScore": round(confidence_score),
    }
