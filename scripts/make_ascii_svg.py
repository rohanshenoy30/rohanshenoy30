from pathlib import Path
from PIL import Image
import html


ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "source-prepped.png"
OUTPUT = ROOT / "rohan-ascii.svg"

# Bright -> dark
RAMP = " .`:-=+*cs#%@"

# Portrait width in characters
CHAR_WIDTH = 100

# Approximate character aspect correction.
# Terminal characters are taller than they are wide.
CHAR_ASPECT = 0.52

# SVG styling
FONT_SIZE = 11
LINE_HEIGHT = 12
TEXT_COLOR = "#C9D1D9"
BACKGROUND = "#0D1117"


def brightness_to_char(value):
    # White -> space, dark -> dense ASCII characters
    index = int(((255 - value) / 255) * (len(RAMP) - 1))
    return RAMP[index]


def image_to_ascii(image):
    width, height = image.size

    char_height = max(
        20,
        int(CHAR_WIDTH * height / width * CHAR_ASPECT)
    )

    image = image.resize(
        (CHAR_WIDTH, char_height),
        Image.Resampling.LANCZOS
    )

    pixels = image.load()

    rows = []

    for y in range(char_height):
        row = ""

        for x in range(CHAR_WIDTH):
            row += brightness_to_char(pixels[x, y])

        rows.append(row)

    return rows


def build_svg(rows):
    width = CHAR_WIDTH * FONT_SIZE * 0.62 + 20
    height = len(rows) * LINE_HEIGHT + 20

    animation_duration = 0.55
    row_delay = 0.035

    parts = []

    parts.append(
        f'''<svg xmlns="http://www.w3.org/2000/svg"
        width="{width:.0f}"
        height="{height:.0f}"
        viewBox="0 0 {width:.0f} {height:.0f}">

        <rect width="100%" height="100%" fill="{BACKGROUND}"/>

        <style>
            .ascii {{
                font-family: "SFMono-Regular", "Menlo", "Monaco",
                             "Courier New", monospace;
                font-size: {FONT_SIZE}px;
                fill: {TEXT_COLOR};
                white-space: pre;
            }}
        </style>
        '''
    )

    for i, row in enumerate(rows):
        escaped = html.escape(row)

        y = 15 + i * LINE_HEIGHT
        clip_id = f"rowclip{i}"

        delay = i * row_delay

        parts.append(
            f'''
            <clipPath id="{clip_id}">
                <rect x="0" y="{y - FONT_SIZE}"
                      width="0" height="{LINE_HEIGHT + 4}">
                    <animate
                        attributeName="width"
                        from="0"
                        to="{width:.0f}"
                        dur="{animation_duration}s"
                        begin="{delay:.3f}s"
                        fill="freeze"/>
                </rect>
            </clipPath>

            <g clip-path="url(#{clip_id})">
                <text
                    x="10"
                    y="{y}"
                    class="ascii">{escaped}</text>
            </g>
            '''
        )

    parts.append("</svg>")

    return "\n".join(parts)


def main():
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT}. "
            "Run prep_photo.py first."
        )

    print("Loading prepared image...")
    image = Image.open(INPUT).convert("L")

    print("Converting image to ASCII...")
    rows = image_to_ascii(image)

    print(f"Generated {len(rows)} rows × {CHAR_WIDTH} characters")

    svg = build_svg(rows)

    OUTPUT.write_text(svg, encoding="utf-8")

    print("Done!")
    print(f"Saved: {OUTPUT}")


if __name__ == "__main__":
    main()
