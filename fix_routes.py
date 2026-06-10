#!/usr/bin/env python3
"""Re-fetch problem routes using anchor points sampled from the actual OSM trail geometry."""
import json, subprocess, time, urllib.parse, collections

BBOX = "(40.0,-75.2,42.3,-72.5)"

def overpass(name_re, bbox=BBOX):
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
            print(f"  overpass retry {attempt+1} for {name_re[:30]}")
    else:
        raise RuntimeError(f"overpass failed: {name_re}")
    pts = []
    for el in d.get("elements", []):
        for g in el.get("geometry", []) or []:
            pts.append((g["lat"], g["lon"]))
    print(f"  {name_re[:40]}: {len(pts)} pts")
    return pts

def anchors(pts, n, axis):
    """n points spread along the trail, sorted by lat (axis=0) or lon (axis=1)."""
    pts = sorted(set(pts), key=lambda p: p[axis])
    if len(pts) < n:
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
    tags = collections.Counter()
    DED = {"cycleway", "path", "footway", "pedestrian", "track", "bridleway", "steps"}
    ded = tot = 0
    for m in p["messages"][1:]:
        tagstr = m[9].split()
        hw = next((t.split("=", 1)[1] for t in tagstr if t.startswith("highway=")), "")
        dist = int(m[3])
        ok = hw in DED or (hw == "service" and ("bicycle=designated" in tagstr or "motor_vehicle=no" in tagstr))
        ded += dist * ok
        tot += dist
    print(f"  {rid}: {int(p['track-length'])/1000*0.621:.1f} mi, {100*ded//max(tot,1)}% car-free")

def lonlats(*points):
    return "|".join(f"{lon},{lat}" for lat, lon in points)

# (route id, [(label, name_regex, n_anchors, axis, lat_range)], start point, end point)
print("querying OSM trail geometries...")
mb = anchors(overpass("Maybrook Trailway"), 6, 0)
drt = anchors(overpass("Dutchess Rail Trail|William R. Steinhaus"), 4, 1)
hv = anchors(overpass("Harlem Valley Rail Trail"), 8, 0)
hvrt = anchors(overpass("Hudson Valley Rail Trail"), 3, 1)
wv = anchors(overpass("Wallkill Valley Rail Trail"), 5, 0)
hht = anchors(overpass("Henry Hudson Trail"), 8, 1)
bb = anchors(overpass("Bethpage Bikeway"), 6, 0)
ns = anchors(overpass("North Shore Rail Trail"), 5, 1)
pq = anchors(overpass("Pequonnock River Trail"), 6, 0)
sb = anchors(overpass("Sussex Branch Trail"), 5, 0)
sr = anchors(overpass("Saddle River Pathway|Saddle River County Park"), 5, 0)
dr = anchors(overpass("Delaware and Raritan Canal", "(40.30,-74.80,40.56,-74.40)"), 6, 0)
time.sleep(1)

print("re-fetching routes through on-trail anchors...")
# Maybrook + Dutchess: Southeast station -> trail -> Hopewell -> DRT -> Poughkeepsie
fetch("maybrook", lonlats((41.4153, -73.6029), *mb, *sorted(drt, key=lambda p: -p[1]), (41.7065, -73.9379)))
# Harlem Valley: Wassaic station -> Copake Falls
fetch("harlem-valley", lonlats((41.7920, -73.5600), *hv))
# Walkway: Poughkeepsie -> walkway -> HVRT -> New Paltz -> WVRT north -> Kingston
fetch("walkway", lonlats((41.7065, -73.9379), (41.7107, -73.9217), *sorted(hvrt, key=lambda p: -p[1]),
                         (41.7480, -74.0838), *wv, (41.9270, -74.0210)))
# Henry Hudson Trail: Matawan -> Popamora Point (sort west->east)
fetch("hht", lonlats((40.4147, -74.2249), *hht, (40.4090, -73.9990)))
# Bethpage Bikeway: Massapequa -> Syosset
fetch("massapequa", lonlats((40.6776, -73.4700), *bb, (40.8252, -73.4990)))
# Port Jefferson: Setauket greenway -> station -> NSRT -> Wading River
fetch("port-jefferson", lonlats((40.9410, -73.0940), (40.9290, -73.0560), (40.9357, -73.0531), *ns))
# Pequonnock: Bridgeport station -> Newtown line
fetch("pequonnock", lonlats((41.1780, -73.1870), *pq))
# Sussex Branch: Netcong -> Newton
fetch("sussex", lonlats((40.8980, -74.7070), *sb))
# Saddle River: Ridgewood -> Rochelle Park (north->south)
fetch("saddle-river", lonlats((40.9810, -74.1170), *sorted(sr, key=lambda p: -p[0])))
# D&R: Princeton -> canal anchors (south->north) -> New Brunswick
fetch("dr-canal", lonlats((40.3430, -74.6590), *dr, (40.5530, -74.5310), (40.5000, -74.4440)))
print("done")
