import yaml
import sys
from typing import List
import os
from jinja2 import Environment, FileSystemLoader
import argparse
import glob
import openai


def find_yaml_files(dbt_project_path):
    yaml_files = glob.glob(os.path.join(dbt_project_path, "**/*.yml"), recursive=True)
    yaml_files.extend(glob.glob(os.path.join(dbt_project_path, "**/*.yaml"), recursive=True))
    return yaml_files


def generate_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that suggests improvements to dbt models."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

