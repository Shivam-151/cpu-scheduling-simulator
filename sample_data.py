from models import Process


def get_sample_processes():
    return [
        Process("P1", 0, 5, 2),
        Process("P2", 1, 3, 1),
        Process("P3", 2, 8, 4),
        Process("P4", 3, 6, 3),
    ]