################################################################################
#
# infix2postfix.py
# By: Denver Coneybeare
# July 14, 2011
#
# An implementation of the infix-to-postfix syntax-directed translation scheme
# built up in chapter 2 of "Compilers: Principles, Techniques, and Tools" by
# Alfred V. Aho, Ravi Sethi, and Jeffery D. Ullman
#
################################################################################

import io
import sys

################################################################################

class Token:
    """
    A token returned from a lexical analyzer.
    """

    def __init__(self, id, value, offset):
        """
        Initializes a new instance of LexicalAnalyzer.
        *id* must be an integer whose value identifies the token type.
        *value* must be an object that represents the parsed value.
        *offset* must be an integer that represents the index of the first
        character of this token's lexeme from the input stream.
        """
        self.id = id
        self.value = value
        self.offset = offset

################################################################################

class LexicalAnalyzer:
    """
    Lexical analyzer that turns the input stream into tokens.
    """

    T_NUMBER = "T_NUMBER"
    T_PLUS = "T_PLUS"
    T_MINUS = "T_MINUS"
    T_LPAREN = "T_LPAREN"
    T_RPAREN = "T_RPAREN"

    DIGITS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
    WHITESPACE = (" ", "\t", "\n", "\r")

    def __init__(self, expression):
        """
        Initializes a new instance of LexicalAnalyzer.
        *expression* must be a string to parse.
        """
        self.stream = iter(expression)
        self.offset = 0
        self.buffer = None

    def __iter__(self):
        """
        Part of the iterator protocol.
        Unconditionally returns self.
        """
        return self

    def __next__(self):
        """
        Part of the iterator protocol.
        Returns the next token in the tuple (id, value).
        Raises StopIteration at end-of-input.
        Raises TranslationError if an invalid character is found.
        """
        while True:
            c = self._getchar()

            if c in self.DIGITS:
                out = io.StringIO()
                while c in self.DIGITS:
                    out.write(c)
                    try:
                        c = self._getchar()
                    except StopIteration:
                        break # end-of-input
                else:
                    self._ungetchar(c)

                value = out.getvalue()
                return Token(self.T_NUMBER, value, self.offset)

            elif c == "+":
                return Token(self.T_PLUS, c, self.offset)

            elif c == "-":
                return Token(self.T_MINUS, c, self.offset)

            elif c == "(":
                return Token(self.T_LPAREN, c, self.offset)

            elif c == ")":
                return Token(self.T_RPAREN, c, self.offset)

            elif c in self.WHITESPACE:
                pass # ignore whitespace

            else:
                raise TranslationError(self.offset, "invalid character: %s" % c)

    def _getchar(self):
        if self.buffer is not None:
            c = self.buffer
            self.buffer = None
        else:
            c = next(self.stream)

        self.offset += 1
        return c

    def _ungetchar(self, c):
        assert self.buffer is None
        self.buffer = c
        self.offset -= 1

################################################################################

class TranslationError(Exception):
    """
    Exception raised when Translator.go() fails.
    """

    def __init__(self, offset, *args, **kwargs):
        """
        Initializes a new instance of Translator.
        *offset* must be an integer that represents the index of the first
        character of the input where the error occurred.
        The remaining arguments are simply given to the constructor of the
        superclass.
        """
        Exception.__init__(self, *args, **kwargs)
        self.offset = offset

################################################################################

class Translator:
    """
    A class that translates infix mathematical expressions to postfix.
    """

    def __init__(self, tokens):
        """
        Initializes a new instance of Translator.
        *tokens* must be an iterator that returns Token objects to translate.
        """
        self.tokens = tokens
        self.result = io.StringIO()

    def go(self):
        """
        Parses this translator's token stream and returns the translated result.
        Returns a string whose value is this translator's token stream converted
        from infix notation to postfix notation.
        Raises TranslationError on error.
        """
        self.lookahead = next(self.tokens, None)
        self.t_expr()
        if self.lookahead is not None:
            raise TranslationError(self.tokens.offset,
                'extranuous characters: "%s"' % self.lookahead.value)
        return self.result.getvalue()

    def t_expr(self):
        self.t_factor()
        self.t_rest()

    def t_rest(self):
        # The "rest" nonterminal is "tail-recursive", so recursive calls to
        # t_rest() are replaced with a "while" loop to increase performance
        while True:
            if self.lookahead is None:
                break
            elif self.lookahead.id == self.tokens.T_PLUS:
                self.lookahead = next(self.tokens, None)
                self.t_factor()
                self.result.write("+ ")
            elif self.lookahead.id == self.tokens.T_MINUS:
                self.lookahead = next(self.tokens, None)
                self.t_factor()
                self.result.write("- ")
            else:
                break

    def t_factor(self):
        if self.lookahead is None:
            raise TranslationError(self.tokens.offset,
                "expected term but reached end-of-input")
        elif self.lookahead.id == self.tokens.T_LPAREN:
            self.lookahead = next(self.tokens, None)
            self.t_expr()
            if self.lookahead is None:
                raise TranslationError(self.tokens.offset,
                    "expected RPAREN but reached end-of-input")
            elif self.lookahead.id is not self.tokens.T_RPAREN:
                raise TranslationError(self.tokens.offset,
                    "expected RPAREN but got \"%s\"" % self.lookahead.value)
        elif self.lookahead.id == self.tokens.T_NUMBER:
            self.result.write("%s " % self.lookahead.value)
        else:
            raise TranslationError(self.tokens.offset,
                'expected term but found "%s"' % self.lookahead.value)

        self.lookahead = next(self.tokens, None)

################################################################################

def main(expressions):
    """
    The main entry point for the infix2postfix application.
    *expressions* must be an iterable of strings to be translated.
    Returns 0 if all of the given expressions were successfully translated;
    returns or 1 if at least one translation failed.
    """
    all_translations_successful = True

    for expression in expressions:
        print('"%s" ->' % expression, end="")
        lexer = LexicalAnalyzer(expression)
        translator = Translator(lexer)
        try:
            translation = translator.go()
        except TranslationError as e:
            all_translations_successful = False
            print(" error at %i: %s" % (e.offset, e.args[0]))
        else:
            print(' "%s"' % translation)

    return 0 if all_translations_successful else 1

################################################################################

if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
