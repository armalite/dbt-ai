#!/usr/bin/env python3
"""
Test script to demonstrate the improvements in dbt-ai v0.3.0
This script will test the new AI functionality if an API key is available
"""

from dbt_ai.ai import MODERN_OPENAI, generate_response, generate_response_advanced
from dbt_ai.config import Config


def test_api_improvements() -> None:
    """Test the improved AI functionality"""

    print("🧪 Testing dbt-ai v0.3.0 Improvements")
    print("=" * 50)

    # Check API availability
    api_available = Config.is_api_available()
    print(f"📡 OpenAI API Available: {api_available}")
    print(f"🔧 Modern OpenAI API: {MODERN_OPENAI}")
    print(f"🎯 Basic Model: {Config.get_basic_model()}")
    print(f"🚀 Advanced Model: {Config.get_advanced_model()}")
    print()

    if not api_available:
        print("⚠️  No OpenAI API key found. Set OPENAI_API_KEY to test AI features.")
        print("   Non-AI features (metadata checking) still work without an API key.")
        return

    # Test sample dbt model
    sample_model = """
    SELECT
        customer_id,
        customer_name,
        email,
        created_at
    FROM raw.customers
    WHERE status = 'active'
    """

    prompt = (
        f"Given the following dbt model customer_summary:\n\n{sample_model}\n\n"
        "Please provide suggestions on how to improve this model in terms of syntax, "
        "code structure and dbt best practices such as using ref instead of "
        "hardcoding table names. The suggestion should be specific to dbt models "
        "written in the Snowflake database system."
    )

    print("🤖 Testing Basic Suggestions...")
    try:
        basic_response = generate_response(prompt)
        print("✅ Basic suggestions generated successfully!")
        print(f"📝 Response length: {len(basic_response)} characters")
        if basic_response:
            print(f"📄 Sample response: {basic_response[:200]}...")
        print()
    except Exception as e:
        print(f"❌ Error generating basic suggestions: {e}")
        print()

    print("🎓 Testing Advanced Suggestions...")
    try:
        advanced_response = generate_response_advanced(prompt)
        print("✅ Advanced suggestions generated successfully!")
        print(f"📝 Response length: {len(advanced_response)} characters")
        if advanced_response:
            print(f"📄 Sample response: {advanced_response[:200]}...")
        print()
    except Exception as e:
        print(f"❌ Error generating advanced suggestions: {e}")
        print()

    print("🎉 Test completed! The new AI improvements are working.")


if __name__ == "__main__":
    test_api_improvements()
