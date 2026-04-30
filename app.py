import io
import datetime
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modules.user_profile import build_profile
from modules.food_loader import load_foods, get_all_food_names
from modules.analyzer import compare
from modules.auth import register, login




st.set_page_config(page_title="CalorieCraft", layout="wide")
# session states
if "results" not in st.session_state:
    st.session_state["results"] = None
if "profile" not in st.session_state:
    st.session_state["profile"] = None
if "items" not in st.session_state:
    st.session_state["items"] = None
if "plan_history" not in st.session_state:
    st.session_state["plan_history"] = []
if "skip_meals" not in st.session_state:
    st.session_state["skip_meals"] = {"Breakfast": False, "Lunch": False, "Dinner": False}
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None



def goal_label(x):
    if x == "weight_loss":
        return "Weight Loss — Reduce calories & sugar"
    if x == "muscle_gain":
        return "Muscle Gain — Maximize protein intake"
    return "Balanced — Equal focus on all nutrients"

def fill_label(x):
    if x == "calories":
        return "Calories — hit your calorie target"
    if x == "protein":
        return "Protein — maximize protein intake"
    if x == "cost":
        return "Cost — prefer cheaper items"
    return "Health Score — most nutritious first"


#user login and registration interface
if st.session_state["logged_in"] == False:
    st.title("Welcome to CalorieCraft")
    st.caption("Personalized Meal Planning & Food Tracking")
    st.markdown("---")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        st.subheader("Login")
        v1 = st.text_input("Username", key="login_user")
        v2 = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", type="primary", use_container_width=True):
            ok, msg = login(v1, v2)
            if ok == True:
                st.session_state["logged_in"] = True
                st.session_state["username"] = v1.strip().lower()
                st.rerun()
            else:
                st.error(msg)
    with tab2:
        st.subheader("Create Account")
        v3 = st.text_input("Choose a username", key="reg_user")
        v4 = st.text_input("Choose a password", type="password", key="reg_pass")
        v5 = st.text_input("Confirm password", type="password", key="reg_pass2")
        if st.button("Register", use_container_width=True):
            if v4 != v5:
                st.error("Passwords do not match.")
            else:
                ok, msg = register(v3, v4)
                if ok == True:
                    st.success(msg + " You can now login.")
                else:
                    st.error(msg)
    st.stop()


#main app code
st.sidebar.title("CalorieCraft")
st.sidebar.caption("Logged in as **" + str(st.session_state["username"]) + "**")
if st.sidebar.button("Logout"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.rerun()
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigate", ["User Profile", "Meal Plan Results", "Plan History"], index=0)
if page == "User Profile":
    st.title("Step 1 — Set Your Dietary Goals")
    st.markdown("Welcome to **CalorieCraft**! Fill in your constraints below, then click **Run Optimization** to get your personalized meal plan.")
    st.markdown("---")
    with st.expander(" TDEE Calculator (auto-suggest calorie limit)", expanded=False):
        st.markdown("Uses the **Mifflin-St Jeor** formula to estimate your Total Daily Energy Expenditure.")
        c1, c2 = st.columns(2)
        with c1:
            x1 = st.selectbox("Gender", ["Male", "Female"])
            x2 = st.number_input("Age (years)", min_value=10, max_value=100, value=25)
            x3 = st.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.5)
        with c2:
            x4 = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
            x5 = st.selectbox("Activity Level", [
                "Sedentary (desk job)",
                "Lightly Active (1-3 days/week)",
                "Moderately Active (3-5 days/week)",
                "Very Active (6-7 days/week)",
                "Extra Active (athlete)",
            ])
        if x5 == "Sedentary (desk job)":
            mm = 1.2
        elif x5 == "Lightly Active (1-3 days/week)":
            mm = 1.375
        elif x5 == "Moderately Active (3-5 days/week)":
            mm = 1.55
        elif x5 == "Very Active (6-7 days/week)":
            mm = 1.725
        else:
            mm = 1.9
        if x1 == "Male":
            bmr = 10 * x3 + 6.25 * x4 - 5 * x2 + 5
        else:
            bmr = 10 * x3 + 6.25 * x4 - 5 * x2 - 161
        tdee = int(bmr * mm)
        st.metric("Estimated TDEE", str(tdee) + " kcal/day")
        if st.button("Use this as my calorie limit"):
            st.session_state["suggested_calories"] = tdee
            st.success("Calorie limit set to " + str(tdee) + " kcal. See it applied below.")
    st.markdown("---")
    col1, col2 = st.columns(2)


    with col1:
        st.subheader("Dietary Goal")
        var1 = st.selectbox(
            "What is your goal?",
            options=["weight_loss", "muscle_gain", "balanced"],
            format_func=goal_label,
        )
        st.subheader("Calorie & Budget Limits")
        if "suggested_calories" in st.session_state:
            tmp1 = st.session_state["suggested_calories"]
        else:
            tmp1 = 2000
        if tmp1 > 3500:
            tmp1 = 3500
        var2 = st.slider("Daily calorie limit (kcal)", min_value=800, max_value=3500, value=tmp1, step=50)
        var3 = st.number_input("Daily food budget (Rs.)", min_value=50, max_value=2000, value=500, step=10)

        st.subheader("Diet Type")
        var4 = st.toggle("Vegetarian only ", value=False)
    with col2:
        st.subheader("Nutrition Constraints")
        var5 = st.number_input("Minimum protein required (g)", min_value=0, max_value=200, value=50, step=5)
        var6 = st.number_input("Maximum sugar allowed (g)", min_value=10, max_value=300, value=80, step=5)

        st.subheader("Fill Priority")
        st.caption("When filling up to your calorie target, prefer items that score highest on:")
        var7 = st.selectbox(
            "Fill priority",
            options=["calories", "protein", "cost", "health_score"],
            format_func=fill_label,
            label_visibility="collapsed",
        )
        st.subheader("Auto-assigned Weights")
        st.caption("Based on your goal:  \n`health_score = w1·protein − w2·sugar − w3·fat`")
        pp = build_profile(var1, var2, var3, var5, var6)
        rrr = {"Goal": pp.goal_label, "w1 (protein)": pp.w1, "w2 (sugar)": pp.w2, "w3 (fat)": pp.w3}
        st.dataframe(pd.DataFrame([rrr]), use_container_width=True, hide_index=True)
    st.markdown("---")
    st.subheader("Skip Meals")
    st.caption("Toggle off any meal you don't want included in today's plan.")
    s1, s2, s3 = st.columns(3)
    sk1 = not s1.toggle("🌅 Breakfast", value=True)
    sk2 = not s2.toggle("☀️ Lunch", value=True)
    sk3 = not s3.toggle("🌙 Dinner", value=True)
    if sk1 and sk2 and sk3:
        st.warning("You've skipped all meals — at least one must be active.")
        sk1 = False
        sk2 = False
        sk3 = False
    st.markdown("---")
    with st.expander("-X- Food Exclusions (allergies / dislikes)", expanded=False):
        nn = get_all_food_names()
        ex = st.multiselect("Select foods to exclude from your plan:", options=nn, placeholder="Type to search...")
    st.markdown("---")


    if st.button("Run Optimization", type="primary", use_container_width=True):
        with st.spinner("Loading food data and generating your meal plan..."):
            prof = build_profile(var1, var2, var3, var5, var6)
            if var4 == True:
                f1 = True
            else:
                f1 = None
            if len(ex) > 0:
                f2 = ex
            else:
                f2 = None
            it1 = load_foods(prof.w1, prof.w2, prof.w3, veg_only=f1, excluded_names=f2)
            res = compare(it1, prof, fill_priority=var7)
            st.session_state["profile"] = prof
            st.session_state["items"] = it1
            st.session_state["results"] = res
            st.session_state["fill_priority"] = var7
            st.session_state["skip_meals"] = {"Breakfast": sk1, "Lunch": sk2, "Dinner": sk3}
            ent = {}
            ent["timestamp"] = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
            ent["goal"] = prof.goal_label
            ent["calories"] = round(res["dp"]["total_calories"])
            ent["protein"] = round(res["dp"]["total_protein"], 1)
            ent["cost"] = round(res["dp"]["total_cost"])
            ent["items"] = len(res["dp"]["selected_items"])
            ent["veg_only"] = var4
            hh = st.session_state["plan_history"]
            hh.insert(0, ent)
            if len(hh) > 5:
                hh = hh[0:5]
            st.session_state["plan_history"] = hh
        nn2 = len(res["dp"]["selected_items"])
        st.success("Done! Your meal plan has **" + str(nn2) + " food items**.  \nNavigate to **Meal Plan Results** in the sidebar to see the full breakdown.")


# MEAL PLAN LOGIC-sidebar
elif page == "Meal Plan Results":
    st.title("Your Meal Plan")


    if st.session_state["results"] is None:
        st.warning("No results yet. Please go to **User Profile** and click **Run Optimization** first.")
        st.stop()

    res = st.session_state["results"]
    prof = st.session_state["profile"]
    pl = res["dp"]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Calories", str(round(pl["total_calories"])) + " kcal")
    m2.metric("Total Cost", "Rs. " + str(round(pl["total_cost"])))
    m3.metric("Total Protein", str(round(pl["total_protein"], 1)) + " g")
    m4.metric("Goal", prof.goal_label)
    st.markdown("---")
    st.subheader("Constraint Status")
    cm = pl["constraints_met"]
    klist = ["calorie_limit", "budget", "min_protein", "max_sugar"]
    lbl = {}
    lbl["calorie_limit"] = "Calorie ≤ " + str(prof.calorie_limit) + " kcal"
    lbl["budget"] = "Budget ≤ Rs. " + str(int(prof.budget))
    lbl["min_protein"] = "Protein ≥ " + str(int(prof.min_protein)) + " g"
    lbl["max_sugar"] = "Sugar ≤ " + str(int(prof.max_sugar)) + " g"
    cls = st.columns(4)
    for i in range(len(klist)):
        kk = klist[i]
        ll = lbl[kk]
        ok = cm[kk]
        if ok == True:
            ic = "✅👍"
            bg = "#d4edda"
            fg = "#155724"
        else:
            ic = "❌✖️"
            bg = "#f8d7da"
            fg = "#721c24"
        html = '<div style="background:' + bg + ';color:' + fg + ';padding:12px 8px;border-radius:8px;text-align:center;font-weight:600;">' + ic + ' ' + ll + '</div>'
        cls[i].markdown(html, unsafe_allow_html=True)


    st.markdown("")
    def aggregate_items(item_list):
        ag = {}
        for it in item_list:
            nm = it["name"]
            if nm in ag:
                ag[nm]["servings"] = ag[nm]["servings"] + 1
                ag[nm]["Cal (kcal)"] = ag[nm]["Cal (kcal)"] + round(it["calories"], 1)
                ag[nm]["Protein (g)"] = ag[nm]["Protein (g)"] + round(it["protein_g"], 1)
                ag[nm]["Sugar (g)"] = ag[nm]["Sugar (g)"] + round(it["sugar_g"], 1)
                ag[nm]["Fat (g)"] = ag[nm]["Fat (g)"] + round(it["fat_g"], 1)
                ag[nm]["Cost (Rs.)"] = ag[nm]["Cost (Rs.)"] + round(it["cost_inr"], 1)
            else:
                rr = {}
                rr["calories_each"] = it["calories"]
                rr["servings"] = 1
                rr["Cal (kcal)"] = round(it["calories"], 1)
                rr["Protein (g)"] = round(it["protein_g"], 1)
                rr["Sugar (g)"] = round(it["sugar_g"], 1)
                rr["Fat (g)"] = round(it["fat_g"], 1)
                rr["Cost (Rs.)"] = round(it["cost_inr"], 1)
                ag[nm] = rr
        return ag
    ag = aggregate_items(pl["selected_items"])



# MEAL CHART inside MEAL PLAN
    st.markdown("---")
    st.subheader("Meals for Today")
    if "skip_meals" in st.session_state:
        sm = st.session_state["skip_meals"]
    else:
        sm = {"Breakfast": False, "Lunch": False, "Dinner": False}
    base = {"Breakfast": 0.30, "Lunch": 0.40, "Dinner": 0.30}
    tt = 0.0
    raw = {}
    for mm in base:
        if sm.get(mm, False) == False:
            raw[mm] = base[mm]
            tt = tt + base[mm]
    rats = {}
    for mm in raw:
        rats[mm] = raw[mm] / tt
    tcal = pl["total_calories"]
    aglist = []
    for nm in ag:
        aglist.append((nm, ag[nm]))
    for i in range(len(aglist)):
        for j in range(i + 1, len(aglist)):
            if aglist[j][1]["Cal (kcal)"] > aglist[i][1]["Cal (kcal)"]:
                aglist[i], aglist[j] = aglist[j], aglist[i]
    def split_meals(sorted_items, total_cal, ratios):
        tg = {}
        for m in ratios:
            tg[m] = total_cal * ratios[m]
        bk = {}
        bc = {}
        for m in ratios:
            bk[m] = []
            bc[m] = 0.0
        for p in sorted_items:
            nm = p[0]
            d = p[1]
            if d["servings"] > 1:
                lb = nm + " ×" + str(d["servings"])
            else:
                lb = nm
            best = None
            bd = None
            for m in tg:
                df = abs(bc[m] + d["Cal (kcal)"] - tg[m])
                if bd is None or df < bd:
                    bd = df
                    best = m
            rr = {}
            rr["Food"] = lb
            rr["Cal (kcal)"] = d["Cal (kcal)"]
            rr["Protein (g)"] = d["Protein (g)"]
            rr["Sugar (g)"] = d["Sugar (g)"]
            rr["Fat (g)"] = d["Fat (g)"]
            rr["Cost (Rs.)"] = d["Cost (Rs.)"]
            bk[best].append(rr)
            bc[best] = bc[best] + d["Cal (kcal)"]
        return bk, bc
    bk, bc = split_meals(aglist, tcal, rats)
    icns = {"Breakfast": "🌅 Breakfast", "Lunch": "☀️ Lunch", "Dinner": "🌙 Dinner"}
    morder = ["Breakfast", "Lunch", "Dinner"]
    tlbl = []
    for m in morder:
        tlbl.append(icns[m])
    tabs = st.tabs(tlbl)
    for i in range(len(morder)):
        mk = morder[i]
        with tabs[i]:
            if sm.get(mk, False) == True:
                st.info("⏭️ " + mk + " was skipped for today.")
            else:
                rws = bk.get(mk, [])
                if len(rws) > 0:
                    st.dataframe(pd.DataFrame(rws), use_container_width=True, hide_index=True)
                    st.caption("**" + mk + " total: " + str(round(bc.get(mk, 0))) + " kcal**")
                else:
                    st.info("No items assigned to this meal.")


# entire food list for a day
    st.markdown("---")
    st.subheader("All Foods in Your Plan")

    rws = []
    for nm in ag:
        d = ag[nm]
        if d["servings"] > 1:
            lb = nm + " ×" + str(d["servings"])
        else:
            lb = nm
        rr = {}
        rr["Food"] = lb
        rr["Cal (kcal)"] = round(d["Cal (kcal)"], 1)
        rr["Protein (g)"] = round(d["Protein (g)"], 1)
        rr["Sugar (g)"] = round(d["Sugar (g)"], 1)
        rr["Fat (g)"] = round(d["Fat (g)"], 1)
        rr["Cost (Rs.)"] = round(d["Cost (Rs.)"], 1)
        rws.append(rr)

    dfp = pd.DataFrame(rws)
    st.dataframe(dfp, use_container_width=True, hide_index=True)

    # swap food logic
    st.markdown("---")
    st.subheader("🔄 Swap a Food Item")
    pn = []
    for r in rws:
        nm2 = r["Food"].split(" ×")[0]
        pn.append(nm2)
    sc1, sc2 = st.columns(2)
    with sc1:
        sw1 = st.selectbox("Remove this item:", ["(none)"] + pn)
    with sc2:
        afn = get_all_food_names()
        nip = []
        for nm2 in afn:
            if nm2 not in pn:
                nip.append(nm2)
        sw2 = st.selectbox("Replace with:", ["(none)"] + nip)
    if st.button("Apply Swap") and sw1 != "(none)" and sw2 != "(none)":
        ia = st.session_state["items"]
        im = {}
        for it in ia:
            im[it["name"]] = it
        ni = []
        for it in pl["selected_items"]:
            if it["name"] != sw1:
                ni.append(it)
        if sw2 in im:
            ni.append(im[sw2])
        res["dp"]["selected_items"] = ni
        from modules.dp_optimizer import _compute_totals, _check_constraints
        tt2 = _compute_totals(ni)
        res["dp"]["total_calories"] = tt2["calories"]
        res["dp"]["total_cost"] = tt2["cost"]
        res["dp"]["total_protein"] = tt2["protein"]
        res["dp"]["total_sugar"] = tt2["sugar"]
        res["dp"]["total_fat"] = tt2["fat"]
        res["dp"]["constraints_met"] = _check_constraints(tt2, prof)
        st.session_state["results"] = res
        st.success("Swapped **" + sw1 + "** → **" + sw2 + "**. Page will refresh.")
        st.rerun()

    #doughnut and charts-VISUALIZATION
    st.markdown("---")
    st.subheader("Nutrition Breakdown")
    cc1, cc2 = st.columns(2)
    with cc1:
        st.markdown("**Macronutrient Distribution**")
        pg = pl["total_protein"]
        fg2 = pl["total_fat"]
        sg = pl["total_sugar"]
        cb = (pl["total_calories"] - pg * 4 - fg2 * 9) / 4
        if cb < 0:
            cb = 0
        fig1 = go.Figure(go.Pie(
            labels=["Protein", "Fat", "Carbs (est.)", "Sugar"],
            values=[pg, fg2, cb, sg],
            hole=0.45,
            marker_colors=["#636EFA", "#EF553B", "#00CC96", "#FFA15A"],
            textinfo="label+percent",
        ))
        fig1.update_layout(showlegend=True, margin=dict(t=20, b=20, l=20, r=20), height=320)
        st.plotly_chart(fig1, use_container_width=True)
    with cc2:
        st.markdown("**DP vs Greedy — Health Score**")
        gr = res["greedy"]
        fig2 = go.Figure(go.Bar(
            x=["Dynamic Programming", "Greedy"],
            y=[pl["total_score"], gr["total_score"]],
            marker_color=["#636EFA", "#EF553B"],
            text=[str(round(pl["total_score"], 2)), str(round(gr["total_score"], 2))],
            textposition="outside",
        ))
        fig2.update_layout(yaxis_title="Total Health Score", template="plotly_white", showlegend=False, margin=dict(t=20, b=20), height=320)
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")
    st.subheader("Nutrition Summary")
    n1, n2, n3, n4, n5 = st.columns(5)
    n1.metric("Calories", str(round(pl["total_calories"])) + " kcal")
    n2.metric("Cost", "Rs. " + str(round(pl["total_cost"])))
    n3.metric("Protein", str(round(pl["total_protein"], 1)) + " g")
    n4.metric("Sugar", str(round(pl["total_sugar"], 1)) + " g")
    n5.metric("Fat", str(round(pl["total_fat"], 1)) + " g")
    st.markdown("---")

# extracting whole meal plan as CSV
    bf = io.StringIO()
    dfp.to_csv(bf, index=False)
    st.download_button(
        label="⬇️ Export Meal Plan as CSV",
        data=bf.getvalue(),
        file_name="caloriecrcraft_meal_plan.csv",
        mime="text/csv",
        use_container_width=True,
    )

# plan history page-sidebar
elif page == "Plan History":
    st.title("Plan History")
    st.caption("Your last 5 generated plans.")
    hh = st.session_state["plan_history"]
    if len(hh) == 0:
        st.info("No plans generated yet. Go to **User Profile** and run an optimization first.")
    else:
        for i in range(len(hh)):
            e = hh[i]
            ll = "#" + str(i + 1) + " — " + e["timestamp"] + "  |  " + e["goal"] + "  |  " + str(e["calories"]) + " kcal"
            with st.expander(ll, expanded=(i == 0)):
                h1, h2, h3, h4 = st.columns(4)
                h1.metric("Calories", str(e["calories"]) + " kcal")
                h2.metric("Protein", str(e["protein"]) + " g")
                h3.metric("Cost", "Rs. " + str(e["cost"]))
                h4.metric("Items", e["items"])
                if e.get("veg_only") == True:
                    vt = "Yes"
                else:
                    vt = "No"
                st.caption("Vegetarian only: " + vt)
