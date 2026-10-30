import json
import os
from urllib.parse import urlparse

from flask import Flask, render_template_string, request

PAGE = """
<!doctype html>
<title>Assignment Submission Portal</title>
<h1>Assignment Submission Portal</h1>

{% if errors %}
  <ul id="errors" style="color:red">
    {% for e in errors %}<li>{{ e }}</li>{% endfor %}
  </ul>
{% endif %}
{% if message %}<p id="message" style="color:green">{{ message }}</p>{% endif %}

<form method="post">
  <p><input name="name" placeholder="Name" value="{{ form.name }}"></p>
  <p><input name="reg_no" placeholder="Registration number" value="{{ form.reg_no }}"></p>
  <p><input name="title" placeholder="Assignment title" value="{{ form.title }}"></p>
  <p><input name="url" placeholder="Submission URL" value="{{ form.url }}"></p>
  <button type="submit">Submit</button>
</form>

<h2>Saved submissions</h2>
<table border="1" cellpadding="6">
  <tr><th>Name</th><th>Reg No</th><th>Title</th><th>URL</th></tr>
  {% for s in submissions %}
  <tr><td>{{ s.name }}</td><td>{{ s.reg_no }}</td><td>{{ s.title }}</td><td>{{ s.url }}</td></tr>
  {% endfor %}
</table>
"""


def is_valid_url(url):
    parts = urlparse(url.strip())
    return parts.scheme in ("http", "https") and bool(parts.netloc)
    

def validate(data):
    errors = []
    if not data["name"]:
        errors.append("Name is required.")
    if not data["reg_no"]:
        errors.append("Registration number is required.")
    if not data["title"]:
        errors.append("Assignment title is required.")
    if not data["url"]:
        errors.append("Submission URL is required.")
    elif not is_valid_url(data["url"]):
        errors.append("Submission URL is invalid (use http:// or https://).")
    return errors

#making submission.json file
def create_app(data_file=None):
    app = Flask(__name__)
    path = data_file or os.environ.get("DATA_FILE", "submissions.json")

    def load():
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(items):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

    @app.route("/", methods=["GET", "POST"])
    def index():
        errors, message, status = [], None, 200
        form = {"name": "", "reg_no": "", "title": "", "url": ""}

        if request.method == "POST":
            form = {k: request.form.get(k, "").strip() for k in form}
            errors = validate(form)
            if errors:
                status = 400
            else:
                items = load()
                items.append(form)
                save(items)
                message = "Submission saved."
                form = {"name": "", "reg_no": "", "title": "", "url": ""}

        html = render_template_string(
            PAGE, errors=errors, message=message, form=form, submissions=load()
        )
        return html, status

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=True)