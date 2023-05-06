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

