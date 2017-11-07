import click
from soda.compiler.algorithm_lexer import AlgorithmLexer
from soda.compiler.algorithm_parser import AlgorithmParser
from soda.distributed_environment import behavior


@click.group()
@click.pass_context
def main(ctx):
    ctx.obj = {}
    ctx.obj['lexer'] = AlgorithmLexer()
    ctx.obj['lexer'].build()


@main.command(short_help='Run lexical analysis.')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def lex(ctx, filepath):
    '''
    Run lexical analysis.

        FILEPATH - path to file with algorithm description.
    '''

    ctx.obj['lexer'].lexical_analysis(filepath=filepath)


@main.command(short_help='Run parsing.')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def parse(ctx, filepath):
    '''
    Run parsing.

        FILEPATH - path to file with algorithm description.
    '''

    behavior_ = behavior.Behavior()
    parser_ = AlgorithmParser()

    parser_.build(ctx.obj['lexer'], behavior_)
    parser_.parsing(filepath=filepath)