"""
Setup script for email_parser package.
"""
from setuptools import setup, find_packages

setup(
    name="email_parser",
    version="1.0.0",
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
    ],
    python_requires=">=3.12",
)