import base64
import string
import random

from jinja2 import Environment, FileSystemLoader, select_autoescape


DEFAULT_TEMPLATE_DIR = 'distributor/templates'

def append_random_suffix(content):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(8))
    return f"{content}_{random_string}"


class Template:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(DEFAULT_TEMPLATE_DIR),
            autoescape=select_autoescape())

    def generate_from_template(self, template, template_vars):
        template = self.env.get_template(template)
        output = template.render(template_vars)
        return output