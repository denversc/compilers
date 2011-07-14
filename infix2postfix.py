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

class TranslationError(Exception):
    """
    Exception raised when Translator.go() fails.
    """
    pass

################################################################################

class Translator:
    """
    A class that translates infix mathematical expressions to postfix.
    """

    def __init__(self, expression):
        """
        Initializes a new instance of Translator.
        *expression* must be a string to parse
        """
        self.expression = expression
        self.stream = iter(expression)
        self.result = io.StringIO()

    def go(self):
        """
        Parses this translator's expression and returns the translated result.
        Returns a string whose value is this translator's expression converted
        from infix notation to postfix notation.
        Raises TranslationError on error.
        """
        self.lookahead = next(self.stream, None)
        self.t_expr()
        if self.lookahead is not None:
            raise TranslationError('unexpected "%s"' % self.lookahead)
        return self.result.getvalue()

    def t_expr(self):
        self.t_term()
        self.t_rest()

    def t_rest(self):
        # The "rest" nonterminal is "tail-recursive", so recursive calls to
        # t_rest() are replaced with a "while" loop to increase performance
        while True:
            if self.lookahead == "+":
                self.lookahead = next(self.stream, None)
                self.t_term()
                self.result.write("+")
            elif self.lookahead == "-":
                self.lookahead = next(self.stream, None)
                self.t_term()
                self.result.write("-")
            else:
                break

    def t_term(self):
        if self.lookahead is None:
            raise TranslationError("expected term but reached end-of-input")
        elif self.lookahead == "0":
            self.result.write("0")
        elif self.lookahead == "1":
            self.result.write("1")
        elif self.lookahead == "2":
            self.result.write("2")
        elif self.lookahead == "3":
            self.result.write("3")
        elif self.lookahead == "4":
            self.result.write("4")
        elif self.lookahead == "5":
            self.result.write("5")
        elif self.lookahead == "6":
            self.result.write("6")
        elif self.lookahead == "7":
            self.result.write("7")
        elif self.lookahead == "8":
            self.result.write("8")
        elif self.lookahead == "9":
            self.result.write("9")
        else:
            raise TranslationError('expected term but found "%s"' % self.lookahead)

        self.lookahead = next(self.stream, None)

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
        translator = Translator(expression)
        try:
            translation = translator.go()
        except TranslationError as e:
            all_translations_successful = False
            print(" error: %s" % e)
        else:
            print(' "%s"' % translation)

    return 0 if all_translations_successful else 1

################################################################################

if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
