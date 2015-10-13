# Always prefer setuptools over distutils
from os import path
try:
    from setuptools import setup, find_packages
except ImportError:
    print("warning: you do not have setuptools installed - cannot use \"develop\" option")
    from distutils.core import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='tinyevolver',
    version='0.1',

    description='A simple, tiny engine for creating genetic algorithms.',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/olliemath/Python-TinyEvolver/',

    # Author details
    author='Oliver Margetts',
    author_email='oliver.margetts@gmail.com',

    # Choose your license
    license='GNU GPL V.2',

    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Scientists',
        'Intended Audience :: Developers',
        'Topic :: Software Development'
        'Topic :: Genetic Algorithms',
        'Topic :: Optimization',
        'Topic :: Modelling',

        'License :: OSI Approved :: GNU GPL V.2',

        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='genetic algorithms optimization',

    packages=find_packages(),
)
