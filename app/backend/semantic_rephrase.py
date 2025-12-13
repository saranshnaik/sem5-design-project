from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer, util
import torch, re

# Lazy global objects
rephrase_pipe = None
similarity_model = None

def load_models():
    global rephrase_pipe, similarity_model
    if rephrase_pipe and similarity_model:
        return rephrase_pipe, similarity_model

    print("🔄 Loading Mistral-7B-Instruct and MiniLM for semantic rephrasing...")
    model_name = "mistralai/Mistral-7B-Instruct-v0.3"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32
    )
    rephrase_pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=150,
        temperature=0.3,
        do_sample=True
    )
    similarity_model = SentenceTransformer("all-MiniLM-L6-v2")
    return rephrase_pipe, similarity_model


def build_grammatical_rephrase_prompt(user_input):
    """
    Builds a prompt for purely grammatical rephrasing.
    Keeps all factual, numeric, and personal details untouched.
    """
    return (
        "You are a precise language corrector. "
        "Your task is to rewrite the following text with perfect grammar, punctuation, and clarity. "
        "Do NOT remove, replace, or generalize any information such as names, numbers, or account details. "
        "Keep the tone and meaning identical.\n\n"
        f"Text:\n{user_input}\n\n"
        "Grammatically improved version:"
    )


def rephrase_safe(user_input):
    pipe, _ = load_models()
    prompt = build_grammatical_rephrase_prompt(user_input)
    raw = pipe(prompt)[0]["generated_text"]
    result = raw.split("Grammatically improved version:")[-1].strip()
    result = re.sub(r"\s+([.,!?])", r"\1", result)
    return result

