"""
Setup script for email_parser package.
"""
from setuptools import setup, find_packages

setup(
    name="email_parser",
    version="2.2.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "email-validator>=2.0.0",
        "pypdf2>=3.0.0",
        "pillow>=10.0.0",
        "filetype>=1.0.0",
        "openpyxl>=3.1.0",
        "pandas>=2.0.0",
        "chardet>=5.0.0",
        "mistralai>=1.5.2",
        "mammoth>=1.6.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "tiktoken>=0.5.0",
        "python-docx>=0.8.11",
    ],
    python_requires=">=3.12",
)