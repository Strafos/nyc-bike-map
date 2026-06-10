#!/usr/bin/env python3
"""Combine BRouter geojson tracks + metadata into routes.js for the map."""
import json, os

DATA = os.path.join(os.path.dirname(__file__), 'data')

# ways physically separated from car traffic
DEDICATED_HW = {'cycleway', 'path', 'footway', 'pedestrian', 'track', 'bridleway', 'steps'}

def way_class(waytags, prev):
    """1 = dedicated car-free path, 0 = on road."""
    tags = waytags.split()
    hw = next((t.split('=', 1)[1] for t in tags if t.startswith('highway=')), None)
    if hw is None:
        return prev
    if hw in DEDICATED_HW:
        return 1
    if hw == 'service' and ('bicycle=designated' in tags or 'motor_vehicle=no' in tags or 'vehicle=no' in tags):
        return 1  # car-banned park drives etc.
    return 0

def coords(fid, step_target=900):
    d = json.load(open(os.path.join(DATA, f'{fid}.geojson')))
    feat = d['features'][0]
    c = feat['geometry']['coordinates']
    p = feat['properties']

    # classify every track point from the per-way messages
    parsed, prev = [], 1
    for m in (p.get('messages') or [])[1:]:
        prev = way_class(m[9], prev)
        parsed.append((int(m[0]), int(m[1]), prev, int(m[3])))
    full, j, cur = [], 0, (parsed[0][2] if parsed else 1)
    for pt in c:
        full.append(parsed[j][2] if j < len(parsed) else cur)
        if j < len(parsed) and round(pt[0] * 1e6) == parsed[j][0] and round(pt[1] * 1e6) == parsed[j][1]:
            cur = parsed[j][2]
            j += 1
    ded = sum(d for _, _, cl, d in parsed if cl == 1)
    tot = sum(d for _, _, _, d in parsed) or 1
    pathpct = round(100 * ded / tot)

    step = max(1, len(c) // step_target)
    idx = list(range(0, len(c), step))
    if idx[-1] != len(c) - 1:
        idx.append(len(c) - 1)
    pts = [c[i] for i in idx]
    cls = [full[i] for i in idx]
    runs = []  # run-length encoding: [end_index_exclusive, class]
    for i, cl in enumerate(cls):
        if runs and runs[-1][1] == cl:
            runs[-1][0] = i + 1
        else:
            runs.append([i + 1, cl])

    stats = {
        'mi': round(int(p['track-length']) / 1000 * 0.621371, 1),
        'climb_ft': round(int(p.get('filtered ascend', 0)) * 3.281),
        'pathpct': pathpct,
    }
    ele = [round((pt[2] if len(pt) > 2 else 0) * 3.281) for pt in pts]
    return [[round(pt[1], 5), round(pt[0], 5)] for pt in pts], ele, runs, stats

# Governors Island perimeter loop — hand-drawn (BRouter zigzags on the island)
GOV_LOOP = [
    [40.6932, -74.0157], [40.6928, -74.0135], [40.6925, -74.0118], [40.6915, -74.0100],
    [40.6905, -74.0085], [40.6890, -74.0062], [40.6875, -74.0042], [40.6862, -74.0030],
    [40.6848, -74.0042], [40.6838, -74.0055], [40.6826, -74.0082], [40.6817, -74.0108],
    [40.6813, -74.0128], [40.6818, -74.0152], [40.6830, -74.0175], [40.6845, -74.0192],
    [40.6862, -74.0205], [40.6880, -74.0212], [40.6895, -74.0207], [40.6908, -74.0195],
    [40.6920, -74.0178], [40.6932, -74.0157],
]

ROUTES = [
    # ============ RIDE FROM YOUR DOOR ============
    dict(id='central-park', group='ride', color='#2e7d32', name='Central Park Loop',
         tagline='The classic — fully car-free since 2018',
         carfree=100, time='45–75 min',
         desc="Cars were banned from Central Park's drives in 2018, so the full 6.1-mile loop is yours, starting straight from Columbus Circle's Merchants' Gate. Ride counterclockwise (one-way for bikes): north on East Drive, south on West Drive.",
         notes=["Harlem Hill (north end) is the only real climb — 0.3 mi at ~4-5%",
                "Cut the loop short via the 102nd St or 72nd St transverse crossings",
                "Watch for runners and horse carriages south of 72nd St"],
         oneway=False),
    dict(id='hrg-south', group='ride', color='#1565c0', name='Hudson River Greenway → Battery Park',
         tagline='Busiest bike path in America, 100% car-free',
         carfree=95, time='40–60 min each way',
         desc="One block west of Columbus Circle the greenway begins at W 59th St; from there it's an uninterrupted car-free waterfront path all the way to the southern tip of Manhattan. Pass the Boat Basin, Pier 84, the Intrepid, Little Island, Tribeca piers, and finish at the Battery with harbor views.",
         notes=["Essentially car-free from the W 59th St entrance onward",
                "Gets crowded below 14th St on weekends — go early",
                "Connects onward to the Brooklyn Bridge, Staten Island Ferry and Governors Island ferry"],
         oneway=True),
    dict(id='hrg-north', group='ride', color='#00838f', name='Greenway North → Little Red Lighthouse & Inwood',
         tagline='Cherry Walk, the GWB, and the quiet end of Manhattan',
         carfree=95, time='45–70 min each way',
         desc="The northern half of the Hudson River Greenway is the quiet half: the Cherry Walk hugs the water from 100th to 125th St, then Fort Washington Park brings you to the Little Red Lighthouse directly under the George Washington Bridge. Continue to Dyckman St and the ballfields at Inwood.",
         notes=["Spectacular in April when the cherry trees bloom",
                "Optional: climb up to the GWB and cross into NJ (see Piermont/Nyack route)",
                "Combine with the Harlem River side for a top-of-Manhattan loop"],
         oneway=True),
    dict(id='randalls', group='ride', color='#558b2f', name="Randall's Island via Central Park",
         tagline='Car-free island of ballfields over a pedestrian-only bridge',
         carfree=85, time='1–1.5 hours round trip',
         desc="Cross Central Park on the loop drives, exit at Engineers' Gate (E 90th), and take the East River esplanade north to the 103rd St footbridge — a pedestrian/bike-only span onto Randall's Island. The island is laced with car-free paths, waterfront loops, and connects onward to the Bronx via the RFK shared path.",
         notes=["Short on-street crosstown blocks between the park and the river esplanade",
                "The 103rd St footbridge (Wards Island Bridge) is bikes & pedestrians only",
                "Island perimeter path ≈ 4 mi with skyline + Hell Gate Bridge views",
                "Continue to the Bronx via the car-free Randall's Island Connector"],
         oneway=True),
    dict(id='waterfront-loop', group='ride', color='#6a1b9a', name='Manhattan Waterfront Greenway — Full Loop',
         tagline='Circumnavigate the island, ~32 miles',
         carfree=85, time='3–4.5 hours',
         desc="The big one: all the way around Manhattan. Hudson River Greenway south, around the Battery, up the East River Esplanade past the bridges, Carl Schurz Park, the Harlem River, Swindler Cove, over the top at Inwood and back down the Hudson. A genuine NYC rite of passage.",
         notes=["Main on-street gap: East Midtown ~E 41st–E 60th St (marked lanes, busy traffic)",
                "Short street sections in East Harlem and Washington Heights",
                "East River Esplanade sections occasionally close for construction — check NYC DOT alerts",
                "Bring water; few services along the Harlem River stretch"],
         oneway=False),
    dict(id='coney', group='ride', color='#d81b60', name='Prospect Park + Ocean Parkway → Coney Island',
         tagline="America's first bike path, ending at the boardwalk",
         carfree=85, time='~2 hours each way (subway back option)',
         desc="Down the greenway, over the Brooklyn Bridge, and into Prospect Park's car-free loop drive. Exit at Park Circle onto the Ocean Parkway Malls path — opened in 1894 as the first dedicated bike path in America — and ride it dead straight to the Riegelmann Boardwalk, Nathan's, and the Cyclone.",
         notes=["Car-free: greenway, bridge, Prospect Park loop, Ocean Pkwy path, boardwalk",
                "On-street: ~1.5 mi through Downtown Brooklyn between the bridge and the park",
                "Ocean Pkwy path crosses many side streets — keep speed reasonable",
                "Return: D/F/N/Q from Coney Island–Stillwell Av (bikes allowed on subway), or loop back via the Shore Parkway waterfront path"],
         oneway=True),
    dict(id='brooklyn', group='ride', color='#c62828', name='Brooklyn Bridge → Waterfront Greenway → Verrazzano',
         tagline='Over the famous bridge, then harbor views to Bay Ridge',
         carfree=75, time='2–3 hours one way',
         desc="Down the Hudson Greenway, across the Brooklyn Bridge on its protected two-way bike lane (opened 2021), through Brooklyn Bridge Park and Red Hook, then onto the Shore Parkway waterfront path with the Verrazzano-Narrows Bridge growing in front of you the whole way.",
         notes=["Car-free: greenway, bridge, Brooklyn Bridge Park, Shore Parkway path",
                "On-street: Red Hook & Sunset Park (~3 mi, mostly marked/protected lanes on Columbia St)",
                "Return option: R train from Bay Ridge–95 St (bikes allowed on subway, ~70 min)",
                "Detour: Valentino Pier in Red Hook for the best Statue of Liberty view + Steve's key lime pie",
                "The Shore Parkway path east of the Verrazzano to Caesar's Bay (Bensonhurst) is drawn — from there it's ~2 more mi to Coney Island"],
         oneway=True),
    dict(id='pelham', group='ride', color='#7cb342', name='Mosholu–Pelham Greenway → Orchard Beach & City Island',
         tagline="The Bronx's parkway greenways to a beach and a fishing village",
         carfree=80, time='~2 hours each way (6-train back option)',
         desc="Up the greenway to Inwood, across the Broadway Bridge, through Van Cortlandt Park, then east on the Mosholu Parkway greenway path, past the Botanical Garden, and along the Pelham Parkway path into Pelham Bay Park — NYC's largest park. Finish on the Orchard Beach promenade or cross the bridge to City Island for seafood shacks.",
         notes=["Greenway paths run beside the parkways — separated from traffic, frequent cross streets",
                "Short on-street links in Norwood and around Bronx Park (~2 mi total)",
                "City Island itself is on-road (quiet, one main street)",
                "Bail-out: 6 train from Pelham Bay Park station (bikes allowed on subway)",
                "Pelham Bay Park has miles of additional car-free trails (Hunter Island, lagoon)"],
         oneway=True),
    dict(id='piermont', group='ride', color='#5d4037', name='GWB → Palisades → Piermont → Old Erie Path → Nyack',
         tagline='The legendary north-Jersey ride, done the low-traffic way',
         carfree=60, time='3+ hours one way — take the train home from Tarrytown',
         desc="Cross the George Washington Bridge's car-free path, drop into Palisades Interstate Park, and take Henry Hudson Drive — a scenic park road with very light, slow traffic — under the cliffs to Alpine. A short stretch of 9W leads to Piermont's marsh-side village, then the car-free Old Erie Path rail trail runs along the cliff to Nyack. Come home over the Cuomo Bridge path and the Hudson Line from Tarrytown.",
         notes=["Honest disclosure: ~60% car-free. Henry Hudson Drive is a park road shared with light seasonal car traffic; ~3 mi of US-9W has a shoulder, not a lane",
                "GWB south path, Old Erie Path and Joseph B. Clarke Rail Trail are fully car-free",
                "Serious climbing: the Palisades exit (Alpine Hill) is the big one",
                "Loop home: Cuomo Bridge path (car-free) → Tarrytown → Metro-North Hudson Line",
                "Extend north: Nyack Beach State Park's riverside path to Hook Mountain (car-free, gravel)"],
         trains=[dict(line='hudson', label='Metro-North Hudson Line (return)', boardAt='Tarrytown', alightAt='Harlem–125th St / Grand Central')],
         oneway=True),
    dict(id='empire-north', group='ride', color='#e65100', name='Empire State Trail → Brewster (Putnam Rail Trail)',
         tagline='Epic day ride: rail-trail to the Hudson Valley, train home',
         carfree=85, time='5–7 hours (ride up, Metro-North back)',
         desc="The flagship adventure. Greenway north to Inwood, cross into the Bronx, pick up the Putnam Trail in Van Cortlandt Park, and then it's old railbed nearly the whole way: South County Trailway → North County Trailway → Putnam Trailway, paved and car-free through Westchester horse country to Brewster. Roll straight onto a Metro-North Harlem Line train home.",
         notes=["~85% car-free: the rail trail itself is fully separated; ~4 mi of Bronx streets connect it",
                "This is the official Empire State Trail route (it continues to Albany & Canada!)",
                "Bail-out: turn around anywhere — it's an out-and-back corridor",
                "Return: Harlem Line Brewster → Harlem–125th St ≈ 1h20",
                "Food stops: Elmsford, Millwood, Yorktown Heights, Mahopac right off the trail"],
         trains=[dict(line='harlem', label='Metro-North Harlem Line (return)', boardAt='Brewster', alightAt='Harlem–125th St or Grand Central')],
         oneway=True),

    # ============ BIKE + FERRY ============
    dict(id='governors', group='ferry', color='#ad1457', name='Governors Island Loop (bike + ferry)',
         tagline='Completely car-free island, 8 minutes from the Battery',
         carfree=100, time='Half day with the ride down',
         desc="Ride the Hudson Greenway to the Battery (8 mi, car-free), then hop the Trust for Governors Island ferry at the Battery Maritime Building. The island has zero cars: a 2.2-mi perimeter promenade, the Hills with their harbor panoramas, and miles of interior paths.",
         notes=["Ferry: Battery Maritime Building (10 South St), every 30–60 min; bikes ride free; ~8 min crossing",
                "Island open year-round; ferry is free Sat/Sun mornings before noon",
                "NYC Ferry South Brooklyn route also stops there (bikes $1)",
                "Rentals/Citi Bike on-island if friends join without bikes"],
         trains=[dict(line='ferry', label='Governors Island Ferry', boardAt='Battery Maritime Building', alightAt='Soissons Landing')],
         oneway=False),
    dict(id='staten', group='ferry', color='#ff7043', name='Staten Island Ferry → FDR Boardwalk → Great Kills',
         tagline='Free harbor cruise, then ocean boardwalk and a national park beach',
         carfree=65, time='Half day — ferry is free, 25 min each way',
         desc="Ride to the Battery, roll onto the free Staten Island Ferry (bikes board first, lower deck), and cruise past the Statue of Liberty. From St. George, follow Bay Street south to South Beach, where the Franklin D. Roosevelt Boardwalk runs car-free along the ocean under the Verrazzano to Midland Beach, Miller Field, and on into Great Kills Park — a Gateway National Recreation Area peninsula with beaches and a marina at Crooke's Point.",
         notes=["Ferry: free, every 30 min, 25 min crossing, bikes always welcome on the lowest deck",
                "Boardwalk + Father Capodanno path + Gateway NRA paths: ~7 mi car-free along the ocean",
                "On-street: ~3 mi on Bay St (bike lane, moderate traffic) between the terminal and the beach",
                "Quietest big view of the harbor you can get for $0"],
         trains=[dict(line='siferry', label='Staten Island Ferry (free)', boardAt='Whitehall Terminal', alightAt='St. George Terminal')],
         oneway=True),
    dict(id='liberty', group='ferry', color='#26a69a', name='Liberty State Park (ferry or PATH)',
         tagline='Statue of Liberty front-row views on car-free park paths',
         carfree=100, time='2–3 hours including the ride down',
         desc="Ride the greenway to Brookfield Place, take the short NY Waterway ferry across to Liberty Landing, and you're in Liberty State Park: the 2-mile Liberty Walkway along the harbor, the haunting CRRNJ Train Shed, and point-blank views of the Statue of Liberty and Ellis Island, all on car-free park paths.",
         notes=["Ferry: NY Waterway from Brookfield Place to Liberty Landing (~10 min, bikes OK)",
                "Alternative: PATH to Grove St (bikes allowed off-peak) + 1.5 mi ride",
                "Or ride all the way via the GWB and the Hudson River Waterfront Walkway (long)",
                "Combine with Liberty Science Center or the Communipaw green for a picnic"],
         trains=[dict(line='libferry', label='NY Waterway Liberty Landing Ferry', boardAt='Brookfield Place Terminal', alightAt='Liberty Landing Marina')],
         oneway=False),
    dict(id='sandy-hook', group='ferry', color='#0277bd', name='Seastreak → Sandy Hook (Gateway NRA)',
         tagline='Fast catamaran to a 7-mile car-free beach peninsula',
         carfree=90, time='Beach day — ~45 min fast ferry + ~17 mi riding round trip',
         desc="The Seastreak catamaran from Pier 11 or E 35th St gets you to Highlands, NJ in about 45 minutes. Cross the Shrewsbury River bridge path and you're on Sandy Hook's Multi-Use Pathway: seven car-free miles up the peninsula past ocean beaches, the holly forest, Nike missile relics and Fort Hancock's officer's row, ending at the 1764 lighthouse — the oldest in America — with the Manhattan skyline floating across the harbor.",
         notes=["The Multi-Use Pathway is fully separated; only short street blocks in Highlands",
                "Seastreak carries bikes (small surcharge; in summer some sailings dock at Sandy Hook itself — check the seasonal schedule)",
                "North Beach observation deck has the best skyline-over-water view in the region",
                "Bail-out: it's flat and an out-and-back — turn around whenever",
                "Summer weekends sell out: reserve the ferry both ways"],
         trains=[dict(line='seastreak', label='Seastreak Ferry', boardAt='Pier 11 / E 35th St', alightAt='Highlands, NJ')],
         oneway=True),

    # ============ TRAIN + TRAIL ============
    dict(id='cuomo', group='train', color='#00695c', name='Tarrytown → Cuomo Bridge → Nyack → Nyack Beach',
         tagline='Car-free across the Hudson, then a cliff-foot river beach',
         carfree=56, time='Half day — 40 min train + ~15 mi round trip',
         desc="A short Hudson Line hop to Tarrytown puts you at the foot of the Gov. Mario M. Cuomo Bridge, whose shared-use path is a destination in itself: 3.6 miles over the widest part of the Hudson, with six scenic overlooks. Roll off in South Nyack and coast into the village for coffee, ending at Nyack Beach State Park where the river meets the cliffs.",
         notes=["Path open 6 AM–10 PM year-round; it's a single 12-ft shared path, so ride considerately",
                "Short on-street stretch in Tarrytown and Nyack village (quiet streets)",
                "Keep going on gravel: the car-free riverside path continues ~4 mi to Haverstraw under Hook Mountain (not drawn — gap in the map data, but it is ridable)",
                "Seasonal shortcut home: the Haverstraw–Ossining NY Waterway ferry connects back to the Hudson Line across the river",
                "Train: ~40 min from Harlem–125th St"],
         trains=[dict(line='hudson', label='Metro-North Hudson Line', boardAt='Harlem–125th St / Grand Central', alightAt='Tarrytown')],
         oneway=True),
    dict(id='bear-mountain', group='train', color='#bf360c', name='Peekskill → Bear Mountain → Perkins Summit',
         tagline='The iconic Hudson Highlands climb — an on-road classic',
         carfree=15, time='Half day — 55 min train + ~2,400 ft of climbing',
         desc="Included with the constraint relaxed, because it's the most famous train-and-climb ride in the region: from Peekskill station, the Goat Trail (Bear Mountain Bridge Road) is carved into the cliff face high above the Hudson, then the Bear Mountain Bridge walkway crosses to the Inn, and Perkins Memorial Drive switchbacks to the stone tower on the summit — on a clear day you can see four states and the Manhattan skyline.",
         notes=["⚠ This is an ON-ROAD route (~15% car-free): the Goat Trail and Perkins Drive are shared with cars. Ride single file; weekday mornings are quietest",
                "Perkins Memorial Drive is open roughly Apr–Nov, closed in winter",
                "The Bear Mountain Bridge has a protected walkway — stop mid-span",
                "Food and water at Bear Mountain Inn; Peekskill has good cafés by the station",
                "Shorter option: skip the summit and just do the Goat Trail + bridge out-and-back"],
         trains=[dict(line='hudson', label='Metro-North Hudson Line', boardAt='Harlem–125th St / Grand Central', alightAt='Peekskill')],
         oneway=True),
    dict(id='bronx-river', group='train', color='#827717', name='Bronx River Greenway: Kensico Dam → Soundview',
         tagline='Ride a river greenway home from Westchester',
         carfree=75, time='Half/full day — 50 min train out, ~28 mi following the river',
         desc="Take the Harlem Line to Valhalla and start at the monumental Kensico Dam Plaza. The Bronx River Pathway follows its namesake river south through White Plains, Scarsdale and Bronxville parkland to Shoelace Park and the Botanical Garden, then continues as the Bronx River Greenway through River Park, Starlight Park and Concrete Plant Park to Soundview Park, where the river meets the East River — the whole river, dam to salt water.",
         notes=["The pathway is car-free parkland path with several short on-street gaps (Scarsdale, Mount Vernon)",
                "Sundays May–Sept: 'Bicycle Sundays' close the Bronx River Parkway itself to cars between the Westchester County Center and Scarsdale",
                "Bail-outs: Botanical Garden Metro-North station mid-route; 6 train near Soundview at the end",
                "South of Starlight Park there's a short on-street connector along the old Sheridan Expressway access road",
                "Train: Harlem Line to Valhalla, ~50 min (some trains change at North White Plains)"],
         trains=[dict(line='harlem', label='Metro-North Harlem Line', boardAt='Harlem–125th St / Grand Central', alightAt='Valhalla')],
         oneway=True),
    dict(id='oca', group='train', color='#8e24aa', name='Old Croton Aqueduct: Croton Dam → Van Cortlandt',
         tagline='26 miles of shaded dirt trail atop a 19th-century aqueduct',
         carfree=85, time='Day trip — 50 min train + ~4 hours riding',
         desc="The 1842 aqueduct that first brought water to NYC is now a near-continuous car-free dirt trail along the Hudson's east bank. Train to Croton-Harmon, climb 3 miles to the trail's true start beneath the thundering spillway of the New Croton Dam, then follow it south through Ossining, Sleepy Hollow, Tarrytown, Irvington and Yonkers' Untermyer Gardens, finishing in Van Cortlandt Park where you can pick up the greenway home.",
         notes=["Surface: packed dirt/grass — fine on a hybrid or gravel bike, jarring on skinny slicks",
                "Car-free trail with short street jogs through the river villages",
                "The route now starts at Croton Gorge Park under the dam — one of the great picnic spots in the Hudson Valley",
                "Passes Sleepy Hollow's Headless Horseman country and Untermyer Gardens (worth a stop)",
                "Bail-outs: every Hudson Line station from Ossining to Greystone is minutes off the trail",
                "Train: Hudson Line to Croton-Harmon, ~50 min"],
         trains=[dict(line='hudson', label='Metro-North Hudson Line', boardAt='Harlem–125th St / Grand Central', alightAt='Croton-Harmon')],
         oneway=True),
    dict(id='walkway', group='train', color='#4527a0', name='Walkway Over the Hudson → New Paltz → Rosendale → Kingston',
         tagline="World's longest elevated pedestrian bridge, then rail-trail to a college town",
         carfree=95, time='Day trip — 1h50 train; 28 mi one way to Kingston, bail anywhere',
         desc="Metro-North Hudson Line to its last stop, Poughkeepsie. Three blocks from the station you climb onto the Walkway Over the Hudson — a 1.28-mi former railroad bridge 212 ft above the river. On the west bank the Hudson Valley Rail Trail continues, paved and car-free, to New Paltz for lunch beneath the Shawangunk cliffs — and if your legs agree, the Wallkill Valley Rail Trail continues north through farm fields, over the spectacular 940-ft Rosendale trestle 150 ft above Rondout Creek, and on into uptown Kingston's Stockade District.",
         notes=["Train: Hudson Line, ~1h50; the ride up the river is half the fun — sit on the left",
                "Trail is flat, paved, fully separated — great for any fitness level",
                "Alternative from the same station: Dutchess Rail Trail heads 13 mi east to Hopewell Junction",
                "The New Paltz → Rosendale section (drawn) is the Wallkill Valley Rail Trail: car-free, partly stone dust",
                "Natural turnarounds: Walkway only (3 mi), New Paltz (13 mi), Rosendale (20 mi), Kingston (28 mi)",
                "Return options: ride back to Poughkeepsie, or cross the Kingston–Rhinecliff Bridge (~9 mi) to Rhinecliff Amtrak",
                "Combine with the Maybrook Trailway route for a giant two-line loop"],
         trains=[dict(line='hudson', label='Metro-North Hudson Line', boardAt='Harlem–125th St / Grand Central', alightAt='Poughkeepsie')],
         oneway=True),
    dict(id='maybrook', group='train', color='#3949ab', name='Maybrook Trailway + Dutchess Rail Trail traverse',
         tagline='Forty-some car-free miles between two train lines — the connoisseur’s loop',
         carfree=98, time='Full day — Harlem Line out, Hudson Line home',
         desc="The newest jewel of the Empire State Trail: take the Harlem Line to Southeast, and ride the Maybrook Trailway — 23 miles of brand-new (2020) car-free pavement through Putnam and Dutchess woods, swamps and rock cuts — to Hopewell Junction's restored depot. There the Dutchess Rail Trail continues 13 more car-free miles to Poughkeepsie, where the Hudson Line takes you home along the river.",
         notes=["95% car-free station to station (measured) — the longest separated ride in the region",
                "Remote and quiet: pack food and water, services only at Hopewell Junction",
                "Crosses the Appalachian Trail near Pawling",
                "Out: Harlem Line to Southeast (~1h25). Home: Hudson Line from Poughkeepsie (~1h50)",
                "Add the Walkway Over the Hudson at the end if you have legs left"],
         trains=[dict(line='harlem', label='Metro-North Harlem Line (out)', boardAt='Harlem–125th St / Grand Central', alightAt='Southeast'),
                 dict(line='hudson', label='Metro-North Hudson Line (return)', boardAt='Poughkeepsie', alightAt='Harlem–125th St / Grand Central')],
         oneway=True),
    dict(id='harlem-valley', group='train', color='#00acc1', name='Harlem Valley Rail Trail: Wassaic → Millerton → Copake Falls',
         tagline='23 continuous car-free miles at the end of the line',
         carfree=100, time='Day trip — ~2h train; ride as much of the 23-mi trail as you like',
         desc="Ride the Harlem Line to its very last stop, Wassaic, and the rail trail starts at the platform: smooth pavement up the Harlem Valley through Amenia's farmland to Millerton (Harney tea, Oakhurst Diner), then onward on the newly completed northern section — 23 continuous car-free miles in all — through Boston Corner and under the Taconic ridge to Copake Falls in Taconic State Park.",
         notes=["100% car-free — the trail literally begins at the station",
                "Train: Harlem Line to Wassaic, right at the 2-hour mark; weekend trains carry bike cars",
                "The Millerton → Copake Falls section (Phase IV) opened in late 2024, completing the 23-mile trail — it's all drawn here",
                "Swimming hole + Bash Bish Falls hike from the Copake Falls end",
                "Quiet midweek; bring layers — it's noticeably cooler than the city"],
         trains=[dict(line='harlem', label='Metro-North Harlem Line', boardAt='Harlem–125th St / Grand Central', alightAt='Wassaic')],
         oneway=True),
    dict(id='jones-beach', group='train', color='#f9a825', name='LIRR → Jones Beach → Ocean Pkwy Greenway → Captree',
         tagline='Car-free causeway to the ocean, then 15 miles of barrier-island path',
         carfree=95, time='Beach day — ~55 min train; 5.5 mi to the beach, 23 to Captree',
         desc="LIRR Babylon branch to Wantagh, then the Ellen Farrant Memorial Bikeway: a fully separated path through Cedar Creek Park and across the salt-marsh causeway alongside Wantagh Parkway, to the Jones Beach boardwalk. From there the Ocean Parkway Coastal Greenway — a separated path rebuilt in 2021 — runs the length of the barrier island past Tobay and Gilgo surf beaches to Captree State Park at the Fire Island Inlet. Egrets, ospreys, and ocean the whole way.",
         notes=["Train: ~55 min from Penn Station; avoid peak-hour trains",
                "Path is 100% car-free from Cedar Creek Park to the beach",
                "The full Ocean Parkway Coastal Greenway to Captree is drawn — turn around at the boardwalk for the short version",
                "No shade and steady wind on the barrier island: bring water and check the wind direction",
                "Summer weekends: ride early, beach crowds peak by 11 AM"],
         trains=[dict(line='lirr', label='LIRR Babylon Branch', boardAt='Penn Station', alightAt='Wantagh')],
         oneway=True),
    dict(id='massapequa', group='train', color='#388e3c', name='Bethpage Bikeway: Massapequa → Trail View → Syosset',
         tagline='A green tunnel across Long Island, LIRR branch to LIRR branch',
         carfree=90, time='Half/full day — ~50 min train out, ~17 mi, train home from Syosset',
         desc="Step off the LIRR at Massapequa and the path starts across the street: a paved, car-free ribbon through the ponds and pine barrens of Massapequa Preserve, becoming the Bethpage Bikeway through Bethpage State Park, then riding the Trail View State Park right-of-way north across the island to Syosset — about 13 paved bikeway miles, station to station, where the Port Jefferson branch carries you home. A true cross-Long-Island traverse.",
         notes=["Car-free bikeway nearly the whole way; short street links near Syosset station",
                "Point-to-point between two LIRR branches: out via Babylon branch, home via Port Jefferson branch from Syosset",
                "Combine with Jones Beach: ride south instead via the Massapequa–Tobay connector for an ocean finish",
                "Bethpage State Park picnic grounds make the natural midpoint break"],
         trains=[dict(line='lirr', label='LIRR Babylon Branch', boardAt='Penn Station', alightAt='Massapequa')],
         oneway=True),
    dict(id='long-beach', group='train', color='#0091ea', name='LIRR → Long Beach Boardwalk → Point Lookout',
         tagline='The easiest beach day on the calendar, now with a fishing-village finish',
         carfree=85, time='Beach day — ~55 min direct train + ~17 mi round trip',
         desc="The LIRR's Long Beach branch runs straight to the beach — no transfers. Three blocks from the station you're on the 2.2-mile boardwalk, rebuilt beautifully after Sandy, with the Atlantic on one side and surf-town Long Beach on the other. Cruise it end to end, then follow the Lido Boulevard path east past Nickerson Beach to the fishing village of Point Lookout for chowder at the inlet. Swim, eat, repeat.",
         notes=["Boardwalk cycling: 5–10 AM in summer season, anytime off-season. The drawn line and measured % use the parallel streets because the map data tags the boardwalk no-bikes — the real ride is better than the number",
                "The Lido Blvd path to Point Lookout is drawn — flat, separated, ~4 mi each way",
                "Direct trains from Penn Station roughly every 30–60 min",
                "Combine with Atlantic Beach and the Rockaways via the Atlantic Beach Bridge for a two-boardwalk day"],
         trains=[dict(line='lirr-lb', label='LIRR Long Beach Branch', boardAt='Penn Station', alightAt='Long Beach')],
         oneway=True),
    dict(id='queens-greenway', group='train', color='#c51162', name='Eastern Queens Greenway: Flushing Meadows → Fort Totten',
         tagline="Park-to-park across Queens on the world's first highway",
         carfree=80, time='Half/full day — ~40 min subway + 18 mi (LIRR back from Bayside)',
         desc="The missing eastern spoke: 7 train to Mets–Willets Point, then a chain of green: Flushing Meadows–Corona Park (Unisphere!), Kissena Park's lake, Cunningham Park, and the restored Vanderbilt Motor Parkway — built 1908 as the world's first limited-access highway, now a car-free bike path through the woods — then Alley Pond Park and Joe Michaels Mile along Little Neck Bay to the Civil War battery at Fort Totten.",
         notes=["Park paths and the Motor Parkway are car-free; street links between parks (~3.5 mi total, mostly marked lanes)",
                "This is the signed Brooklyn–Queens Greenway eastern half",
                "Return: LIRR Port Washington branch from Bayside (~35 min to Penn), or ride back",
                "The Motor Parkway section is a genuinely weird and wonderful piece of history — Gatsby-era concrete under your tires"],
         trains=[dict(line='seven', label='7 Train (subway — bikes anytime)', boardAt='Times Sq / Bryant Park', alightAt='Mets–Willets Point')],
         oneway=True),
    dict(id='port-jefferson', group='train', color='#5c6bc0', name='Port Jefferson: Setauket Greenway + North Shore Rail Trail',
         tagline='Two far-east rail trails and a ferry trick up their sleeve',
         carfree=85, time='Full day — ~1h55 train (right at your 2-hour edge), up to 17 mi one way',
         desc="At the eastern edge of your two-hour circle: LIRR to Port Jefferson, where the wooded Setauket Greenway runs west through Long Island's Revolutionary-spy country — and a short road link east picks up the North Shore Rail Trail, ten car-free miles (opened 2022) along the old Wading River railbed through Miller Place, Rocky Point and Shoreham to Wading River. The bonus trick: Port Jefferson's harbor has a car ferry across the Sound to Bridgeport, so you can come home on Metro-North or tack on the Pequonnock trail.",
         notes=["Both rail trails are car-free; ~2 mi of road links join them through Port Jefferson (use 25A shoulder or village streets)",
                "The North Shore Rail Trail has 36 road crossings — flat and family-friendly between them",
                "Port Jefferson village: harborfront food and ice cream",
                "Cross-Sound combo: PJ–Bridgeport ferry (~75 min, bikes welcome) → Pequonnock trail or Metro-North home",
                "Train: Port Jefferson branch, usually a change at Huntington, ~1h55"],
         trains=[dict(line='lirr-pj', label='LIRR Port Jefferson Branch', boardAt='Penn Station', alightAt='Port Jefferson'),
                 dict(line='pbferry', label='Port Jeff–Bridgeport Ferry (return option)', boardAt='Port Jefferson Harbor', alightAt='Bridgeport → Metro-North home')],
         oneway=True),
    dict(id='rockaway', group='train', color='#ef6c00', name='A Train → Rockaway Boardwalk → Riis Park',
         tagline='Surf-town boardwalk cruising, subway bikes always welcome',
         carfree=95, time='Beach day — ~1h15 subway + ~11 mi riding round trip',
         desc="Bikes ride the subway anytime, so take the A from 59th St out over Jamaica Bay to Broad Channel. Cross the Cross Bay Bridge on its path, hit the 5.5-mile concrete boardwalk at Beach 94th, and cruise west past the surf breaks to Jacob Riis Park, finishing on Fort Tilden's car-free battery roads among the dunes.",
         notes=["Subway: B/C at 86th St → transfer to A at 59th St–Columbus Circle",
                "Boardwalk is car-free but OSM tags it no-bikes (summer rules), so the drawn line and measured % use the parallel streets — in reality, ride the boardwalk before 10 AM in summer or anytime off-season",
                "Alternative: Jamaica Bay Greenway loops the whole bay if you want miles",
                "Tacos at Rockaway Beach 97th St concessions; Riis Park has summer food vendors"],
         trains=[dict(line='atrain', label='A Train (subway — bikes anytime)', boardAt='59 St–Columbus Circle', alightAt='Broad Channel')],
         oneway=True),
    dict(id='jamaica-bay', group='train', color='#00bfa5', name='Jamaica Bay Greenway Loop',
         tagline='Lap the whole bay: boardwalk, runways, grasslands, salt marsh',
         carfree=85, time='Half/full day — A train out, ~24 mi loop',
         desc="The recently completed Jamaica Bay Greenway laps NYC's biggest wild place: from Broad Channel over the Cross Bay Bridge to the Rockaway boardwalk, west to Riis Park, across the Gil Hodges Bridge path, through Floyd Bennett Field's abandoned runways, along the Belt Parkway shore path past Plumb Beach and Canarsie Pier, up through Shirley Chisholm State Park's grassland hills, and back over the bay — herons, ospreys and jets out of JFK the whole way.",
         notes=["Mostly separated greenway path; short on-street links in Howard Beach and near Flatbush Ave",
                "All three water crossings (Cross Bay, Gil Hodges, North Channel) have bike/walk paths",
                "Shirley Chisholm State Park's gravel hill loops have the best skyline-over-marsh views in Brooklyn",
                "Bail-outs: A train at Broad Channel and Howard Beach; NYC Ferry at Rockaway",
                "Pairs with the Rockaway boardwalk route — same train, opposite directions"],
         trains=[dict(line='atrain', label='A Train (subway — bikes anytime)', boardAt='59 St–Columbus Circle', alightAt='Broad Channel')],
         oneway=False),
    dict(id='dr-canal', group='train', color='#00897b', name='D&R Canal Towpath: Princeton → New Brunswick',
         tagline='Mule-towpath miles past locks and woods, two-station loop',
         carfree=90, time='Full day — NJ Transit out, NJ Transit home',
         desc="NJ Transit to Princeton Junction, the Dinky shuttle into Princeton, and you're on the Delaware & Raritan Canal towpath: a flat, shaded gravel path along the 1834 canal, past locks, spillways and Revolutionary War country, following the Millstone River north to Bound Brook and the Raritan into New Brunswick — where the Northeast Corridor train carries you home.",
         notes=["Surface: crushed stone/gravel — best on wider tires",
                "Car-free the whole way; short street links at the Princeton and New Brunswick ends",
                "The other classic arm: Princeton → Washington Crossing → Lambertville/New Hope along the Delaware feeder canal (similar distance) — gorgeous, but no train home from Lambertville",
                "Out: NE Corridor to Princeton Jct (~1h15) + Dinky. Home: NE Corridor from New Brunswick (~55 min)"],
         trains=[dict(line='nec', label='NJ Transit Northeast Corridor (out)', boardAt='Penn Station', alightAt='Princeton Jct → Dinky to Princeton'),
                 dict(line='nec', label='NJ Transit Northeast Corridor (return)', boardAt='New Brunswick', alightAt='Penn Station')],
         oneway=True),
    dict(id='columbia', group='train', color='#f4511e', name='Columbia Trail: High Bridge → Long Valley → Flanders',
         tagline='Gorge scenery on a gravel rail trail in deep NJ',
         carfree=95, time='Full day — ~1h50 train + up to ~31 mi riding round trip',
         desc="Raritan Valley Line to its last stop, High Bridge, and the Columbia Trail begins in the middle of town: a crushed-stone rail trail up the South Branch of the Raritan, through the dramatic Ken Lockwood Gorge (trout fishermen below, hawks above) to the mill town of Long Valley and its excellent brewpub — and the railbed keeps going, climbing gently to the trail's true end at Bartley Road in Flanders, 15 miles from the start.",
         notes=["Surface: crushed stone — gravel/hybrid tires recommended",
                "Car-free with a handful of quiet road crossings",
                "Ken Lockwood Gorge is the highlight — worth slowing down for",
                "Train: Raritan Valley Line from Penn (change at Newark most hours), ~1h50",
                "Long Valley Brew Pub sits right at the turnaround"],
         trains=[dict(line='rvl', label='NJ Transit Raritan Valley Line', boardAt='Penn Station (change Newark)', alightAt='High Bridge')],
         oneway=True),
    dict(id='pequonnock', group='train', color='#1e88e5', name='Pequonnock River Trail: Bridgeport → Monroe → Newtown line',
         tagline="Connecticut's wooded rail trail straight from the platform",
         carfree=85, time='Day trip — ~1h25 train + up to ~34 mi riding round trip',
         desc="New Haven Line express to Bridgeport, then ride north out of the city onto the Pequonnock River Trail: a paved-and-gravel rail trail climbing gently through the hemlock woods of Trumbull's Pequonnock valley past Old Mine Park and Monroe's Wolfe Park, with the corridor continuing on the old Housatonic railbed to the Newtown town line — 16+ miles of trail in all. A surprisingly wild ride 90 minutes from Manhattan.",
         notes=["Car-free trail in several segments with short on-road links between them (and ~1.5 mi of city streets from the station)",
                "Surface alternates paved and stone dust — any tire wider than 28mm is happy",
                "The Parlor Rock section follows an 1880s amusement park ruin",
                "Train: New Haven Line to Bridgeport, ~1h25 on expresses"],
         trains=[dict(line='nhl', label='Metro-North New Haven Line', boardAt='Harlem–125th St / Grand Central', alightAt='Bridgeport')],
         oneway=True),
    dict(id='fcht', group='train', color='#304ffe', name='Metro-North → New Haven → Farmington Canal Trail',
         tagline="New England's great rail trail, straight off the last stop",
         carfree=95, time='Full day — ~1h50 express train + up to ~32 mi round trip',
         desc="Ride the New Haven Line to its namesake end and the Farmington Canal Heritage Trail begins blocks from Union Station — its final downtown link opened in May 2025. The old canal towpath-turned-railbed glides through Yale's campus edge, then runs north through Hamden with a 6-mile stretch of zero street crossings, to Lock 12's restored canal park in Cheshire. The trail ultimately continues 48+ car-free miles toward Massachusetts.",
         notes=["Paved and separated essentially the whole way; turn around at Lock 12 (Cheshire) for a ~32-mi day",
                "The downtown New Haven section (Temple St → Orange St → Long Wharf) was completed in 2025",
                "Mandatory bookend: apizza at Pepe's or Sally's on Wooster St, a mile from the trailhead",
                "Express trains GCT → New Haven run ~1h48 — board at Harlem–125th St to save 10 min"],
         trains=[dict(line='nhl', label='Metro-North New Haven Line', boardAt='Harlem–125th St / Grand Central', alightAt='New Haven Union Station')],
         oneway=True),
    dict(id='sussex', group='train', color='#ff6f00', name='Sussex Branch Trail: Netcong → Newton → Branchville',
         tagline='Cinder-path gravel riding through the NJ Skylands',
         carfree=95, time='Day trip — ~1h25 NJ Transit + gravel miles',
         desc="The deep-northwest gravel option: NJ Transit's Morris & Essex line to Netcong, then the Sussex Branch Trail — the cinder bed of an 1848 iron-mine railroad — north through Kittatinny Valley State Park, skirting Cranberry Lake and rock cuts full of ferns to Andover and the fields outside Newton. Rough, quiet, and the wildest-feeling trail in this collection.",
         notes=["Surface: dark cinder dirt with ballast rock — a gravel or mountain bike is the right tool",
                "The full 21-mi trail to Branchville is drawn; Newton makes a sane turnaround",
                "At Warbasse Junction it crosses the 25-mi Paulinskill Valley Trail — a whole second gravel network if you want more",
                "Waterloo Village (restored Morris Canal town) is a short detour at the south end",
                "Train: M&E to Netcong, ~1h25 (direct Dover trains or change at Dover)"],
         trains=[dict(line='mne', label='NJ Transit Morris & Essex Line', boardAt='Penn Station', alightAt='Netcong')],
         oneway=True),
    dict(id='ahet', group='train', color='#5e35b1', name='Amtrak → Hudson → AHET to Kinderhook & Niverville',
         tagline='The 2-hour-radius stretch goal: Empire State Trail upstate',
         carfree=80, time='Full day — 1h55 Amtrak + ride; book a bike reservation',
         desc="Right at the edge of your two-hour circle: Amtrak's Empire Service up the river to Hudson, NY (the train hugs the water the whole way). From the station, the Albany-Hudson Electric Trail — an Empire State Trail segment on a 1900s trolley right-of-way — rolls north through farms and hamlets to Kinderhook and Niverville — and if you're feeling immortal it continues all the way to Albany (36 mi), where Amtrak can bring you home from Albany-Rensselaer.",
         notes=["Amtrak requires a $20 bike reservation (carry-on racks); book when you buy your ticket",
                "Trail is a mix of car-free path and quiet-road sections (~80% separated)",
                "Hudson itself — Warren St — is worth an hour of wandering",
                "Penn Station → Hudson ~1h55 on Empire Service"],
         trains=[dict(line='empire', label='Amtrak Empire Service', boardAt='Penn Station (Moynihan)', alightAt='Hudson, NY')],
         oneway=True),
    dict(id='hht', group='train', color='#9e9d24', name='Henry Hudson Trail: Matawan → Atlantic Highlands',
         tagline='Raritan Bayshore rail trail with skyline-over-water views',
         carfree=95, time='Day trip — ~1h05 train out, ferry-home option',
         desc="NJ Coast Line to Aberdeen-Matawan, where the Henry Hudson Trail begins: a paved former railbed skimming the Raritan Bayshore through Union Beach, Keansburg and Port Monmouth, with the Manhattan skyline hanging over the water to your left, past Atlantic Highlands' harbor and on to its true end at Popamora Point in Highlands — where the bridge path to Sandy Hook begins.",
         notes=["Car-free rail trail with quiet road crossings; the bayshore section is the keeper",
                "Finish: lunch at Atlantic Highlands marina",
                "Best return: the Seastreak ferry home from Atlantic Highlands harbor (commuter sailings — check times) — train out, boat home",
                "The trail now ends at Popamora Point, touching the Sandy Hook route — combine them for the full bayshore-to-ocean day"],
         trains=[dict(line='njcl', label='NJ Transit North Jersey Coast Line', boardAt='Penn Station', alightAt='Aberdeen-Matawan'),
                 dict(line='seastreak', label='Seastreak (return option)', boardAt='Atlantic Highlands Harbor', alightAt='Pier 11 / E 35th St')],
         oneway=True),
    dict(id='edgar-felix', group='train', color='#880e4f', name='Edgar Felix Bikeway: Manasquan → Allaire State Park',
         tagline='Jersey Shore rail trail with a beach at one end and a ghost town at the other',
         carfree=90, time='Day trip — ~1h50 NJ Coast Line + ~11 mi round trip (plus beach)',
         desc="The southernmost spoke, right at the 2-hour line: the NJ Coast Line to Manasquan, where the paved Edgar Felix Memorial Bikeway starts a few blocks from the station and runs inland through pine woods to Allaire State Park and its preserved 1830s iron-furnace village. Ride back and finish with your front wheel in the Atlantic at Manasquan's beachfront.",
         notes=["Paved, car-free rail trail; a few quiet street blocks at the Manasquan end",
                "Allaire Village: working 19th-century blacksmith and bakery, plus a narrow-gauge steam railroad",
                "Manasquan beach + Squan Village food two blocks from the trailhead",
                "Train: North Jersey Coast Line, change at Long Branch, ~1h50"],
         trains=[dict(line='njcl', label='NJ Transit North Jersey Coast Line', boardAt='Penn Station (change at Long Branch)', alightAt='Manasquan')],
         oneway=True),
    dict(id='heritage', group='train', color='#6d4c41', name='Heritage Trail: Harriman → Goshen → Middletown',
         tagline="Orange County's black-dirt rail trail off the Port Jervis Line",
         carfree=95, time='Day trip — ~1h25 train (transfer at Secaucus)',
         desc="The northwest spoke: NJ Transit's Port Jervis Line (transfer at Secaucus) to Harriman, where the paved Heritage Trail follows the old Erie main line through Monroe, Chester and the historic harness-racing town of Goshen to Middletown — rolling farm country, the black-dirt onion fields, and a string of trailside creameries.",
         notes=["Paved, car-free rail trail nearly the whole way",
                "Goshen makes the natural lunch turnaround (~13 mi) if Middletown is too far",
                "⚠ Port Jervis Line service is sparse, especially weekends — check the schedule home before you leave",
                "Bertoni Gelato in Monroe and the Chester creamery are mandatory stops"],
         trains=[dict(line='pjline', label='NJ Transit Port Jervis Line', boardAt='Penn Station (change at Secaucus)', alightAt='Harriman')],
         oneway=True),
    dict(id='saddle-river', group='train', color='#33691e', name='Saddle River County Park Path: Ridgewood → Rochelle Park',
         tagline="Bergen County's linear park, duck ponds and all",
         carfree=95, time='Half day — ~50 min train (transfer at Secaucus)',
         desc="The due-west easy option: NJ Transit to Ridgewood, then the Saddle River pathway — a paved, car-free ribbon of county parkland strung along the river through Glen Rock, Fair Lawn and Saddle Brook, past duck ponds, picnic groves and the old Easton Tower mill. Flat, gentle, and perfect for a low-effort afternoon.",
         notes=["Car-free path end to end; a few park-road crossings",
                "Out-and-back from Ridgewood ≈ 13 mi round trip",
                "Train: Main/Bergen County line via Secaucus transfer, ~50 min",
                "Ridgewood's downtown (cafés, bakeries) is right by the station"],
         trains=[dict(line='njt-main', label='NJ Transit Main/Bergen Line', boardAt='Penn Station (change at Secaucus)', alightAt='Ridgewood')],
         oneway=True),
]

HUDSON_PTS = [
    [40.7527, -73.9772], [40.8053, -73.9389], [40.8200, -73.9330], [40.8500, -73.9230],
    [40.8780, -73.9180], [40.9360, -73.9010], [40.9940, -73.8810], [41.0330, -73.8730],
    [41.0762, -73.8662], [41.1190, -73.8730], [41.1620, -73.8720], [41.1900, -73.8821],
    [41.2450, -73.9230], [41.2857, -73.9300], [41.3200, -73.9750], [41.3850, -73.9560],
    [41.4200, -73.9550], [41.5048, -73.9840], [41.5900, -73.9530], [41.6500, -73.9420],
    [41.7065, -73.9379]]

TRAINLINES = {
    'hudson': dict(name='Metro-North Hudson Line', color='#5f6a72', pts=HUDSON_PTS),
    'harlem': dict(name='Metro-North Harlem Line', color='#5f6a72', pts=[
        [40.7527, -73.9772], [40.8053, -73.9389], [40.8610, -73.8900], [40.9120, -73.8350],
        [40.9520, -73.8050], [41.0330, -73.7760], [41.0710, -73.7720], [41.1100, -73.7950],
        [41.2040, -73.7270], [41.2590, -73.6850], [41.3470, -73.6620], [41.3946, -73.6168],
        [41.4153, -73.6029], [41.5120, -73.6050], [41.5620, -73.6000], [41.7410, -73.5770],
        [41.7920, -73.5600]]),
    'lirr': dict(name='LIRR Babylon Branch', color='#5f6a72', pts=[
        [40.7506, -73.9935], [40.7420, -73.9180], [40.7000, -73.8300], [40.6995, -73.8087],
        [40.6750, -73.7280], [40.6577, -73.5832], [40.6680, -73.5400], [40.6837, -73.5107],
        [40.6776, -73.4700]]),
    'atrain': dict(name='A Train', color='#5f6a72', pts=[
        [40.7681, -73.9819], [40.7570, -73.9899], [40.7323, -74.0003], [40.7102, -74.0094],
        [40.6920, -73.9870], [40.6784, -73.9054], [40.6740, -73.8530], [40.6604, -73.8304],
        [40.6340, -73.8220], [40.6088, -73.8159]]),
    'ferry': dict(name='Governors Island Ferry', color='#5f6a72', pts=[
        [40.7016, -74.0117], [40.6918, -74.0145]]),
    'siferry': dict(name='Staten Island Ferry', color='#5f6a72', pts=[
        [40.7010, -74.0132], [40.6437, -74.0733]]),
    'libferry': dict(name='Liberty Landing Ferry', color='#5f6a72', pts=[
        [40.7128, -74.0163], [40.7077, -74.0431]]),
    'nec': dict(name='NJ Transit Northeast Corridor + Princeton Dinky', color='#5f6a72', pts=[
        [40.7506, -73.9935], [40.7614, -74.0758], [40.7344, -74.1644], [40.6740, -74.2150],
        [40.5680, -74.3290], [40.5000, -74.4440], [40.3160, -74.6230], [40.3430, -74.6590]]),
    'rvl': dict(name='NJ Transit Raritan Valley Line', color='#5f6a72', pts=[
        [40.7506, -73.9935], [40.7614, -74.0758], [40.7344, -74.1644], [40.6580, -74.3040],
        [40.6490, -74.3470], [40.6180, -74.4070], [40.5683, -74.6100], [40.6150, -74.7700],
        [40.6660, -74.8950]]),
    'nhl': dict(name='Metro-North New Haven Line', color='#5f6a72', pts=[
        [40.7527, -73.9772], [40.8053, -73.9389], [40.8400, -73.8800], [40.9110, -73.7840],
        [41.0210, -73.6250], [41.0470, -73.5420], [41.0950, -73.4210], [41.1320, -73.2590],
        [41.1780, -73.1870], [41.2230, -73.0570], [41.2970, -72.9270]]),
    'mne': dict(name='NJ Transit Morris & Essex Line', color='#5f6a72', pts=[
        [40.7506, -73.9935], [40.7614, -74.0758], [40.7479, -74.1718], [40.7163, -74.3577],
        [40.7970, -74.4810], [40.8870, -74.5560], [40.8980, -74.7070]]),
    'empire': dict(name='Amtrak Empire Service', color='#5f6a72', pts=
        [[40.7506, -73.9935], [40.8270, -73.9530]] + HUDSON_PTS[4:] +
        [[41.9210, -73.9510], [42.2520, -73.7910]]),
    'seastreak': dict(name='Seastreak Ferry', color='#5f6a72', pts=[
        [40.7032, -74.0068], [40.6300, -74.0200], [40.5200, -73.9950], [40.4030, -73.9870]]),
    'njcl': dict(name='NJ Transit North Jersey Coast Line', color='#5f6a72', pts=[
        [40.7506, -73.9935], [40.7614, -74.0758], [40.7344, -74.1644], [40.6040, -74.2780],
        [40.5070, -74.2660], [40.4850, -74.2810], [40.4147, -74.2249], [40.3490, -74.0760],
        [40.2970, -73.9920], [40.2200, -74.0140], [40.1218, -74.0488]]),
    'lirr-lb': dict(name='LIRR Long Beach Branch', color='#5f6a72', pts=[
        [40.7506, -73.9935], [40.6995, -73.8087], [40.6650, -73.7000], [40.6550, -73.6760],
        [40.6040, -73.6550], [40.5887, -73.6580]]),
    'seven': dict(name='7 Train', color='#5f6a72', pts=[
        [40.7556, -73.9870], [40.7508, -73.9400], [40.7470, -73.8910], [40.7547, -73.8456]]),
    'lirr-pj': dict(name='LIRR Port Jefferson Branch', color='#5f6a72', pts=[
        [40.7506, -73.9935], [40.6995, -73.8087], [40.7410, -73.6410], [40.7680, -73.5290],
        [40.8250, -73.4990], [40.8530, -73.4100], [40.8560, -73.1960], [40.9357, -73.0531]]),
    'pbferry': dict(name='Port Jefferson–Bridgeport Ferry', color='#5f6a72', pts=[
        [40.9500, -73.0700], [41.1730, -73.1820]]),
    'njt-main': dict(name='NJ Transit Main/Bergen County Line', color='#5f6a72', pts=[
        [40.7506, -73.9935], [40.7614, -74.0758], [40.8570, -74.1210], [40.9150, -74.1710],
        [40.9600, -74.1330], [40.9810, -74.1170]]),
    'pjline': dict(name='NJ Transit Port Jervis Line', color='#5f6a72', pts=[
        [40.7506, -73.9935], [40.7614, -74.0758], [40.8570, -74.1210], [40.9150, -74.1710],
        [40.9810, -74.1170], [41.0570, -74.1410], [41.1130, -74.1490], [41.1940, -74.1850],
        [41.3093, -74.1440]]),
}

# surface + filterable tags per route
EXTRAS = {
    'central-park':   ('paved', ['loop']),
    'hrg-south':      ('paved', []),
    'hrg-north':      ('paved', []),
    'randalls':       ('paved', []),
    'waterfront-loop':('paved', ['loop']),
    'coney':          ('paved', ['beach', 'food']),
    'brooklyn':       ('paved', ['food']),
    'pelham':         ('paved', ['beach', 'food']),
    'piermont':       ('paved', ['climb', 'food']),
    'empire-north':   ('paved', ['climb', 'food']),
    'governors':      ('paved', ['loop']),
    'staten':         ('paved', ['beach']),
    'liberty':        ('paved', ['loop']),
    'cuomo':          ('paved', ['food']),
    'bronx-river':    ('paved', []),
    'oca':            ('dirt',  []),
    'walkway':        ('paved', ['food']),
    'maybrook':       ('paved', []),
    'harlem-valley':  ('paved', ['food']),
    'jones-beach':    ('paved', ['beach']),
    'massapequa':     ('paved', []),
    'rockaway':       ('paved', ['beach', 'food']),
    'dr-canal':       ('gravel', []),
    'columbia':       ('gravel', ['food']),
    'pequonnock':     ('mixed', []),
    'ahet':           ('mixed', ['food']),
    'sandy-hook':     ('paved', ['beach']),
    'hht':            ('paved', ['food']),
    'long-beach':     ('paved', ['beach', 'food']),
    'queens-greenway':('paved', []),
    'port-jefferson': ('paved', ['food']),
    'saddle-river':   ('paved', []),
    'heritage':       ('paved', ['food']),
    'bear-mountain':  ('paved', ['climb', 'food']),
    'fcht':           ('paved', ['food']),
    'sussex':         ('dirt',  []),
    'jamaica-bay':    ('paved', ['beach', 'loop']),
    'edgar-felix':    ('paved', ['beach']),
}

out = []
for r in ROUTES:
    if r['id'] == 'governors':
        pts, ele, segs = GOV_LOOP, [10] * len(GOV_LOOP), [[len(GOV_LOOP), 1]]
        stats = {'mi': 2.2, 'climb_ft': 80, 'pathpct': 100}
    else:
        pts, ele, segs, stats = coords(r['id'])
    r['pts'] = pts
    r['ele'] = ele
    r['segs'] = segs
    r['mi'] = stats['mi']
    r['climb'] = stats['climb_ft']
    r['carfree'] = stats['pathpct']  # measured from OSM way tags, replaces hand estimate
    r['surface'], r['tags'] = EXTRAS[r['id']]
    out.append(r)

root = os.path.dirname(__file__)
data_js = ('// Route geometries from BRouter (OpenStreetMap data)\n'
           'const ROUTES = ' + json.dumps(out) + ';\n'
           'const TRAINLINES = ' + json.dumps(TRAINLINES) + ';\n')

with open(os.path.join(root, 'routes.js'), 'w') as f:
    f.write(data_js)

# standalone single-file build: inline the data into the template
template = open(os.path.join(root, 'template.html')).read()
assert '/*__DATA__*/' in template, 'template missing /*__DATA__*/ marker'
with open(os.path.join(root, 'index.html'), 'w') as f:
    f.write(template.replace('/*__DATA__*/', data_js))

total = sum(len(r['pts']) for r in out)
print(f"index.html (standalone) written: {len(out)} routes, {total} points, "
      f"{os.path.getsize(os.path.join(root, 'index.html'))//1024} KB")
for r in out:
    print(f"  {r['id']:18s} {r['mi']:6.1f} mi  {r['climb']:5d} ft climb  {len(r['pts'])} pts")
