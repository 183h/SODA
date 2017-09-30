import click


@click.group()
def main():
    pass


@main.command()
def lexer():
    '''
    Run lexical analysis
    '''
    pass