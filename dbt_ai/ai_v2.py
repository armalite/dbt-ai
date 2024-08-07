import openai
import os
import requests
import json

# Define the templates
basic_template = """
You are a helpful assistant that suggests only very basic improvements to dbt models based on the model content provided to you. Apply the rules outlined below. 
Assume you are making suggestions to a very new data engineer who is new to dbt and maybe even SQL. Your suggestions should help ensure this new engineer is most effectively using dbt.

More rules:
- Do not provide suggestions regarding capturing metadata in a yml file, because this information is being provided as part of a separate check in this application.
- Do NOT suggest writing comments in models.
- Do NOT suggest using LIMIT if the model is already selecting a small number of records (e.g. under 1000).
- Do NOT suggest using JOIN to filter records if the model is already selecting a small number of records (e.g. under 1000).
- Do NOT suggest to consider adding a comment at the top of the model to explain the purpose of the query and any relevant context.
- Avoid providing too many conditional suggestions such as "If this table is big, then do this".
- If you find or say that there are no recommendations to provide, then do not proceed any further to provide anything else. Maybe add a compliment if it's nicely written!
- Limit to 4 suggestions maximum.

Format the output as a JSON object with the following structure:
{
    "model_name": "{model_name}",
    "suggestions": [
        { "suggestion": "suggestion 1" },
        { "suggestion": "suggestion 2" },
        { "suggestion": "suggestion 3" },
        { "suggestion": "suggestion 4" }
    ]
}
"""

advanced_template = """
You are a helpful assistant that suggests only very advanced improvements to dbt models based on the model content provided to you. Apply the rules outlined below. 
Assume you are making suggestions to a highly skilled data engineer with strong knowledge of dbt and SQL.

More rules:
- Avoid providing too many conditional suggestions such as "If this table is big, then do this".
- If you find or say that there are no advanced recommendations to provide, then do not proceed any further to provide non-advanced recommendations. Maybe add a compliment if it's nicely written!
- Limit to 4 suggestions maximum.

Format the output as a JSON object with the following structure:
{
    "model_name": "{model_name}",
    "suggestions": [
        { "suggestion": "suggestion 1" },
        { "suggestion": "suggestion 2" },
        { "suggestion": "suggestion 3" },
        { "suggestion": "suggestion 4" }
    ]
}
"""

def generate_prompt(model_content, model_name, level='basic'):
    if level == 'basic':
        template = basic_template
    else:
        template = advanced_template

    prompt = template.format(model_name=model_name)
    return prompt + model_content

def generate_response(prompt) -> dict:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.1,
    )
    response_content = response.choices[0].message["content"].strip()
    return json.loads(response_content)

def format_response_for_display(parsed_response):
    model_name = parsed_response["model_name"]
    suggestions = parsed_response["suggestions"]
    formatted_suggestions = "\n".join([f"- {s['suggestion']}" for s in suggestions])
    return f"Suggestions for model `{model_name}`:\n{formatted_suggestions}"

# Update the functions to use the generate_prompt and generate_response

def generate_response_basic(model_content, model_name) -> dict:
    prompt = generate_prompt(model_content, model_name, level='basic')
    return generate_response(prompt)

def generate_response_advanced(model_content, model_name) -> dict:
    prompt = generate_prompt(model_content, model_name, level='advanced')
    return generate_response(prompt)

def generate_dalle_image(prompt: str, image_size: str = "1024x1024"):
    final_prompt = f"Draw a set of connected balls representing the nodes and edges of the following graph description: \
                    {prompt} \
                    "
    print(f"Generating AI image using DALL-E with the following prompt: {final_prompt}")
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=image_size,
    )

    image_url = response.data[0].url.strip()
    image_binary = requests.get(image_url).content

    return image_binary

def generate_models(prompt: str, sources_yml: str) -> list[str]:
    # Combine prompt and sources.yml content
    prompt_with_sources = f"{prompt}\n\nSources YAML:\n\n{sources_yml}\n\n"
    output_dir = "models"
    # Generate response using OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that will write dbt models based on the provided prompt. The prompt includes useful information such as the contents of the sources.yml file. \
                If the logic needs to be split into multiple dbt models, please delimit the contents of each model with '===', which will be used to split the data to write into separate sql files later. \
                Do not put any explanations. Each model content should be divided with a === so that splitting by === would divide the models. The first line in the split model should have a 'model_name: modelname' with the actual model name. \
                The following lines after the model name should be the sql content with NO codeblock syntax. The last line of that model file should be the line prior to the next === \
                The user will likely provide enough information such as any join requirements, or aggregation requirements so use this information to correctly structure your dbt model queries. \
                    In the absence of any specific join or aggregation requirements - feel free to suggest some code samples (nothing large) that are commented out, that might be useful to a new dbt user",
            },
            {"role": "user", "content": prompt_with_sources},
        ],
        max_tokens=400,
        n=1,
        stop=None,
        temperature=0,
    )

    # Extract the models from the response
    models = response.choices[0].message["content"].split("MODEL:")
    return models

# Example usage
model_content = "SELECT * FROM my_table"  # Example model content
model_name = "example_model"

# Generate basic suggestions
basic_response_content = generate_response_basic(model_content, model_name)
basic_display_content = format_response_for_display(basic_response_content)
print(basic_display_content)

# Generate advanced suggestions
advanced_response_content = generate_response_advanced(model_content, model_name)
advanced_display_content = format_response_for_display(advanced_response_content)
print(advanced_display_content)
