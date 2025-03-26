import requests, sys
import json
import re
from lxml import etree
import os
import time
from tqdm import tqdm

# Add a retry mechanism with exponential backoff
def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers={'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'})
            return response
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1, 2, 4 seconds
    raise Exception("Failed to fetch after multiple retries")

def parse_dictionary_html(word: str) -> dict:
    """
    Fetch and extract dictionary information for a word from Cambridge Dictionary.
    
    This function connects to Cambridge Dictionary online, downloads the
    dictionary page for the given word, and extracts the word's definitions,
    examples, and parts of speech (noun, verb, etc.).
    """
    r = fetch_with_retry('https://dictionary.cambridge.org/dictionary/english/' + word)
    
    # Parse HTML
    html = r.text
    page = etree.HTML(html)
    
    # Check if the page is valid (contains dictionary content)
    if page.xpath("//title[contains(text(), 'Cambridge English Dictionary')]") and not page.xpath("//div[contains(@class, 'entry-body__el')]"):
        raise Exception(f"Word '{word}' not found in dictionary or invalid response received")
    
    # Extract word from title or use the input word
    word_matches = re.search(r'<title>([^|]+)\|', html)
    if word_matches:
        word = word_matches.group(1).strip().lower()
    else:
        # Try to extract from dictionary content
        word_elements = page.xpath("//span[contains(@class, 'hw dhw')]")
        if word_elements:
            word = word_elements[0].text.strip().lower()
    
    result = {
        "word": word,
        "partsOfSpeech": []
    }
    
    # Find all parts of speech (noun, verb, etc.)
    pos_elements = page.xpath("//div[contains(@class, 'pos-header')]/div[contains(@class, 'posgram')]/span[@class='pos dpos']")
    
    # Process each part of speech
    processed_pos = set()
    for pos_element in pos_elements:
        pos_type = pos_element.text.strip().lower()
        
        # Skip if we've already processed this part of speech
        if pos_type in processed_pos:
            continue
        
        processed_pos.add(pos_type)
        
        # Create entry for this part of speech
        pos_entry = {
            "type": pos_type
        }
        
        # Find all definition blocks that belong to this part of speech
        def_blocks = page.xpath(f"//span[@class='pos dpos' and text()='{pos_type}']/ancestor::div[contains(@class, 'pos-header')]/following-sibling::div[contains(@class, 'pos-body')]//div[contains(@class, 'def-block')]")
        
        first_definition = None
        first_definition_with_example = None
        
        for def_block in def_blocks:
            # Look for the main definition text element
            definition_element = def_block.xpath(".//div[contains(@class, 'def ddef_d')]")
            if not definition_element:
                continue  # Skip this block if no definition found
                
            # Extract the text of the definition
            definition_text = definition_element[0].xpath("string()").strip()
            # Clean up: Remove trailing colon from definition if present
            if definition_text.endswith(':'):
                definition_text = definition_text[:-1]
            
            # Find usage examples for this definition
            example_elements = def_block.xpath(".//div[contains(@class, 'examp dexamp')]")
            example_text = ""
            
            # Get the first example if any exist
            if example_elements:
                example_text = example_elements[0].xpath("string()").strip()
            
            # Save the first definition we encounter as our fallback option
            if first_definition is None:
                first_definition = {
                    "definition": definition_text
                }
                if example_text:
                    first_definition["example"] = example_text
            
            # Prefer definitions with examples - stop looking once we find one
            if example_text and first_definition_with_example is None:
                first_definition_with_example = {
                    "definition": definition_text,
                    "example": example_text
                }
                break
        
        # Use definition with example if found, otherwise use first definition
        if first_definition_with_example:
            pos_entry["definition"] = first_definition_with_example["definition"]
            pos_entry["example"] = first_definition_with_example["example"]
        elif first_definition:
            pos_entry["definition"] = first_definition["definition"]
            if "example" in first_definition:
                pos_entry["example"] = first_definition["example"]
        
        # Only add entry if it has a definition
        if "definition" in pos_entry:
            result["partsOfSpeech"].append(pos_entry)
    
    return result

def read_words_from_file(file_path):
    """
    Read a list of words from a text file.
    
    Each word should be on its own line in the file.
    Empty lines are skipped.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

def determine_output_filename(input_file, args):
    """
    Determine the output filename based on the input file and command line arguments.
    """
    base_name = input_file.replace('.txt', '')
    return args[-1] if len(args) > (3 if args[1] == "--file" else 2) else f"{base_name}.json"

def process_word_list(words_file, output_file):
    """
    Look up multiple words from a file and save their definitions to a JSON file.
    
    This function reads words from the specified file, looks up each word
    in the Cambridge Dictionary, and saves all the results to a single
    output file. A short delay is added between lookups to avoid
    overloading the dictionary website.
    """
    words = read_words_from_file(words_file)
    results = []
    
    print(f"Processing {len(words)} words from {words_file}...")
    
    for i, word in enumerate(tqdm(words, desc="Processing words")):
        print(f"Processing word {i+1}/{len(words)}: {word}")
        try:
            result = parse_dictionary_html(word)
            results.append(result)
            # Add a small delay to be nice to the server
            if i < len(words) - 1:  # Don't wait after the last word
                time.sleep(2)  # Increased delay to avoid being blocked
        except Exception as e:
            print(f"Error processing word '{word}': {e}")
    
    # Save all results to a single JSON file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"All processed data saved to {output_file}")

def print_usage():
    print("Usage: python cli.py <word> [output_file]")
    print("   or: python cli.py --file <words_file> [output_file]")
    print("   or: python cli.py <words_file.txt> [output_file]")

def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
        
    # Handle file processing cases
    if sys.argv[1].endswith('.txt') or sys.argv[1] == "--file":
        if sys.argv[1] == "--file" and len(sys.argv) < 3:
            print("Error: Missing filename after --file flag")
            print_usage()
            sys.exit(1)
            
        words_file = sys.argv[2] if sys.argv[1] == "--file" else sys.argv[1]
        
        # Check if file exists
        if not os.path.exists(words_file):
            print(f"Error: File '{words_file}' not found")
            sys.exit(1)
            
        output_file = determine_output_filename(words_file, sys.argv)
        
        process_word_list(words_file, output_file)
    else:
        # Single word processing
        word = sys.argv[1]
        
        # Default output file name based on word
        if len(sys.argv) > 2:
            output_file = sys.argv[2]
        else:
            output_file = f"result_{word}.json"
        
        # Parse HTML and get structured data
        result = parse_dictionary_html(word)
        
        # Save to JSON file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
        
        print(f"Parsed data saved to {output_file}")
        
        # Also print to console
        print("\nExtracted data:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # Check if the script is run with arguments
    if len(sys.argv) == 1:
        print_usage()
        sys.exit(1)
    else:
        main()