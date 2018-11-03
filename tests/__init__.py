import os
import sys

TESTS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(TESTS_DIR)

if ROOT_DIR:
    sys.path.append(ROOT_DIR)

    import layers
    import config
