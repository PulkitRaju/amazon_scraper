import json
import pandas as pd
import os

# Define input and output file paths
script_dir = os.path.dirname(os.path.abspath(__file__))
input_jsonl_file = 'output.jsonl' # Assuming it's in the same directory as the script
output_excel_file = 'output.xlsx' # Output Excel file name

# --- Optional: Specify full paths if files are elsewhere ---
# input_jsonl_file = os.path.join(script_dir, 'path', 'to', 'output.jsonl')
# output_excel_file = os.path.join(script_dir, 'path', 'to', 'output.xlsx')
# ----------------------------------------------------------

def convert_jsonl_to_excel(jsonl_path, excel_path):
    """Reads a JSON Lines file and converts it to an Excel file."""
    data = []
    try:
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # Trim whitespace and check if line is not empty
                    line = line.strip()
                    if line:
                        data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON line: {line.strip()} - Error: {e}")
    except FileNotFoundError:
        print(f"Error: Input file not found at {jsonl_path}")
        return
    except Exception as e:
        print(f"An error occurred while reading {jsonl_path}: {e}")
        return

    if not data:
        print("No valid data found in the input file to convert.")
        return

    try:
        # Convert list of dictionaries to pandas DataFrame
        df = pd.DataFrame(data)
        
        # Write DataFrame to Excel file
        # index=False prevents pandas from writing the DataFrame index as a column
        df.to_excel(excel_path, index=False, engine='openpyxl')
        print(f"Successfully converted {jsonl_path} to {excel_path}")
        
    except ImportError:
        print("Error: 'pandas' or 'openpyxl' library not found. ")
        print("Please install them using: pip install pandas openpyxl")
    except Exception as e:
        print(f"An error occurred while writing to {excel_path}: {e}")

if __name__ == '__main__':
    # Check if the input file exists before attempting conversion
    if os.path.exists(input_jsonl_file):
        convert_jsonl_to_excel(input_jsonl_file, output_excel_file)
    else:
        print(f"Error: Input file '{input_jsonl_file}' not found in the script directory.")
        print("Please make sure 'output.jsonl' exists or update the path in the script.") 