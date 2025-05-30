from xml.etree.ElementTree import indent

p = {1:"one", 2:"two"}
print([1, 2, 4] + [3, 5, 4])
print("std" in "sbd-int")

import datetime # e.g., 8420

print(datetime.datetime.now().year)

def encode_year(year: int, a=117, b=53, m=10000):
    return (a * year + b) % m

def decode_year(code: int, a=117, b=53, m=10000):
    a_inv = pow(a, -1, m)  # modular inverse
    return ((code - b) * a_inv) % m

def encode_serial(serial: int, a=211, b=79, m=10000):
    return (a * serial + b) % m

def decode_serial(code: int, a=211, b=79, m=10000):
    a_inv = pow(a, -1, m)
    return ((code - b) * a_inv) % m


year_code = encode_year(2025)  # e.g., 6318
serial_code = encode_serial(70)

print(f"1331-{year_code:04d}-{serial_code:04d}")
print(decode_year(6978), decode_serial(4849))
{}.get("j")
print(sum([1,2,3,4]))
f = 6
print("f".isdigit())
def num(a, b):
    print(a)
x = 5
spent = 30_000 * (2025*365+506)
money = 897_000_000 * 1600
print((spent/money)*100)
print((5/15)*100)
class bee:
    def __init__(self):
        self.wings = 4

import json
with open("questions.json", mode="r")as file:
    dict = json.load(file)


def never_use_this():
    """Completely deletes the postgres database without a trace"""
    import psycopg2
    import psycopg2.extensions
    from psycopg2 import sql

    # Database credentials
    admin_db = "postgres"  # Default admin DB to connect to
    host = "localhost"
    user = "postgres"
    password = "root"
    port = 5432

    # Database to delete
    target_db = "ivyleague"

    # Connect to the admin DB
    conn = psycopg2.connect(
        dbname=admin_db,
        user=user,
        password=password,
        host=host,
        port=port
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Check if the DB exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (target_db,))
    exists = cur.fetchone()

    if exists:
        # Terminate all connections to the target DB
        cur.execute(sql.SQL("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = %s AND pid <> pg_backend_pid()
        """), [target_db])

        # Drop the database
        cur.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(target_db)))
        print(f"Database '{target_db}' has been dropped.")
    else:
        print(f"Database '{target_db}' does not exist.")

    # Clean up
    cur.close()
    conn.close()


# never_use_this()
# from services.account_services import send_signup_message, verify_email
# send_signup_message("test_user", "opolopothings@gmail.com")
d = datetime.datetime.now().day
e = datetime.datetime.now().weekday()
f = datetime.datetime.now().isoweekday()
print(d, e, f)
try:
    print({}.get("dskk", 0)/100)
except TypeError as e:
    print("ba code")
