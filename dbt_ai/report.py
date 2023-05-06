import sys
from typing import List
import os
from jinja2 import Environment, FileSystemLoader
import argparse
import glob


def generate_html_report(models, output_path):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("report_template.html")

    rendered_report = template.render(models=models)
    with open(output_path, "w") as f:
        f.write(rendered_report)
