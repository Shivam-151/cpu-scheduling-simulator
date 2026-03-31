from metrics import (
    clone_processes,
    calculate_metrics,
    build_result_table,
    average,
    compress_gantt,
)


def fcfs(processes):
    procs = clone_processes(processes)
    procs.sort(key=lambda x: (x.arrival, x.pid))

    time = 0
    gantt = []

    for p in procs:
        if time < p.arrival:
            gantt.append(("Idle", time, p.arrival))
            time = p.arrival

        p.first_start = time
        start = time
        time += p.burst
        p.completion = time
        gantt.append((p.pid, start, time))

    calculate_metrics(procs)
    table = build_result_table(procs)

    return {
        "name": "FCFS",
        "gantt": compress_gantt(gantt),
        "table": table,
        "avg_waiting": average(table, "waiting"),
        "avg_turnaround": average(table, "turnaround"),
        "avg_response": average(table, "response"),
    }


def sjf_non_preemptive(processes):
    procs = clone_processes(processes)
    n = len(procs)
    completed = 0
    time = 0
    done = set()
    gantt = []

    while completed < n:
        ready = [p for p in procs if p.arrival <= time and p.pid not in done]

        if not ready:
            next_arrival = min(p.arrival for p in procs if p.pid not in done)
            gantt.append(("Idle", time, next_arrival))
            time = next_arrival
            continue

        current = min(ready, key=lambda x: (x.burst, x.arrival, x.pid))
        current.first_start = time
        start = time
        time += current.burst
        current.completion = time
        gantt.append((current.pid, start, time))

        done.add(current.pid)
        completed += 1

    calculate_metrics(procs)
    table = build_result_table(procs)

    return {
        "name": "SJF",
        "gantt": compress_gantt(gantt),
        "table": table,
        "avg_waiting": average(table, "waiting"),
        "avg_turnaround": average(table, "turnaround"),
        "avg_response": average(table, "response"),
    }


def priority_non_preemptive(processes):
    procs = clone_processes(processes)
    n = len(procs)
    completed = 0
    time = 0
    done = set()
    gantt = []

    while completed < n:
        ready = [p for p in procs if p.arrival <= time and p.pid not in done]

        if not ready:
            next_arrival = min(p.arrival for p in procs if p.pid not in done)
            gantt.append(("Idle", time, next_arrival))
            time = next_arrival
            continue

        current = min(ready, key=lambda x: (x.priority, x.arrival, x.pid))
        current.first_start = time
        start = time
        time += current.burst
        current.completion = time
        gantt.append((current.pid, start, time))

        done.add(current.pid)
        completed += 1

    calculate_metrics(procs)
    table = build_result_table(procs)

    return {
        "name": "Priority",
        "gantt": compress_gantt(gantt),
        "table": table,
        "avg_waiting": average(table, "waiting"),
        "avg_turnaround": average(table, "turnaround"),
        "avg_response": average(table, "response"),
    }


def round_robin(processes, quantum):
    if quantum <= 0:
        raise ValueError("Time quantum must be greater than 0.")

    procs = clone_processes(processes)
    procs.sort(key=lambda x: (x.arrival, x.pid))

    n = len(procs)
    time = 0
    index = 0
    completed = 0
    ready_queue = []
    gantt = []

    while completed < n:
        while index < n and procs[index].arrival <= time:
            ready_queue.append(procs[index])
            index += 1

        if not ready_queue:
            if index < n:
                next_arrival = procs[index].arrival
                gantt.append(("Idle", time, next_arrival))
                time = next_arrival
                continue
            else:
                break

        current = ready_queue.pop(0)

        if current.first_start is None:
            current.first_start = time

        run_time = min(quantum, current.remaining)
        start = time
        time += run_time
        current.remaining -= run_time
        gantt.append((current.pid, start, time))

        while index < n and procs[index].arrival <= time:
            ready_queue.append(procs[index])
            index += 1

        if current.remaining > 0:
            ready_queue.append(current)
        else:
            current.completion = time
            completed += 1

    calculate_metrics(procs)
    table = build_result_table(procs)

    return {
        "name": "Round Robin",
        "gantt": compress_gantt(gantt),
        "table": table,
        "avg_waiting": average(table, "waiting"),
        "avg_turnaround": average(table, "turnaround"),
        "avg_response": average(table, "response"),
    }