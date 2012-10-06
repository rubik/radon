from paramunittest import *
from radon.metrics import *


COMPUTE_MI_CASES = [
    ((0, 0, 0, 0), 0),
    ((0, 1, 2, 0), ),
    ((10, 2, 5, .5), ),
    ((200, 10, 78, 45), ),
