from jinja2 import Environment, FileSystemLoader
import webbrowser 
import markdown2
import os


def markdown_filter(value):
    return markdown2.markdown(value, extras=["fenced-code-blocks"])


def generate_html_report(models, output_path, missing_metadata: list[str]):
    template_path = os.path.join(os.path.dirname(__file__), "templates", "report_template.html")
    env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
    env.filters['markdown'] = markdown_filter
    template = env.get_template(os.path.basename(template_path))

    rendered_report = template.render(models=models, missing_metadata=missing_metadata)
    with open(output_path, "w") as f:
        f.write(rendered_report)

    # Open the report in a new browser tab
    webbrowser.open(output_path)
