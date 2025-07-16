-- Base de dados completa de códigos de área dos EUA (NANP)
-- Remove a limitação de apenas alguns códigos de área
-- Fonte: North American Numbering Plan Administration (NANPA)

CREATE TABLE IF NOT EXISTS usa_area_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_code TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    timezone TEXT NOT NULL,
    region TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Inserir todos os códigos de área dos EUA
INSERT INTO usa_area_codes (area_code, state, city, timezone, region) VALUES
-- Alabama
('205', 'Alabama', 'Birmingham', 'America/Chicago', 'South'),
('251', 'Alabama', 'Mobile', 'America/Chicago', 'South'),
('256', 'Alabama', 'Huntsville', 'America/Chicago', 'South'),
('334', 'Alabama', 'Montgomery', 'America/Chicago', 'South'),
('659', 'Alabama', 'Birmingham', 'America/Chicago', 'South'),

-- Alaska
('907', 'Alaska', 'Anchorage', 'America/Anchorage', 'West'),

-- Arizona
('480', 'Arizona', 'Scottsdale', 'America/Phoenix', 'West'),
('520', 'Arizona', 'Tucson', 'America/Phoenix', 'West'),
('602', 'Arizona', 'Phoenix', 'America/Phoenix', 'West'),
('623', 'Arizona', 'Glendale', 'America/Phoenix', 'West'),
('928', 'Arizona', 'Flagstaff', 'America/Phoenix', 'West'),

-- Arkansas
('479', 'Arkansas', 'Fort Smith', 'America/Chicago', 'South'),
('501', 'Arkansas', 'Little Rock', 'America/Chicago', 'South'),
('870', 'Arkansas', 'Jonesboro', 'America/Chicago', 'South'),

-- California
('209', 'California', 'Stockton', 'America/Los_Angeles', 'West'),
('213', 'California', 'Los Angeles', 'America/Los_Angeles', 'West'),
('279', 'California', 'Sacramento', 'America/Los_Angeles', 'West'),
('310', 'California', 'Beverly Hills', 'America/Los_Angeles', 'West'),
('323', 'California', 'Los Angeles', 'America/Los_Angeles', 'West'),
('341', 'California', 'Oakland', 'America/Los_Angeles', 'West'),
('408', 'California', 'San Jose', 'America/Los_Angeles', 'West'),
('415', 'California', 'San Francisco', 'America/Los_Angeles', 'West'),
('424', 'California', 'Los Angeles', 'America/Los_Angeles', 'West'),
('442', 'California', 'Oceanside', 'America/Los_Angeles', 'West'),
('510', 'California', 'Oakland', 'America/Los_Angeles', 'West'),
('530', 'California', 'Redding', 'America/Los_Angeles', 'West'),
('559', 'California', 'Fresno', 'America/Los_Angeles', 'West'),
('562', 'California', 'Long Beach', 'America/Los_Angeles', 'West'),
('619', 'California', 'San Diego', 'America/Los_Angeles', 'West'),
('626', 'California', 'Pasadena', 'America/Los_Angeles', 'West'),
('628', 'California', 'San Francisco', 'America/Los_Angeles', 'West'),
('650', 'California', 'Palo Alto', 'America/Los_Angeles', 'West'),
('657', 'California', 'Anaheim', 'America/Los_Angeles', 'West'),
('661', 'California', 'Bakersfield', 'America/Los_Angeles', 'West'),
('669', 'California', 'San Jose', 'America/Los_Angeles', 'West'),
('707', 'California', 'Santa Rosa', 'America/Los_Angeles', 'West'),
('714', 'California', 'Anaheim', 'America/Los_Angeles', 'West'),
('747', 'California', 'Burbank', 'America/Los_Angeles', 'West'),
('760', 'California', 'Oceanside', 'America/Los_Angeles', 'West'),
('805', 'California', 'Oxnard', 'America/Los_Angeles', 'West'),
('818', 'California', 'Burbank', 'America/Los_Angeles', 'West'),
('831', 'California', 'Salinas', 'America/Los_Angeles', 'West'),
('858', 'California', 'San Diego', 'America/Los_Angeles', 'West'),
('909', 'California', 'San Bernardino', 'America/Los_Angeles', 'West'),
('916', 'California', 'Sacramento', 'America/Los_Angeles', 'West'),
('925', 'California', 'Concord', 'America/Los_Angeles', 'West'),
('949', 'California', 'Irvine', 'America/Los_Angeles', 'West'),
('951', 'California', 'Riverside', 'America/Los_Angeles', 'West'),

-- Colorado
('303', 'Colorado', 'Denver', 'America/Denver', 'West'),
('719', 'Colorado', 'Colorado Springs', 'America/Denver', 'West'),
('720', 'Colorado', 'Denver', 'America/Denver', 'West'),
('970', 'Colorado', 'Fort Collins', 'America/Denver', 'West'),

-- Connecticut
('203', 'Connecticut', 'Bridgeport', 'America/New_York', 'Northeast'),
('475', 'Connecticut', 'Bridgeport', 'America/New_York', 'Northeast'),
('860', 'Connecticut', 'Hartford', 'America/New_York', 'Northeast'),
('959', 'Connecticut', 'Hartford', 'America/New_York', 'Northeast'),

-- Delaware
('302', 'Delaware', 'Wilmington', 'America/New_York', 'Northeast'),

-- Florida
('239', 'Florida', 'Fort Myers', 'America/New_York', 'South'),
('305', 'Florida', 'Miami', 'America/New_York', 'South'),
('321', 'Florida', 'Orlando', 'America/New_York', 'South'),
('352', 'Florida', 'Gainesville', 'America/New_York', 'South'),
('386', 'Florida', 'Daytona Beach', 'America/New_York', 'South'),
('407', 'Florida', 'Orlando', 'America/New_York', 'South'),
('561', 'Florida', 'West Palm Beach', 'America/New_York', 'South'),
('689', 'Florida', 'Orlando', 'America/New_York', 'South'),
('727', 'Florida', 'St. Petersburg', 'America/New_York', 'South'),
('754', 'Florida', 'Fort Lauderdale', 'America/New_York', 'South'),
('772', 'Florida', 'Port St. Lucie', 'America/New_York', 'South'),
('786', 'Florida', 'Miami', 'America/New_York', 'South'),
('813', 'Florida', 'Tampa', 'America/New_York', 'South'),
('850', 'Florida', 'Tallahassee', 'America/Chicago', 'South'),
('863', 'Florida', 'Lakeland', 'America/New_York', 'South'),
('904', 'Florida', 'Jacksonville', 'America/New_York', 'South'),
('941', 'Florida', 'Sarasota', 'America/New_York', 'South'),
('954', 'Florida', 'Fort Lauderdale', 'America/New_York', 'South'),

-- Georgia
('229', 'Georgia', 'Albany', 'America/New_York', 'South'),
('404', 'Georgia', 'Atlanta', 'America/New_York', 'South'),
('470', 'Georgia', 'Atlanta', 'America/New_York', 'South'),
('478', 'Georgia', 'Macon', 'America/New_York', 'South'),
('678', 'Georgia', 'Atlanta', 'America/New_York', 'South'),
('706', 'Georgia', 'Columbus', 'America/New_York', 'South'),
('762', 'Georgia', 'Columbus', 'America/New_York', 'South'),
('770', 'Georgia', 'Atlanta', 'America/New_York', 'South'),
('912', 'Georgia', 'Savannah', 'America/New_York', 'South'),

-- Hawaii
('808', 'Hawaii', 'Honolulu', 'Pacific/Honolulu', 'West'),

-- Idaho
('208', 'Idaho', 'Boise', 'America/Boise', 'West'),
('986', 'Idaho', 'Boise', 'America/Boise', 'West'),

-- Illinois
('217', 'Illinois', 'Springfield', 'America/Chicago', 'Midwest'),
('224', 'Illinois', 'Evanston', 'America/Chicago', 'Midwest'),
('309', 'Illinois', 'Peoria', 'America/Chicago', 'Midwest'),
('312', 'Illinois', 'Chicago', 'America/Chicago', 'Midwest'),
('331', 'Illinois', 'Aurora', 'America/Chicago', 'Midwest'),
('447', 'Illinois', 'Normal', 'America/Chicago', 'Midwest'),
('464', 'Illinois', 'Evanston', 'America/Chicago', 'Midwest'),
('618', 'Illinois', 'Carbondale', 'America/Chicago', 'Midwest'),
('630', 'Illinois', 'Aurora', 'America/Chicago', 'Midwest'),
('708', 'Illinois', 'Cicero', 'America/Chicago', 'Midwest'),
('773', 'Illinois', 'Chicago', 'America/Chicago', 'Midwest'),
('779', 'Illinois', 'Rockford', 'America/Chicago', 'Midwest'),
('815', 'Illinois', 'Rockford', 'America/Chicago', 'Midwest'),
('847', 'Illinois', 'Evanston', 'America/Chicago', 'Midwest'),
('872', 'Illinois', 'Chicago', 'America/Chicago', 'Midwest'),

-- Indiana
('219', 'Indiana', 'Gary', 'America/Chicago', 'Midwest'),
('260', 'Indiana', 'Fort Wayne', 'America/New_York', 'Midwest'),
('317', 'Indiana', 'Indianapolis', 'America/New_York', 'Midwest'),
('463', 'Indiana', 'Indianapolis', 'America/New_York', 'Midwest'),
('574', 'Indiana', 'South Bend', 'America/New_York', 'Midwest'),
('765', 'Indiana', 'Muncie', 'America/New_York', 'Midwest'),
('812', 'Indiana', 'Evansville', 'America/New_York', 'Midwest'),

-- Iowa
('319', 'Iowa', 'Cedar Rapids', 'America/Chicago', 'Midwest'),
('515', 'Iowa', 'Des Moines', 'America/Chicago', 'Midwest'),
('563', 'Iowa', 'Davenport', 'America/Chicago', 'Midwest'),
('641', 'Iowa', 'Mason City', 'America/Chicago', 'Midwest'),
('712', 'Iowa', 'Sioux City', 'America/Chicago', 'Midwest'),

-- Kansas
('316', 'Kansas', 'Wichita', 'America/Chicago', 'Midwest'),
('620', 'Kansas', 'Hutchinson', 'America/Chicago', 'Midwest'),
('785', 'Kansas', 'Topeka', 'America/Chicago', 'Midwest'),
('913', 'Kansas', 'Kansas City', 'America/Chicago', 'Midwest'),

-- Kentucky
('270', 'Kentucky', 'Bowling Green', 'America/Chicago', 'South'),
('364', 'Kentucky', 'Bowling Green', 'America/Chicago', 'South'),
('502', 'Kentucky', 'Louisville', 'America/New_York', 'South'),
('606', 'Kentucky', 'Ashland', 'America/New_York', 'South'),
('859', 'Kentucky', 'Lexington', 'America/New_York', 'South'),

-- Louisiana
('225', 'Louisiana', 'Baton Rouge', 'America/Chicago', 'South'),
('318', 'Louisiana', 'Shreveport', 'America/Chicago', 'South'),
('337', 'Louisiana', 'Lafayette', 'America/Chicago', 'South'),
('504', 'Louisiana', 'New Orleans', 'America/Chicago', 'South'),
('985', 'Louisiana', 'Hammond', 'America/Chicago', 'South'),

-- Maine
('207', 'Maine', 'Portland', 'America/New_York', 'Northeast'),

-- Maryland
('240', 'Maryland', 'Rockville', 'America/New_York', 'Northeast'),
('301', 'Maryland', 'Rockville', 'America/New_York', 'Northeast'),
('410', 'Maryland', 'Baltimore', 'America/New_York', 'Northeast'),
('443', 'Maryland', 'Baltimore', 'America/New_York', 'Northeast'),
('667', 'Maryland', 'Baltimore', 'America/New_York', 'Northeast'),

-- Massachusetts
('339', 'Massachusetts', 'Boston', 'America/New_York', 'Northeast'),
('351', 'Massachusetts', 'Lowell', 'America/New_York', 'Northeast'),
('413', 'Massachusetts', 'Springfield', 'America/New_York', 'Northeast'),
('508', 'Massachusetts', 'Worcester', 'America/New_York', 'Northeast'),
('617', 'Massachusetts', 'Boston', 'America/New_York', 'Northeast'),
('774', 'Massachusetts', 'Worcester', 'America/New_York', 'Northeast'),
('781', 'Massachusetts', 'Boston', 'America/New_York', 'Northeast'),
('857', 'Massachusetts', 'Boston', 'America/New_York', 'Northeast'),
('978', 'Massachusetts', 'Lowell', 'America/New_York', 'Northeast'),

-- Michigan
('231', 'Michigan', 'Muskegon', 'America/New_York', 'Midwest'),
('248', 'Michigan', 'Troy', 'America/New_York', 'Midwest'),
('269', 'Michigan', 'Kalamazoo', 'America/New_York', 'Midwest'),
('313', 'Michigan', 'Detroit', 'America/New_York', 'Midwest'),
('517', 'Michigan', 'Lansing', 'America/New_York', 'Midwest'),
('586', 'Michigan', 'Warren', 'America/New_York', 'Midwest'),
('616', 'Michigan', 'Grand Rapids', 'America/New_York', 'Midwest'),
('679', 'Michigan', 'Detroit', 'America/New_York', 'Midwest'),
('734', 'Michigan', 'Ann Arbor', 'America/New_York', 'Midwest'),
('810', 'Michigan', 'Flint', 'America/New_York', 'Midwest'),
('906', 'Michigan', 'Marquette', 'America/New_York', 'Midwest'),
('947', 'Michigan', 'Troy', 'America/New_York', 'Midwest'),
('989', 'Michigan', 'Saginaw', 'America/New_York', 'Midwest'),

-- Minnesota
('218', 'Minnesota', 'Duluth', 'America/Chicago', 'Midwest'),
('320', 'Minnesota', 'St. Cloud', 'America/Chicago', 'Midwest'),
('507', 'Minnesota', 'Rochester', 'America/Chicago', 'Midwest'),
('612', 'Minnesota', 'Minneapolis', 'America/Chicago', 'Midwest'),
('651', 'Minnesota', 'St. Paul', 'America/Chicago', 'Midwest'),
('763', 'Minnesota', 'Brooklyn Park', 'America/Chicago', 'Midwest'),
('952', 'Minnesota', 'Bloomington', 'America/Chicago', 'Midwest'),

-- Mississippi
('228', 'Mississippi', 'Biloxi', 'America/Chicago', 'South'),
('601', 'Mississippi', 'Jackson', 'America/Chicago', 'South'),
('662', 'Mississippi', 'Tupelo', 'America/Chicago', 'South'),

-- Missouri
('314', 'Missouri', 'St. Louis', 'America/Chicago', 'Midwest'),
('417', 'Missouri', 'Springfield', 'America/Chicago', 'Midwest'),
('573', 'Missouri', 'Columbia', 'America/Chicago', 'Midwest'),
('636', 'Missouri', 'O''Fallon', 'America/Chicago', 'Midwest'),
('660', 'Missouri', 'Sedalia', 'America/Chicago', 'Midwest'),
('816', 'Missouri', 'Kansas City', 'America/Chicago', 'Midwest'),

-- Montana
('406', 'Montana', 'Billings', 'America/Denver', 'West'),

-- Nebraska
('308', 'Nebraska', 'North Platte', 'America/Chicago', 'Midwest'),
('402', 'Nebraska', 'Omaha', 'America/Chicago', 'Midwest'),
('531', 'Nebraska', 'Omaha', 'America/Chicago', 'Midwest'),

-- Nevada
('702', 'Nevada', 'Las Vegas', 'America/Los_Angeles', 'West'),
('725', 'Nevada', 'Las Vegas', 'America/Los_Angeles', 'West'),
('775', 'Nevada', 'Reno', 'America/Los_Angeles', 'West'),

-- New Hampshire
('603', 'New Hampshire', 'Manchester', 'America/New_York', 'Northeast'),

-- New Jersey
('201', 'New Jersey', 'Jersey City', 'America/New_York', 'Northeast'),
('551', 'New Jersey', 'Jersey City', 'America/New_York', 'Northeast'),
('609', 'New Jersey', 'Trenton', 'America/New_York', 'Northeast'),
('640', 'New Jersey', 'Jersey City', 'America/New_York', 'Northeast'),
('732', 'New Jersey', 'New Brunswick', 'America/New_York', 'Northeast'),
('848', 'New Jersey', 'New Brunswick', 'America/New_York', 'Northeast'),
('856', 'New Jersey', 'Camden', 'America/New_York', 'Northeast'),
('862', 'New Jersey', 'Newark', 'America/New_York', 'Northeast'),
('908', 'New Jersey', 'Elizabeth', 'America/New_York', 'Northeast'),
('973', 'New Jersey', 'Newark', 'America/New_York', 'Northeast'),

-- New Mexico
('505', 'New Mexico', 'Albuquerque', 'America/Denver', 'West'),
('575', 'New Mexico', 'Las Cruces', 'America/Denver', 'West'),

-- New York
('212', 'New York', 'New York', 'America/New_York', 'Northeast'),
('315', 'New York', 'Syracuse', 'America/New_York', 'Northeast'),
('332', 'New York', 'New York', 'America/New_York', 'Northeast'),
('347', 'New York', 'New York', 'America/New_York', 'Northeast'),
('516', 'New York', 'Hempstead', 'America/New_York', 'Northeast'),
('518', 'New York', 'Albany', 'America/New_York', 'Northeast'),
('585', 'New York', 'Rochester', 'America/New_York', 'Northeast'),
('607', 'New York', 'Binghamton', 'America/New_York', 'Northeast'),
('631', 'New York', 'Brentwood', 'America/New_York', 'Northeast'),
('646', 'New York', 'New York', 'America/New_York', 'Northeast'),
('680', 'New York', 'Syracuse', 'America/New_York', 'Northeast'),
('716', 'New York', 'Buffalo', 'America/New_York', 'Northeast'),
('718', 'New York', 'New York', 'America/New_York', 'Northeast'),
('838', 'New York', 'Brentwood', 'America/New_York', 'Northeast'),
('845', 'New York', 'Poughkeepsie', 'America/New_York', 'Northeast'),
('914', 'New York', 'Yonkers', 'America/New_York', 'Northeast'),
('917', 'New York', 'New York', 'America/New_York', 'Northeast'),
('929', 'New York', 'New York', 'America/New_York', 'Northeast'),

-- North Carolina
('252', 'North Carolina', 'Greenville', 'America/New_York', 'South'),
('336', 'North Carolina', 'Greensboro', 'America/New_York', 'South'),
('704', 'North Carolina', 'Charlotte', 'America/New_York', 'South'),
('743', 'North Carolina', 'Greensboro', 'America/New_York', 'South'),
('828', 'North Carolina', 'Asheville', 'America/New_York', 'South'),
('910', 'North Carolina', 'Fayetteville', 'America/New_York', 'South'),
('919', 'North Carolina', 'Raleigh', 'America/New_York', 'South'),
('980', 'North Carolina', 'Charlotte', 'America/New_York', 'South'),
('984', 'North Carolina', 'Raleigh', 'America/New_York', 'South'),

-- North Dakota
('701', 'North Dakota', 'Fargo', 'America/Chicago', 'Midwest'),

-- Ohio
('216', 'Ohio', 'Cleveland', 'America/New_York', 'Midwest'),
('220', 'Ohio', 'Newark', 'America/New_York', 'Midwest'),
('234', 'Ohio', 'Akron', 'America/New_York', 'Midwest'),
('330', 'Ohio', 'Akron', 'America/New_York', 'Midwest'),
('380', 'Ohio', 'Columbus', 'America/New_York', 'Midwest'),
('419', 'Ohio', 'Toledo', 'America/New_York', 'Midwest'),
('440', 'Ohio', 'Parma', 'America/New_York', 'Midwest'),
('513', 'Ohio', 'Cincinnati', 'America/New_York', 'Midwest'),
('567', 'Ohio', 'Toledo', 'America/New_York', 'Midwest'),
('614', 'Ohio', 'Columbus', 'America/New_York', 'Midwest'),
('740', 'Ohio', 'Newark', 'America/New_York', 'Midwest'),
('937', 'Ohio', 'Dayton', 'America/New_York', 'Midwest'),

-- Oklahoma
('405', 'Oklahoma', 'Oklahoma City', 'America/Chicago', 'South'),
('539', 'Oklahoma', 'Tulsa', 'America/Chicago', 'South'),
('580', 'Oklahoma', 'Lawton', 'America/Chicago', 'South'),
('918', 'Oklahoma', 'Tulsa', 'America/Chicago', 'South'),

-- Oregon
('458', 'Oregon', 'Eugene', 'America/Los_Angeles', 'West'),
('503', 'Oregon', 'Portland', 'America/Los_Angeles', 'West'),
('541', 'Oregon', 'Eugene', 'America/Los_Angeles', 'West'),
('971', 'Oregon', 'Portland', 'America/Los_Angeles', 'West'),

-- Pennsylvania
('215', 'Pennsylvania', 'Philadelphia', 'America/New_York', 'Northeast'),
('267', 'Pennsylvania', 'Philadelphia', 'America/New_York', 'Northeast'),
('272', 'Pennsylvania', 'Scranton', 'America/New_York', 'Northeast'),
('412', 'Pennsylvania', 'Pittsburgh', 'America/New_York', 'Northeast'),
('445', 'Pennsylvania', 'Philadelphia', 'America/New_York', 'Northeast'),
('484', 'Pennsylvania', 'Allentown', 'America/New_York', 'Northeast'),
('570', 'Pennsylvania', 'Scranton', 'America/New_York', 'Northeast'),
('610', 'Pennsylvania', 'Allentown', 'America/New_York', 'Northeast'),
('717', 'Pennsylvania', 'Harrisburg', 'America/New_York', 'Northeast'),
('724', 'Pennsylvania', 'New Castle', 'America/New_York', 'Northeast'),
('814', 'Pennsylvania', 'Erie', 'America/New_York', 'Northeast'),
('878', 'Pennsylvania', 'Pittsburgh', 'America/New_York', 'Northeast'),

-- Rhode Island
('401', 'Rhode Island', 'Providence', 'America/New_York', 'Northeast'),

-- South Carolina
('803', 'South Carolina', 'Columbia', 'America/New_York', 'South'),
('843', 'South Carolina', 'Charleston', 'America/New_York', 'South'),
('854', 'South Carolina', 'Charleston', 'America/New_York', 'South'),
('864', 'South Carolina', 'Greenville', 'America/New_York', 'South'),

-- South Dakota
('605', 'South Dakota', 'Sioux Falls', 'America/Chicago', 'Midwest'),

-- Tennessee
('423', 'Tennessee', 'Chattanooga', 'America/New_York', 'South'),
('615', 'Tennessee', 'Nashville', 'America/Chicago', 'South'),
('629', 'Tennessee', 'Nashville', 'America/Chicago', 'South'),
('731', 'Tennessee', 'Jackson', 'America/Chicago', 'South'),
('865', 'Tennessee', 'Knoxville', 'America/New_York', 'South'),
('901', 'Tennessee', 'Memphis', 'America/Chicago', 'South'),
('931', 'Tennessee', 'Clarksville', 'America/Chicago', 'South'),

-- Texas
('214', 'Texas', 'Dallas', 'America/Chicago', 'South'),
('254', 'Texas', 'Killeen', 'America/Chicago', 'South'),
('281', 'Texas', 'Houston', 'America/Chicago', 'South'),
('325', 'Texas', 'Abilene', 'America/Chicago', 'South'),
('346', 'Texas', 'Houston', 'America/Chicago', 'South'),
('361', 'Texas', 'Corpus Christi', 'America/Chicago', 'South'),
('409', 'Texas', 'Beaumont', 'America/Chicago', 'South'),
('430', 'Texas', 'Dallas', 'America/Chicago', 'South'),
('432', 'Texas', 'Midland', 'America/Chicago', 'South'),
('469', 'Texas', 'Dallas', 'America/Chicago', 'South'),
('512', 'Texas', 'Austin', 'America/Chicago', 'South'),
('713', 'Texas', 'Houston', 'America/Chicago', 'South'),
('726', 'Texas', 'San Antonio', 'America/Chicago', 'South'),
('737', 'Texas', 'Austin', 'America/Chicago', 'South'),
('806', 'Texas', 'Lubbock', 'America/Chicago', 'South'),
('817', 'Texas', 'Fort Worth', 'America/Chicago', 'South'),
('830', 'Texas', 'New Braunfels', 'America/Chicago', 'South'),
('832', 'Texas', 'Houston', 'America/Chicago', 'South'),
('903', 'Texas', 'Tyler', 'America/Chicago', 'South'),
('915', 'Texas', 'El Paso', 'America/Denver', 'South'),
('936', 'Texas', 'Huntsville', 'America/Chicago', 'South'),
('940', 'Texas', 'Wichita Falls', 'America/Chicago', 'South'),
('945', 'Texas', 'Dallas', 'America/Chicago', 'South'),
('956', 'Texas', 'Laredo', 'America/Chicago', 'South'),
('972', 'Texas', 'Dallas', 'America/Chicago', 'South'),
('979', 'Texas', 'College Station', 'America/Chicago', 'South'),

-- Utah
('385', 'Utah', 'Salt Lake City', 'America/Denver', 'West'),
('435', 'Utah', 'St. George', 'America/Denver', 'West'),
('801', 'Utah', 'Salt Lake City', 'America/Denver', 'West'),

-- Vermont
('802', 'Vermont', 'Burlington', 'America/New_York', 'Northeast'),

-- Virginia
('276', 'Virginia', 'Martinsville', 'America/New_York', 'South'),
('434', 'Virginia', 'Lynchburg', 'America/New_York', 'South'),
('540', 'Virginia', 'Roanoke', 'America/New_York', 'South'),
('571', 'Virginia', 'Arlington', 'America/New_York', 'South'),
('703', 'Virginia', 'Arlington', 'America/New_York', 'South'),
('757', 'Virginia', 'Virginia Beach', 'America/New_York', 'South'),
('804', 'Virginia', 'Richmond', 'America/New_York', 'South'),

-- Washington
('206', 'Washington', 'Seattle', 'America/Los_Angeles', 'West'),
('253', 'Washington', 'Tacoma', 'America/Los_Angeles', 'West'),
('360', 'Washington', 'Olympia', 'America/Los_Angeles', 'West'),
('425', 'Washington', 'Bellevue', 'America/Los_Angeles', 'West'),
('509', 'Washington', 'Spokane', 'America/Los_Angeles', 'West'),
('564', 'Washington', 'Olympia', 'America/Los_Angeles', 'West'),

-- West Virginia
('304', 'West Virginia', 'Charleston', 'America/New_York', 'South'),
('681', 'West Virginia', 'Charleston', 'America/New_York', 'South'),

-- Wisconsin
('262', 'Wisconsin', 'Kenosha', 'America/Chicago', 'Midwest'),
('274', 'Wisconsin', 'Green Bay', 'America/Chicago', 'Midwest'),
('414', 'Wisconsin', 'Milwaukee', 'America/Chicago', 'Midwest'),
('534', 'Wisconsin', 'Eau Claire', 'America/Chicago', 'Midwest'),
('608', 'Wisconsin', 'Madison', 'America/Chicago', 'Midwest'),
('715', 'Wisconsin', 'Eau Claire', 'America/Chicago', 'Midwest'),
('920', 'Wisconsin', 'Green Bay', 'America/Chicago', 'Midwest'),

-- Wyoming
('307', 'Wyoming', 'Cheyenne', 'America/Denver', 'West'),

-- Códigos especiais (toll-free)
('800', 'Toll-Free', 'Nationwide', 'America/New_York', 'Special'),
('833', 'Toll-Free', 'Nationwide', 'America/New_York', 'Special'),
('844', 'Toll-Free', 'Nationwide', 'America/New_York', 'Special'),
('855', 'Toll-Free', 'Nationwide', 'America/New_York', 'Special'),
('866', 'Toll-Free', 'Nationwide', 'America/New_York', 'Special'),
('877', 'Toll-Free', 'Nationwide', 'America/New_York', 'Special'),
('888', 'Toll-Free', 'Nationwide', 'America/New_York', 'Special')

ON CONFLICT (area_code) DO NOTHING;

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_usa_area_codes_state ON usa_area_codes(state);
CREATE INDEX IF NOT EXISTS idx_usa_area_codes_region ON usa_area_codes(region);
CREATE INDEX IF NOT EXISTS idx_usa_area_codes_active ON usa_area_codes(active);

-- Comentários da tabela
-- Comentários removidos para compatibilidade com SQLite
-- Esta tabela contém a base de dados completa de códigos de área dos EUA (NANP)
-- Remove a limitação de apenas alguns códigos de área