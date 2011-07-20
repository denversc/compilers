################################################################################
#
# infix2postfix2.py
# By: Denver Coneybeare
# July 20, 2011
#
# An implementation of the infix-to-postfix syntax-directed translation scheme
# culminated at the end of chapter 2 of "Compilers: Principles, Techniques, and
# Tools" by Alfred V. Aho, Ravi Sethi, and Jeffery D. Ullman
#
################################################################################

import io
import sys

################################################################################

class CharacterIterator:
    """
    An iterator that allows pushing back a value.
    """

    def __init__(self, s):
        """
        Initializes a new instance of this class.
        *s* must be an iterable object, valid for being specified to iter(),
        such as a string or list.
        """
        self.iter = iter(s)
        self._pushback = None

    def pushback(self, c):
        """
        Pushes an object back to this iterator such that it will be returned as
        the next element.  The push back buffer can only store one object;
        therefore, this method must only be invoked when the pushback buffer is
        empty.
        *c* is the object to push back; may be any object other than None.
        """
        assert c is not None
        assert self._pushback is None
        self._pushback = c

    def __iter__(self):
        return self

    def __next__(self):
        if self._pushback is not None:
            pushback = self._pushback
            self._pushback = None
            return pushback
        else:
            return next(self.iter)

################################################################################

class ParseException(Exception):
    """
    Exception raised when a parsing error occurs.
    """
    pass

################################################################################

class Token:
    """
    Represents a token generated by instances of Lexer.
    """

    def __init__(self, id, lexeme):
        """
        Initializes a new instance of this class.
        *id* is the ID to assign to this token to identify the type of token,
        such as an "identifier" or "operator".
        *lexeme* must be a string whose value is the sequence of characters
        read from the input stream that were read to form this token
        """
        self.id = id
        self.lexeme = lexeme

################################################################################

class Lexer:
    """
    The lexical analyzer for parsing infix expressions.
    This class acts as an iterator and therefore should be used directly in a
    looping construct, such as a "for" loop.  The iterator returns Token
    objects and raises ParseException if an unrecognized character is found.

    This class defines many T_ values which are used as the "id" of generated
    tokens.

    This class has int attributes "lineno" and "linecol" which are the line
    number and column within the current line, respectively, of the
    most-recently-read character.
    """

    T_EOF = "eof"
    T_ADD = "+"
    T_SUBTRACT = "-"
    T_MULTIPLY = "*"
    T_DIVIDE = "/"
    T_MODULO = "mod"
    T_INTDIVIDE = "div"
    T_NUMBER = "number"
    T_ID = "id"
    T_LPAREN = "LPAREN"
    T_RPAREN = "RPAREN"
    T_EXPR_SEP = "EXPR_SEP"

    def __init__(self, f):
        """
        Initializes a new instance of this class.
        *f* must be the stream to parse, such as a file; technically, this can
        be any iterator that generates strings, such as a list of strings.
        """
        self.f = f
        self.lineno = 0
        self.linecol = 0

        predefined_tokens = (
            Token(self.T_MODULO, "mod"),
            Token(self.T_INTDIVIDE, "div"),
        )

        self.symbol_table = {x.lexeme: x for x in predefined_tokens}

    def __iter__(self):
        for line in self.f:
            self.lineno += 1
            self.linecol = 0

            chars = CharacterIterator(line)
            for c in chars:
                self.linecol += 1

                if c.isspace():
                    pass # skip whitespace
                elif c == "+":
                    yield Token(self.T_ADD, c)
                elif c == "-":
                    yield Token(self.T_SUBTRACT, c)
                elif c == "*":
                    yield Token(self.T_MULTIPLY, c)
                elif c == "/":
                    yield Token(self.T_DIVIDE, c)
                elif c == ")":
                    yield Token(self.T_LPAREN, c)
                elif c == "(":
                    yield Token(self.T_RPAREN, c)
                elif c == ";":
                    yield Token(self.T_EXPR_SEP, c)

                elif c.isdigit():
                    buf = io.StringIO()
                    buf.write(c)
                    for c in chars:
                        if c.isdigit():
                            buf.write(c)
                        else:
                            chars.pushback(c)
                            break
                    lexeme = buf.getvalue()
                    yield Token(self.T_NUMBER, lexeme)

                elif c.isalpha():
                    buf = io.StringIO()
                    buf.write(c)
                    for c in chars:
                        if c.isalpha() or c.isdigit():
                            buf.write(c)
                        else:
                            chars.pushback(c)
                            break

                    lexeme = buf.getvalue()

                    if lexeme in self.symbol_table:
                        token = self.symbol_table[lexeme]
                    else:
                        token = Token(self.T_ID, lexeme)
                        self.symbol_table[lexeme] = token

                    yield token
                else:
                    raise ParseException("invalid character: %s" % c)

            yield Token(self.T_EOF, None)

################################################################################

def main():
    """
    The main method.
    Returns 0 on success, 1 on failure
    """
    lexer = Lexer(sys.stdin)
    try:
        for token in lexer:
            print("Token(id=%s lexeme=%s)" % (token.id, token.lexeme))
    except ParseException as e:
        print("ERROR: at line %i column %i: %s" %
            (lexer.lineno, lexer.linecol, e))
        return 1

    return 0

################################################################################

if __name__ == "__main__":
    exitcode = main()
    sys.exit(exitcode)
