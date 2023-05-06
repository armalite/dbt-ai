
import sys
from typing import List
import os
from jinja2 import Environment, FileSystemLoader
import argparse
import glob




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

def suggest_dbt_model_improvements(file_path, model_name):
    with open(file_path, "r") as f:
        content = f.read()

    prompt = f"Given the following dbt model {model_name}:\n\n{content}\n\nPlease provide suggestions on how to improve this model in terms of syntax, code structure and dbt best practices such as using ref instead of hardcoding table names:"
    response = generate_response(prompt)
    return response