from pathlib import Path
from datetime import datetime
import json
import re

import requests
from bs4 import BeautifulSoup


USERNAME = "rohanshenoy30"

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "contributions.json"

URL = f"https://github.com/users/{USERNAME}/contributions"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_page():
    print(f"Fetching contributions for {USERNAME}...")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def parse_contributions(html):
    soup = BeautifulSoup(html, "html.parser")

    days = []

    # GitHub contribution cells
    for cell in soup.select("td.ContributionCalendar-day"):

        date = cell.get("data-date")
        level = cell.get("data-level")

        if not date:
            continue

        try:
            level = int(level or 0)
        except ValueError:
            level = 0

        days.append({
            "date": date,
            "level": level
        })

    # Fallback for GitHub markup changes
    if not days:

        for cell in soup.select("[data-date]"):

            date = cell.get("data-date")
            level = cell.get("data-level")

            if not date:
                continue

            try:
                level = int(level or 0)
            except ValueError:
                level = 0

            days.append({
                "date": date,
                "level": level
            })

    if not days:
        raise RuntimeError(
            "Could not find contribution data. "
            "GitHub may have changed its HTML structure."
        )

    # Remove duplicates
    unique = {}

    for day in days:
        unique[day["date"]] = day["level"]

    days = [
        {
            "date": date,
            "level": level
        }
        for date, level in sorted(unique.items())
    ]

    return days


def calculate_stats(days):

    total = 0

    for day in days:
        total += day["level"]

    # Note:
    # GitHub's visual level is not the exact contribution count.
    # We'll obtain exact contribution counts from aria-label text
    # in the renderer if available.
    #
    # For now, this is the activity-level total.

    active_days = [
        day for day in days
        if day["level"] > 0
    ]

    longest_streak = 0
    current_streak = 0

    previous_date = None
    streak = 0

    for day in active_days:

        current_date = datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        ).date()

        if previous_date is not None:

            difference = (
                current_date - previous_date
            ).days

            if difference == 1:
                streak += 1
            else:
                streak = 1

        else:
            streak = 1

        longest_streak = max(
            longest_streak,
            streak
        )

        previous_date = current_date

    # Current streak
    today = datetime.now().date()

    current_streak = 0

    day_map = {
        datetime.strptime(
            day["date"],
            "%Y-%m-%d"
        ).date(): day["level"]
        for day in days
    }

    check = today

    while day_map.get(check, 0) > 0:

        current_streak += 1

        from datetime import timedelta
        check -= timedelta(days=1)

    return {
        "active_days": len(active_days),
        "activity_level_sum": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak
    }


def main():

    html = fetch_page()

    days = parse_contributions(html)

    stats = calculate_stats(days)

    output = {
        "username": USERNAME,
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "stats": stats
    }

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        json.dumps(
            output,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"Found {len(days)} contribution days."
    )

    print(
        f"Active days: {stats['active_days']}"
    )

    print(
        f"Current streak: {stats['current_streak']}"
    )

    print(
        f"Longest streak: {stats['longest_streak']}"
    )

    print(
        f"Saved: {OUTPUT}"
    )


if __name__ == "__main__":
    main()
