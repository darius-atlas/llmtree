from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="llmtree",
    version="1.0.1",
    author="Artem-Darius Weber",
    author_email="mit.3tlasa@gmail@gmail.com",
    description="CLI tool for preparing project data for LLM context",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/darius-atlas/llmtree",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "llmtree=llmtree.cli:main",
        ],
    },
    install_requires=[],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
    },
)