import os

from jinja2 import PackageLoader, Environment


class Templates:
    Env = Environment(loader=PackageLoader("conf", "templates"))

    @classmethod
    def get_login_tpl(cls, username, login_url):
        template = cls.Env.get_template('login.html')
        return template.render(username=username, login_url=login_url)
