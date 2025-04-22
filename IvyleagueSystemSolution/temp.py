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

from werkzeug.security import generate_password_hash, check_password_hash
print(check_password_hash("pbkdf2:sha256:1000000$zxG7O6ST$6ec9723a0ea37e6c9ffecf47d4a1c8b6f4c6f85b2584f7a2f5ce46b57858f2f3", "a@123456"))
