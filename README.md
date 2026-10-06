# ADLP — Banking Chatbot

A **Banking Chatbot** that implements **Accidental Data Leakage Prevention (ADLP)** through user-query sanitization. The system detects potentially sensitive information in user queries, allows selected sensitive entities to be removed, rephrases the sanitized query, and compares the resulting LLM response with the response generated from the original query.

The project uses the **T5-small** model for text rephrasing/sanitization-related processing and was developed as part of a **Design Project in the 5th Semester**.

## Features

- Banking chatbot interface
- User query sanitization
- Detection of potentially sensitive information using tagged entities
- Automatic handling of missing opening brackets in detected tags
- Selective removal of sensitive information from queries
- Query rephrasing after sanitization
- LLM-based response generation
- Original vs. filtered response comparison
- Semantic similarity evaluation to detect meaning drift
- Quality logging for sanitized queries and generated responses
- Flask-based backend API
- Frontend interface for interacting with the chatbot

## How ADLP Works

The application follows a query-processing pipeline:

```text
User Query
    │
    ▼
Query Sanitization
    │
    ▼
Sensitive Information Detection
    │
    ▼
Tagged Query
    │
    ▼
User Selects Tags to Remove
    │
    ▼
Sensitive Data Removal
    │
    ▼
Query Rephrasing
    │
    ▼
LLM Response Generation
    │
    ▼
Semantic Comparison
    │
    ▼
Quality / Meaning-Drift Evaluation
```

The objective is to prevent sensitive information from being unnecessarily passed to the downstream language model while preserving the intended meaning of the user's query.

## Technologies Used

- **Python**
- **Flask**
- **Hugging Face Transformers**
- **T5-small**
- **Regular Expressions (Regex)**
- **LLM APIs / LLM integration**
- **HTML / CSS / JavaScript**
- **Python virtual environment / pip**

## Project Structure

```text
ADLP/
├── app/
│   ├── backend/
│   │   ├── app.py
│   │   ├── utils.py
│   │   ├── llm_handler.py
│   │   └── ...
│   └── frontend/
│       ├── templates/
│       └── static/
├── data/
├── model/
├── examples/
├── images/
├── requirements.txt
├── test.py
├── .gitignore
├── .gitattributes
└── README.md
```

The exact contents of the `app/`, `data/`, and `model/` directories may vary as the project contains the supporting implementation, datasets/resources, and model-training code.

## Backend API

The Flask backend exposes several endpoints.

### Home

```http
GET /
```

Serves the chatbot frontend.

### Sanitize Query

```http
POST /sanitize
```

Receives a user query, sanitizes it, detects sensitive tags, and returns the processed query.

Example request:

```json
{
    "query": "..."
}
```

Example response structure:

```json
{
    "sanitized": "...",
    "tags": {}
}
```

### Filter Sensitive Tags

```http
POST /filter
```

Removes the selected sensitive tags from the sanitized query and rephrases the resulting text.

Example request:

```json
{
    "sanitized": "...",
    "remove_tags": ["..."]
}
```

### Generate LLM Response

```http
POST /llm
```

Generates a response for a supplied query using the configured language-model backend.

Example request:

```json
{
    "query": "..."
}
```

### Compare Responses

```http
POST /compare
```

Generates responses for both the original and filtered queries and computes a semantic similarity score.

Example request:

```json
{
    "original": "...",
    "filtered": "..."
}
```

Example response structure:

```json
{
    "filtered_response": "...",
    "similarity": 0.85
}
```

A lower similarity score can indicate that sanitization or rephrasing may have caused significant meaning drift.

## Model

The project uses the **T5-small** transformer model as part of its text-processing pipeline.

The repository also contains a `model/` directory for model-training-related code and resources.

The exact model-loading and training configuration is defined by the project's Python implementation and requirements.

## Response Quality Evaluation

The system does more than simply remove sensitive information.

After sanitization and rephrasing, it can generate responses for both:

```text
Original Query
       │
       ▼
Original LLM Response

Filtered Query
       │
       ▼
Filtered LLM Response
```

The two responses are then compared semantically.

This helps evaluate whether removing sensitive information changes the intended meaning of the query. The backend also logs the comparison and quality information for development and evaluation.

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-name>
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

On Linux/macOS:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The application may require configuration for the LLM backend and other external services.

Any API keys or credentials should be stored locally using environment variables or a local configuration mechanism.

**Do not commit real API keys or other secrets to the repository.**

## Running the Application

From the backend directory, run the Flask application:

```bash
python app.py
```

The Flask development server will start locally.

Open the local URL displayed in the terminal in a web browser to access the chatbot interface.

## Testing

The repository includes:

```text
test.py
```

which can be used for testing the application's functionality.

Additional test cases and project resources may be present in the `data/` and `examples/` directories.

## Project Objective

The primary objective of the project is to demonstrate how **Accidental Data Leakage Prevention** can be incorporated into an LLM-powered application.

Instead of directly forwarding every user query to an LLM, the system introduces a sanitization layer that:

1. Identifies potentially sensitive information.
2. Allows sensitive entities to be removed.
3. Rephrases the remaining query.
4. Sends the safer query to the LLM.
5. Compares the resulting response with the original response.
6. Measures potential semantic drift.

This provides a practical approach to balancing **privacy and response usefulness** in LLM-based applications.

## Project Status

This project was developed as an academic **Design Project during the 5th Semester**. It represents a prototype implementation of ADLP/user-query sanitization for a banking chatbot rather than a production banking system.

## Real-World Impact

The research contribution of this project was recognized at the **ETTIS 2026 Conference**. A corresponding paper has been accepted for publication with **Springer** and is expected to be published in early 2027.

## Course

**Design Project — 5th Semester**

## Author

**Saransh**

## Purpose

This project was developed to explore the practical implementation of **Accidental Data Leakage Prevention (ADLP)** and **user query sanitization** in an LLM-powered banking chatbot, with a focus on reducing sensitive-data exposure while preserving the semantic intent of user queries.
