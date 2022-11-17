"""Wiki Link Parser"""
import re
from typing import TypedDict


class WikiParser:
    """Wiki Link Parser."""
    

    @staticmethod
    def get_note_hashtags(text: str) -> list[str]:
        """Get all hashtags from the given text and return a list of them."""
        hashtag_regex = r"#(\w+)"
        hashtag_list = re.findall(hashtag_regex, text)
        return hashtag_list