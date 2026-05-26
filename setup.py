from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="claisum",
    version="0.1.0",
    author="Claisum",
    author_email="contact@claisum.dev",
    description="Customize and mod your favorite apps — Discord themes, plugins, and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claisum/Claisum.py",
    packages=find_packages(),
    python_requires=">=3.12",
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
        "colorama>=0.4",
        "rich>=13.0",
    ],
    entry_points={
        "console_scripts": [
            "claisum=claisum.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    keywords="discord theme plugin mod customize cli",
)
