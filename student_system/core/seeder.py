import random
import string
import sys
import os

# Ensure the parent directory is in sys.path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try relative import first, fall back to absolute
try:
    from .database import get_connection
except ImportError:
    from core.database import get_connection



COLLEGES = [
    ("CCS",  "College of Computer Studies"),
    ("COE",  "College of Engineering"),
    ("CSM",  "College of Science and Mathematics"),
    ("CEBA", "College of Economics, Business and Accountancy"),
    ("CHS",  "College of Health Sciences"),
    ("CASS", "College of Arts and Social Sciences"),
    ("CED",  "College of Education"),
]

PROGRAMS = [
    # CCS — College of Computer Studies
    ("BSCS",     "Bachelor of Science in Computer Science",                        "CCS"),
    ("BSIT",     "Bachelor of Science in Information Technology",                  "CCS"),
    ("BSIS",     "Bachelor of Science in Information Systems",                     "CCS"),

    # COE — College of Engineering
    ("BSCHE",    "Bachelor of Science in Chemical Engineering",                    "COE"),
    ("BSCE",     "Bachelor of Science in Civil Engineering",                       "COE"),
    ("BSCOE",    "Bachelor of Science in Computer Engineering",                    "COE"),
    ("BSEE",     "Bachelor of Science in Electrical Engineering",                  "COE"),
    ("BSECE",    "Bachelor of Science in Electronics and Communications Engineering", "COE"),
    ("BSME",     "Bachelor of Science in Mechanical Engineering",                  "COE"),
    ("BSCerE",   "Bachelor of Science in Ceramics Engineering",                    "COE"),
    ("BSMetE",   "Bachelor of Science in Metallurgical Engineering",               "COE"),
    ("BSMining", "Bachelor of Science in Mining Engineering",                      "COE"),

    # CSM — College of Science and Mathematics
    ("BSMATH",   "Bachelor of Science in Mathematics",                             "CSM"),
    ("BSSTAT",   "Bachelor of Science in Statistics",                              "CSM"),
    ("BSPHYS",   "Bachelor of Science in Physics",                                 "CSM"),
    ("BSCHEM",   "Bachelor of Science in Chemistry",                               "CSM"),
    ("BSAnBio",  "Bachelor of Science in Animal Biology",                          "CSM"),
    ("BSMarBio", "Bachelor of Science in Marine Biology",                          "CSM"),
    ("BSMicBio", "Bachelor of Science in Microbiology",                            "CSM"),

    # CEBA — College of Economics, Business and Accountancy
    ("BSA",      "Bachelor of Science in Accountancy",                             "CEBA"),
    ("BSECON",   "Bachelor of Science in Economics",                               "CEBA"),
    ("BSBA-MM",  "Bachelor of Science in Business Administration - Marketing Management", "CEBA"),
    ("BSHM",     "Bachelor of Science in Hospitality Management",                  "CEBA"),

    # CHS — College of Health Sciences
    ("BSN",      "Bachelor of Science in Nursing",                                 "CHS"),

    # CASS — College of Arts and Social Sciences
    ("BAE",    "Bachelor of Arts in English",                                    "CASS"),
    ("BAH",   "Bachelor of Arts in History",                                    "CASS"),
    ("BAPS", "Bachelor of Arts in Political Science",                          "CASS"),
    ("BAP",  "Bachelor of Arts in Psychology",                                 "CASS"),
    ("BAS",  "Bachelor of Arts in Sociology",                                  "CASS"),

    # CED — College of Education
    ("BEED",     "Bachelor of Elementary Education",                               "CED"),
    ("BSED-BIO", "Bachelor of Secondary Education Major in Biology",               "CED"),
    ("BSED-CHEM","Bachelor of Secondary Education Major in Chemistry",             "CED"),
    ("BSED-MATH","Bachelor of Secondary Education Major in Mathematics",           "CED"),
    ("BSED-PHYS","Bachelor of Secondary Education Major in Physics",               "CED"),
    ("BPEd",     "Bachelor in Physical Education",                                 "CED"),
]

FIRST_NAMES = [
    # Male
    "Juan", "Jose", "Pedro", "Carlos", "Miguel", "Luis", "Ramon", "Eduardo",
    "Roberto", "Antonio", "Rodel", "Danilo", "Mark", "John", "James",
    "Michael", "Kevin", "Ryan", "Jerome", "Adrian", "Felix", "Gilbert",
    "Harold", "Renato", "Ernesto", "Alvin", "Bernard", "Christian", "Dennis",
    "Edgar", "Ferdinand", "George", "Henry", "Ivan", "Joel", "Kenneth",
    "Leonardo", "Manuel", "Nathan", "Oscar", "Patrick", "Quirino", "Richard",
    "Samuel", "Timothy", "Ulysses", "Victor", "Walter", "Xavier", "Yusuf",
    "Aaron", "Benedict", "Cedric", "Dominic", "Eugene", "Francis", "Gerard",
    "Homer", "Ignacio", "Jason", "Leandro", "Marco", "Nestor", "Oliver",
    "Paolo", "Raul", "Stefan", "Teodoro", "Urbano", "Vicente", "Warren",
    "Aldrin", "Benito", "Crisanto", "Dante", "Efren", "Florante", "Gino",
    "Hermie", "Ismael", "Jomar", "Kristopher", "Lito", "Marlon", "Noel",
    "Orlan", "Percival", "Rodrigo", "Salvador", "Tirso", "Valentino",
    # Female
    "Maria", "Ana", "Rosa", "Elena", "Carmen", "Patricia", "Isabel",
    "Maricel", "Lorna", "Cynthia", "Sheila", "Kristine", "Jennifer",
    "Christine", "Jasmine", "Grace", "Paula", "Angela", "Melissa", "Donna",
    "Rowena", "Vanessa", "Rosario", "Marianne", "Liza", "Abigail", "Beatriz",
    "Carla", "Diana", "Elvira", "Fatima", "Gloria", "Hannah", "Irene",
    "Josephine", "Karen", "Lorena", "Maribel", "Nora", "Olivia", "Pauline",
    "Rachel", "Sandra", "Teresa", "Uma", "Virginia", "Wendy", "Ximena",
    "Yolanda", "Zenaida", "Almira", "Brenda", "Cecilia", "Dolores", "Esther",
    "Felicia", "Gina", "Herminia", "Imelda", "Josefa", "Katrina", "Ligaya",
    "Marites", "Norma", "Ofelia", "Pilar", "Rhodora", "Salome", "Teresita",
    "Ursula", "Vilma", "Wenda", "Yvonne", "Zara", "Analiza", "Bernadette",
    "Corazon", "Daisy", "Edna", "Florinda", "Glenda", "Hazel", "Ivy",
    "Jessa", "Kristel", "Lailanie", "Mylene", "Nimfa", "Ophelia", "Precious",
]

LAST_NAMES = [
    "Santos", "Reyes", "Cruz", "Bautista", "Ocampo", "Garcia", "Mendoza",
    "Torres", "Flores", "Gonzales", "Dela Cruz", "Ramos", "Aquino", "Lopez",
    "Villanueva", "Castillo", "Morales", "Pascual", "Domingo", "Navarro",
    "Aguilar", "Salazar", "Sy", "Tan", "Lim", "Uy", "Chua", "Go",
    "Fernandez", "Rivera", "Soriano", "Diaz", "Castro", "Guevarra", "Macaraeg",
    "Manalo", "Santiago", "Bernardo", "Concepcion", "Esguerra", "Espiritu",
    "Magno", "Mercado", "Perez", "Pineda", "Quizon", "Sison", "Valdez",
    "Yap", "Zabala", "Abella", "Buenaventura", "Cañete", "Delos Reyes",
    "Evangelista", "Fuentes", "Guerrero", "Herrera", "Ibañez", "Jimenez",
    "Lacson", "Maglalang", "Nieto", "Orozco", "Palma", "Quijano", "Roxas",
    "Silverio", "Tablante", "Umali", "Vargas", "Wenceslao", "Ybañez",
    "Zaragoza", "Alcantara", "Baluyot", "Corpuz", "Dimalanta", "Enriquez",
    "Fontanilla", "Guzman", "Hilario", "Ilustre", "Javier", "Katigbak",
    "Lagman", "Macapagal", "Natividad", "Obra", "Pimentel", "Quisumbing",
    "Romualdez", "Sulit", "Tolentino", "Ureta", "Velasco", "Villafuerte",
    "Yacat", "Zamora", "Abalos", "Bagasao", "Caguioa", "Datumanong",
    "Escudero", "Fariñas", "Gatchalian", "Honasan", "Imelda", "Joson",
    "Kintanar", "Lacuna", "Mañalac", "Nograles", "Osmeña", "Padilla",
    "Remulla", "Sotto", "Tañada", "Ungab", "Villar", "Warlito", "Zubiri",
]


def seed() -> None:
    conn = get_connection()

    # Check if already seeded
    count = conn.execute("SELECT COUNT(*) FROM student").fetchone()[0]
    if count >= 5000:
        print("[Seeder] Database already seeded, skipping.")
        return

    print("[Seeder] Seeding colleges...")
    for code, name in COLLEGES:
        conn.execute(
            "INSERT OR IGNORE INTO college (code, name) VALUES (?, ?)", (code, name)
        )

    print("[Seeder] Seeding programs...")
    for code, name, college in PROGRAMS:
        conn.execute(
            "INSERT OR IGNORE INTO program (code, name, college) VALUES (?, ?, ?)",
            (code, name, college)
        )

    print("[Seeder] Seeding 5000 students...")
    program_codes = [p[0] for p in PROGRAMS]
    genders = ["Male", "Female", "Other"]
    existing_ids: set[str] = set()

    existing_names: set[str] = set()

    current_year = 2026
    students = []
    
    while len(students) < 5000:
        # To limit to Year 4, the earliest enrollment year is 2022 (2026 - 2022 = 4)
        # To include Year 1, the latest enrollment year is 2025 (2026 - 2025 = 1)
        enrolled_year = random.randint(2022, 2025) 
        number = random.randint(1, 9999)
        student_id = f"{enrolled_year}-{number:04d}"
        
        if student_id in existing_ids:
            continue

        firstname = random.choice(FIRST_NAMES)
        lastname = random.choice(LAST_NAMES)
        full_name = f"{firstname} {lastname}"
        
        if full_name in existing_names:
            continue

        # Calculate year level: 2022=4, 2023=3, 2024=2, 2025=1
        yr = current_year - enrolled_year 

        existing_ids.add(student_id)
        existing_names.add(full_name)

        course = random.choice(program_codes)
        gender = random.choices(genders, weights=[48, 48, 4])[0]

        students.append((student_id, firstname, lastname, course, yr, gender))

    conn.executemany(
        "INSERT OR IGNORE INTO student (id, firstname, lastname, course, year, gender) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        students
    )
    conn.commit()
    print(f"[Seeder] Done. {len(students)} students inserted.")
