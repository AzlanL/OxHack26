"""Exact lazy Work Function Algorithm for k servers in Euclidean R^2.

Only initial robot positions and observed request points are used as DP support.
When a new location appears, replay request history on the expanded support.
Intended for a small number of robots and requests.
"""
from __future__ import annotations
from dataclasses import dataclass
from itertools import combinations, permutations
from math import hypot, isfinite


Point = tuple[float, float]
State = tuple[Point, ...]


def point(p) -> Point:
    x, y = map(float, p)
    if not (isfinite(x) and isfinite(y)):
        raise ValueError('Coordinates must be finite')
    return x, y


def dist(a: Point, b: Point) -> float:
    return hypot(a[0] - b[0], a[1] - b[1])


def replace(state: State, old: Point, new: Point) -> State:
    return tuple(sorted((set(state) - {old}) | {new}))


def config_dist(a: State, b: State) -> float:
    # Min-cost matching, not sorted matching: sorted order fails in R^2.
    return min(sum(dist(x, y) for x, y in zip(a, p))
               for p in permutations(b))


@dataclass(frozen=True)
class Step:
    request: Point
    moved_from: Point | None
    moved_to: Point | None
    positions: State
    step_cost: float
    total_cost: float
    offline_optimum_so_far: float
    num_states: int


class WFA2D:
    def __init__(self, initial_positions):
        initial = tuple(sorted(point(p) for p in initial_positions))
        if not initial or len(set(initial)) != len(initial):
            raise ValueError('Use >=1 robots at distinct starting positions')
        self.initial = initial
        self.current = initial
        self.k = len(initial)
        self.history: list[Point] = []
        self.support = set(initial)
        self.total_cost = 0.0
        self.work = {initial: 0.0}

    def _rebuild_work(self):
        # Recompute from scratch because new points may introduce new states.
        states = list(combinations(sorted(self.support), self.k))
        work = {s: config_dist(self.initial, s) for s in states}
        for r in self.history:
            updated = {}
            for s in states:
                if r in s:
                    updated[s] = work[s]
                else:
                    updated[s] = min(
                        work[replace(s, x, r)] + dist(r, x)
                        for x in s
                    )
            work = updated
        self.work = work

    def serve(self, location) -> Step:
        r = point(location)
        self.history.append(r)
        self.support.add(r)
        self._rebuild_work()
        if r in self.current:
            next_state, old = self.current, None
            cost = 0.0
        else:
            next_state, old = min(
                ((replace(self.current, x, r), x) for x in self.current),
                key=lambda pair: (
                    self.work[pair[0]] + dist(pair[1], r), pair[0]
                )
            )
            cost = dist(old, r)
        self.current = next_state
        self.total_cost += cost
        return Step(r, old, r if old is not None else None,
                    self.current, cost, self.total_cost,
                    min(self.work.values()), len(self.work))

    @property
    def offline_optimum(self):
        return min(self.work.values())

    @property
    def competitive_bound(self):
        c = sum(dist(a, b) for a, b in combinations(self.initial, 2))
        return self.k * self.offline_optimum + c


if __name__ == '__main__':
    wfa = WFA2D([(0, 0), (5, 0), (2, 4)])
    for request in [(1, 1), (4, 2), (1, 1), (3, 3), (0, 2)]:
        step = wfa.serve(request)
        print(step)
    print('WFA:', round(wfa.total_cost, 3),
          'OPT:', round(wfa.offline_optimum, 3),
          'bound:', round(wfa.competitive_bound, 3))
