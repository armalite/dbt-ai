# flake8: noqa

import openai


def generate_response(prompt) -> list:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that suggests improvements to dbt models. \
            For the suggestions for each model you provide, simply start it with 'Suggestions for model <model name>' \
            followed by a new line. Surround the model name with ` so it is rendered like code and that underscores in the name dont get rendered. \
            Keep your suggestions fairly concise and easy to read. Order your suggestions in a logical order. \
            Add a new line in between list entries in your suggestions to help the application render it in html more nicely. Make sure \
            this is done for all the model suggestions. Favor using new lines for every point - do not randomize the formatting. \
             ",
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=400,
        n=1,
        stop=None,
        temperature=0,
    )
    return response.choices[0].message["content"].strip()
