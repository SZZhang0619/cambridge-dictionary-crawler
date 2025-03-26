# Cambridge Dictionary Crawler

A Python-based web scraper that extracts definitions, examples, and parts of speech from the Cambridge Dictionary website. The tool stores the data in JSON format for easy use in language-learning tools or further analysis.

## Installation

```bash
pip install -e .
```

Or install from GitHub:

```bash
pip install git+https://github.com/SZZhang0619/cambridge-dictionary-crawler.git
```

## Usage

After installation, you can use the tool in the following ways:

### Command Line

**Look up a single word:**

```bash
crawler_dictionary word [output_file.json]
```

**Process multiple words from a text file:**

```bash
crawler_dictionary --file words.txt [output_file.json]
```

**or simply:**

```bash
crawler_dictionary words.txt [output_file.json]
```

## Example Output

```json
{
  "word": "example",
  "partsOfSpeech": [
    {
      "type": "noun",
      "definition": "something that is typical or representative of a particular thing",
      "example": "This painting is a wonderful example of her early work."
    }
  ]
}
```

## Features

* Extract word definitions, examples, and parts of speech
* Process single words or multiple words from a file
* Automatic retry mechanism with exponential backoff
* Progress bar for multiple word processing
* Output to JSON format

## Dependencies
* requests
* beautifulsoup4
* lxml
* tqdm

## License

This project is licensed under the MIT License - see the LICENSE file for details.


