from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="text-agent",
    version="0.1.0",
    author="kamiyamazgc",
    description="Document Pipeline System - Convert various document formats to readable Japanese text",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kamiyamazgc/text_agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "text-agent=docpipe.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "docpipe": ["*.yaml", "*.yml"],
    },
)
