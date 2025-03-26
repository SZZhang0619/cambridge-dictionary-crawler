"""
Cambridge Dictionary Crawler

A package for extracting word definitions, examples, and parts of speech
from the Cambridge Dictionary website.
"""

__version__ = "1.0.0"

from .cli import parse_dictionary_html, process_word_list

# Expose main functions for easier imports
__all__ = ["parse_dictionary_html", "process_word_list"]