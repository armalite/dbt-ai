from jinja2 import Environment, FileSystemLoader
import webbrowser 
import markdown2


def markdown_filter(value):
    return markdown2.markdown(value, extras=["fenced-code-blocks"])


def generate_html_report(models, output_path):
    env = Environment(loader=FileSystemLoader("dbt_ai/templates"))
    env.filters['markdown'] = markdown_filter
    template = env.get_template("report_template.html")

    rendered_report = template.render(models=models)
    with open(output_path, "w") as f:
        f.write(rendered_report)

    # Open the report in a new browser tab
    webbrowser.open(output_path)
