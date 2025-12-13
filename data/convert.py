import json
import re

input_file = "new_cleaned.jsonl"
output_file = "new_cleaned_single_tag.jsonl"

# Full list of tag types
tag_types = [
    "ACCOUNT_NUMBER", "ADDRESS", "APPLICATION_ID", "BRANCH_CODE",
    "CARD_NUMBER", "CHEQUE_NUMBER", "CUSTOMER_ID", "DATE_RANGE",
    "DOB", "DOCUMENT_ID", "EMAIL", "EMPLOYEE_ID", "FUND_ID",
    "ID_NUMBER", "IFSC_CODE", "NAME", "ORGANIZATION", "PHONE",
    "POLICY_ID", "SWIFT_CODE", "USERNAME", "USER_ID", "VEHICLE_ID"
]

# Build a regex that matches all of them
pattern_open = re.compile(r"<(" + "|".join(tag_types) + r")>", re.IGNORECASE)
pattern_close = re.compile(r"</(" + "|".join(tag_types) + r")>", re.IGNORECASE)

converted_count = 0

with open(input_file, "r", encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
    for line in fin:
        if not line.strip():
            continue
        data = json.loads(line)
        sanitized = data.get("sanitized_query", "")

        # Replace all tag types with <SENSITIVE> / </SENSITIVE>
        sanitized = pattern_open.sub("<SENSITIVE>", sanitized)
        sanitized = pattern_close.sub("</SENSITIVE>", sanitized)

        new_record = {
            "original_query": data.get("original_query", ""),
            "sanitized_query": sanitized
        }
        fout.write(json.dumps(new_record, ensure_ascii=False) + "\n")
        converted_count += 1

print(f"✅ Done. Converted {converted_count} samples.")
print(f"New dataset saved to: {output_file}")
