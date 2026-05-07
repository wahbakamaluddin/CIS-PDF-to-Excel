import re
import sys
import json
import pandas as pd
import tika
from tika import parser

tika.initVM()

if len(sys.argv) < 3:
    print("[!] Please provide input and output filename!")
    print(f"Usage: python {sys.argv[0]} <input.pdf> <output>\n")
    print("Note: For <output>, no need to provide file extension.")
    sys.exit()

cispdf = sys.argv[1]
outfile = sys.argv[2]

cisjson = f"{outfile}.json"
cisexcel = f"{outfile}.xlsx"
cistext = "cis_text.txt"

print(f"[+] Converting '{cispdf}' to text...")

raw = parser.from_file(cispdf)
data = raw.get("content", "")

print("[+] Creating temp text file...")

with open(cistext, "w", encoding="utf-8") as f:
    f.write(data)

with open(cistext, "r", encoding="utf-8") as filer:
    with open("temp.txt", "w", encoding="utf-8") as filew:
        for line in filer:
            if line.strip():
                filew.write(line)

flagStart = False
flagDesc = False
flagRationale = False
flagAudit = False
flagRecom = False
flagComplete = False

cis_title = ""
cis_desc = ""
cis_rationale = ""
cis_audit = ""
cis_recom = ""

listObj = []

print("[+] Converting to JSON...")

with open("temp.txt", "r", encoding="utf-8") as filer:
    for line in filer:
        if not line.strip():
            continue

        if re.match(r"^[0-9]+\.[0-9]+", line):
            cis_title = line
            cis_desc = ""
            cis_rationale = ""
            cis_audit = ""
            cis_recom = ""

            flagStart = True
            flagDesc = False
            flagRationale = False
            flagAudit = False
            flagRecom = False
            flagComplete = False

        if flagStart:
            if "Description:" in line:
                flagDesc = True
                continue

            if "Rationale:" in line:
                flagDesc = False
                flagRationale = True
                continue

            if "Audit:" in line:
                flagRationale = False
                flagAudit = True
                continue

            if "Remediation:" in line:
                flagAudit = False
                flagRecom = True
                continue

            if (
                "References:" in line
                or "Additional Information:" in line
                or "CIS Controls:" in line
            ):
                flagRecom = False
                flagComplete = True

            if flagDesc:
                cis_desc += line

            if flagRationale:
                cis_rationale += line

            if flagAudit:
                cis_audit += line

            if flagRecom:
                cis_recom += line

            if flagComplete:
                x = {
                    "title": cis_title.replace("\n", "").strip(),
                    "description": cis_desc.replace("\n", " ").replace("| P a g e", "").strip(),
                    "rationale": cis_rationale.replace("\n", " ").replace("| P a g e", "").strip(),
                    "audit": cis_audit.replace("\n", " ").replace("| P a g e", "").strip(),
                    "recommendations": cis_recom.replace("\n", " ").replace("| P a g e", "").strip(),
                }

                listObj.append(x)

                cis_title = ""
                cis_desc = ""
                cis_rationale = ""
                cis_audit = ""
                cis_recom = ""

                flagStart = False
                flagDesc = False
                flagRationale = False
                flagAudit = False
                flagRecom = False
                flagComplete = False

print(f"[+] Writing to '{cisjson}' ...")

with open(cisjson, "w", encoding="utf-8") as json_file:
    json.dump(listObj, json_file, indent=4, separators=(",", ": "))

print(f"[+] Creating '{cisexcel}' ...")

df_json = pd.read_json(cisjson)
df_json.to_excel(cisexcel, index=False)

print("[+] Done!")