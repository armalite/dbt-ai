import openai


def generate_response(prompt) -> list:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that suggests improvements to dbt models."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=80,
        n=1,
        stop=None,
        temperature=0.3,
    )
    return response.choices[0].message["content"].strip()
