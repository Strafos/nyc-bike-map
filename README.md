# NYC Car-Free Bike Map

An interactive map of **38 bike routes (~725 miles)** within a 2-hour journey of Midtown
Manhattan by bike, train, or ferry — nearly all majority **dedicated car-free path**
(greenways, rail trails, boardwalks), plus a couple of legendary on-road classics,
clearly marked.

**[Open the map](https://strafos.github.io/nyc-bike-map/)** — it's a single standalone
`index.html`; everything (route geometry, elevation, metadata) is inlined.

## Features

- Solid lines = dedicated car-free path; dashed colored lines = on-road sections —
  classified per segment from OpenStreetMap way tags, with a measured car-free % per route
- Railway-hatched gray lines = train/subway transfers; dotted = ferries
- Elevation profile, path-vs-road strip, time estimates, train boarding info per route
- Search + filters (car-free %, surface, beach, loops, transit), GPX download, deep links
  (`index.html#maybrook`), CyclOSM bike-infrastructure base layer

## How it's built

- Route geometries: [BRouter](https://brouter.de) (trekking profile) over OpenStreetMap,
  with waypoints anchored to trail geometry verified via Overpass
- Trail extents verified against Rails-to-Trails/TrailLink, county parks departments,
  and trail associations — see [AUDIT.md](AUDIT.md) for the line-by-line coverage audit
- `fetch_routes*.sh` + `fix_routes*.py` download geometry into `data/`;
  `build_data.py` classifies segments and inlines everything into `index.html`
  from `template.html`

```sh
python3 build_data.py   # regenerate index.html from data/ + template.html
```

Map data © OpenStreetMap contributors. Tiles: CARTO, CyclOSM.
