from setuptools import setup, find_packages
import src

setup(
    name='MrProgrammerBot',
    version=src.__version__,
    packages=find_packages(),
    author='Andrew Volski',
    author_email='andrew.volski@gmail.com',
    install_requires=['discord', 'requests']
)