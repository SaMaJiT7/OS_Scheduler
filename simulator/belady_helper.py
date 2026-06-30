def build_next_occurrence(trace):
    n = len(trace)
    pages = set(trace)
    next_occurrence = {pid: [None] * n for pid in pages}

    for pid in pages:
        next_seen = None
        for i in range(n - 1, -1, -1):
            if trace[i] == pid:
                next_seen = i
            next_occurrence[pid][i] = next_seen

    return next_occurrence
