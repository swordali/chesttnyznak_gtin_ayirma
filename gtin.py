from zipfile import ZipFile
from collections import defaultdict
import os

zip_path = "all_full_codes_with_crypto_tail (3).zip"
outdir = "gtin_ayrilmis"
os.makedirs(outdir, exist_ok=True)

gtins = [
    "04695660284417",
    "04695660284394",
    "04695660284301",
    "04695660284318",
    "04695660284295",
    "04695660284400",
]

# Dosyada kodlar 01 + GTIN + 215... şeklinde başlıyor
prefixes = ["01" + g for g in gtins]

with ZipFile(zip_path, "r") as z:
    txt_name = [n for n in z.namelist() if n.lower().endswith(".txt")][0]
    text = z.read(txt_name).decode("utf-8", errors="ignore")

lines = [x.strip() for x in text.splitlines() if x.strip()]

groups = defaultdict(list)

for line in lines:
    for prefix in prefixes:
        pos = line.find(prefix)
        if pos != -1:
            groups[prefix].append(line[pos:])
            break

print("Toplam satır:", len(lines))

for prefix in prefixes:
    filename = prefix + ".txt"
    path = os.path.join(outdir, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(groups[prefix]))
        if groups[prefix]:
            f.write("\n")

    print(filename, "->", len(groups[prefix]), "kod")
