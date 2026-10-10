import os
import glob
import re

base_dir = r"D:\crew\experiment\comperatore-seguros"

html_files = glob.glob(os.path.join(base_dir, "**", "*.html"), recursive=True)

print(f"Found {len(html_files)} HTML files:")
for f in html_files:
    print("-", f)

# Replacements to make across subpages:
# 1. "Mauricio Comperatore (PAS Matrícula SSN)" -> "Mauricio Comperatore (PAS Matrícula SSN N° 51526)"
# 2. "Mauricio Comperatore (PAS y Martillero)" -> "Mauricio Comperatore (PAS Matrícula SSN N° 51526 y Martillero)"
# 3. "Productor Asesor de Seguros Matriculado SSN Ley 22.400" -> "Productor Asesor de Seguros Matriculado SSN Ley 22.400 (Matrícula N° 51526)"
# 4. "Productor Asesor de Seguros (PAS)" in context of registration -> include Matrícula N° 51526
# 5. Footers with "(PAS Matrícula SSN)"

for fpath in html_files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    orig = content

    # Replace variations
    content = content.replace("Mauricio Comperatore (PAS Matrícula SSN)", "Mauricio Comperatore (PAS Matrícula SSN N° 51526)")
    content = content.replace("Mauricio Comperatore (PAS y Martillero)", "Mauricio Comperatore (PAS Matrícula SSN N° 51526 y Martillero)")
    content = content.replace("Mauricio Comperatore &bull; Productor Asesor de Seguros Matriculado SSN Ley 22.400", "Mauricio Comperatore &bull; Productor Asesor de Seguros Matriculado SSN Ley 22.400 (Matrícula N° 51526)")
    content = content.replace("Productor Asesor de Seguros Matriculado (SSN Ley 22.400)", "Productor Asesor de Seguros Matriculado (SSN Ley 22.400 - Matrícula N° 51526)")

    # Also check if schema.org Person jobTitle needs 51526
    content = re.sub(r'"jobTitle":\s*"Productor Asesor de Seguros Matriculado"', r'"jobTitle": "Productor Asesor de Seguros Matriculado (Matrícula SSN N° 51526)"', content)
    content = re.sub(r'"jobTitle":\s*"Productor Asesor de Seguros Matriculado y Martillero Público"', r'"jobTitle": "Productor Asesor de Seguros Matriculado (Matrícula SSN N° 51526) y Martillero Público"', content)

    # In subpage navbars, if it has "Mendoza, Argentina &bull; ...", make sure Mauricio's PAS title appears
    # Also in footers, add SSN official link if missing
    if "Superintendencia de Seguros de la Nación" not in content:
        content = content.replace("&bull; Mendoza, Argentina</p>", "&bull; <a href=\"https://www.argentina.gob.ar/ssn\" target=\"_blank\" rel=\"noopener noreferrer\" class=\"underline hover:text-slate-300\">Superintendencia de Seguros de la Nación</a> &bull; Mendoza, Argentina</p>")

    if content != orig:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated {os.path.basename(os.path.dirname(fpath)) or 'root'}/{os.path.basename(fpath)}")
    else:
        print(f"No changes needed for {os.path.basename(os.path.dirname(fpath)) or 'root'}/{os.path.basename(fpath)}")
