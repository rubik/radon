'''This module contains functions related to raw metrics.

The main function is :func:`~radon.raw.analyze`, and should be the only one
that is used.
'''

import tokenize
import operator
import collections
try:
    import StringIO as io
except ImportError:  # pragma: no cover
    import io


__all__ = ['OP', 'COMMENT', 'TOKEN_NUMBER', 'NL', 'EM', 'Module', '_generate',
           '_less_tokens', '_find', '_logical', 'analyze']

COMMENT = tokenize.COMMENT
OP = tokenize.OP
NL = tokenize.NL
EM = tokenize.ENDMARKER

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
    return list(tokenize.generate_tokens(io.StringIO(code).readline))


def _less_tokens(tokens, remove):
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
    '''
    sloc_increment = multi_increment = 0
    try:
        tokens = _generate(line)
    except tokenize.TokenError:
        # A multi-line string or statement has been encountered:
        # start adding lines and stop when tokenize stops complaining
        while True:
            sloc_increment += 1
            line = '\n'.join([line, next(lines)])
            try:
                tokens = _generate(line)
            except tokenize.TokenError:
                continue
            if tokens[0][0] == 3 and len(tokens) == 2:
                # Multi-line string detected
                multi_increment += line.count('\n') + 1
            break
    return tokens, sloc_increment, multi_increment


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
        processed = list(_less_tokens(sub_tokens, [COMMENT]))
        try:
            # Verify whether a colon is present among the tokens and that
            # it is the last token.
            token_pos = _find(processed, OP, ':')
            return 2 - (token_pos == len(processed) - 2)
        except ValueError:
            # The colon is not present
            # If the line is only composed by comments, newlines and endmarker
            # then it does not count as a logical line.
            # Otherwise it count as 1.
            if not list(_less_tokens(processed, [NL, EM])):
                return 0
            return 1
    return sum(aux(sub) for sub in _split_tokens(tokens, OP, ';'))


def remove_lines(doc, lines_to_remove):
    '''Removes lines from a document.
    :param doc: [str], document cast into an array.
    :param lines_to_remove: [int], list of lines to remove from the doc.
    :return: [str], doc with specified lines removed.
    '''

    for line_number in lines_to_remove:
        doc[line_number] = []
    return [line.strip() for line in doc if line]


def is_multiline_string(doc, line_count, quote_type):
    '''Cases to catch multiline_strings.
    :param doc: [str], a document cast into an array.
    :param line_count: int, zero based index that points to the current line
                 in an docuement.
    :param quote_type: str, one of the two multiline quotes available in python.
    :return: bool, True if the triple quoted line is a multiline string.
    '''

    line = doc[line_count]
    previous_line = doc[line_count-1]

    if line.count('=') and line.index('=') < line.index(quote_type)\
            or line_count != 0 and '=' in previous_line:
        return True

    else:
        return False


def find_multiline_comments(lines_to_remove, end, doc, line_count, quote_type):
    '''
    :param lines_to_remove: [int], a zero based index that represents lines to
                            to be removed from a document.
    :param end: bool, if True then the first of the two multiline comments has
                been found.
    :param doc: [str], a document cast into an array.
    :param line_count: int, zero based index that points to the current line
                 in an docuement.
    :param quote_type: str, one of the two multiline quotes available in python.
    :return: tuple, lines_to_remove = same as that passed in, with additions.
                    end = bool, updated version of end paramater.
    '''

    # Exceptions: Quote type needs to exist, to get the first line of a
    # multine comment it cannot be the last.
    if quote_type and end is False and line_count < len(doc) - 1:
        quote_type = quote_type[0]
        end = True

        if is_multiline_string(doc, line_count, quote_type):
            return lines_to_remove, False

        lines_to_remove.append(line_count)
        return lines_to_remove, end

    elif end and not quote_type:
        lines_to_remove.append(line_count)

    elif end and quote_type:
        lines_to_remove.append(line_count)
        end = False

    return lines_to_remove, end


def find_comments(lines_to_remove, line_count, line):
    '''Find single line comments in a python file.
    :param lines_to_remove: [int], a zero based index that represents lines to
                            to be removed from a document.
    :param line_count: int, zero based index that points to the current line
                       in an docuement.
    :param line: str, the current line in a document being examined.
    :return: [int], same as parameter with additional indices that were found.
    '''

    if not line:
        return lines_to_remove

    if line[0] == "#" or line.count("'''") == 2 or line.count('"""') == 2:
        lines_to_remove.append(line_count)

    return lines_to_remove


def remove_python_documentation(doc):
    '''Removes all the documentation from python code.
    :param doc: [str], each line of a code recasted as an array
    :return: [str], doc that was passed in, excluding lines of documentation.
    '''

    multi_quos = ["'''", '"""']
    lines_to_remove = []
    end = False

    for line_count, line in enumerate(doc):

        lines_to_remove = find_comments(lines_to_remove, line_count, line)

        quote_type = [multi_quo for multi_quo in multi_quos\
                if multi_quo in doc[line_count]]

        # end is True if the first of a pair of multiline comments is found and
        # end will revert back to False when both pairs are found.
        lines_to_remove, end = find_multiline_comments(
            lines_to_remove=lines_to_remove,
            end=end,
            doc=doc,
            line_count=line_count,
            quote_type=quote_type)

    return remove_lines(doc, lines_to_remove)


def analyze(source):
    '''Analyze the source code and return a namedtuple with the following
    fields:

        * **loc**: The number of lines of code (total)
        * **lloc**: The number of logical lines of code
        * **sloc**: The number of source lines of code (not necessarily
            corresponding to the LLOC)
        * **comments**: The number of Python comment lines
        * **multi**: The number of lines which represent multi-line strings
        * **blank**: The number of blank lines (or whitespace-only ones)

    The equation :math:`sloc + blanks = loc` should always hold.
    Multiline strings are not counted as comments, since, to the Python
    interpreter, they are not comments but strings.
    '''
    sloc = lloc = comments = multi = blank = 0
    loc = len(remove_python_documentation([line.strip() for line in source\
            if line]))
    lines = iter(source.splitlines())
    for lineno, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            blank += 1
            continue
        # If this is not a blank line, then it counts as a
        # source line of code
        sloc += 1
        try:
            # Process a logical line that spans on multiple lines
            tokens, sloc_incr, multi_incr = _get_all_tokens(line, lines)
        except StopIteration:
            raise SyntaxError('SyntaxError at line: {0}'.format(lineno))
        # Update tracked metrics
        sloc += sloc_incr
        multi += multi_incr
        # Add the comments
        comments += list(map(TOKEN_NUMBER, tokens)).count(COMMENT)
        # Process a logical line
        # Split it on semicolons because they increase the number of logical
        # lines
        for sub_tokens in _split_tokens(tokens, OP, ';'):
            lloc += _logical(sub_tokens)
    return Module(loc, lloc, sloc, comments, multi, blank)
