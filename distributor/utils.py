from jinja2 import Environment, FileSystemLoader, select_autoescape

DEFAULT_TEMPLATE_DIR = 'distributor/templates'


class Template:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader(DEFAULT_TEMPLATE_DIR),
            autoescape=select_autoescape())

    def generate_from_template(self, template, template_vars, file_name):
        template = self.env.get_template(template)
        output = template.render(template_vars)

        with open(file_name, "w") as file:
            file.write(output)
