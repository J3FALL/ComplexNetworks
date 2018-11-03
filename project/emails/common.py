import os
from typing import Iterable

ROOT_FOLDER = os.path.dirname(os.path.dirname(__file__))

FIGURES_FOLDER = os.path.join(ROOT_FOLDER, 'figures')
DATA_FOLDER = os.path.join(ROOT_FOLDER, 'data')

GRAPH_PATH = os.path.join(DATA_FOLDER, 'emails.txt')
EXTENDED_BA_PATH = os.path.join(DATA_FOLDER, 'extended_ba.csv')
REDUCED_GRAPH_PATH = os.path.join(DATA_FOLDER, 'reduced_graph.csv')
GEPHI_METRICS = os.path.join(DATA_FOLDER, 'gephi_metrics.csv')

ROBUSTNESS_FOLDER = os.path.join(DATA_FOLDER, 'robustness')
ROBUSTNESS_ATTACK_FOLDER = os.path.join(ROBUSTNESS_FOLDER, 'attack')
ROBUSTNESS_FAIL_FOLDER = os.path.join(ROBUSTNESS_FOLDER, 'fail')

ROBUSTNESS_ATTACK_HISTORY = os.path.join(ROBUSTNESS_ATTACK_FOLDER, 'attack_history.txt')
ROBUSTNESS_FAIL_HISTORY = os.path.join(ROBUSTNESS_FAIL_FOLDER, 'fail_history.txt')

SIR_FOLDER = os.path.join(DATA_FOLDER, 'sir')


def join_values(values: Iterable, sep: str = ' ') -> str:
    return sep.join([str(val) for val in values])
