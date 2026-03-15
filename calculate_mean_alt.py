import math
import matplotlib

matplotlib.use("MacOSX")  # Use MacOSX backend for better performance on Mac
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from datetime import date

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

# print(f"TLE count : {len(tles)}")
# print(f"Mean perigee altitude : {sum(perigees)/len(perigees):.2f} km")
# print(f"Mean apogee altitude  : {sum(apogees)/len(apogees):.2f} km")
# print(f"Min perigee : {min(perigees):.2f} km")
# print(f"Max apogee  : {max(apogees):.2f} km")
# print(perigees)
# print(apogees)
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
        "spacecraft": "Crew-9 (Dragon Freedom)",
        "event": "depart",
        "date": date(2025, 3, 18),
        "doy": 77,
    },
    # Space X Crew-10
    {
        "spacecraft": "Crew-10 (Dragon Endurance)",
        "event": "arrive",
        "date": date(2025, 3, 15),
        "doy": 74,
    },
    {
        "spacecraft": "Crew-10 (Dragon Endurance)",
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
        "spacecraft": "Ax-4 (Dragon)",
        "event": "arrive",
        "date": date(2025, 6, 26),
        "doy": 177,
    },
    {
        "spacecraft": "Ax-4 (Dragon)",
        "event": "depart",
        "date": date(2025, 7, 14),
        "doy": 195,
    },
    # Space X Crew-11
    {
        "spacecraft": "Crew-11 (Dragon Endeavour)",
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

# Get data from dictionary into format of [dock_doy, undock_doy] pairs for each mission. If no dock or undock event, use 0 (docked in 2024) or 366 (undock planned in 2026) as placeholder. 366 to show nicer on graph. Dictionary format better for adding future events if we wwant to expand.
missions = {}
for e in crew_events_2025:
    name = e["spacecraft"]
    if name not in missions:
        missions[name] = {}
    missions[name][e["event"]] = e["doy"]

crewed_missions = [
    [events.get("arrive", 0), events.get("depart", 366)] for events in missions.values()
]

""" Plot mean ISS altitude over 2025 with crewed mission events. Show range of events as shaded region."""


fig, ax = plt.subplots(figsize=(12, 6))
plot = ax.plot(
    day_of_year,
    mean_iss_alt,
    label="Mean ISS Altitude (km)",
    color="blue",
)
ax.set_xlabel("Day of Year (2025)")
ax.set_ylabel("Mean Altitude (km)")
ax.set_title("Mean ISS Altitude in 2025 with Crewed Mission Events")
ax.grid()

# Add shaded regions for crewed missions
for arrive, depart in crewed_missions:
    if arrive < depart:  # Only plot if there's a valid range
        ax.axvspan(arrive, depart, color="orange", alpha=0.3)

# Create legend for shaded regions
orange_patch = mpatches.Patch(
    color="orange", alpha=0.3, label="Crewed Mission Duration"
)
plt.legend(handles=[orange_patch], loc="upper right")
plt.plot(
    plot[0].get_xdata(),
    plot[0].get_ydata(),
    color="blue",
    label="Mean ISS Altitude (km)",
)
plt.show()


# x = [1, 2, 3]
# y = [2, 3, 4]
# plt.plot(x, y)
# plt.show()
