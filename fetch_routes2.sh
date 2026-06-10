#!/bin/bash
# Round 2: expand to full 2-hour journey radius
set -u
cd "$(dirname "$0")/data"

fetch() {
  local id="$1"; local lonlats="$2"
  echo "Fetching $id ..."
  curl -s --max-time 90 "https://brouter.de/brouter?lonlats=${lonlats}&profile=trekking&alternativeidx=0&format=geojson" -o "${id}.geojson"
  if grep -q '"FeatureCollection"' "${id}.geojson"; then
    echo "  OK ($(wc -c < ${id}.geojson) bytes)"
  else
    echo "  FAILED: $(head -c 200 ${id}.geojson)"; echo
  fi
}

HOME_PT="-73.9819,40.7681"  # Columbus Circle (legacy; superseded by fetch_routes6.sh)

# 13. Prospect Park + Ocean Parkway -> Coney Island
fetch coney "${HOME_PT}|-73.9795,40.7912|-74.0041,40.7128|-73.9701,40.6743|-73.9740,40.6610|-73.9720,40.6532|-73.9680,40.6250|-73.9620,40.5770|-73.9810,40.5737"

# 14. Mosholu-Pelham greenways -> Orchard Beach & City Island
fetch pelham "${HOME_PT}|-73.9795,40.7912|-73.9320,40.8718|-73.9106,40.8743|-73.8790,40.8730|-73.8550,40.8570|-73.8210,40.8530|-73.7945,40.8670|-73.7860,40.8470"

# 15. Bronx River Pathway: Kensico Dam (Valhalla) -> Bronx Park (train out, ride back)
fetch bronx-river "-73.7660,41.0710|-73.7760,41.0330|-73.8030,40.9900|-73.8320,40.9380|-73.8510,40.9120|-73.8660,40.8900|-73.8830,40.8650"

# 16. Old Croton Aqueduct: Croton-Harmon -> Van Cortlandt Park
fetch oca "-73.8821,41.1900|-73.8640,41.1610|-73.8620,41.0890|-73.8680,41.0390|-73.8720,41.0140|-73.8950,40.9550|-73.8967,40.8867"

# 17. GWB -> Palisades Henry Hudson Dr -> Piermont -> Old Erie Path -> Nyack
fetch piermont "${HOME_PT}|-73.9795,40.7912|-73.9468,40.8500|-73.9710,40.8505|-73.9180,40.9460|-73.9170,41.0100|-73.9182,41.0404|-73.9210,41.0800|-73.9180,41.0907"

# 18. Staten Island Ferry -> FDR Boardwalk (South/Midland Beach)
fetch staten "-74.0733,40.6437|-74.0630,40.6060|-74.0600,40.5950|-74.0930,40.5640"

# 19. Liberty State Park loop
fetch liberty "-74.0431,40.7077|-74.0330,40.7036|-74.0440,40.6950|-74.0580,40.6930"

# 20. Maybrook Trailway + Dutchess Rail Trail: Southeast -> Hopewell Jct -> Poughkeepsie
fetch maybrook "-73.6029,41.4153|-73.6480,41.4790|-73.7300,41.5380|-73.8040,41.5840|-73.8900,41.6660|-73.9379,41.7065"

# 21. Harlem Valley Rail Trail: Wassaic -> Millerton
fetch harlem-valley "-73.5600,41.7920|-73.5560,41.8480|-73.5110,41.9520"

# 22. D&R Canal Towpath: Princeton -> New Brunswick
fetch dr-canal "-74.6590,40.3430|-74.6130,40.3760|-74.6090,40.4310|-74.5310,40.5530|-74.4480,40.4980|-74.4440,40.5000"

# 23. Columbia Trail: High Bridge -> Long Valley
fetch columbia "-74.8950,40.6660|-74.8390,40.7190|-74.7800,40.7860"

# 24. Pequonnock River Trail: Bridgeport -> Monroe
fetch pequonnock "-73.1870,41.1780|-73.2000,41.2430|-73.2070,41.3050"

# 25. Massapequa Preserve + Bethpage Bikeway: Massapequa -> Bethpage State Park
fetch massapequa "-73.4700,40.6776|-73.4560,40.7080|-73.4660,40.7450"

# 26. Albany-Hudson Electric Trail: Hudson -> Kinderhook (Amtrak Empire Service)
fetch ahet "-73.7910,42.2520|-73.7440,42.3210|-73.7080,42.3950"

echo "Done."
