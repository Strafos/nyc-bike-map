#!/bin/bash
# Round 3: fill directional gaps — lower harbor, Queens, Orange County, Bergen, far LI
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

# 27. Seastreak ferry -> Highlands -> Sandy Hook multi-use path to Fort Hancock
fetch sandy-hook "-73.9870,40.4030|-73.9905,40.4155|-74.0000,40.4400|-74.0030,40.4620"

# 28. Henry Hudson Trail: Aberdeen-Matawan -> Atlantic Highlands (NJ bayshore)
fetch hht "-74.2249,40.4147|-74.1780,40.4460|-74.1300,40.4440|-74.0980,40.4330|-74.0330,40.4140"

# 29. LIRR -> Long Beach boardwalk
fetch long-beach "-73.6580,40.5887|-73.6440,40.5855|-73.6750,40.5815"

# 30. Eastern Queens Greenway: Flushing Meadows -> Kissena -> Vanderbilt Motor Pkwy -> Alley Pond -> Little Neck Bay -> Fort Totten
fetch queens-greenway "-73.8456,40.7547|-73.8448,40.7460|-73.8400,40.7280|-73.8060,40.7450|-73.7680,40.7350|-73.7350,40.7440|-73.7560,40.7700|-73.7770,40.7900"

# 31. Setauket - Port Jefferson Station Greenway
fetch port-jefferson "-73.0531,40.9357|-73.0560,40.9290|-73.0940,40.9410"

# 32. Saddle River County Park path: Ridgewood -> Rochelle Park
fetch saddle-river "-74.1170,40.9810|-74.0980,40.9690|-74.0900,40.9400|-74.0840,40.9070"

# 33. Heritage Trail: Harriman -> Monroe -> Chester -> Goshen -> Middletown
fetch heritage "-74.1440,41.3093|-74.1870,41.3300|-74.2710,41.3470|-74.3240,41.4020|-74.4230,41.4460"

# 34. Bear Mountain classic: Peekskill -> goat trail -> Bear Mtn Bridge -> Perkins Drive summit (on-road classic)
fetch bear-mountain "-73.9300,41.2857|-73.9430,41.3050|-73.9870,41.3215|-73.9890,41.3125|-74.0064,41.3105"

echo "Done."
