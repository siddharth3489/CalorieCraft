import time
import tracemalloc
import plotly.graph_objects as go
from modules.dp_optimizer import run_dp, _run_dp
from modules.greedy_optimizer import run_greedy
def compare(items, profile, fill_priority="calories"):
    r1 = run_dp(items, profile, fill_priority=fill_priority)
    r2 = run_greedy(items, profile)
    s1 = r1["total_score"]
    s2 = r2["total_score"]
    if s1 > 0:
        gap = (s1 - s2) / s1 * 100
    else:
        gap = 0.0
    set1 = set()
    for x in r1["selected_items"]:
        set1.add(x["name"])
    set2 = set()
    for x in r2["selected_items"]:
        set2.add(x["name"])
    a = list(set1 - set2)
    a.sort()
    b = list(set2 - set1)
    b.sort()
    c = list(set1 & set2)
    c.sort()

    out = {}
    out["dp"] = r1
    out["greedy"] = r2
    out["accuracy_gap_pct"] = round(gap, 2)
    out["only_in_dp"] = a
    out["only_in_greedy"] = b
    out["common_items"] = c
    return out



def _time_dp(items, calorie_limit):
    tracemalloc.start()
    t1 = time.perf_counter()
    _run_dp(items, calorie_limit)
    t2 = (time.perf_counter() - t1) * 1000
    _, m1 = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return round(t2, 3), round(m1 / 1024, 2)
def _time_greedy(items, profile):
    tracemalloc.start()
    t1 = time.perf_counter()


    arr = list(items)
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            ri = 0
            rj = 0
            if arr[i]["calories"] > 0:
                ri = arr[i]["health_score"] / arr[i]["calories"]
            if arr[j]["calories"] > 0:
                rj = arr[j]["health_score"] / arr[j]["calories"]
            if rj > ri:
                arr[i], arr[j] = arr[j], arr[i]
    rem = profile.calorie_limit
    for x in arr:
        if x["calories"] <= rem:
            rem = rem - x["calories"]
    t2 = (time.perf_counter() - t1) * 1000
    _, m1 = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return round(t2, 3), round(m1 / 1024, 2)

def benchmark_scalability(all_items, profile, sizes=None):
    if sizes is None:
        sizes = [20, 50, 100, 200]
    out = []
    for n in sizes:
        sub = all_items[:n]
        a1, a2 = _time_dp(sub, profile.calorie_limit)
        b1, b2 = _time_greedy(sub, profile)
        d1 = run_dp(sub, profile)
        d2 = run_greedy(sub, profile)
        row = {}
        row["n"] = n
        row["dp_time_ms"] = a1
        row["greedy_time_ms"] = b1

        row["dp_memory_kb"] = a2
        row["greedy_memory_kb"] = b2
        row["dp_score"] = round(d1["total_score"], 3)
        row["greedy_score"] = round(d2["total_score"], 3)
        out.append(row)
    return out



def plot_time_vs_size(benchmark_data):
    a = []
    b = []
    c = []
    for d in benchmark_data:
        a.append(d["n"])
        b.append(d["dp_time_ms"])
        c.append(d["greedy_time_ms"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a, y=b, mode="lines+markers", name="DP", line=dict(color="#636EFA", width=2)))
    fig.add_trace(go.Scatter(x=a, y=c, mode="lines+markers", name="Greedy", line=dict(color="#EF553B", width=2)))
    fig.update_layout(title="Execution Time vs Dataset Size", xaxis_title="Number of Food Items (n)", yaxis_title="Time (ms)", legend=dict(x=0.01, y=0.99), template="plotly_white")
    return fig

def plot_memory_vs_size(benchmark_data):
    a = []
    b = []
    c = []
    for d in benchmark_data:
        a.append(d["n"])
        b.append(d["dp_memory_kb"])
        c.append(d["greedy_memory_kb"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=a, y=b, mode="lines+markers", name="DP", line=dict(color="#636EFA", width=2)))
    fig.add_trace(go.Scatter(x=a, y=c, mode="lines+markers", name="Greedy", line=dict(color="#EF553B", width=2)))
    fig.update_layout(title="Memory Usage vs Dataset Size", xaxis_title="Number of Food Items (n)", yaxis_title="Peak Memory (KB)", legend=dict(x=0.01, y=0.99), template="plotly_white")
    return fig



def plot_score_comparison(dp_result, greedy_result):
    fig = go.Figure(go.Bar(
        x=["Dynamic Programming", "Greedy"],
        y=[dp_result["total_score"], greedy_result["total_score"]],
        marker_color=["#636EFA", "#EF553B"],
        text=[str(round(dp_result["total_score"], 3)), str(round(greedy_result["total_score"], 3))],
        textposition="outside",
    ))
    fig.update_layout(title="Health Score Comparison: DP vs Greedy", yaxis_title="Total Health Score", template="plotly_white", showlegend=False)
    return fig
