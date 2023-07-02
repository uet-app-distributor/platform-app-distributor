import base64

from jinja2 import Environment, FileSystemLoader, select_autoescape


DEFAULT_TEMPLATE_DIR = 'distributor/templates'

def prepare_random_suffix(string):
    base64_bytes = base64.b64encode(string.encode("ascii"))
    return base64_bytes.decode("ascii")[:16]


class Template:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(DEFAULT_TEMPLATE_DIR),
            autoescape=select_autoescape())

    def generate_from_template(self, template, template_vars):
        template = self.env.get_template(template)
        output = template.render(template_vars)
        return output