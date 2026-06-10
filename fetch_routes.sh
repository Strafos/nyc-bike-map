#!/bin/bash
# Fetch bike route geometries from BRouter (trekking profile prefers cycleways/greenways)
set -u
cd "$(dirname "$0")/data"

fetch() {
  local id="$1"; local lonlats="$2"
  echo "Fetching $id ..."
  curl -s --max-time 90 "https://brouter.de/brouter?lonlats=${lonlats}&profile=trekking&alternativeidx=0&format=geojson" -o "${id}.geojson"
  # quick sanity check
  if grep -q '"FeatureCollection"' "${id}.geojson"; then
    echo "  OK ($(wc -c < ${id}.geojson) bytes)"
  else
    echo "  FAILED: $(head -c 200 ${id}.geojson)"
  fi
}

HOME_PT="-73.9819,40.7681"   # Columbus Circle (legacy; superseded by fetch_routes6.sh)

# 1. Central Park loop (counterclockwise)
fetch central-park "${HOME_PT}|-73.9648,40.7880|-73.9745,40.7756|-73.9810,40.7685|-73.9732,40.7647|-73.9660,40.7723|-73.9590,40.7848|-73.9527,40.7975|-73.9633,40.7925|-73.9648,40.7880|${HOME_PT}"

# 2. Hudson River Greenway south to Battery
fetch hrg-south "${HOME_PT}|-73.9795,40.7912|-73.9933,40.7717|-74.0102,40.7328|-74.0157,40.7046"

# 3. Hudson River Greenway north to GWB & Inwood
fetch hrg-north "${HOME_PT}|-73.9795,40.7912|-73.9596,40.8186|-73.9468,40.8500|-73.9320,40.8718"

# 4. Manhattan Waterfront Greenway full loop
fetch waterfront-loop "${HOME_PT}|-73.9795,40.7912|-74.0157,40.7046|-73.9737,40.7195|-73.9704,40.7437|-73.9420,40.7770|-73.9290,40.8023|-73.9339,40.8278|-73.9217,40.8597|-73.9320,40.8718|-73.9596,40.8186|-73.9795,40.7912|${HOME_PT}"

# 5. Brooklyn Bridge -> Brooklyn Waterfront Greenway -> Verrazzano
fetch brooklyn "${HOME_PT}|-73.9795,40.7912|-74.0133,40.7177|-74.0041,40.7128|-73.9955,40.7027|-73.9967,40.6984|-74.0107,40.6753|-74.0337,40.6420|-74.0345,40.6065"

# 6. Empire State Trail north: Putnam corridor to Brewster
fetch empire-north "${HOME_PT}|-73.9795,40.7912|-73.9320,40.8718|-73.8967,40.8867|-73.8430,40.9650|-73.8160,41.0540|-73.8257,41.1456|-73.7929,41.1990|-73.7787,41.2709|-73.7387,41.3723|-73.6840,41.4304|-73.6168,41.3946"

# 7. Governors Island loop (from ferry landing)
fetch governors "-74.0145,40.6918|-74.0202,40.6877|-74.0163,40.6838|-74.0102,40.6862|-74.0145,40.6918"

# 8. Walkway Over the Hudson + Hudson Valley Rail Trail to New Paltz
fetch walkway "-73.9379,41.7065|-73.9217,41.7107|-73.9610,41.7117|-74.0838,41.7480"

# 9. Tarrytown -> Mario Cuomo Bridge path -> Nyack
fetch cuomo "-73.8662,41.0762|-73.8730,41.0700|-73.9180,41.0830|-73.9180,41.0907"

# 10. Wantagh -> Jones Beach (Ellen Farrant Memorial Bikeway)
fetch jones-beach "-73.5107,40.6837|-73.5057,40.6670|-73.5080,40.6300|-73.5070,40.5963"

# 11. Broad Channel -> Rockaway boardwalk -> Riis Park
fetch rockaway "-73.8159,40.6088|-73.8210,40.5870|-73.8400,40.5780|-73.8770,40.5673"

# 12. Randall's Island via Central Park + 103rd St footbridge
fetch randalls "${HOME_PT}|-73.9648,40.7880|-73.9590,40.7847|-73.9390,40.7858|-73.9213,40.7931|-73.9201,40.8006"

echo "Done."
