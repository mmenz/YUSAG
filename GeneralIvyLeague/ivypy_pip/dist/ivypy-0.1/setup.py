import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="ivypy",
    version="0.1",
    author="Michael Menz",
    author_email="menzdogma@gmail.com",
    description=("A package for retrieving ivy league sports data"),
    license="BSD",
    keywords="ivy league sports",
    url="",
    packages=['ivypy'],
    long_description=read('README'),
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
