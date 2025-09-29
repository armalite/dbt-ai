# flake8: noqa

import json
import os
import requests
from typing import List, Optional, Dict, Any

try:
    # Try modern OpenAI API first
    from openai import OpenAI

    MODERN_OPENAI = True
    OpenAIClient = OpenAI
except ImportError:
    # Fallback to legacy API
    import openai

    MODERN_OPENAI = False
    OpenAIClient = None

from pydantic import ValidationError

from .models import DbtModelSuggestions, DbtSuggestion, DbtModelsResponse, DbtModelDefinition
from .config import Config


# Configuration - now using Config class
MAX_TOKENS = Config.get_max_tokens()
TEMPERATURE = Config.get_temperature()


def get_openai_client() -> Optional[Any]:
    """Get OpenAI client if API key is available"""
    api_key = Config.get_openai_api_key()
    if not api_key:
        return None

    if MODERN_OPENAI:
        return OpenAI(api_key=api_key)
    else:
        openai.api_key = api_key
        return None  # Use global openai module for legacy API


def get_model_name(advanced: bool = False) -> str:
    """Get appropriate model name based on task complexity"""
    if advanced:
        return Config.get_advanced_model() if MODERN_OPENAI else Config.get_fallback_model()
    return Config.get_basic_model() if MODERN_OPENAI else Config.get_fallback_model()


def call_chat_completion(
    messages: List[Dict],
    model: str,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
    json_mode: bool = False,
):
    """Compatibility wrapper for chat completion calls"""
    if MODERN_OPENAI:
        client = get_openai_client()
        if not client:
            return None

        kwargs = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}  # type: ignore

        return client.chat.completions.create(**kwargs)
    else:
        # Legacy API
        if not get_openai_client():  # This sets the API key
            return None

        kwargs = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "n": 1,
            "stop": None,
        }

        import openai as openai_legacy
        return openai_legacy.ChatCompletion.create(**kwargs)  # type: ignore


def generate_response(prompt: str) -> str:
    """Generate basic dbt model improvement suggestions with structured output"""
    if not get_openai_client():
        return ""

    system_prompt = """You are a dbt expert helping new data engineers improve their dbt models. 
    
    RULES TO FOLLOW:
    - Focus on basic, foundational improvements suitable for beginners
    - Provide specific, actionable suggestions
    - Do NOT suggest adding comments to models
    - Do NOT suggest YAML metadata (handled separately)
    - Do NOT suggest LIMIT for small datasets (<1000 records)
    - Do NOT suggest JOINs just for filtering small datasets
    - Avoid conditional suggestions like "If table is big, then..."
    - Maximum 4 suggestions
    - If no improvements needed, say so and compliment good practices
    
    FOCUS AREAS:
    - Using ref() instead of hardcoded table names
    - Proper SQL syntax and formatting
    - Basic dbt best practices
    - Code structure and readability
    - Appropriate use of CTEs
    
    Respond with structured JSON in this format:
    {
        "model_name": "extracted_model_name",
        "suggestions": [
            {
                "suggestion": "specific improvement text",
                "priority": "high|medium|low",
                "category": "syntax|performance|best_practice|structure"
            }
        ],
        "overall_assessment": "brief overall assessment",
        "has_recommendations": true/false
    }"""

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]

    try:
        response = call_chat_completion(
            messages=messages,
            model=get_model_name(advanced=False),
            json_mode=MODERN_OPENAI,  # Only try JSON mode with modern API
        )

        if not response:
            return ""

        if MODERN_OPENAI:
            response_text = response.choices[0].message.content
        else:
            response_text = response.choices[0].message["content"]

        # Try to parse as JSON if using modern API
        if MODERN_OPENAI:
            try:
                json_data = json.loads(response_text)
                suggestions_obj = DbtModelSuggestions(**json_data)

                # Format as the original string format for backwards compatibility
                if not suggestions_obj.has_recommendations:
                    return suggestions_obj.overall_assessment or "No recommendations needed - model looks good!"

                result_lines = [f"Suggestions for model `{suggestions_obj.model_name}`:"]
                result_lines.append("")

                for suggestion in suggestions_obj.suggestions:
                    result_lines.append(f"- {suggestion.suggestion}")

                if suggestions_obj.overall_assessment:
                    result_lines.append("")
                    result_lines.append(suggestions_obj.overall_assessment)

                return "\n".join(result_lines)

            except (json.JSONDecodeError, ValidationError):
                # Fallback to raw response if JSON parsing fails
                pass

        return response_text.strip()

    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return ""


def generate_response_advanced(prompt: str) -> str:
    """Generate advanced dbt model improvement suggestions with structured output"""
    if not get_openai_client():
        return ""

    system_prompt = """You are a senior dbt consultant providing advanced optimization suggestions for experienced data engineers.
    
    RULES TO FOLLOW:
    - Provide only advanced, sophisticated recommendations
    - Focus on performance optimization, complex dbt features, and architectural improvements
    - Do NOT provide basic suggestions (those are handled separately)
    - Avoid conditional suggestions like "If table is big, then..."
    - Maximum 4 suggestions
    - If no advanced improvements are needed, state that clearly
    
    ADVANCED FOCUS AREAS:
    - Performance optimization techniques (incremental models, partitioning, clustering)
    - Advanced dbt features (macros, tests, snapshots, hooks)
    - Complex SQL patterns and optimization
    - Data warehouse specific optimizations
    - Architecture and data modeling patterns
    - Advanced testing strategies
    
    EXAMPLE ADVANCED SUGGESTIONS:
    - Implement incremental processing with merge strategies for large datasets
    - Add clustering keys for better query performance in Snowflake
    - Use window functions for complex analytics rather than self-joins
    - Implement data quality tests at multiple grain levels
    - Consider splitting into multiple models for better modularity and testing
    - Use dbt macros to eliminate repetitive code patterns
    
    Respond with structured JSON in this format:
    {
        "model_name": "extracted_model_name",
        "suggestions": [
            {
                "suggestion": "specific advanced improvement text",
                "priority": "high|medium|low",
                "category": "performance|architecture|testing|optimization"
            }
        ],
        "overall_assessment": "brief advanced assessment",
        "has_recommendations": true/false
    }"""

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]

    try:
        response = call_chat_completion(
            messages=messages,
            model=get_model_name(advanced=True),
            json_mode=MODERN_OPENAI,  # Only try JSON mode with modern API
        )

        if not response:
            return ""

        if MODERN_OPENAI:
            response_text = response.choices[0].message.content
        else:
            response_text = response.choices[0].message["content"]

        # Try to parse as JSON if using modern API
        if MODERN_OPENAI:
            try:
                json_data = json.loads(response_text)
                suggestions_obj = DbtModelSuggestions(**json_data)

                # Format as the original string format for backwards compatibility
                if not suggestions_obj.has_recommendations:
                    return (
                        suggestions_obj.overall_assessment
                        or "No advanced recommendations needed - model is well optimized!"
                    )

                result_lines = [f"Suggestions for model `{suggestions_obj.model_name}`:"]
                result_lines.append("")

                for suggestion in suggestions_obj.suggestions:
                    result_lines.append(f"- {suggestion.suggestion}")

                if suggestions_obj.overall_assessment:
                    result_lines.append("")
                    result_lines.append(suggestions_obj.overall_assessment)

                return "\n".join(result_lines)

            except (json.JSONDecodeError, ValidationError):
                # Fallback to raw response if JSON parsing fails
                pass

        return response_text.strip()

    except Exception as e:
        print(f"Error generating advanced suggestions: {e}")
        return ""


def generate_dalle_image(prompt: str, image_size: str = "1024x1024") -> bytes:
    """Generate DALL-E image with improved prompting"""

    final_prompt = f"""Create a clean, professional diagram showing connected nodes representing a data lineage graph. 
    The diagram should show: {prompt}
    
    Style: Technical diagram with clear node connections, suitable for data engineering documentation.
    Use circles or boxes for nodes, arrows for connections, and include labels where appropriate."""

    print(f"Generating AI image using DALL-E with prompt: {final_prompt[:100]}...")

    try:
        if MODERN_OPENAI:
            client = get_openai_client()
            if not client:
                raise ValueError("OpenAI API key not available")

            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=final_prompt,
                    size=image_size,
                    quality="standard",
                    n=1,
                )

                image_url = response.data[0].url
                image_binary = requests.get(image_url).content
                return image_binary

            except Exception:
                # Try with DALL-E 2 as fallback
                response = client.images.generate(
                    model="dall-e-2",
                    prompt=final_prompt[:1000],  # DALL-E 2 has shorter prompt limit
                    size=image_size,
                    n=1,
                )

                image_url = response.data[0].url
                image_binary = requests.get(image_url).content
                return image_binary
        else:
            # Legacy API
            if not get_openai_client():  # This sets the API key
                raise ValueError("OpenAI API key not available")

            import openai as openai_legacy
            response = openai_legacy.Image.create(  # type: ignore
                prompt=final_prompt[:1000],  # Keep it shorter for compatibility
                n=1,
                size=image_size,
            )

            image_url = response.data[0].url.strip()
            image_binary = requests.get(image_url).content
            return image_binary

    except Exception as e:
        print(f"Error generating image: {e}")
        raise


def generate_models(prompt: str, sources_yml: str) -> List[str]:
    """Generate dbt models based on prompt and sources with improved structure"""
    if not get_openai_client():
        return []

    system_prompt = """You are a dbt expert that creates well-structured dbt models based on user requirements.
    
    INSTRUCTIONS:
    1. Create dbt models that follow best practices
    2. Use proper dbt syntax including ref() and source() functions
    3. Split complex logic into multiple models when appropriate
    4. Include helpful commented examples for beginners when logic is simple
    5. Use the provided sources.yml information to understand available data
    
    OUTPUT FORMAT:
    - Each model should be separated by "==="
    - First line after === should be "model_name: actual_model_name" 
    - Following lines should contain the SQL content (no code blocks)
    - End with === before the next model
    
    EXAMPLE OUTPUT:
    ===
    model_name: customers
    SELECT 
        customer_id,
        customer_name,
        email
    FROM {{ source('raw', 'customers') }}
    WHERE is_active = true
    ===
    model_name: orders_summary  
    SELECT 
        customer_id,
        COUNT(*) as order_count,
        SUM(order_total) as total_spent
    FROM {{ source('raw', 'orders') }}
    GROUP BY customer_id
    ==="""

    prompt_with_sources = f"""USER REQUEST:
{prompt}

AVAILABLE SOURCES:
{sources_yml}

Please create appropriate dbt models based on the request above."""

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt_with_sources}]

    try:
        response = call_chat_completion(messages=messages, model=get_model_name(advanced=False))

        if not response:
            return []

        if MODERN_OPENAI:
            response_text = response.choices[0].message.content
        else:
            response_text = response.choices[0].message["content"]

        # Split the models by "===" and filter out empty parts
        models = [model.strip() for model in response_text.split("===") if model.strip()]

        # Clean up and format models
        cleaned_models = []
        for model in models:
            if model and ("model_name:" in model or "MODEL:" in model):
                cleaned_models.append(model)

        return cleaned_models if cleaned_models else models

    except Exception as e:
        print(f"Error generating models: {e}")
        return []
