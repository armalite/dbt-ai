# flake8: noqa
import openai
import json
from typing import List, Dict

# Prompt Rules
BASIC_RULES = """
You are reviewing a dbt model written by a junior data engineer. Your job is to provide helpful, safe, and minimal suggestions — only if they are clearly applicable based on the SQL.

🔒 Hard rules:
- Do NOT suggest performance features such as `is_incremental()`, `partition_by`, or timestamp filters unless the SQL already contains a large upstream source and timestamp logic.
- Do NOT suggest deduplication logic (e.g., `row_number()`, `rank()`, `dense_rank()`) unless the model already includes joins or ambiguous keys.
- Do NOT suggest YAML metadata — this is reviewed separately.
- Do NOT suggest or praise the use of comments unless actual SQL comments (`--`) are present.
- Do NOT suggest replacing `UNION ALL` with `UNION` unless duplicates are clearly being removed or deduplicated elsewhere.
- Do NOT suggest macros like `dbt_utils.star()` or `union_relations()` unless they are already used in the model.
- Do NOT give speculative compliments like “good use of ref” unless its usage is non-trivial.
- Avoid filler or vague praise, especially when the model is trivial.
- Avoid speculative or conditional advice such as “if the table grows...”, “if the model gets large...”
- If the model is already clean, say so and give a short compliment. Do NOT invent weak suggestions just to fill space.

✅ You may suggest:
- Avoiding `SELECT *` and selecting columns explicitly
- Using `ref()` if a hardcoded table is found
- Flattening unnecessary nesting or removing unused CTEs
- Suggesting simple tests like `not_null`, `unique`, or `accepted_values`

Limit to a maximum of **4 clear, context-aware suggestions**.
"""


ADVANCED_RULES = """
You are reviewing a dbt model written by a senior data engineer. Your job is to provide advanced, actionable suggestions — but only if they are clearly supported by the model's SQL content.

🔒 Hard rules:
- Do NOT suggest `is_incremental()`, `partition_by`, timestamp filters, or any performance tuning unless the model already selects from a large source and includes relevant logic (e.g., `updated_at`, `created_at`, or surrogate keys).
- Do NOT suggest deduplication (e.g., using `row_number()`, `rank()`, `dense_rank()`) unless the model already involves joins, merges, or shows evidence of duplicate keys.
- Do NOT suggest macros such as `dbt_utils.star()` or `union_relations()` unless they are already present in the SQL.
- Do NOT suggest comments — assume these are handled elsewhere.
- Do NOT suggest YAML metadata improvements — assume handled separately.
- Do NOT suggest replacing `UNION ALL` with `UNION` unless there is evidence of deduplication or intended row reduction.
- Do NOT include filler phrases like “consider using CTEs” or “good use of ref” unless usage is non-trivial.
- Avoid speculative advice like “if this model is run frequently…” or “if the source is large…” — base your suggestions strictly on the SQL content provided.
- Do NOT fall back to basic recommendations (e.g., avoiding `SELECT *`) unless they clearly apply.

✅ You may suggest:
- Use of advanced SQL patterns such as window functions, if already partially used or appropriate
- Strategic use of `is_incremental()` if logic shows incremental pattern intent
- Restructuring or modularising overly complex logic into intermediate models
- dbt-native optimisations or macros only when appropriate and supported by context

Limit to a maximum of **4 advanced, context-driven suggestions only**.
If no advanced suggestions apply, clearly state that and do not fall back to basic advice.
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
  Note: Only include style feedback based on actual code patterns seen in the SQL. Do not make assumptions (e.g., do not compliment use of comments unless comments are present).
  "test_recommendations": ["..."]
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
        {"role": "user", "content": f"Here is the SQL code for model '{model_name}':\n\n```sql\n{model_content}\n```"},
    ]


# Provider Interface
class LLMClient:
    def generate(self, messages: List[Dict[str, str]]) -> str:
        raise NotImplementedError


class OpenAIClient(LLMClient):
    def __init__(self, model="gpt-4o"):
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


def generate_review(
    model_content: str,
    model_name: str,
    level: str = "basic",
    provider: str = "openai",
    model: str = "gpt-4",
    classification: dict = None,
) -> dict:
    if classification:
        messages = generate_contextual_prompt(model_content, model_name, classification, level)
    else:
        messages = generate_prompt(model_content, model_name, level)

    llm = get_llm_client(provider, model)
    content = llm.generate(messages)

    try:
        start = content.index("{")
        end = content.rindex("}") + 1
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
                '{\n  "model_name": "...",\n  "summary": "...",\n  "model_type": "..."\n}'
            ),
        },
        {"role": "user", "content": f"SQL for model '{model_name}':\n\n```sql\n{model_content}\n```"},
    ]

    llm = get_llm_client()
    content = llm.generate(prompt)

    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        return json.loads(content[start:end])
    except Exception as e:
        print("❌ Failed to parse classification JSON. Raw response:")
        print(content)
        raise e


def generate_contextual_prompt(
    model_content: str, model_name: str, classification: dict, level: str = "basic"
) -> List[Dict[str, str]]:
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
        {"role": "user", "content": f"Here is the SQL code for model '{model_name}':\n\n```sql\n{model_content}\n```"},
    ]
