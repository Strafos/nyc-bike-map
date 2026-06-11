#!/bin/bash
# Round 7: Philly extension — high-signal trails reachable by Amtrak/NJT/SEPTA.
set -u
cd "$(dirname "$0")/data"

fetch() {
  local id="$1"; local lonlats="$2"
  echo "Fetching $id ..."
  curl -s --max-time 120 "https://brouter.de/brouter?lonlats=${lonlats}&profile=trekking&alternativeidx=0&format=geojson" -o "${id}.geojson"
  if grep -q '"FeatureCollection"' "${id}.geojson"; then
    echo "  OK ($(wc -c < "${id}.geojson") bytes)"
  else
    echo "  FAILED: $(head -c 200 "${id}.geojson")"; echo
  fi
}

# Schuylkill River Trail: Center City/30th St -> Manayunk -> Norristown -> Valley Forge -> Phoenixville.
fetch philly-schuylkill "-75.1820,39.9568|-75.1900,39.9630|-75.2070,40.0100|-75.2230,40.0230|-75.2560,40.0450|-75.3060,40.0670|-75.3440,40.1140|-75.4210,40.1010|-75.5150,40.1330"

# Wissahickon Valley: Falls Bridge / SRT -> Forbidden Drive -> Chestnut Hill edge.
fetch philly-wissahickon "-75.2070,40.0100|-75.2200,40.0200|-75.2240,40.0400|-75.2245,40.0600|-75.2180,40.0790"

# Pennypack: SEPTA Fox Chase -> Pennypack Park/Lorimer corridor toward the northeast suburbs.
fetch philly-pennypack "-75.0836,40.0760|-75.0710,40.0840|-75.0530,40.0940|-75.0390,40.1080|-75.0190,40.1250|-75.0020,40.1440"

# Chester Valley Trail: Valley Forge / King of Prussia edge -> Exton.
fetch philly-chester-valley "-75.5150,40.0440|-75.5400,40.0550|-75.5850,40.0580|-75.6300,40.0590|-75.6540,40.0290"

# Cynwyd Heritage Trail + Manayunk Bridge connector from the Schuylkill corridor.
fetch philly-cynwyd "-75.2320,40.0080|-75.2335,40.0167|-75.2240,40.0290"

# Delaware River Trail: South Philly riverfront -> Penn's Landing -> Penn Treaty.
fetch philly-delaware "-75.1410,39.9300|-75.1420,39.9460|-75.1400,39.9540|-75.1340,39.9690"

echo "Done."
