from pathlib import Path
import json
from datetime import datetime


ROOT = Path(__file__).resolve().parent.parent

INPUT = ROOT / "data" / "contributions.json"
OUTPUT = ROOT / "assets" / "contrib-heatmap.svg"


# GitHub-inspired palette
COLORS = [
    "#161B22",  # no contributions
    "#0E4429",
    "#006D32",
    "#26A641",
    "#39D353",
]


CELL_SIZE = 13
GAP = 4

LEFT = 45
TOP = 55

WIDTH = 860
HEIGHT = 180


def load_data():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT}. "
            "Run fetch_contributions.py first."
        )

    with open(INPUT, "r", encoding="utf-8") as f:
        return json.load(f)


def build_day_map(data):

    return {
        day["date"]: day["level"]
        for day in data["days"]
    }


def parse_date(value):

    return datetime.strptime(
        value,
        "%Y-%m-%d"
    ).date()


def build_grid(day_map):

    dates = sorted(
        parse_date(date)
        for date in day_map
    )

    if not dates:
        return []

    # Use the most recent 365 days
    end_date = dates[-1]

    from datetime import timedelta

    start_date = end_date - timedelta(days=364)

    cells = []

    current = start_date

    while current <= end_date:

        level = day_map.get(
            current.strftime("%Y-%m-%d"),
            0
        )

        # Python weekday:
        # Monday = 0
        # Sunday = 6

        weekday = current.weekday()

        day_offset = (
            current - start_date
        ).days

        week = day_offset // 7

        cells.append({
            "date": current.strftime("%Y-%m-%d"),
            "level": level,
            "week": week,
            "weekday": weekday
        })

        current += timedelta(days=1)

    return cells


def make_cell(cell, index):

    x = LEFT + cell["week"] * (
        CELL_SIZE + GAP
    )

    y = TOP + cell["weekday"] * (
        CELL_SIZE + GAP
    )

    color = COLORS[
        min(
            cell["level"],
            len(COLORS) - 1
        )
    ]

    # Staggered diagonal reveal
    delay = (
        cell["week"] * 0.025
        + cell["weekday"] * 0.025
    )

    return f"""
    <rect
        x="{x}"
        y="{y}"
        width="{CELL_SIZE}"
        height="{CELL_SIZE}"
        rx="3"
        fill="{color}"
        opacity="0">

        <animate
            attributeName="opacity"
            from="0"
            to="1"
            dur="0.25s"
            begin="{delay:.3f}s"
            fill="freeze"
        />

    </rect>
    """


def build_svg(data, cells):

    stats = data.get(
        "stats",
        {}
    )

    active_days = stats.get(
        "active_days",
        0
    )

    current_streak = stats.get(
        "current_streak",
        0
    )

    longest_streak = stats.get(
        "longest_streak",
        0
    )

    cell_svg = "\n".join(
        make_cell(cell, i)
        for i, cell in enumerate(cells)
    )

    # 53 weeks × 7 days
    grid_width = (
        53 * CELL_SIZE
        + 52 * GAP
    )

    grid_height = (
        7 * CELL_SIZE
        + 6 * GAP
    )

    # Legend
    legend_x = 690
    legend_y = 145

    legend = []

    legend.append(
        '<text x="575" y="155" class="legend">'
        'Less'
        '</text>'
    )

    for i, color in enumerate(COLORS):

        x = legend_x + i * 20

        legend.append(
            f'''
            <rect
                x="{x}"
                y="{legend_y}"
                width="13"
                height="13"
                rx="3"
                fill="{color}"
            />
            '''
        )

    legend.append(
        '<text x="800" y="155" class="legend">'
        'More'
        '</text>'
    )

    legend_svg = "\n".join(legend)

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
    font-family: "SFMono-Regular", "Menlo",
                 "Monaco", "Courier New", monospace;
    font-size: 18px;
    font-weight: bold;
    fill: #F0F6FC;
}}

.subtitle {{
    font-family: "SFMono-Regular", "Menlo",
                 "Monaco", "Courier New", monospace;
    font-size: 11px;
    fill: #8B949E;
}}

.legend {{
    font-family: "SFMono-Regular", "Menlo",
                 "Monaco", "Courier New", monospace;
    font-size: 10px;
    fill: #8B949E;
}}

.stat {{
    font-family: "SFMono-Regular", "Menlo",
                 "Monaco", "Courier New", monospace;
    font-size: 11px;
    fill: #58A6FF;
}}

</style>

<text
x="25"
y="30"
class="title">
rohanshenoy30 / contributions
</text>

<text
x="25"
y="45"
class="subtitle">
activity over the last year
</text>

<!-- Contribution cells -->

{cell_svg}

<!-- Legend -->

{legend_svg}

<!-- Stats -->

<text
x="25"
y="155"
class="stat">
{active_days} active days
</text>

<text
x="175"
y="155"
class="stat">
current streak: {current_streak} days
</text>

<text
x="370"
y="155"
class="stat">
longest streak: {longest_streak} days
</text>

</svg>
"""

    return svg


def main():

    print("Loading contribution data...")

    data = load_data()

    print("Building contribution grid...")

    day_map = build_day_map(data)

    cells = build_grid(day_map)

    print(
        f"Rendering {len(cells)} contribution cells..."
    )

    svg = build_svg(
        data,
        cells
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print("Done!")

    print(
        f"Saved: {OUTPUT}"
    )


if __name__ == "__main__":
    main()
