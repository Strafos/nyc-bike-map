#!/bin/bash
# Round 5: exhaustive-sweep additions + full-extent extensions
set -u
cd "$(dirname "$0")/data"

fetch() {
  local id="$1"; local lonlats="$2"
  echo "Fetching $id ..."
  curl -s --max-time 120 "https://brouter.de/brouter?lonlats=${lonlats}&profile=trekking&alternativeidx=0&format=geojson" -o "${id}.geojson"
  if grep -q '"FeatureCollection"' "${id}.geojson"; then
    echo "  OK ($(wc -c < ${id}.geojson) bytes)"
  else
    echo "  FAILED: $(head -c 200 ${id}.geojson)"; echo
  fi
}

# Farmington Canal Heritage Trail: New Haven Union Station -> Hamden -> Cheshire Lock 12
fetch fcht "-72.9270,41.2980|-72.9230,41.3070|-72.9120,41.3730|-72.9180,41.4350|-72.9230,41.4790"

# Sussex Branch Trail: Netcong -> Cranberry Lake -> Andover -> Newton
fetch sussex "-74.7070,40.8980|-74.7220,40.9070|-74.7400,40.9540|-74.7370,41.0090|-74.7530,41.0380"

# Jamaica Bay Greenway loop from Broad Channel (CCW: Rockaway -> Riis -> Gil Hodges Br -> Floyd Bennett -> Plumb Beach -> Canarsie -> Shirley Chisholm -> Howard Beach)
fetch jamaica-bay "-73.8159,40.6088|-73.8230,40.5850|-73.8770,40.5673|-73.8950,40.5900|-73.9170,40.5840|-73.8830,40.6260|-73.8700,40.6480|-73.8430,40.6570|-73.8159,40.6088"

# Port Jefferson mega-route: Setauket greenway -> station -> North Shore Rail Trail -> Wading River
fetch port-jefferson "-73.0940,40.9410|-73.0560,40.9290|-73.0531,40.9357|-73.0290,40.9320|-72.9200,40.9390|-72.8440,40.9460"

# Henry Hudson Trail: extend to Popamora Point / Highlands (meets the Sandy Hook route)
fetch hht "-74.2249,40.4147|-74.1780,40.4460|-74.1300,40.4440|-74.0980,40.4330|-74.0330,40.4140|-73.9990,40.4090"

# Cuomo/Nyack: extend Hook Mountain path to Haverstraw waterfront
fetch cuomo "-73.8662,41.0762|-73.8730,41.0700|-73.9180,41.0830|-73.9180,41.0907|-73.9170,41.1030|-73.9230,41.1350|-73.9690,41.1930"

echo "Done."
