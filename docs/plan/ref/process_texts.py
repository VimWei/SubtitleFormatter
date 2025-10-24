import os
import glob
import re
from deepmultilingualpunctuation import PunctuationModel

# 1. Define input and output directories
input_dir = "input"
output_dir = "output"

# 2. Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)
print(f"Output directory '{output_dir}' is ready.")

# 3. Initialize the model
# Define the path to the local model.
# This model should be downloaded beforehand to enable offline use.
local_model_path = "models/fullstop-punctuation-multilang-large"
print(f"Loading punctuation model from '{local_model_path}'... (This may take a moment)")
model = PunctuationModel(model=local_model_path)
print("Model loaded.")

# 4. Find all .txt files in the input directory recursively
input_files = glob.glob(os.path.join(input_dir, '**', '*.txt'), recursive=True)

if not input_files:
    print(f"No .txt files found in '{input_dir}'.")
    exit()

print(f"Found {len(input_files)} files to process.")

# 5. Process each file
for filepath in input_files:
    filename = os.path.basename(filepath)
    output_filepath = os.path.join(output_dir, filename)

    print(f"Processing '{filename}'...")

    try:
        # Use utf-8-sig to handle potential BOM (Byte Order Mark) at the start of files
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            text = f.read()

        if not text.strip():
            print(f"Skipping empty file: '{filename}'")
            with open(output_filepath, 'w', encoding='utf-8') as f:
                f.write('') # Create an empty output file
            continue

        # Step 1: Use the simple and robust restore_punctuation method.
        # It handles long texts automatically.
        punctuated_text = model.restore_punctuation(text)

        # Step 2: Split text into sentences.
        # The regex splits the text after a period, question mark, or exclamation mark.
        sentences = re.split(r'(?<=[.?!])\s+', punctuated_text.strip())

        # Step 3: Capitalize each sentence and put it on a new line.
        processed_lines = []
        for sentence in sentences:
            s = sentence.strip()
            if s:
                # Find the first letter and capitalize it, preserving the rest of the case.
                for i, char in enumerate(s):
                    if char.isalpha():
                        processed_lines.append(s[:i] + s[i].upper() + s[i+1:])
                        break
                else:
                    processed_lines.append(s) # Append if no letter found

        capitalized_text = '\n'.join(processed_lines)

        # Step 4: Apply the user's precise replacement rules.
        result = capitalized_text.replace(' - ', ', ')
        result = result.replace('- ', ', ')

        # Step 5: Write the final, corrected text to the output file.
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(result)

        print(f"Successfully saved punctuated text to '{output_filepath}'.")

    except Exception as e:
        print(f"Failed to process file {filename}: {e}")

print("\nAll files processed successfully.")