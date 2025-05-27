from io import StringIO
from io import BytesIO
import json

l = ["ewjjadniqwa\nfcgc", "fnsnosns\ngcvgcg", "snfosncions\ndxezxyx"]


buffer2 = BytesIO()
buffer = BytesIO()
for i in l:
    buffer2.write(i.encode("utf-8"))
    buffer2.write(b"\n\n")
buffer2.seek(0)

data = {"ewjjadniqwa": "fcgc", "fnsnosns": "gcvgcg", "snfosncions": "dxezxyx"}

buffer.write(json.dumps(data).encode("utf-8"))
buffer.seek(0)

print(buffer2.read())
print(buffer.read())


w = {1:[12, "r"]}
w[1].append(3)
for i, j in w.items():
    print(i, j)
print(len(w))
print("log:"[:3])

info = {
    'SBL STANDARD': ['2025-05-01T11:48:01.214356', '20 people attended the SBL STANDARD class held on the 06th of April, year 2025', "['Teaching Materials', 'Admin'] were left out of the marking."],
    'DIPIFR STANDARD': ['2025-05-01T11:48:05.481626', '10 people attended the DIPIFR STANDARD class held on the 05th of April, year 2025', "['Teaching Materials', 'Admin'] were left out of the marking."],
    'TX STANDARD': ['2025-05-01T11:48:09.803908', '14 people attended the TX STANDARD class held on the 06th of April, year 2025', "['Teaching Materials', 'Admin'] were left out of the marking."]
}
buffer = BytesIO()
for key, value in info.items():
    buffer.write(f"{value[0]}|{key}\n".encode("utf-8"))
    for i, item in enumerate(value):
        buffer.write(item.encode("utf-8") if i != 0 else b"")
        buffer.write(b"\n")
    buffer.write(b"\n\n")
buffer.seek(0)
print(info)
print("info content:", buffer.read())