import click


@click.group()
def main():
    pass


@main.command()
@click.argument('FILEPATH', type=click.Path(exists=True))
def lexer(filepath):
    '''
    Run lexical analysis
    '''

    file = open(filepath, 'r')