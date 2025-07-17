# flake8: noqa
import openai
import json
from typing import List, Dict

# Prompt Rules
BASIC_RULES = """
You are reviewing a dbt model written by a junior data engineer who is still learning dbt and SQL.

Your goal is to suggest only very basic improvements that help them follow clean, maintainable practices without overwhelming them.

Strict rules:
- Do NOT suggest using comments, LIMIT clauses, or JOINs unless they are clearly needed.
- Do NOT suggest YAML metadata (handled separately).
- Do NOT suggest window functions, ranking functions, or deduplication logic.
- Do NOT suggest `is_incremental()` or `partition_by`, unless already used in the SQL.
- Do NOT suggest macros like `dbt_utils.star()` or `union_relations()` unless already present.
- Avoid vague suggestions like "consider improving performance" or "refactor for clarity".
- Avoid conditional advice like “If this is a large table…” — assume the engineer knows their data.
- If there are no clear improvements, simply say the model looks clean and well-structured.

Limit your response to a maximum of 4 meaningful suggestions.

Focus areas:
- Column selection style (avoid SELECT *)
- Refactoring simple logic for readability
- Using `ref()` instead of hardcoded table names
- Naming clarity in aliases or CTEs
- Suggesting simple tests like `not_null` or `unique` for key fields
"""


ADVANCED_RULES = """
You are reviewing a dbt model written by a senior data engineer who is comfortable with SQL and dbt.

Your goal is to provide **advanced, actionable suggestions** that improve performance, structure, and maintainability.

Strict rules:
- Do NOT suggest YAML metadata or documentation improvements — these are handled separately.
- Avoid vague or speculative suggestions like "consider improving performance".
- Avoid generic advice like “split into intermediate models” unless the model is clearly complex.
- Only recommend `is_incremental()` or `partition_by` if the model selects from a large source with timestamps or surrogate keys.
- Only recommend window functions if the model already does row-level logic or lacks deduplication.

Limit to 4 strong, relevant suggestions only. If no advanced suggestions are possible, say so clearly and avoid falling back to basic advice.

Focus areas:
- Window functions for ranking, deduplication, or cumulative metrics
- `is_incremental()` and performance-aware filtering
- Breaking up complex logic into intermediate models
- Use of macros like `dbt_utils.star()` or `union_relations()` — only when appropriate
- Optimising joins, filters, or large scans
"""


STRUCTURED_RESPONSE_INSTRUCTIONS = """
Format the output as **valid JSON** using this schema:
{
  "model_name": "<model name>",
  "summary": "Short summary of what the model does",
  "suggestions": [
    { "suggestion": "..." },
    { "suggestion": "..." }
  ],
  "style_feedback": ["..."],
  "test_recommendations": ["..."],
  "tag_suggestions": ["..."]
}
"""

def generate_prompt(model_content: str, model_name: str, level: str = "basic") -> List[Dict[str, str]]:
    rules = BASIC_RULES if level == "basic" else ADVANCED_RULES
    prompt = f"""
{rules}

{STRUCTURED_RESPONSE_INSTRUCTIONS}
"""
    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Here is the SQL code for model '{model_name}':\n\n```sql\n{model_content}\n```"}
    ]

# Provider Interface
class LLMClient:
    def generate(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError

class OpenAIClient(LLMClient):
    def __init__(self, model="gpt-4"):
        self.model = model

    def generate(self, messages):
        print("🧠 Sending messages to OpenAI...")
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=0.2,
        )
        content = response.choices[0].message.content.strip()
        print(f"📤 Raw LLM response:\n{content}\n")
        return content

def get_llm_client(provider: str = "openai", model: str = "gpt-4") -> LLMClient:
    if provider == "openai":
        return OpenAIClient(model)
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def generate_review(model_content: str, model_name: str, level: str = "basic", provider: str = "openai", model: str = "gpt-4", classification: dict = None) -> dict:
    if classification:
        messages = generate_contextual_prompt(model_content, model_name, classification, level)
    else:
        messages = generate_prompt(model_content, model_name, level)

    llm = get_llm_client(provider, model)
    content = llm.generate(messages)

    try:
        start = content.index('{')
        end = content.rindex('}') + 1
        json_text = content[start:end]
        return json.loads(json_text)
    except Exception as e:
        print("❌ Failed to parse structured JSON. Raw response:")
        print(content)
        raise e


def classify_model(model_content: str, model_name: str = "") -> str:
    prompt = [
        {
            "role": "system",
            "content": (
                "You are a dbt model classifier.\n"
                "Given the SQL for a dbt model, return a short summary and classify it into one of:\n"
                "- static_cte: hardcoded rows using CTEs\n"
                "- ref_based: uses ref() to pull from another model\n"
                "- source_based: uses source() to pull from external source\n"
                "- external_table: uses a fully qualified table name (e.g. database.schema.table)\n\n"
                "Only classify based on the SQL provided. Do not guess or add fluff.\n"
                "Format your response as valid JSON:\n"
                "{\n  \"model_name\": \"...\",\n  \"summary\": \"...\",\n  \"model_type\": \"...\"\n}"
            )
        },
        {
            "role": "user",
            "content": f"SQL for model '{model_name}':\n\n```sql\n{model_content}\n```"
        }
    ]

    llm = get_llm_client()
    content = llm.generate(prompt)

    try:
        start = content.index('{')
        end = content.rindex('}') + 1
        return json.loads(content[start:end])
    except Exception as e:
        print("❌ Failed to parse classification JSON. Raw response:")
        print(content)
        raise e


def generate_contextual_prompt(model_content: str, model_name: str, classification: dict, level: str = "basic") -> List[Dict[str, str]]:
    model_type = classification.get("model_type", "")
    summary = classification.get("summary", "")

    base_rules = BASIC_RULES if level == "basic" else ADVANCED_RULES

    # Inject targeted overrides
    if model_type == "static_cte":
        extra_rules = (
            "\nAdditional rules:\n"
            "- Do NOT recommend incremental models, partitioning, or macros like union_relations().\n"
            "- Do NOT suggest window functions unless the model explicitly uses ranking or deduplication logic.\n"
            "- This is a static model with no upstream dependencies.\n"
            "- Only suggest minor logic or test improvements."
        )
    elif model_type == "ref_based":
        extra_rules = (
            "\nAdditional rules:\n"
            "- Only suggest deduplication (row_number, rank) if there's evidence of duplicated data.\n"
            "- Do NOT assume filtering by ID needs a window function.\n"
        )
    elif model_type == "external_table":
        extra_rules = (
            "\nAdditional rules:\n"
            "- Only suggest window functions if multiple rows are expected.\n"
            "- Do NOT suggest window functions when filtering on exact ID match unless there's evidence of duplicates.\n"
        )

    else:
        extra_rules = ""

    # Compose full prompt
    prompt = f"""
{base_rules}
{extra_rules}

{STRUCTURED_RESPONSE_INSTRUCTIONS}
The model has been classified as: {model_type}
Summary: {summary}
"""

    return [
        {"role": "system", "content": prompt},
        {"role": "user", "content": f"Here is the SQL code for model '{model_name}':\n\n```sql\n{model_content}\n```"}
    ]
