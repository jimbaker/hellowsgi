import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
#from clamp.commands import clamp_command

setup(
    name = "hellowsgi",
    version = "0.1",
    packages = find_packages(),
    install_requires = ["clamp>=0.4", "fireside"],
    clamp = {
        "modules": ["clamped"],

        # FIXME - this should drive the construction of an appropriate web.xml, which is materialized during war construction;
        # so each handler ever used is registered in some file, then put together in one place
        # need to see how this is done in common tools like gunicorn/modwsgi
        # and of course, presumably not too different than what paste does

        # "wsgi.handler": "hellowsgi.simple_app",
    },
    #cmdclass = { "install": clamp_command }
)
