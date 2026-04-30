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

# knapsack for optimal selection
def _run_dp(items, calorie_limit):
    n = len(items)
    C = calorie_limit

    a1 = []
    a2 = []
    for x in items:
        a1.append(int(round(x["calories"])))
        a2.append(x["health_score"])
    dp = []
    for i in range(n + 1):
        row = []
        for j in range(C + 1):
            row.append(0.0)
        dp.append(row)
    for i in range(1, n + 1):
        b1 = a1[i - 1]
        b2 = a2[i - 1]
        for c in range(C + 1):
            dp[i][c] = dp[i - 1][c]
            if b1 <= c:
                tmp = dp[i - 1][c - b1] + b2
                if tmp > dp[i][c]:
                    dp[i][c] = tmp
    var1 = []
    c = C
    i = n
    while i > 0:
        if dp[i][c] != dp[i - 1][c]:
            var1.append(i - 1)
            c = c - a1[i - 1]
        i = i - 1
    var1.reverse()
    return var1, dp[n][C]

#filtering item under budget & sugarconstraints
def apply_secondary_constraints(selected, profile):
    arr = list(selected)

    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[j]["health_score"] < arr[i]["health_score"]:
                arr[i], arr[j] = arr[j], arr[i]
    def chk(lst):
        s1 = 0
        s2 = 0
        for q in lst:
            s1 = s1 + q["cost_inr"]
            s2 = s2 + q["sugar_g"]
        if s1 <= profile.budget and s2 <= profile.max_sugar:
            return True
        return False
    while len(arr) > 0 and not chk(arr):
        arr.pop(0)
    return arr


# algo filling remaing or non completed constraints
def fill_remaining(selected, all_items, profile, fill_priority="calories"):
    MAX_SERVINGS = 3
    STOP_GAP = 50
    u1 = 0
    u2 = 0
    u3 = 0
    for z in selected:
        u1 = u1 + z["calories"]
        u2 = u2 + z["cost_inr"]
        u3 = u3 + z["sugar_g"]
    r1 = profile.calorie_limit - u1

    r2 = profile.budget - u2
    r3 = profile.max_sugar - u3
    arr = list(all_items)

    def keyfn(x):
        if fill_priority == "calories":
            return x["calories"]
        if fill_priority == "protein":
            return x["protein_g"]
        if fill_priority == "cost":
            return -x["cost_inr"]
        
        if fill_priority == "health_score":
            return x["health_score"]
        return x["calories"]

    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if keyfn(arr[j]) > keyfn(arr[i]):
                arr[i], arr[j] = arr[j], arr[i]
    cnts = {}
    for z in selected:
        nm = z["name"]
        if nm in cnts:
            cnts[nm] = cnts[nm] + 1

        else:
            cnts[nm] = 1
    out = list(selected)
    flag = True
    while flag == True and r1 > STOP_GAP:
        flag = False
        for it in arr:
            nm = it["name"]
            cur = cnts.get(nm, 0)
            if cur >= MAX_SERVINGS:
                continue
            if it["calories"] <= r1 and it["cost_inr"] <= r2 and it["sugar_g"] <= r3:
                out.append(it)
                cnts[nm] = cur + 1

                r1 = r1 - it["calories"]
                r2 = r2 - it["cost_inr"]
                r3 = r3 - it["sugar_g"]
                flag = True
                break
    return out

# return optimized plan
def run_dp(items, profile, fill_priority="calories"):
    tracemalloc.start()
    t1 = time.perf_counter()
    idx_list, raw_score = _run_dp(items, profile.calorie_limit)
    t2 = (time.perf_counter() - t1) * 1000
    _, m1 = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    m2 = m1 / 1024
    var1 = []

    for k in idx_list:
        var1.append(items[k])
    var1 = apply_secondary_constraints(var1, profile)

    var1 = fill_remaining(var1, items, profile, fill_priority)
    var2 = compute_totals(var1)
    s1 = 0.0
    for y in var1:
        s1 = s1 + y["health_score"]
    out = {}
    out["algorithm"] = "Dynamic Programming"
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
