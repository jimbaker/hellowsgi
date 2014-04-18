import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "hellowsgi",
    version = "0.1",
    packages = find_packages(),
    install_requires = ["bottle", "clamp", "fireside","mako"]
)
