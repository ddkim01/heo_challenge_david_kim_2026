import math
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import date, datetime, timedelta
from matplotlib.lines import Line2D
from matplotlib.legend_handler import HandlerPatch

matplotlib.use("MacOSX")  # Use MacOSX backend for better performance on Mac


# Earth constants
mu = 398600  # km³/s²  (Earth's gravitational parameter)
r_earth = 6378  # km      (Earth's equatorial radius)

"""Translate TLE data into cleaner format. Pluck epoch, year, day of year, eccentricity, and mean motion. Then calculate perigee and apogee altitudes from eccentricity and mean motion."""


# Claude's addition - couldnt figure out how to read the TLE data
def parse_tles(filepath):
    with open(filepath) as f:
        lines = [l.strip() for l in f if l.strip()]

    tles = []
    for i in range(0, len(lines) - 1, 2):
        line1, line2 = lines[i], lines[i + 1]

        # Learned that epoch characters are always indexed 18 to 32 in TLE data
        epoch_str = line1[18:32]
        year = int(epoch_str[:2])
        year += 2000 if year < 57 else 1900
        day_of_year = float(epoch_str[2:])

        # From Line 2: eccentricity and mean motion
        eccentricity = float("0." + line2[26:33])
        mean_motion = float(line2[52:63])  # revolutions per day

        tles.append((year, day_of_year, eccentricity, mean_motion))
    return tles


"""Calculate the perigee and apogee altitudes given revs per day and eccentricity"""


def perigee_apogee(eccentricity, mean_motion_rev_per_day):
    n = mean_motion_rev_per_day * 2 * math.pi / 86400  # rad/s
    a = (mu / n**2) ** (1 / 3)  # semi-major axis, km
    perigee_alt = a * (1 - eccentricity) - r_earth  # km above surface
    apogee_alt = a * (1 + eccentricity) - r_earth  # km above surface
    return perigee_alt, apogee_alt


tles = parse_tles("iss_tle_2025.txt")

perigees = []
apogees = []
for year, doy, ecc, mm in tles:
    p, a = perigee_apogee(ecc, mm)
    perigees.append(p)
    apogees.append(a)

day_of_year = []
for j in range(len(tles)):
    day_of_year.append(tles[j][1])

mean_iss_alt = []
for k in range(len(tles)):
    mean_iss_alt.append((perigees[k] + apogees[k]) / 2)

""" Collate data of crewed missions to ISS in 2025 include docking and undocking events. doy is calculated by hand from date"""
crew_events_2025 = [
    # Space X Crew-9
    {
        "spacecraft": "SpaceX Crew-9 (Dragon Freedom)",
        "event": "depart",
        "date": date(2025, 3, 18),
        "doy": 77,
    },
    # Space X Crew-10
    {
        "spacecraft": "SpaceX Crew-10 (Dragon Endurance)",
        "event": "arrive",
        "date": date(2025, 3, 15),
        "doy": 74,
    },
    {
        "spacecraft": "SpaceX Crew-10 (Dragon Endurance)",
        "event": "depart",
        "date": date(2025, 8, 8),
        "doy": 220,
    },
    # Soyuz MS-26
    {
        "spacecraft": "Soyuz MS-26",
        "event": "depart",
        "date": date(2025, 4, 19),
        "doy": 109,
    },
    # Soyuz MS-27
    {
        "spacecraft": "Soyuz MS-27",
        "event": "arrive",
        "date": date(2025, 4, 8),
        "doy": 98,
    },
    {
        "spacecraft": "Soyuz MS-27",
        "event": "depart",
        "date": date(2025, 12, 8),
        "doy": 342,
    },
    # Axiom Space Mission 4
    {
        "spacecraft": "Axiom-4 (Dragon)",
        "event": "arrive",
        "date": date(2025, 6, 26),
        "doy": 177,
    },
    {
        "spacecraft": "Axiom-4 (Dragon)",
        "event": "depart",
        "date": date(2025, 7, 14),
        "doy": 195,
    },
    # Space X Crew-11
    {
        "spacecraft": "SpaceX Crew-11 (Dragon Endeavour)",
        "event": "arrive",
        "date": date(2025, 8, 2),
        "doy": 214,
    },
    # Soyuz MS-28
    {
        "spacecraft": "Soyuz MS-28",
        "event": "arrive",
        "date": date(2025, 11, 27),
        "doy": 331,
    },
]

# Get data from dictionary into format of [dock_doy, undock_doy] pairs for each mission.
# If no dock or undock event, use 0 (docked in 2024) or 366 (undock planned in 2026) as placeholder.
missions = {}
for o in crew_events_2025:
    name = o["spacecraft"]
    if name not in missions:
        missions[name] = {}
    missions[name][o["event"]] = o["doy"]

crewed_missions = [
    [events.get("arrive", 0), events.get("depart", 366)] for events in missions.values()
]

""" Plot mean ISS altitude over 2025 with crewed mission events."""


def plot_iss_chart():
    BG = "#FAF9F6"
    base = datetime(2025, 1, 1)
    dates = [base + timedelta(days=doy - 1) for doy in day_of_year]

    # Detect reboost peaks: large positive jumps in altitude
    reboost_peaks = [
        u
        for u in range(1, len(mean_iss_alt) - 1)
        if mean_iss_alt[u] - mean_iss_alt[u - 1] > 0.5
        and mean_iss_alt[u] >= mean_iss_alt[u + 1]
    ]

    fig, ax = plt.subplots(figsize=(16, 7))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # Reboost vertical bands (+-5 data points around each peak)
    # for idx in reboost_peaks:
    #     band_start = dates[max(0, idx - 5)]
    #     band_end = dates[min(len(dates) - 1, idx + 5)]
    #     ax.axvspan(band_start, band_end, color="#ffd8b1", alpha=0.85, zorder=1)

    # Altitude line
    ax.plot(
        dates,
        mean_iss_alt,
        color="#FF0800",
        linewidth=2.3,
        label="Mean altitude",
        zorder=4,
    )

    # Upward arrows at reboost peaks
    for idx in reboost_peaks:
        ax.annotate(
            "",
            xy=(dates[idx], mean_iss_alt[idx]),
            xytext=(dates[idx], mean_iss_alt[idx] - 0.8),
            arrowprops=dict(arrowstyle="->", color="#000000", lw=2.5),
            zorder=5,
        )

    # Grid
    ax.yaxis.grid(True, color="gray", alpha=0.4, linestyle="-", zorder=0)
    ax.xaxis.grid(False)
    # --- Mission bars ---
    COLORS = {
        "dragon": "#005EFF",
        "soyuz": "#757575",
    }

    def bar_color(name):
        n = name.lower()
        if "soyuz" in n:
            return COLORS["soyuz"]
        if "dragon" in n or "crew" in n or "ax-4" in n:
            return COLORS["dragon"]
        return COLORS["other"]

    # Greedy row assignment to avoid bar overlap
    mission_list = list(missions.items())
    row_ends = []
    row_of = []
    for name, events in mission_list:
        arrive = events.get("arrive", 0)
        assigned = -1
        for r, end in enumerate(row_ends):
            if arrive >= end:
                row_ends[r] = events.get("depart", 366)
                assigned = r
                break
        if assigned == -1:
            row_ends.append(events.get("depart", 366))
            assigned = len(row_ends) - 1
        row_of.append(assigned)

    n_rows = len(row_ends)
    row_h = 0.22
    row_gap = 0.05
    data_min = min(mean_iss_alt)
    bar_top = data_min - 0.4  # small gap below the data line

    for i, (name, events) in enumerate(mission_list):
        arrive = events.get("arrive", 0)
        depart = events.get("depart", 366)
        row = row_of[i]

        start_d = (
            datetime(2025, 1, 1) if arrive <= 1 else base + timedelta(days=arrive - 1)
        )
        end_d = (
            datetime(2025, 12, 31)
            if depart >= 365
            else base + timedelta(days=depart - 1)
        )

        y0 = bar_top - (n_rows - 1 - row) * (row_h + row_gap)
        color = bar_color(name)
        width = mdates.date2num(end_d) - mdates.date2num(start_d)

        ax.broken_barh(
            [(mdates.date2num(start_d), width)],
            (y0, row_h),
            facecolors=color,
            alpha=0.85,
            zorder=3,
        )

        # Strip parenthetical sub-name for a cleaner label
        label = name.split(" (")[0]
        mid = mdates.num2date((mdates.date2num(start_d) + mdates.date2num(end_d)) / 2)
        ax.text(
            mid,
            y0 + row_h / 2,
            label,
            ha="center",
            va="center",
            fontsize=7.5,
            color="white",
            fontname="Arial",
            zorder=5,
        )

    # Y limits to show bars below data
    total_bar_h = n_rows * (row_h + row_gap)
    ax.set_ylim(bar_top - total_bar_h - 0.3, max(mean_iss_alt) + 1.5)

    # X axis: month labels across 2025
    ax.set_xlim(datetime(2025, 1, 1), datetime(2025, 12, 31))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))

    # Styling
    # for spine in ax.spines.values():
    #     spine.set_color("#000000")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#000000")
    ax.tick_params(colors="black", labelsize=9)
    ax.set_xlabel(
        "2025",
        color="#000000",
        labelpad=8,
        fontweight="bold",
        fontname="Arial",
        fontsize=13,
    )
    ax.set_ylabel(
        "Mean Altitude (km)",
        color="#000000",
        labelpad=8,
        fontweight="bold",
        fontname="Arial",
        fontsize=13,
    )
    ax.set_title(
        "International Space Station (ZARYA) — Average Altitude & Crewed Missions in 2025",
        color="black",
        fontsize=16,
        pad=12,
        fontweight="bold",
        fontname="Arial",
    )
    # Legend
    legend_handles = [
        Line2D([0], [0], color="#FF0000", linewidth=3, label="Mean altitude"),
        # mpatches.Patch(
        #     facecolor="#ffd8b1", alpha=0.9, edgecolor="gray", label="Reboost event"),
        plt.arrow(
            0,
            0,
            0.1,
            0.1,
            label="Reboost event",
            color="#000000",
            lw=0.5,
            head_width=0.3,
            head_length=0.3,
        ),
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper right",
        facecolor="#2a2a4e",
        edgecolor="#000000",
        labelcolor="white",
        framealpha=0.8,
    )

    plt.tight_layout()
    plt.savefig("iss_plot_2025.png", dpi=150, bbox_inches="tight", facecolor=BG)
    plt.show()


plot_iss_chart()
