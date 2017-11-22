import click
from soda.compiler.algorithm_lexer import AlgorithmLexer
from soda.compiler.algorithm_parser import AlgorithmParser
from soda.compiler.topology_lexer import TopologyLexer
from soda.compiler.topology_parser import TopologyParser
from soda.distributed_environment.algorithm_behavior import AlgorithmBehavior
from soda.distributed_environment.topology import Topology
from soda.simulator import Simulator


@click.group()
@click.pass_context
def main(ctx):
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

    behavior = AlgorithmBehavior()
    parser = AlgorithmParser()

    parser.build(ctx.obj['algorithm_lexer'], behavior)
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
@click.argument('ALGORITHM', type=click.Path(exists=True))
@click.argument('TOPOLOGY', type=click.Path(exists=True))
@click.pass_context
def sim(ctx, algorithm, topology):
    '''
    Run topology parsing.

        FILEPATH - path to file with topology description.
    '''

    algorithm_behavior = AlgorithmBehavior()
    algorithm_parser = AlgorithmParser()
    environment_topology = Topology()
    topology_parser = TopologyParser()

    algorithm_parser.build(ctx.obj['algorithm_lexer'], algorithm_behavior)
    algorithm_parser.parsing(filepath=algorithm)

    topology_parser.build(ctx.obj['topology_lexer'], environment_topology)
    topology_parser.parsing(filepath=topology)

    simulator = Simulator(algorithm_behavior, environment_topology)
    simulator.create_entities()

    # for e in simulator.entities:
    #     print (e.id, "\n", e.ip, "\n", e.in_port, "\n", e.out_port, "\n", e.state, "\n", e.behavior, "\n", e.neighbours)
    simulator.simulate()