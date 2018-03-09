import click
from soda.compiler.algorithm_lexer import AlgorithmLexer
from soda.compiler.algorithm_parser import AlgorithmParser
from soda.compiler.topology_lexer import TopologyLexer
from soda.compiler.topology_parser import TopologyParser
from soda.distributed_environment.algorithm import Algorithm
from soda.distributed_environment.topology import Topology
from soda.simulator import Simulator
from logging import basicConfig, INFO


@click.group()
@click.pass_context
def main(ctx):
    basicConfig(filename='simulation.log', filemode='w', level=INFO)

    ctx.obj = {}
    ctx.obj['algorithm_lexer'] = AlgorithmLexer()
    ctx.obj['algorithm_lexer'].build()
    ctx.obj['topology_lexer'] = TopologyLexer()
    ctx.obj['topology_lexer'].build()


@main.command(short_help='Run algorithm lexical analysis.')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def lexalg(ctx, filepath):
    '''
    Run algorithm lexical analysis.

        FILEPATH - path to file with algorithm description.
    '''

    ctx.obj['algorithm_lexer'].lexical_analysis(filepath=filepath)


@main.command(short_help='Run algorithm parsing.')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def parsealg(ctx, filepath):
    '''
    Run algorithm parsing.

        FILEPATH - path to file with algorithm description.
    '''

    algorithm = Algorithm()
    parser = AlgorithmParser()

    parser.build(ctx.obj['algorithm_lexer'], algorithm)
    parser.parsing(filepath=filepath)


@main.command(short_help='Run topology lexical analysis.')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def lextop(ctx, filepath):
    '''
    Run topology lexical analysis.

        FILEPATH - path to file with topology description.
    '''

    ctx.obj['topology_lexer'].lexical_analysis(filepath=filepath)


@main.command(short_help='Run topology parsing.')
@click.argument('FILEPATH', type=click.Path(exists=True))
@click.pass_context
def parsetop(ctx, filepath):
    '''
    Run topology parsing.

        FILEPATH - path to file with topology description.
    '''

    topology = Topology()
    parser = TopologyParser()

    parser.build(ctx.obj['topology_lexer'], topology)
    parser.parsing(filepath=filepath)


@main.command(short_help='Run simulation.')
@click.argument('ALGORITHM_FILE', type=click.Path(exists=True))
@click.argument('TOPOLOGY_FILE', type=click.Path(exists=True))
@click.pass_context
def sim(ctx, algorithm_file, topology_file):
    '''
    Compile algorithm, topology and start simulation.

        FILEPATH - path to file with topology description.
    '''

    algorithm = Algorithm()
    algorithm_parser = AlgorithmParser()
    topology = Topology()
    topology_parser = TopologyParser()

    algorithm_parser.build(ctx.obj['algorithm_lexer'], algorithm)
    algorithm_parser.parsing(filepath=algorithm_file)

    topology_parser.build(ctx.obj['topology_lexer'], topology)
    topology_parser.parsing(filepath=topology_file)

    simulator = Simulator(algorithm, topology)
    simulator.create_entities()
    simulator.simulate()