# Sabit değerler
AIRCRAFT_TYPES = [
    ('TB2', 'TB2'),
    ('TB3', 'TB3'),
    ('AKINCI', 'AKINCI'),
    ('KIZILELMA', 'KIZILELMA'),
]

TEAM_TYPES = [
    ('BODY', 'Gövde'),
    ('WING', 'Kanat'),
    ('TAIL', 'Kuyruk'),
    ('AVIONICS', 'Aviyonik'),
    ('ASSEMBLY', 'Montaj'),
]

# Her uçak tipi için gerekli parça sayıları
REQUIRED_PARTS = {
    'TB2': {'AVIONICS': 1, 'BODY': 1, 'WING': 1, 'TAIL': 1},
    'TB3': {'AVIONICS': 1, 'BODY': 1, 'WING': 1, 'TAIL': 1},
    'AKINCI': {'AVIONICS': 1, 'BODY': 1, 'WING': 1, 'TAIL': 1},
    'KIZILELMA': {'AVIONICS': 1, 'BODY': 1, 'WING': 1, 'TAIL': 1},
} 