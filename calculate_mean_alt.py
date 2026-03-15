import math

# Earth constants
mu = 398600  # km³/s²  (Earth's gravitational parameter)
r_earth = 6378  # km      (Earth's equatorial radius)


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

print(len(day_of_year) == len(mean_iss_alt))
