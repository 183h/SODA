# SODA
Simulator of distributed algorithms

## Dependencies
SODA is developed under **python 3.5** version.

Python dependencies are listed in file **requirements.txt**. Dependencies are installed via **pip** with command:

`pip install -r /path/to/requirements.txt`

## Installation
SODA can be installed via **pip** with command, executed inside clonned repository:

`pip install -e .`

Afterwards it can be run in terminal via:

`soda`

## Usage
Run `soda --help`.


```
Usage: soda [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  lexalg    Run algorithm lexical analysis.
  lextop    Run topology lexical analysis.
  parsealg  Run algorithm parsing.
  parsetop  Run topology parsing.
  sim       Run simulation.
```
