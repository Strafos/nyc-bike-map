#!/bin/bash
# Round 4: extend routes to true full trail extents (verified against county/trail sources)
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

HOME_PT="-73.9819,40.7681"  # Columbus Circle (legacy; superseded by fetch_routes6.sh)

# HVRT now 23 continuous mi: Wassaic -> Millerton -> Under Mountain Rd -> Copake Falls (Taconic SP)
fetch harlem-valley "-73.5600,41.7920|-73.5560,41.8480|-73.5110,41.9520|-73.5440,42.0290|-73.5220,42.1170"

# Walkway + HVRT to New Paltz, continuing on Wallkill Valley RT to the Rosendale trestle
fetch walkway "-73.9379,41.7065|-73.9217,41.7107|-73.9610,41.7117|-74.0838,41.7480|-74.0780,41.8450"

# Bethpage Bikeway full 13+ mi: Massapequa -> Bethpage SP -> Trail View SP -> Syosset LIRR
fetch massapequa "-73.4700,40.6776|-73.4560,40.7080|-73.4660,40.7450|-73.4790,40.7770|-73.4830,40.8060|-73.4990,40.8252"

# Pequonnock corridor extends to the Newtown town line (Swamp Rd)
fetch pequonnock "-73.1870,41.1780|-73.2000,41.2430|-73.2070,41.3050|-73.2400,41.3550"

# Jones Beach + Ocean Parkway Coastal Greenway east to Captree
fetch jones-beach "-73.5107,40.6837|-73.5057,40.6670|-73.5080,40.6300|-73.5070,40.5963|-73.4350,40.6090|-73.3920,40.6170|-73.2680,40.6450"

# Bronx River Pathway/Greenway: Kensico Dam all the way south to Soundview Park
fetch bronx-river "-73.7660,41.0710|-73.7760,41.0330|-73.8030,40.9900|-73.8320,40.9380|-73.8510,40.9120|-73.8660,40.8900|-73.8830,40.8650|-73.8800,40.8340|-73.8840,40.8224|-73.8720,40.8120"

# Old Croton Aqueduct: start at Croton Gorge Park (the dam - true northern terminus)
fetch oca "-73.8576,41.2247|-73.8660,41.2080|-73.8640,41.1610|-73.8620,41.0890|-73.8680,41.0390|-73.8720,41.0140|-73.8950,40.9550|-73.8967,40.8867"

# Staten Island: boardwalk continues via Gateway NRA to Great Kills Park
fetch staten "-74.0733,40.6437|-74.0630,40.6060|-74.0600,40.5950|-74.0930,40.5640|-74.1080,40.5530|-74.1190,40.5450"

# Cuomo bridge -> Nyack, then Nyack Beach SP river path toward Hook Mountain
fetch cuomo "-73.8662,41.0762|-73.8730,41.0700|-73.9180,41.0830|-73.9180,41.0907|-73.9170,41.1030|-73.9230,41.1350"

# Long Beach boardwalk + Lido Blvd path east to Point Lookout
fetch long-beach "-73.6580,40.5887|-73.6750,40.5815|-73.6440,40.5855|-73.6000,40.5895|-73.5800,40.5925"

# Columbia Trail full length: High Bridge -> Long Valley -> Bartley Rd (Flanders)
fetch columbia "-74.8950,40.6660|-74.8390,40.7190|-74.7800,40.7860|-74.7300,40.8030"

# AHET continues north: Hudson -> Kinderhook -> Niverville (trail goes on to Albany)
fetch ahet "-73.7910,42.2520|-73.7440,42.3210|-73.7080,42.3950|-73.6620,42.4450"

# Shore Parkway path continues east past the Verrazzano to Caesar's Bay (Bensonhurst)
fetch brooklyn "${HOME_PT}|-73.9795,40.7912|-74.0133,40.7177|-74.0041,40.7128|-73.9955,40.7027|-73.9967,40.6984|-74.0107,40.6753|-74.0337,40.6420|-74.0345,40.6065|-74.0030,40.5970"

# Rockaway: continue west past Riis into Fort Tilden
fetch rockaway "-73.8159,40.6088|-73.8210,40.5870|-73.8400,40.5780|-73.8770,40.5673|-73.8950,40.5610"

echo "Done."
