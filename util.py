import re

def split_iter(string, non_separator_re):
    # https://stackoverflow.com/questions/3862010/is-there-a-generator-version-of-string-split-in-python
    return (x.group(0) for x in re.finditer(non_separator_re, string))