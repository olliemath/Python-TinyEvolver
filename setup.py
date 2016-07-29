# Always prefer setuptools over distutils
from os import path
try:
    from setuptools import setup
except ImportError:
    print("warning: you do not have setuptools installed - cannot use \"develop\" option")
    from distutils.core import setup

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='tinyevolver',
    version='0.2',

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

        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Scientific/Engineering',

        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords=['genetic', 'evolution', 'algorithms', 'optimization'],

    packages=['tinyevolver'],
)
