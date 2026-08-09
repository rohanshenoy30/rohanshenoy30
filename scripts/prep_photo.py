from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "source-photo.jpg"
OUTPUT = ROOT / "source-prepped.png"


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Could not find {INPUT}")

    print("Loading photo...")
    image = Image.open(INPUT).convert("RGBA")

    print("Removing background...")
    foreground = remove(image)

    # Get alpha channel from background removal
    alpha = np.array(foreground.getchannel("A"))

    # Find the bounding box of the subject
    mask = alpha > 20
    coords = np.argwhere(mask)

    if coords.size == 0:
        raise RuntimeError("Could not detect the subject in the image.")

    y_min, x_min = coords.min(axis=0)
    y_max, x_max = coords.max(axis=0)

    # Add a little padding around the subject
    padding = 30

    x_min = max(0, x_min - padding)
    y_min = max(0, y_min - padding)
    x_max = min(foreground.width, x_max + padding)
    y_max = min(foreground.height, y_max + padding)

    print(
        f"Cropping subject: "
        f"({x_min}, {y_min}) → ({x_max}, {y_max})"
    )

    foreground = foreground.crop(
        (x_min, y_min, x_max, y_max)
    )

    # White background
    background = Image.new(
        "RGBA",
        foreground.size,
        (255, 255, 255, 255)
    )

    composited = Image.alpha_composite(
        background,
        foreground
    )

    # Convert to grayscale
    gray = composited.convert("L")

    # Convert to OpenCV
    img = np.array(gray)

    # Improve local contrast
    clahe = cv2.createCLAHE(
        clipLimit=2.5,
        tileGridSize=(8, 8)
    )

    enhanced = clahe.apply(img)

    # Slight blur to reduce noise
    enhanced = cv2.GaussianBlur(
        enhanced,
        (3, 3),
        0
    )

    # Save
    result = Image.fromarray(enhanced)
    result.save(OUTPUT)

    print("Done!")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
