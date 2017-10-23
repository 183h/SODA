import click
from soda.compiler import lexer, parser
from soda.distributed_environment import behavior


@click.group()
@click.pass_context
def main(ctx):
    ctx.obj = {}
    ctx.obj['lexer'] = lexer.Lexer()


@main.command(short_help='Run lexical analysis.')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def lex(ctx, filepath):
    '''
    Run lexical analysis.

        FILEPATH - path to file with algorithm description.
    '''

    file = open(filepath, 'r')

    ctx.obj['lexer'].lexical_analysis(file)


@main.command(short_help='Run parsing.')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def parse(ctx, filepath):
    '''
    Run parsing.

        FILEPATH - path to file with algorithm description.
    '''

    file = open(filepath, 'r')
    behavior_ = behavior.Behavior()
    parser_ = parser.Parser(ctx.obj['lexer'].tokens, behavior_)

    parser_.parsing(file)