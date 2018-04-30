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
@click.option('--log-name', type=click.Path(), default='simulation', help='Name of file for log output. Deafult is simulation.log.')
def main(ctx, log_name):
    basicConfig(filename=log_name + '.log', filemode='w', level=INFO)

    ctx.obj = {}
    ctx.obj['algorithm_lexer'] = AlgorithmLexer()
    ctx.obj['algorithm_lexer'].build()
    ctx.obj['topology_lexer'] = TopologyLexer()
    ctx.obj['topology_lexer'].build()


@main.command(short_help='Run algorithm lexical analysis.')
@click.argument('ALGORITHM_FILE', type=click.Path(exists=True))
@click.pass_context
def lexalg(ctx, algorithm_file):
    '''
    Run algorithm lexical analysis.

        ALGORITHM_FILE - path to file with algorithm description.
    '''

    ctx.obj['algorithm_lexer'].lexical_analysis(filepath=algorithm_file)


@main.command(short_help='Run algorithm parsing.')
@click.argument('ALGORITHM_FILE', type=click.Path(exists=True))
@click.pass_context
def parsealg(ctx, algorithm_file):
    '''
    Run algorithm parsing.

        ALGORITHM_FILE - path to file with algorithm description.
    '''

    algorithm = Algorithm()
    parser = AlgorithmParser()

    parser.build(ctx.obj['algorithm_lexer'], algorithm)
    parser.parsing(filepath=algorithm_file)


@main.command(short_help='Run topology lexical analysis.')
@click.argument('TOPOLOGY_FILE', type=click.Path(exists=True))
@click.pass_context
def lextop(ctx, topology_file):
    '''
    Run topology lexical analysis.

        TOPOLOGY_FILE - path to file with topology description.
    '''

    ctx.obj['topology_lexer'].lexical_analysis(filepath=topology_file)


@main.command(short_help='Run topology parsing.')
@click.argument('TOPOLOGY_FILE', type=click.Path(exists=True))
@click.pass_context
def parsetop(ctx, topology_file):
    '''
    Run topology parsing.

        TOPOLOGY_FILE - path to file with topology description.
    '''

    topology = Topology()
    parser = TopologyParser()

    parser.build(ctx.obj['topology_lexer'], topology)
    parser.parsing(filepath=topology_file)


@main.command(short_help='Run simulation.')
# Pomocou dekorátorov argument, option definujeme povinné argumenty a
# voliteľné nastavenia príkazu. Argument algorithm_file slúži pre vstupný súbor s
# opisom algoritmu a argument topology_file slúži pre vstupný súbor s opisom
# topológie.
@click.argument('ALGORITHM_FILE', type=click.Path(exists=True))
@click.argument('TOPOLOGY_FILE', type=click.Path(exists=True))
@click.option('--no-di', is_flag=True, help='Disable Deadlock Inspector.')
@click.option('--count-impulses', default=1, help='Number of impulses.')
@click.pass_context
def sim(ctx, algorithm_file, topology_file, no_di, count_impulses):
    '''
    Compile algorithm, topology and start simulation.

        ALGORITHM_FILE - path to file with algorithm description.
        TOPOLOGY_FILE - path to file with topology description.
    '''

    algorithm = Algorithm() # Vytvorenie dátovej štruktúry pre opis algoritmu.
    algorithm_parser = AlgorithmParser()

    topology = Topology() # Vytvorenie dátovej štruktúry pre opis topológie.
    topology_parser = TopologyParser()

    # Syntaktická analýza algoritmu a topológie.
    algorithm_parser.build(ctx.obj['algorithm_lexer'], algorithm)
    algorithm_parser.parsing(filepath=algorithm_file)
    topology_parser.build(ctx.obj['topology_lexer'], topology)
    topology_parser.parsing(filepath=topology_file)

    # Vytvorenie entít a spustenie simulácie.
    simulator = Simulator(algorithm, topology)
    simulator.create_entities(count_impulses)
    simulator.simulate(no_di)