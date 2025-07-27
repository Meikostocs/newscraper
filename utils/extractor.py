import re


def extract_between(text: str, str_start: str, str_end: str) -> str:
    pattern = re.escape(str_start) + r'(.*?)' + re.escape(str_end)
    match = re.search(pattern, text, re.DOTALL)
    return str_start + match.group(1) if match else ''
