from flask import Flask, render_template, request, jsonify
from utils import (
    sanitize_query,
    detect_tags,
    add_missing_opening_brackets,
    # rephrase_safe,
    rephrase_text,
    generate_response,
    compare_responses,
)
from llm_handler import query_llm, log_quality

# from semantic_rephrase import rephrase_safe
from transformers import pipeline
import re

original_query = ""

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sanitize", methods=["POST"])
def sanitize():
    data = request.get_json()
    user_query = data.get("query", "")
    global original_query
    original_query = user_query

    sanitized = add_missing_opening_brackets(sanitize_query(user_query))
    tags = detect_tags(sanitized) or {}

    # llm_response = ""
    # if not tags:  # if no sensitive info
    #     llm_response = generate_response(original_query)

    return jsonify({"sanitized": sanitized, "tags": tags})


@app.route("/filter", methods=["POST"])
def filter_tags():
    data = request.get_json()
    sanitized = data.get("sanitized", "")
    remove_tags = data.get("remove_tags", [])
    global original_query

    # print("Before filtering:", sanitized)

    for tag in remove_tags:
        sanitized = re.sub(rf"<{tag}>(.*?)</{tag}>", "", sanitized, flags=re.IGNORECASE)

    sanitized = re.sub(r"</?([A-Z_]+)>", "", sanitized)
    sanitized = re.sub(r"\s{2,}", " ", sanitized).strip()

    # print("After tag removal:", sanitized)

    try:
        rephrased = rephrase_text(sanitized)
    except Exception as e:
        print("Rephrase failed:", e)
        rephrased = sanitized

    # Developer-only semantic comparison (no impact on user)
    try:
        original_response = generate_response(original_query)
        filtered_response = generate_response(rephrased)
        compare_responses(original_response, filtered_response)
    except Exception as e:
        print("Comparison skipped:", e)

    return jsonify({"filtered": rephrased})


@app.route("/llm", methods=["POST"])
def llm():
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Empty query"}), 400

    try:
        response = generate_response(query)
        return jsonify({"response": response})
    except Exception as e:
        print("LLM generation error:", e)
        return jsonify({"error": "Failed to generate LLM response"}), 500


@app.route("/compare", methods=["POST"])
def compare():
    data = request.get_json()
    original = data.get("original", "").strip()
    filtered = data.get("filtered", "").strip()

    if not original or not filtered:
        return jsonify({"error": "Both original and filtered queries required"}), 400

    try:
        # Get responses from LLM
        original_response = generate_response(original)
        filtered_response = generate_response(filtered)

        # Compare semantic similarity
        similarity_score = compare_responses(original_response, filtered_response)

        # Log both for visibility
        print("\n----- 🧠 LLM Comparison (Backend Log) -----")
        print(f"Original Query: {original}")
        print(f"Original Response: {original_response}")
        print(f"\nFiltered Query: {filtered}")
        print(f"Filtered Response: {filtered_response}")
        print(f"Similarity score: {similarity_score:.3f}")
        if round(similarity_score, 3) < 0.70:
            print("⚠ Potential meaning drift detected.")
        else:
            print("✅ Responses semantically consistent.")
        print("===============================\n")
        print("-------------------------------------------")

        # Log overall quality report
        log_quality(original, filtered, original_response, filtered_response)

        return jsonify(
            {
                "filtered_response": filtered_response,
                "similarity": (
                    round(similarity_score, 3) if similarity_score is not None else None
                ),
            }
        )

    except Exception as e:
        print(f"[Compare Error] {e} in app.py")
        return jsonify({"error": "Failed to compare responses"}), 500


if __name__ == "__main__":
    app.run(debug=True)
