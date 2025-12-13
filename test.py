# import re

# def add_missing_opening_brackets(text):
#     """
#     Fix tags like NAME> or /NAME> by adding missing '<'.
#     Works for all your known tag types.
#     """
#     tag_names = [
#         "ACCOUNT_NUMBER", "ADDRESS", "APPLICATION_ID", "BRANCH_CODE",
#         "CARD_NUMBER", "CHEQUE_NUMBER", "CUSTOMER_ID", "DATE_RANGE",
#         "DOB", "DOCUMENT_ID", "EMAIL", "EMPLOYEE_ID", "FUND_ID",
#         "ID_NUMBER", "IFSC_CODE", "NAME", "ORGANIZATION", "PHONE",
#         "POLICY_ID", "SWIFT_CODE", "USERNAME", "USER_ID", "VEHICLE_ID"
#     ]

#     # Fix for tags like NAME> or /NAME>
#     pattern = re.compile(r'(?<!<)(/?(?:' + "|".join(tag_names) + r'))>', re.IGNORECASE)
#     fixed = pattern.sub(r'<\1>', text)

#     return fixed

# input = "I am so angry! I've been on hold for 20 minutes. My name is NAME>Priya Sharma/NAME>, my phone is PHONE>99776543210/PHONE>, and my account is ACCOUNT_NUMBER>887766/ACCOUNT_NUMBER>. I just want to know my balance."
# print(add_missing_opening_brackets(input))

import google.generativeai as genai

genai.configure(api_key="AIzaSyAEH_H7oAiy1Lu0KVgmjHLgUUYN9Y3-NJA")

print("\nAvailable Gemini models:\n" + "-" * 40)
for m in genai.list_models():
    print(m.name)
