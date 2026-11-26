"""Shortest path algorithms for the Smart City Route Optimization System.

The city is a graph:
  - locations  -> vertices
  - roads      -> weighted edges (weight = distance in km)
Roads are two-way, so every road is stored in both directions.
"""
import heapq
import random
import time


class Graph:
    def __init__(self):
        self.adj = {}  # vertex -> list of (neighbour, weight)

    def add_vertex(self, v):
        self.adj.setdefault(v, [])

    def add_road(self, u, v, w):
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj[u].append((v, w))
        self.adj[v].append((u, w))

    def vertices(self):
        return list(self.adj)

    def edges(self):
        """All directed edges (u, v, w) - used by Bellman-Ford."""
        return [(u, v, w) for u in self.adj for v, w in self.adj[u]]


def build_path(parent, source, target):
    path, node = [], target
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()
    return path if path and path[0] == source else []


def dijkstra(graph, source, target):
    """Dijkstra with a min-heap. Time: O((V + E) log V)."""
    dist = {v: float("inf") for v in graph.adj}
    parent = {v: None for v in graph.adj}
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        if u == target:
            break
        for v, w in graph.adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                parent[v] = u
                heapq.heappush(heap, (dist[v], v))
    return dist[target], build_path(parent, source, target)


def bellman_ford(graph, source, target):
    """Bellman-Ford. Time: O(V * E). Stops early if nothing changes."""
    dist = {v: float("inf") for v in graph.adj}
    parent = {v: None for v in graph.adj}
    dist[source] = 0
    edges = graph.edges()
    for _ in range(len(graph.adj) - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
        if not changed:
            break
    return dist[target], build_path(parent, source, target)


def time_it(func, graph, source, target, repeats=3):
    """Run an algorithm a few times, return (distance, path, avg ms)."""
    total = 0
    for _ in range(repeats):
        start = time.perf_counter()
        distance, path = func(graph, source, target)
        total += time.perf_counter() - start
    return distance, path, total / repeats * 1000


# ---------- sample city used on the main page ----------
CITY_ROADS = [
    ("Central Station", "City Hall", 2), ("Central Station", "Market Square", 4),
    ("City Hall", "Market Square", 1), ("City Hall", "University", 5),
    ("Market Square", "Hospital", 7), ("Market Square", "Old Town", 3),
    ("University", "Library", 2), ("University", "Tech Park", 6),
    ("Hospital", "Airport", 8), ("Old Town", "Hospital", 3),
    ("Old Town", "Stadium", 5), ("Library", "Tech Park", 3),
    ("Tech Park", "Airport", 9), ("Stadium", "Airport", 4),
    ("Stadium", "Tech Park", 7),
]


def build_city():
    g = Graph()
    for u, v, w in CITY_ROADS:
        g.add_road(u, v, w)
    return g


# ---------- random graphs for the performance comparison ----------
def random_graph(n, edges_per_vertex=4, seed=1):
    rng = random.Random(seed)
    g = Graph()
    for i in range(n):
        g.add_vertex(i)
    for i in range(1, n):                      # chain keeps graph connected
        g.add_road(i - 1, i, rng.randint(1, 20))
    for _ in range(n * (edges_per_vertex - 1)):  # extra random roads
        u, v = rng.randrange(n), rng.randrange(n)
        if u != v:
            g.add_road(u, v, rng.randint(1, 20))
    return g
