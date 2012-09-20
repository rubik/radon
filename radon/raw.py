import StringIO
import tokenize
import operator
import collections


# Helper for map()
TOKEN_NUMBER = operator.itemgetter(0)

# A module object. It contains the following data:
#   loc = Lines of Code (total lines)
#   lloc = Logical Lines of Code
#   comments = Comments lines
#   blank = Blank lines (or whitespace-only lines)
Module = collections.namedtuple('Module', ['loc', 'lloc', 'sloc',
                                           'comments', 'multi', 'blank'])


def _generate(code):
    '''Pass the code into `tokenize.generate_tokens` and convert the result
    into a list.
    '''
    return list(tokenize.generate_tokens(StringIO.StringIO(code).readline))


def _less_tokens(tokens, remove):
    '''Process the output of `tokenize.generate_tokens` removing
    the tokens specified in `remove`.
    '''
    for token_type, value, (sr, sc), (er, ec), line in tokens:
        if token_type in remove:
            continue
        yield token_type, value, (sr, sc), (er, ec), line


def _find(tokens, token, value):
    '''Return the position of the token with the same (token, value) pair
    supplied. The position is the one of the rightmost term.
    '''
    for index, token_values in reversed(tokens):
        if [token, value] == token_values[:2]:
            return len(tokens) - index - 1
    raise ValueError('(token, value) pair not found')


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
    # Get the tokens and, in the meantime, remove comments
    processed = list(_less_tokens(tokens, [53]))
    try:
        # Verify whether a colon is present among the tokens and that
        # it is the last token.
        token_pos = _find(processed, 51, ':')
        return 2 - (token_pos == len(processed) - 2)
    except ValueError:
        # The colon is not present
        return 1


def analyze(source):
    '''Analyze the source code and return a namedtuple with the following
    fields:
        
        * loc: The number of lines of code (total)
        * lloc: The number of logical lines of code
        * sloc: The number of source lines of code (not necessarily
            corresponding to the LLOC)
        * comments: The number of Python comment lines
        * multi: The number of lines which represent multi-line strings
        * blank: The number of blank lines (or whitespace-only ones)

    The equation:

        sloc + blanks = loc

    should always hold.
    Multiline strings are not counted as comments, since, to the Python
    interpreter, they are not comments but strings.
    '''
    loc = lloc = sloc = comments = multi = blank = 0
    lines = iter(source.splitlines())
    for line in lines:
        loc += 1
        line = line.strip()
        if not line:
            blank += 1
            continue
        # If this is not a blank line, then it counts as a
        # source line of code
        sloc += 1
        try:
            tokens = _generate(line)
        except tokenize.TokenError:
            # A multi-line string or statement has been encountered:
            # start adding lines and stop when tokenize stops complaining
            while True:
                loc += 1
                sloc += 1
                line = '\n'.join([line, next(lines)]).strip()
                try:
                    tokens = _generate(line)
                except tokenize.TokenError:
                    continue
                if tokens[0][0] == 3 and len(tokens) == 2:
                    # Multi-line string detected
                    multi += line.count('\n') + 1
                break
        # Add the comments
        comments += map(TOKEN_NUMBER, tokens).count(53)
        # Process a logical line
        lloc += _logical(tokens)
    return Module(loc, lloc, sloc, comments, multi, blank)
