import click
from compiler import lexer, parser


@click.group()
@click.pass_context
def main(ctx):
    ctx.obj = {}
    ctx.obj['lexer'] = lexer.Lexer()
    ctx.obj['parser'] = parser.Parser(ctx.obj['lexer'].tokens)


@main.command(short_help='run lexical analysis')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def lex(ctx, filepath):
    '''
    Run lexical analysis.

        FILEPATH - path to file with algorithm description.
    '''

    file = open(filepath, 'r')

    ctx.obj['lexer'].lexical_analysis(file)


@main.command(short_help='run parsing')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def parse(ctx, filepath):
    '''
    Run parsing.

        FILEPATH - path to file with algorithm description.
    '''

    file = open(filepath, 'r')

    ctx.obj['parser'].parsing(file)