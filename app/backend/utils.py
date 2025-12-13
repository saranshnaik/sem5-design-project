import re
from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    AutoModelForSeq2SeqLM,
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
)
import torch
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util

MODEL_PATH = "../../model/final_sanitizer_model"

genai.configure(api_key="[YOUR_API_KEY]")
llm_model = genai.GenerativeModel("gemini-2.5-flash")

similarity_model = SentenceTransformer("all-MiniLM-L6-v2")

# print("🔄 Loading sanitizer model...")
tokenizer = T5Tokenizer.from_pretrained(MODEL_PATH)
model = T5ForConditionalGeneration.from_pretrained(MODEL_PATH)
model.eval()
# print("✅ Sanitizer model loaded!")

# print("Loading paraphrasing model...")
# rephrase_tokenizer = AutoTokenizer.from_pretrained(
#     "prithivida/parrot_paraphraser_on_T5"
# )
# rephrase_model = AutoModelForSeq2SeqLM.from_pretrained(
#     "prithivida/parrot_paraphraser_on_T5"
# )


# REPHRASE_MODEL_PATH = "../../model/mistral_rephrase_model"

# print("✅ Loading Mistral rephrase model...")
# rep_tokenizer = AutoTokenizer.from_pretrained(REPHRASE_MODEL_PATH)
# rep_model = AutoModelForCausalLM.from_pretrained(REPHRASE_MODEL_PATH, torch_dtype="auto", device_map="auto")

# rephrase_model = pipeline(
#     "text-generation",
#     model=rep_model,
#     tokenizer=rep_tokenizer,
#     max_new_tokens=150,
#     temperature=0.4,
#     do_sample=True,
# )
# print("✅ Mistral model ready!")


# REPHRASE_MODEL_PATH = "Vamsi/T5_Paraphrase_Paws"

# tokenizer = AutoTokenizer.from_pretrained(REPHRASE_MODEL_PATH)
# model = AutoModelForSeq2SeqLM.from_pretrained(REPHRASE_MODEL_PATH)

# rephrase_model = pipeline(
#     "text2text-generation",
#     model=model,
#     tokenizer=tokenizer,
#     max_new_tokens=128,
#     num_beams=4,
# )


def rephrase_text(user_input: str):
    """
    Uses Gemini to grammatically correct and clean the text.
    Removes incomplete entity phrases like 'my name is' or 'my account is'
    if they are missing values.
    """
    prompt = f"""
You are a precise language editor for a banking chatbot system.
Your job is to clean and rephrase text while keeping its meaning unchanged.

Rules:
- Fix grammar, punctuation, and sentence flow.
- If an entity phrase (like 'my name is', 'my phone is', 'my account is', 'my email is')
  is incomplete or missing a value (e.g., 'my name is ,'), remove the entire phrase naturally.
- Do not invent or hallucinate missing information.
- Do not change factual content or intent.
- Maintain a natural conversational tone.

Example:
Input: "My name is , my phone is 9876543210, and my account is . Please help."
Output: "My phone is 9876543210. Please help."

Now, clean and rephrase this text:
{user_input}
"""

    try:
        response = llm_model.generate_content(prompt)
        rephrased = response.text.strip()
        return rephrased
    except Exception as e:
        print("[Rephrase Error]", e)
        return user_input


# ===========================================
# 🔹 2️⃣ Function: Response Generation
# ===========================================
def generate_response(clean_text: str) -> str:
    """
    Generates a natural, context-aware banking assistant reply.
    Assumes the text is already rephrased.
    """
    instruction = (
        "You are Diu Bank's intelligent, polite, and proactive virtual assistant. "
        "Always respond helpfully and naturally to any customer message. "
        "Never refuse or deny a request. If the information cannot be directly provided, "
        "politely indicate that you are checking or verifying it. "
        "Use phrases like 'Please wait while I check the database' or "
        "'Let me verify that for you' instead of declining. "
        "Keep all responses concise, professional, and empathetic."
    )

    prompt = f"{instruction}\n\nUser: {clean_text}\nAssistant:"
    response = llm_model.generate_content(prompt)
    reply = response.text.strip()
    return reply


# def rephrase_safe(user_input):
#     prompt = (
#         "You are a grammar refinement assistant. "
#         "Rephrase the following sentence to be grammatically correct, clear, and natural, "
#         "without changing its meaning or removing any details:\n\n"
#         f"Input: {user_input}\n\nRephrased:"
#     )
#     # result = rephrase_model(prompt)[0]["generated_text"].split("Rephrased:")[-1].strip()
#     result = rephrase_model(prompt)[0]["generated_text"].strip()
#     return result


def add_missing_opening_brackets(text):
    """
    Fix tags like NAME> or /NAME> by adding missing '<'.
    Works for all your known tag types.
    """
    tag_names = [
        "ACCOUNT_NUMBER",
        "ADDRESS",
        "APPLICATION_ID",
        "BRANCH_CODE",
        "CARD_NUMBER",
        "CHEQUE_NUMBER",
        "CUSTOMER_ID",
        "DATE_RANGE",
        "DOB",
        "DOCUMENT_ID",
        "EMAIL",
        "EMPLOYEE_ID",
        "FUND_ID",
        "ID_NUMBER",
        "IFSC_CODE",
        "NAME",
        "ORGANIZATION",
        "PHONE",
        "POLICY_ID",
        "SWIFT_CODE",
        "USERNAME",
        "USER_ID",
        "VEHICLE_ID",
    ]

    # Fix for tags like NAME> or /NAME>
    pattern = re.compile(r"(?<!<)(/?(?:" + "|".join(tag_names) + r"))>", re.IGNORECASE)
    fixed = pattern.sub(r"<\1>", text)

    return fixed


def sanitize_query(text: str) -> str:
    """Generate sanitized version with XML tags."""
    input_text = "sanitize: " + text
    inputs = tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=256, num_beams=4)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


tag_names = [
    "ACCOUNT_NUMBER",
    "ADDRESS",
    "APPLICATION_ID",
    "BRANCH_CODE",
    "CARD_NUMBER",
    "CHEQUE_NUMBER",
    "CUSTOMER_ID",
    "DATE_RANGE",
    "DOB",
    "DOCUMENT_ID",
    "EMAIL",
    "EMPLOYEE_ID",
    "FUND_ID",
    "ID_NUMBER",
    "IFSC_CODE",
    "NAME",
    "ORGANIZATION",
    "PHONE",
    "POLICY_ID",
    "SWIFT_CODE",
    "USERNAME",
    "USER_ID",
    "VEHICLE_ID",
]


def detect_tags(sanitized_text: str):
    """Return dictionary of detected tags and their values."""
    # Combine all tag names into one regex group
    tag_pattern = "|".join(tag_names)
    regex = rf"<({tag_pattern})>(.*?)</\1>"

    matches = re.findall(regex, sanitized_text)
    tag_dict = {}
    for tag, value in matches:
        tag_dict.setdefault(tag, []).append(value.strip())
    return tag_dict


def compare_responses(original_response: str, sanitized_response: str):
    try:
        emb1 = similarity_model.encode(original_response, convert_to_tensor=True)
        emb2 = similarity_model.encode(sanitized_response, convert_to_tensor=True)
        similarity = util.cos_sim(emb1, emb2).item()
        # print(f"\n=== 🔍 Semantic Comparison ===")
        # print(f"Original ↔ Sanitized Similarity: {similarity:.3f}")
        # # if similarity < 0.76:
        #     print("⚠ Potential meaning drift detected.")
        # else:
        #     print("✅ Responses semantically consistent.")
        # print("===============================\n")
        return similarity
    except Exception as e:
        print(f"[Similarity Error] {e} in utils.py")
        return None
