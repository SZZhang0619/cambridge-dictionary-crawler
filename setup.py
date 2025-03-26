from setuptools import setup, find_packages
import os

setup(
    name="crawler_dictionary",
    version="1.0",
    author="Shouzhi Zhang",
    author_email="h16734953151@gmail.com",
    description="A Python-based web scraper for the Cambridge Dictionary website",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/SZZhang0619/cambridge-dictionary-crawler",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", 
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "lxml",
        "tqdm"
    ],
    entry_points={
        'console_scripts': ['crawler_dictionary=crawler_dictionary.cli:main'],
    },
    include_package_data=True,
)
