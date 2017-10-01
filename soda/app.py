import click
from compiler import lexer, parser

pass_lexer = click.make_pass_decorator(lexer.Lexer, ensure=True)


@click.group()
def main():
    pass

@main.command(short_help='run lexical analysis')
@click.argument('FILEPATH', type=click.Path(exists=True))
@pass_lexer
def lex(lexer, filepath):
    '''
    Run lexical analysis.
    '''

    file = open(filepath, 'r')

    lexer.lexical_analysis(file)

@main.command(short_help='run parsing')
@click.argument('FILEPATH', type=click.Path(exists=True))
def parse(filepath):
    '''
    Run parsing.
    '''

    pass