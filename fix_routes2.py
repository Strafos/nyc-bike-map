#!/usr/bin/env python3
"""Round 2: constrain trail queries to the correct branch via tight bboxes."""
import json, subprocess, time, collections

def overpass(name_re, bbox):
    q = f'[out:json][timeout:80];(way["name"~"{name_re}"]["highway"]{bbox};);out geom 800;'
    for attempt in range(5):
        time.sleep(3 if attempt == 0 else 15)
        out = subprocess.run(
            ["curl", "-s", "--max-time", "90", "https://overpass-api.de/api/interpreter",
             "--data-urlencode", "data=" + q],
            capture_output=True, text=True).stdout
        try:
            d = json.loads(out)
            break
        except json.JSONDecodeError:
            print(f"  overpass retry {attempt+1}")
    else:
        raise RuntimeError(f"overpass failed: {name_re}")
    pts = [(g["lat"], g["lon"]) for el in d.get("elements", []) for g in el.get("geometry", []) or []]
    print(f"  {name_re[:45]}: {len(pts)} pts")
    return pts

def anchors(pts, n, axis):
    pts = sorted(set(pts), key=lambda p: p[axis])
    if len(pts) <= n:
        return pts
    return [pts[int(i * (len(pts) - 1) / (n - 1))] for i in range(n)]

def fetch(rid, lonlats):
    url = f"https://brouter.de/brouter?lonlats={lonlats}&profile=trekking&alternativeidx=0&format=geojson"
    out = subprocess.run(["curl", "-s", "--max-time", "120", url], capture_output=True, text=True).stdout
    if '"FeatureCollection"' not in out:
        print(f"  {rid}: FAILED {out[:120]}")
        return
    open(f"data/{rid}.geojson", "w").write(out)
    d = json.loads(out)
    p = d["features"][0]["properties"]
    DED = {"cycleway", "path", "footway", "pedestrian", "track", "bridleway", "steps"}
    ded = tot = 0
    for m in p["messages"][1:]:
        ts = m[9].split()
        hw = next((t.split("=", 1)[1] for t in ts if t.startswith("highway=")), "")
        ok = hw in DED or (hw == "service" and ("bicycle=designated" in ts or "motor_vehicle=no" in ts))
        ded += int(m[3]) * ok
        tot += int(m[3])
    print(f"  {rid}: {int(p['track-length'])/1000*0.621:.1f} mi, {100*ded//max(tot,1)}% car-free")

def lonlats(*points):
    return "|".join(f"{lon},{lat}" for lat, lon in points)

# Maybrook arm only (exclude Danbury branch east of -73.58)
mb = anchors(overpass("Maybrook Trailway", "(41.40,-73.95,41.60,-73.58)"), 5, 0)
drt = anchors(overpass("Dutchess Rail Trail|William R. Steinhaus", "(41.55,-74.00,41.72,-73.75)"), 4, 1)
# Wallkill north of New Paltz only
wv = anchors(overpass("Wallkill Valley Rail Trail", "(41.745,-74.15,41.93,-74.02)"), 5, 0)
hvrt = anchors(overpass("Hudson Valley Rail Trail", "(41.70,-74.10,41.76,-73.93)"), 3, 1)
# HHT bayshore arm only
hh = anchors(overpass("Henry Hudson Trail", "(40.405,-74.24,40.48,-73.98)"), 7, 1)
# Pequonnock incl. alternate names
pq = anchors(overpass("Pequonnock|Housatonic Rail", "(41.17,-73.30,41.40,-73.15)"), 7, 0)
# D&R towpath ('&' spelling)
dr = anchors(overpass("Raritan Canal", "(40.32,-74.75,40.55,-74.42)"), 6, 0)

print("fetching...")
fetch("maybrook", lonlats((41.4153, -73.6029), *mb, *sorted(drt, key=lambda p: -p[1]), (41.7065, -73.9379)))
fetch("walkway", lonlats((41.7065, -73.9379), (41.7107, -73.9217), *sorted(hvrt, key=lambda p: -p[1]),
                         (41.7480, -74.0838), *wv, (41.9270, -74.0210)))
fetch("hht", lonlats((40.4147, -74.2249), *hh, (40.4090, -73.9990)))
fetch("pequonnock", lonlats((41.1780, -73.1870), *pq))
fetch("dr-canal", lonlats((40.3430, -74.6590), *dr, (40.5530, -74.5310), (40.5000, -74.4440)))
print("done")
