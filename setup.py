from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="smart-file-tidy",
    version="0.1.0",
    author="Smart File Tidy Team",
    description="智能文件整理助手 - 基于AI的文件分类和整理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/smart-file-tidy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
        "anthropic>=0.18.0",
        "openai>=1.12.0",
        "requests>=2.31.0",
        "PyPDF2>=3.0.0",
        "pdfplumber>=0.10.0",
        "Pillow>=10.0.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
    ],
    entry_points={
        "console_scripts": [
            "smart-tidy=src.cli.main:app",
        ],
    },
)
