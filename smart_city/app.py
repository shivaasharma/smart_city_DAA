from flask import Flask, jsonify, render_template, request
from algorithms import (build_city, bellman_ford, dijkstra,
                        random_graph, time_it)

app = Flask(__name__)
city = build_city()


@app.route("/")
def index():
    return render_template("index.html", locations=sorted(city.vertices()))


@app.route("/api/route", methods=["POST"])
def route():
    data = request.get_json()
    src, dst = data["source"], data["destination"]
    if src == dst:
        return jsonify(error="Choose two different locations."), 400
    result = {}
    for name, func in (("dijkstra", dijkstra), ("bellman_ford", bellman_ford)):
        dist, path, ms = time_it(func, city, src, dst, repeats=200)
        result[name] = {"distance": dist, "path": path, "time_ms": round(ms, 4)}
    return jsonify(result)


@app.route("/api/benchmark")
def benchmark():
    rows = []
    for n in (50, 100, 200, 400, 800):
        g = random_graph(n)
        _, _, d_ms = time_it(dijkstra, g, 0, n - 1)
        _, _, b_ms = time_it(bellman_ford, g, 0, n - 1)
        rows.append({"vertices": n,
                     "edges": len(g.edges()) // 2,
                     "dijkstra_ms": round(d_ms, 3),
                     "bellman_ms": round(b_ms, 3)})
    return jsonify(rows)


if __name__ == "__main__":
    app.run(debug=True)
