import click
from compiler import lexer


@click.group()
def main():
    pass


@main.command(short_help='run lexical analysis')
@click.argument('FILEPATH', type=click.Path(exists=True))
def lex(filepath):
    '''
    Run lexical analysis.
    '''

    file = open(filepath, 'r')
    lex = lexer.Lexer()

    lex.lexical_analysis(file)