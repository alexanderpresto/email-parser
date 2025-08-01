"""
PyInstaller hook for email_parser package
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files

# Collect all submodules from email_parser
hiddenimports = collect_submodules('email_parser')

# Collect data files from the package
datas = collect_data_files('email_parser')

# Add tiktoken data files
datas += collect_data_files('tiktoken_ext')

# Add additional data files that might be needed
datas += collect_data_files('mistralai')
datas += collect_data_files('prompt_toolkit')