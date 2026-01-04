'''This module provides functionality for suppressing complexity checks
using inline comments.

Supported comment formats:
    # radon: ignore
    # radon:ignore

The comment can be placed:
    - On the same line as a function/class definition
    - On any line inside a function/class body
'''

import re
import tokenize

try:
    import StringIO as io
except ImportError:  # pragma: no cover
    import io

# Pattern to match "# radon: ignore" or "# radon:ignore"
IGNORE_PATTERN = re.compile(r'#\s*radon:\s*ignore\b', re.IGNORECASE)


def get_ignore_lines(source):
    '''Extract line numbers containing "# radon: ignore" comments.

    :param source: The source code as a string.
    :returns: A set of line numbers (1-indexed) that contain ignore comments.
    '''
    ignore_lines = set()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for token_type, token_string, start, _, _ in tokens:
            if token_type == tokenize.COMMENT:
                if IGNORE_PATTERN.search(token_string):
                    line_no = start[0]
                    ignore_lines.add(line_no)
    except tokenize.TokenError:
        # If tokenization fails, return what we have so far
        pass
    return ignore_lines


def should_ignore_block(block, ignore_lines):
    '''Determine if a block should be ignored based on ignore comments.

    A block is ignored if:
        - The definition line contains "# radon: ignore"
        - The line immediately before the definition contains "# radon: ignore"

    Note: Unlike checking all lines within a block, this only checks the
    definition line and the line before it. This allows placing ignore
    comments on nested functions without affecting the parent function.

    :param block: A Function or Class namedtuple with lineno and endline attributes.
    :param ignore_lines: A set of line numbers containing ignore comments.
    :returns: True if the block should be ignored, False otherwise.
    '''
    if not ignore_lines:
        return False

    # Check if the definition line or the line before it has an ignore comment
    if block.lineno in ignore_lines:
        return True
    if (block.lineno - 1) in ignore_lines:
        return True
    return False


def filter_ignored_blocks(blocks, ignore_lines):
    '''Filter out blocks that should be ignored.

    :param blocks: A list of Function or Class namedtuples.
    :param ignore_lines: A set of line numbers containing ignore comments.
    :returns: A list of blocks that are not ignored.
    '''
    if not ignore_lines:
        return blocks
    return [b for b in blocks if not should_ignore_block(b, ignore_lines)]
