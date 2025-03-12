"""
Example of Excel-to-CSV conversion functionality.
"""
import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the sys.path to import the package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from email_parser.converters.excel_converter import ExcelConverter
from email_parser.utils.logging_config import configure_logging

# Set up logging
configure_logging(log_level=logging.INFO)

def convert_excel_file(excel_path, output_dir="output/converted_excel"):
    """Convert an Excel file to CSV."""
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize the Excel converter
    converter = ExcelConverter(output_dir=output_dir)
    
    # Check if file is an Excel file
    if not converter.is_excel_file(excel_path):
        print(f"File does not appear to be an Excel file: {excel_path}")
        return None
    
    # Define a simple prompt callback for sheet selection
    def prompt_for_sheets(message, sheet_names):
        print(message)
        for i, sheet in enumerate(sheet_names, 1):
            print(f"  {i}. {sheet}")
        
        selection = input("Enter sheet numbers to convert (comma-separated, or 'all'): ")
        
        if selection.lower() == 'all':
            return sheet_names
        
        try:
            indices = [int(i.strip()) - 1 for i in selection.split(',')]
            return [sheet_names[i] for i in indices if 0 <= i < len(sheet_names)]
        except (ValueError, IndexError):
            print("Invalid selection. Converting all sheets.")
            return sheet_names
    
    # Get original filename
    original_filename = os.path.basename(excel_path)
    secure_filename = original_filename  # In a real scenario, we would sanitize this
    
    # Generate a unique email ID for tracking
    email_id = f"excel_conversion_{Path(excel_path).stem}"
    
    # Convert the Excel file to CSV
    conversion_results = converter.convert_excel_to_csv(
        excel_path,
        original_filename,
        secure_filename,
        email_id,
        prompt_callback=prompt_for_sheets
    )
    
    # Print conversion results
    print(f"\nExcel file '{original_filename}' converted to CSV:")
    for result in conversion_results:
        print(f"  - Sheet '{result['sheet_name']}' → {result['csv_filename']}")
    
    return conversion_results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python excel_conversion.py <excel_file_path>")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    if not os.path.isfile(excel_path):
        print(f"Error: File not found: {excel_path}")
        sys.exit(1)
    
    try:
        results = convert_excel_file(excel_path)
        if results:
            print("Excel conversion completed successfully.")
            output_dir = os.path.abspath("output/converted_excel")
            print(f"CSV files are in the '{output_dir}' directory.")
    except Exception as e:
        print(f"Error converting Excel file: {str(e)}")
        sys.exit(1)