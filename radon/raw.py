'''This module contains functions related to raw metrics.

The main function is :func:`~radon.raw.analyze`, and should be the only one
that is used.
'''

import collections
import operator
import tokenize

try:
    import StringIO as io
except ImportError:  # pragma: no cover
    import io


__all__ = [
    'OP',
    'COMMENT',
    'TOKEN_NUMBER',
    'NL',
    'NEWLINE',
    'EM',
    'Module',
    '_generate',
    '_fewer_tokens',
    '_find',
    '_logical',
    'analyze',
]

COMMENT = tokenize.COMMENT
OP = tokenize.OP
NL = tokenize.NL
NEWLINE = tokenize.NEWLINE
EM = tokenize.ENDMARKER

# Helper for map()
TOKEN_NUMBER = operator.itemgetter(0)

# A module object. It contains the following data:
#   loc = Lines of Code (total lines)
#   lloc = Logical Lines of Code
#   comments = Comments lines
#   multi = Multi-line strings (assumed to be docstrings)
#   blank = Blank lines (or whitespace-only lines)
#   single_comments = Single-line comments or docstrings
Module = collections.namedtuple(
    'Module',
    ['loc', 'lloc', 'sloc', 'comments', 'multi', 'blank', 'single_comments'],
)


def _generate(code):
    '''Pass the code into `tokenize.generate_tokens` and convert the result
    into a list.
    '''
    # tokenize.generate_tokens is an undocumented function accepting text
    return list(tokenize.generate_tokens(io.StringIO(code).readline))


def _fewer_tokens(tokens, remove):
    '''Process the output of `tokenize.generate_tokens` removing
    the tokens specified in `remove`.
    '''
    for values in tokens:
        if values[0] in remove:
            continue
        yield values


def _find(tokens, token, value):
    '''Return the position of the last token with the same (token, value)
    pair supplied. The position is the one of the rightmost term.
    '''
    for index, token_values in enumerate(reversed(tokens)):
        if (token, value) == token_values[:2]:
            return len(tokens) - index - 1
    raise ValueError('(token, value) pair not found')


def _split_tokens(tokens, token, value):
    '''Split a list of tokens on the specified token pair (token, value),
    where *token* is the token type (i.e. its code) and *value* its actual
    value in the code.
    '''
    res = [[]]
    for token_values in tokens:
        if (token, value) == token_values[:2]:
            res.append([])
            continue
        res[-1].append(token_values)
    return res


def _get_all_tokens(line, lines):
    '''Starting from *line*, generate the necessary tokens which represent the
    shortest tokenization possible. This is done by catching
    :exc:`tokenize.TokenError` when a multi-line string or statement is
    encountered.
    :returns: tokens, lines
    '''
    buffer = line
    used_lines = [line]
    while True:
        try:
            tokens = _generate(buffer)
        except tokenize.TokenError:
            # A multi-line string or statement has been encountered:
            # start adding lines and stop when tokenize stops complaining
            pass
        else:
            if not any(t[0] == tokenize.ERRORTOKEN for t in tokens):
                return tokens, used_lines

        # Add another line
        next_line = next(lines)
        buffer = buffer + '\n' + next_line
        used_lines.append(next_line)


def _logical(tokens):
    '''Find how many logical lines are there in the current line.

    Normally 1 line of code is equivalent to 1 logical line of code,
    but there are cases when this is not true. For example::

        if cond: return 0

    this line actually corresponds to 2 logical lines, since it can be
    translated into::

        if cond:
            return 0

    Examples::

        if cond:  -> 1

        if cond: return 0  -> 2

        try: 1/0  -> 2

        try:  -> 1

        if cond:  # Only a comment  -> 1

        if cond: return 0  # Only a comment  -> 2
    '''

    def aux(sub_tokens):
        '''The actual function which does the job.'''
        # Get the tokens and, in the meantime, remove comments
        processed = list(_fewer_tokens(sub_tokens, [COMMENT, NL, NEWLINE]))
        try:
            # Verify whether a colon is present among the tokens and that
            # it is the last token.
            token_pos = _find(processed, OP, ':')
            # We subtract 2 from the total because the last token is always
            # ENDMARKER. There are two cases: if the colon is at the end, it
            # means that there is only one logical line; if it isn't then there
            # are two.
            return 2 - (token_pos == len(processed) - 2)
        except ValueError:
            # The colon is not present
            # If the line is only composed by comments, newlines and endmarker
            # then it does not count as a logical line.
            # Otherwise it count as 1.
            if not list(_fewer_tokens(processed, [NL, NEWLINE, EM])):
                return 0
            return 1

    return sum(aux(sub) for sub in _split_tokens(tokens, OP, ';'))


def is_single_token(token_number, tokens):
    '''Is this a single token matching token_number followed by ENDMARKER, NL
    or NEWLINE tokens.
    '''
    return TOKEN_NUMBER(tokens[0]) == token_number and all(
        TOKEN_NUMBER(t) in (EM, NL, NEWLINE) for t in tokens[1:]
    )


def analyze(source):
    '''Analyze the source code and return a namedtuple with the following
    fields:

        * **loc**: The number of lines of code (total)
        * **lloc**: The number of logical lines of code
        * **sloc**: The number of source lines of code (not necessarily
            corresponding to the LLOC)
        * **comments**: The number of Python comment lines
        * **multi**: The number of lines which represent multi-line strings
        * **single_comments**: The number of lines which are just comments with
            no code
        * **blank**: The number of blank lines (or whitespace-only ones)

    The equation :math:`sloc + blanks + multi + single_comments = loc` should
    always hold.  Multiline strings are not counted as comments, since, to the
    Python interpreter, they are not comments but strings.
    '''
    lloc = comments = single_comments = multi = blank = sloc = 0
    lines = (l.strip() for l in source.splitlines())
    lineno = 1
    for line in lines:
        try:
            # Get a syntactically complete set of tokens that spans a set of
            # lines
            tokens, parsed_lines = _get_all_tokens(line, lines)
        except StopIteration:
            raise SyntaxError('SyntaxError at line: {0}'.format(lineno))

        lineno += len(parsed_lines)

        comments += sum(
            1 for t in tokens if TOKEN_NUMBER(t) == tokenize.COMMENT
        )

        # Identify single line comments, conservatively
        if is_single_token(tokenize.COMMENT, tokens):
            single_comments += 1

        # Identify docstrings, conservatively
        elif is_single_token(tokenize.STRING, tokens):
            _, _, (start_row, _), (end_row, _), _ = tokens[0]
            if end_row == start_row:
                # Consider single-line docstrings separately from other
                # multiline docstrings
                single_comments += 1
            else:
                multi += sum(1 for l in parsed_lines if l)  # Skip empty lines
                blank += sum(1 for l in parsed_lines if not l)
        else:  # Everything else is either code or blank lines
            for parsed_line in parsed_lines:
                if parsed_line:
                    sloc += 1
                else:
                    blank += 1

        # Process logical lines separately
        lloc += _logical(tokens)

    loc = sloc + blank + multi + single_comments
    return Module(loc, lloc, sloc, comments, multi, blank, single_comments)
