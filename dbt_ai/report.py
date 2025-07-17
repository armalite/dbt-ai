# flake8: noqa

# flake8: noqa

import os
import webbrowser
import pprint
from importlib import resources
from jinja2 import Environment, FileSystemLoader

def generate_html_report(reviews: list[dict], output_path: str, missing_metadata: list[str] = []):
    # Flatten the review structure so the template can access fields directly
    flat_models = []
    for model in reviews:
        review = model["review"]
        flat_models.append({
            "model_name": model["model_name"],
            "summary": review.get("summary", ""),
            "suggestions": review.get("suggestions", []),
            "style_feedback": review.get("style_feedback", []),
            "test_recommendations": review.get("test_recommendations", []),
            "tag_suggestions": review.get("tag_suggestions", []),
            "metadata_exists": model.get("metadata_exists", True),
        })

    # Debug: print models passed to the template
    print("🚧 DEBUG: Models passed to template:")
    pprint.pprint(flat_models)

    # Load template using importlib.resources (safe for packaging)
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_template.html")

    rendered_report = template.render(models=flat_models, missing_metadata=missing_metadata)

    with open(output_path, "w") as f:
        f.write(rendered_report)

    try:
        webbrowser.open(output_path)
    except:
        print(f"Report saved to {output_path} (webbrowser open failed)")



