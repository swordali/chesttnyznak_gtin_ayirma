import streamlit as st
from zipfile import ZipFile
from collections import defaultdict
import io

st.title("GS1 DataMatrix GTIN Ayırıcı")

uploaded = st.file_uploader("TXT veya ZIP yükle", type=["txt", "zip"])

gtins_text = st.text_area(
    "GTIN listesi",
    value="""04695660284417
04695660284394
04695660284301
04695660284318
04695660284295
04695660284400"""
)

if uploaded:
    raw = uploaded.read()

    if uploaded.name.lower().endswith(".zip"):
        with ZipFile(io.BytesIO(raw), "r") as z:
            txt_files = [n for n in z.namelist() if n.lower().endswith(".txt")]
            if not txt_files:
                st.error("ZIP içinde TXT bulunamadı.")
                st.stop()
            data = z.read(txt_files[0])   # BYTES olarak oku
    else:
        data = raw                         # BYTES olarak oku

    gtins = [g.strip() for g in gtins_text.splitlines() if g.strip()]
    prefixes = [("01" + g).encode("ascii") for g in gtins]

    # Satırları bytes olarak böl, 0x1D karakterini korur
    lines = [line.strip(b"\r\n") for line in data.splitlines() if line.strip(b"\r\n")]

    groups = defaultdict(list)

    for line in lines:
        for prefix in prefixes:
            pos = line.find(prefix)
            if pos != -1:
                groups[prefix].append(line[pos:])  # GS/FNC1 karakterleri korunur
                break

    st.write("Toplam satır:", len(lines))

    output_zip = io.BytesIO()

    with ZipFile(output_zip, "w") as z:
        for prefix in prefixes:
            filename = prefix.decode("ascii") + ".txt"
            content = b"\n".join(groups[prefix])
            if content:
                content += b"\n"

            z.writestr(filename, content)

            st.write(filename, "→", len(groups[prefix]), "kod")

            if groups[prefix]:
                st.code(groups[prefix][0].decode("utf-8", errors="replace"))

    st.download_button(
        "ZIP indir",
        data=output_zip.getvalue(),
        file_name="gtin_ayrilmis.zip",
        mime="application/zip"
    )
