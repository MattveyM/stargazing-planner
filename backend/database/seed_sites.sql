-- Starter list of Pacific Northwest dark-sky spots.
-- Coordinates are approximate (within about 1 mile) and Bortle values are estimates.
-- Double-check each spot on lightpollutionmap.info and Google Maps before relying on it.
-- Run with: psql -d stargazing -f database/seed_sites.sql

DELETE FROM sites;

INSERT INTO sites (name, region, state, latitude, longitude, bortle, road_access, notes) VALUES
-- Washington: Olympic Peninsula and coast
('Hurricane Ridge',                    'Olympic Peninsula', 'WA', 47.9696, -123.4988, 2, 'Seasonal',   'Olympic National Park. Road hours and winter closures vary; check the park website.'),
('Kalaloch Beach',                     'Olympic Peninsula', 'WA', 47.6120, -124.3740, 2, 'Year-round', 'Ocean views to the west; coastal fog is common.'),
('Lake Cushman',                       'Olympic Peninsula', 'WA', 47.4300, -123.2300, 3, 'Year-round', 'Lakeside pullouts along the road.'),
('Fort Flagler State Park',            'Puget Sound',       'WA', 48.0950, -122.7120, 3, 'Year-round', 'Marrowstone Island. Discover Pass required.'),
('Cape Disappointment State Park',     'Washington Coast',  'WA', 46.2900, -124.0560, 3, 'Year-round', 'Mouth of the Columbia River. Discover Pass required.'),
-- Washington: Puget Sound and islands
('Deception Pass State Park',          'Puget Sound',       'WA', 48.4030, -122.6460, 4, 'Year-round', 'Some glow from nearby towns. Discover Pass required.'),
('Lime Kiln Point State Park',         'San Juan Islands',  'WA', 48.5160, -123.1520, 3, 'Year-round', 'San Juan Island; ferry required.'),
-- Washington: Cascades
('Rattlesnake Lake',                   'Cascades',          'WA', 47.4337, -121.7745, 4, 'Year-round', 'Close to Seattle; some city glow to the west.'),
('Snoqualmie Pass',                    'Cascades',          'WA', 47.4246, -121.4134, 4, 'Year-round', 'Easy I-90 access; ski area lights in winter.'),
('Mount Pilchuck Road',                'Cascades',          'WA', 48.0700, -121.8150, 3, 'Seasonal',   'Mountain Loop Highway; upper road is rough and closes in winter.'),
('Artist Point',                       'Cascades',          'WA', 48.8460, -121.6930, 2, 'Seasonal',   'Mount Baker Highway; usually open mid-summer to early fall only.'),
('Diablo Lake Overlook',               'North Cascades',    'WA', 48.7130, -121.1000, 2, 'Year-round', 'North Cascades Highway (SR 20).'),
('Washington Pass Overlook',           'North Cascades',    'WA', 48.5155, -120.6557, 1, 'Seasonal',   'SR 20 closes in winter (usually Nov to Apr).'),
('Lake Wenatchee State Park',          'Cascades',          'WA', 47.8130, -120.7240, 3, 'Year-round', 'Discover Pass required.'),
('Blewett Pass',                       'Cascades',          'WA', 47.3340, -120.5790, 3, 'Year-round', 'US 97 summit pullout; snow in winter.'),
('Cle Elum Lake',                      'Cascades',          'WA', 47.2560, -121.0750, 3, 'Year-round', 'Pullouts along Salmon la Sac Road.'),
('Mount Rainier - Sunrise',            'Mount Rainier',     'WA', 46.9145, -121.6418, 2, 'Seasonal',   'Mount Rainier National Park; road open roughly July to early October.'),
('Mount Rainier - Paradise',           'Mount Rainier',     'WA', 46.7860, -121.7354, 2, 'Seasonal',   'Winter gate hours limit night access; check the park website.'),
('Mount St. Helens - Windy Ridge',     'Mount St. Helens',  'WA', 46.2470, -122.1370, 2, 'Seasonal',   'Forest Road 99; closed in winter. Check road status.'),
('Trout Lake',                         'Mount Adams',       'WA', 45.9970, -121.5280, 2, 'Year-round', 'Small town south of Mount Adams.'),
('Goldendale Observatory State Park',  'Columbia Gorge',    'WA', 45.8390, -120.8156, 2, 'Year-round', 'International Dark Sky Park with public telescope programs.'),
-- Washington: Eastern Washington
('Sun Lakes-Dry Falls State Park',     'Eastern Washington','WA', 47.6000, -119.3600, 2, 'Year-round', 'Very dark desert skies. Discover Pass required.'),
('Ginkgo Petrified Forest (Vantage)',  'Eastern Washington','WA', 46.9480, -119.9890, 2, 'Year-round', 'Near I-90 at the Columbia River.'),
('Palouse Falls State Park',           'Eastern Washington','WA', 46.6630, -118.2240, 2, 'Year-round', 'Popular astrophotography spot. Discover Pass required.'),
('Steptoe Butte State Park',           'Eastern Washington','WA', 47.0330, -117.2970, 2, 'Year-round', 'Road to the summit; 360-degree view.'),
('Mount Spokane State Park',           'Eastern Washington','WA', 47.9230, -117.1130, 3, 'Year-round', 'Spokane glow to the southwest.'),
-- Oregon
('Cape Lookout State Park',            'Oregon Coast',      'OR', 45.3630, -123.9720, 3, 'Year-round', 'Coastal fog is common.'),
('Timberline Lodge',                   'Mount Hood',        'OR', 45.3310, -121.7110, 3, 'Year-round', 'High elevation; lodge lights nearby.'),
('Trillium Lake',                      'Mount Hood',        'OR', 45.2670, -121.7360, 3, 'Seasonal',   'Road is a snow-park route in winter.'),
('Cottonwood Canyon State Park',       'Eastern Oregon',    'OR', 45.4800, -120.4650, 2, 'Year-round', 'International Dark Sky Park.'),
('Smith Rock State Park',              'Central Oregon',    'OR', 44.3670, -121.1400, 3, 'Year-round', 'Some glow from Redmond and Bend.'),
('Prineville Reservoir State Park',    'Central Oregon',    'OR', 44.1450, -120.7370, 2, 'Year-round', 'International Dark Sky Park.'),
('Sunriver Observatory',               'Central Oregon',    'OR', 43.8840, -121.4430, 3, 'Year-round', 'Public observatory programs.'),
('Pine Mountain Observatory',          'Central Oregon',    'OR', 43.7910, -120.9410, 2, 'Seasonal',   'Gravel road; observatory open late spring to early fall.'),
('Painted Hills',                      'Eastern Oregon',    'OR', 44.6610, -120.2730, 1, 'Year-round', 'John Day Fossil Beds; very remote.'),
('Wallowa Lake',                       'Eastern Oregon',    'OR', 45.2870, -117.2120, 2, 'Year-round', 'Far northeast Oregon.'),
('Crater Lake - Rim Village',          'Southern Oregon',   'OR', 42.9110, -122.1460, 1, 'Year-round', 'Crater Lake National Park; south entrance road plowed in winter.'),
('Alvord Desert',                      'Southeast Oregon',  'OR', 42.5300, -118.5300, 1, 'Year-round', 'One of the darkest places in the US; remote dirt roads.');
