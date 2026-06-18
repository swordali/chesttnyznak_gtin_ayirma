import streamlit as st
from zipfile import ZipFile
from collections import defaultdict
import io

st.title("GTIN TXT Ayırıcı")

uploaded = st.file_uploader("TXT veya ZIP dosyanı yükle", type=["txt", "zip"])

gtins_text = st.text_area(
    "GTIN numaraları",
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
                st.error("ZIP içinde TXT dosyası bulunamadı.")
                st.stop()
            text = z.read(txt_files[0]).decode("utf-8", errors="ignore")
    else:
        text = raw.decode("utf-8", errors="ignore")

    gtins = [g.strip() for g in gtins_text.splitlines() if g.strip()]
    prefixes = ["01" + g for g in gtins]

    groups = defaultdict(list)
    lines = [x.strip() for x in text.splitlines() if x.strip()]

    for line in lines:
        for prefix in prefixes:
            pos = line.find(prefix)
            if pos != -1:
                groups[prefix].append(line[pos:])
                break

    st.write("Toplam satır:", len(lines))

    output_zip = io.BytesIO()

    with ZipFile(output_zip, "w") as z:
        for prefix in prefixes:
            filename = f"{prefix}.txt"
            content = "\n".join(groups[prefix])
            if content:
                content += "\n"

            z.writestr(filename, content)
            st.write(filename, "→", len(groups[prefix]), "kod")

    st.download_button(
        "Ayrılmış TXT dosyalarını ZIP olarak indir",
        data=output_zip.getvalue(),
        file_name="gtin_ayrilmis.zip",
        mime="application/zip"
    )
