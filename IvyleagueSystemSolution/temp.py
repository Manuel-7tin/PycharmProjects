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

b = bee()
b.wings=3
print(b.wings)
from flask import Flask, jsonify
app = Flask(__name__)
def do():
    with app.app_context():
        return jsonify(
            {
                    "title": "user.title",
                    "firstname": "user.first_name",
            }
        )
# do()
print(type(do()))#[0].json) #[0].get("title"))

from werkzeug.security import generate_password_hash, check_password_hash
print(check_password_hash("pbkdf2:sha256:1000000$zxG7O6ST$6ec9723a0ea37e6c9ffecf47d4a1c8b6f4c6f85b2584f7a2f5ce46b57858f2f3", "a@123456"))
