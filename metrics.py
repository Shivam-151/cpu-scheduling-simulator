import copy


def clone_processes(processes):
    return [copy.deepcopy(p) for p in processes]


def calculate_metrics(processes):
    for p in processes:
        p.turnaround = p.completion - p.arrival
        p.waiting = p.turnaround - p.burst
        p.response = (p.first_start - p.arrival) if p.first_start is not None else 0


def average(rows, key):
    if not rows:
        return 0
    return round(sum(row[key] for row in rows) / len(rows), 2)


def build_result_table(processes):
    processes = sorted(
        processes,
        key=lambda x: int(x.pid[1:]) if x.pid[1:].isdigit() else x.pid
    )

    return [
        {
            "pid": p.pid,
            "arrival": p.arrival,
            "burst": p.burst,
            "priority": p.priority,
            "completion": p.completion,
            "turnaround": p.turnaround,
            "waiting": p.waiting,
            "response": p.response,
        }
        for p in processes
    ]


def compress_gantt(gantt):
    if not gantt:
        return []

    merged = [gantt[0]]
    for pid, start, end in gantt[1:]:
        last_pid, last_start, last_end = merged[-1]
        if pid == last_pid and start == last_end:
            merged[-1] = (last_pid, last_start, end)
        else:
            merged.append((pid, start, end))
    return merged