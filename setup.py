from setuptools import setup, find_packages
import os

# get the current working directory
here = os.path.abspath(os.path.dirname(__file__))

VERSION = "0.0.1"
DESCRIPTION = "A package for scraping listings from Zillow"
LONG_DESCRIPTION = ""

# Setting up
setup(
    name="zillow_scraper",
    version=VERSION,
    author="Marnel Ramirez",
    author_email="<marnelram@gmail.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["requests", "beautifulsoup4", "pandas"],
    keywords=["python", "zillow", "scraper", "web scraping"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
    ],
)
