import os
import re


def is_valid_color_scheme_test_file_name(file_name):
    return bool(re.match('^color_scheme_test.*\.[a-zA-Z0-9]+$', os.path.basename(file_name)))
