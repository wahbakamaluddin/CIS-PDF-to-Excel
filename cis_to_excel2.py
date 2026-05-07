import re
import sys
import json
import csv
import pandas as pd
import tika
tika.initVM()
from tika import parser


cispdf, outfile = "",""

if len(sys.argv) < 3:
    print("[!] Please provide input and output filename!")
    print("Usage: python {} <input.pdf> <output>\n".format(sys.argv[0]))
    print("Note: For <output>, no need to provide file extension.")
    exit()
else:
    cispdf = sys.argv[1]
    outfile = sys.argv[2]


# json file - converted CIS benchmark to json format with 
cisjson = "{}.json".format(outfile)
cisexcel = "{}.xlsx".format(outfile)

# excel file


# cis text output
cistext = 'cis_text.txt'

#---------------------------------------------------
print("[+] Converting '{}' to text...".format(cispdf))
# tika write get text from pdf
raw = parser.from_file(cispdf)
data = raw['content']

print("[+] creating temp text file...")
# write pdf to text
f = open(cistext,'w', encoding='utf-8')
f.write(data)

# Remove blank lines

with open(cistext, 'r', encoding='utf-8') as filer:
    with open('temp.txt', 'w', encoding='utf-8') as filew:
        for line in filer:
            if not line.strip():
                continue
            if line:
                # start writing
                filew.write(line)

#-------------------------------------------------------

                
flagStart, flagDesc, flagRationale, flagAudit, flagRecom, flagComplete = False, False, False, False, False, False
cis_title, cis_desc, cis_rationale, cis_audit, cis_recom = "", "", "", "", ""
listObj = []

print("[+] Converting to Json...")
with open("temp.txt", 'r', encoding='utf-8') as filer:
    for line in filer:
        if not line.strip():
            continue

        x = {}

        if re.match(r"^[0-9]\.[0-9]", line):
            cis_title, cis_desc, cis_rationale, cis_audit, cis_recom = line, "", "", "", ""
            flagStart, flagDesc, flagRationale, flagAudit, flagRecom, flagComplete = True, False, False, False, False, False

        if flagStart:

            # Description: until Rationale:
            if "Description:" in line:
                flagDesc = True

            if flagDesc:
                if "Description:" in line:
                    continue
                cis_desc += line

            if "Rationale:" in line:
                flagDesc = False
                flagRationale = True
                continue

            # Rationale: until Audit:
            if flagRationale:
                if "Audit:" in line:
                    flagRationale = False
                    flagAudit = True
                    continue
                cis_rationale += line

            # Audit: until Remediation:
            if "Audit:" in line:
                flagAudit = True

            if flagAudit:
                if "Audit:" in line:
                    continue
                cis_audit += line

            if "Remediation:" in line:
                flagAudit = False
                flagRecom = True
                continue

            # Remediation: until References / Additional Information / CIS Controls
            if flagRecom:
                if "Remediation:" in line:
                    continue
                cis_recom += line

            if ("References:" in line) or ("Additional Information:" in line) or ("CIS Controls:" in line):
                flagRecom = False
                flagComplete = True

            if flagComplete:
                cis_title = cis_title.replace('\n', '').strip()

                cis_desc = cis_desc.replace('\n', ' ').replace('Rationale:', '').replace('| P a g e', '').strip()
                cis_rationale = cis_rationale.replace('\n', ' ').replace('Audit:', '').replace('| P a g e', '').strip()
                cis_audit = cis_audit.replace('\n', ' ').replace('Remediation:', '').replace('| P a g e', '').strip()
                cis_recom = cis_recom.replace('\n', ' ').replace('CIS Controls:', '').replace('Additional Information:', '').replace('References:', '').replace('| P a g e', '').strip()

                x['title'] = cis_title
                x['description'] = cis_desc
                x['rationale'] = cis_rationale
                x['audit'] = cis_audit
                x['recommendations'] = cis_recom

                listObj.append(x)

                cis_title, cis_desc, cis_rationale, cis_audit, cis_recom = "", "", "", "", ""
                flagStart = False