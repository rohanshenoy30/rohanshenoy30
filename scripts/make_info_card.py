from pathlib import Path
import html


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "assets" / "info-card.svg"

WIDTH = 560
HEIGHT = 690


def esc(text):
    return html.escape(text)


def make_text(x, y, content, cls, delay):
    return f"""
    <g opacity="0">
        <animate
            attributeName="opacity"
            from="0"
            to="1"
            dur="0.35s"
            begin="{delay:.2f}s"
            fill="freeze"
        />

        <text x="{x}" y="{y}" class="{cls}">
            {esc(content)}
        </text>
    </g>
    """


def main():

    elements = []

    delay = 0.15

    def add(x, y, content, cls):
        nonlocal delay

        elements.append(
            make_text(
                x,
                y,
                content,
                cls,
                delay
            )
        )

        delay += 0.07

    # Header
    add(30, 42, "rohan@github", "title")

    add(
        30,
        72,
        "────────────────────────────────────────",
        "divider"
    )

    # Identity
    add(30, 108, "identity", "section")

    identity = [
        ("Name", "Rohan Shenoy"),
        ("Education", "Manipal Institute of Technology"),
        ("Degree", "Computer Science & Engineering"),
        ("Status", "Final Year"),
    ]

    y = 140

    for key, value in identity:
        add(30, y, key, "key")
        add(150, y, value, "value")
        y += 28

    # Experience
    add(30, 275, "experience", "section")

    experience = [
        ("Microsoft", "AI Business Solutions"),
        ("Deloitte", "Tax Technology Consulting"),
        ("AeroMIT", "Autonomous Drone Research"),
    ]

    y = 307

    for key, value in experience:
        add(30, y, key, "accent")
        add(150, y, value, "value")
        y += 32

    # Focus
    add(30, 420, "focus", "section")

    focus = [
        "Agentic AI",
        "Retrieval-Augmented Generation",
        "Machine Learning",
        "Computer Vision",
        "Robotics",
    ]

    y = 452

    for item in focus:
        add(30, y, "▸", "bullet")
        add(55, y, item, "value")
        y += 27

    # Stack
    add(30, 600, "stack", "section")

    add(
        30,
        630,
        "Python • C++ • C# • .NET • Azure",
        "small"
    )

    add(
        30,
        653,
        "ROS2 • OpenCV • TensorFlow • Git",
        "small"
    )

    svg = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{WIDTH}"
height="{HEIGHT}"
viewBox="0 0 {WIDTH} {HEIGHT}">

<rect
width="100%"
height="100%"
rx="14"
fill="#0D1117"
stroke="#30363D"
stroke-width="2"/>

<style>

.title {{
    font-family: "SFMono-Regular", "Menlo", "Monaco",
                 "Courier New", monospace;
    font-size: 25px;
    font-weight: bold;
    fill: #F0F6FC;
}}

.section {{
    font-family: "SFMono-Regular", "Menlo", "Monaco",
                 "Courier New", monospace;
    font-size: 15px;
    font-weight: bold;
    fill: #58A6FF;
}}

.key {{
    font-family: "SFMono-Regular", "Menlo", "Monaco",
                 "Courier New", monospace;
    font-size: 13px;
    fill: #8B949E;
}}

.value {{
    font-family: "SFMono-Regular", "Menlo", "Monaco",
                 "Courier New", monospace;
    font-size: 13px;
    fill: #C9D1D9;
}}

.accent {{
    font-family: "SFMono-Regular", "Menlo", "Monaco",
                 "Courier New", monospace;
    font-size: 13px;
    font-weight: bold;
    fill: #3FB950;
}}

.bullet {{
    font-family: "SFMono-Regular", "Menlo", "Monaco",
                 "Courier New", monospace;
    font-size: 14px;
    fill: #3FB950;
}}

.small {{
    font-family: "SFMono-Regular", "Menlo", "Monaco",
                 "Courier New", monospace;
    font-size: 11px;
    fill: #8B949E;
}}

.divider {{
    font-family: "SFMono-Regular", "Menlo", "Monaco",
                 "Courier New", monospace;
    font-size: 12px;
    fill: #30363D;
}}

</style>

{''.join(elements)}

</svg>
"""

    OUTPUT.write_text(svg, encoding="utf-8")

    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
