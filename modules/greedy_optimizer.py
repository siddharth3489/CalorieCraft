import time
import tracemalloc
def compute_totals(items):
    var1 = {"calories": 0, "cost": 0, "protein": 0, "sugar": 0, "fat": 0}
    for x in items:
        var1["calories"] = var1["calories"] + x["calories"]
        var1["cost"] = var1["cost"] + x["cost_inr"]
        var1["protein"] = var1["protein"] + x["protein_g"]
        var1["sugar"] = var1["sugar"] + x["sugar_g"]
        var1["fat"] = var1["fat"] + x["fat_g"]
    return var1
def check_constraints(totals, profile):
    var1 = {}
    var1["calorie_limit"] = totals["calories"] <= profile.calorie_limit
    var1["budget"] = totals["cost"] <= profile.budget
    var1["min_protein"] = totals["protein"] >= profile.min_protein
    var1["max_sugar"] = totals["sugar"] <= profile.max_sugar
    return var1


# decides ratio 
def ratio(item):
    if item["calories"] > 0:
        return item["health_score"] / item["calories"]
    return 0

# items maximizing score within constraint
def run_greedy(items, profile):
    tracemalloc.start()
    t1 = time.perf_counter()
    arr = list(items)
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if ratio(arr[j]) > ratio(arr[i]):
                arr[i], arr[j] = arr[j], arr[i]
    var1 = []
    a1 = profile.calorie_limit
    a2 = profile.budget
    a3 = 0.0
    for x in arr:
        b1 = x["calories"]
        b2 = x["cost_inr"]
        b3 = x["sugar_g"]
        if b1 <= a1 and b2 <= a2 and (a3 + b3) <= profile.max_sugar:
            var1.append(x)
            a1 = a1 - b1
            a2 = a2 - b2
            a3 = a3 + b3
    t2 = (time.perf_counter() - t1) * 1000
    _, m1 = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    m2 = m1 / 1024
    s1 = 0.0
    for y in var1:
        s1 = s1 + y["health_score"]
    var2 = compute_totals(var1)
    out = {}
    out["algorithm"] = "Greedy"
    out["selected_items"] = var1
    out["total_score"] = s1
    out["total_calories"] = var2["calories"]
    out["total_cost"] = var2["cost"]
    out["total_protein"] = var2["protein"]
    out["total_sugar"] = var2["sugar"]
    out["total_fat"] = var2["fat"]
    out["exec_time_ms"] = round(t2, 3)
    out["memory_kb"] = round(m2, 2)
    out["constraints_met"] = check_constraints(var2, profile)
    return out
_compute_totals = compute_totals
_check_constraints = check_constraints
