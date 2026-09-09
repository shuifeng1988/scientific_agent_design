"""Task-local rounds; lifetime execution IDs and evidence never reset."""


def budget(state):
    return state.setdefault('budget', dict(round=1, worker_calls=state.get('planner_visits', 0),
                                          execution_base=0))


def execution_used(state):
    return state.get('attempt', 0) - budget(state)['execution_base']


def worker_limit(config, node):
    value = node.get('max_worker_calls_per_round', config.get('max_worker_calls_per_round', 3))
    if type(value) is not int or value < 1:
        raise ValueError('max_worker_calls_per_round must be a positive integer')
    return value
