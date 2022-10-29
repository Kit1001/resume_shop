import inspect

from jinja2 import Environment, PackageLoader, select_autoescape


def render(request, template, context=None, app_name=None):
    # Служебная функция, передает указанный шаблон и контекст в шаблонизатор jinja2.
    if context is None:
        context = {}
    context["request"] = request
    if not app_name:
        app_name = inspect.getmodule(inspect.stack()[1][0]).__package__
    env = Environment(
        loader=PackageLoader(app_name),
        autoescape=select_autoescape()
    )
    content = env.get_template(template)
    return content.render(**context)
