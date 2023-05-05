import sys
from typing import List


def generate_response(prompt):
    response = openai.Completion.create(
        engine="GPT-3.5",  
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

def suggest_dbt_model_improvements(file_path):
    with open(file_path, "r") as f:
        content = f.read()

    prompt = f"Given the following dbt model:\n\n{content}\n\nPlease provide suggestions on how to improve this model:"
    response = generate_response(prompt)
    return response


def main(args: List[str] = sys.argv[1:]) -> None:
    print(f"hello {args[0]}!")


if __name__ == "__main__":
    main()
