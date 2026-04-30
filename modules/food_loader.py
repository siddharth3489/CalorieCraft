import pandas as pd
from pathlib import Path
REQUIRED_COLUMNS = ["name", "calories", "protein_g", "sugar_g", "fat_g", "cost_inr"]
DATA_PATH = Path(__file__).parent.parent / "data" / "food_dataset.csv"


#algo for load, cleans, filters, and scores food data
def load_foods(w1, w2, w3, csv_path=DATA_PATH, veg_only=None, excluded_names=None):
    var1 = pd.read_csv(csv_path)
    var1 = var1.dropna(subset=REQUIRED_COLUMNS)
    var2 = ["calories", "protein_g", "sugar_g", "fat_g", "cost_inr"]
    for x in var2:
        var1[x] = pd.to_numeric(var1[x], errors="coerce")
    var1 = var1.dropna(subset=REQUIRED_COLUMNS)
    var1 = var1[var1["calories"] > 0].reset_index(drop=True)
    if veg_only == True and "veg" in var1.columns:
        var1 = var1[var1["veg"] == "yes"].reset_index(drop=True)
    if excluded_names is not None and len(excluded_names) > 0:
        var1 = var1[~var1["name"].isin(excluded_names)].reset_index(drop=True)
    var1["health_score"] = w1 * var1["protein_g"] - w2 * var1["sugar_g"] - w3 * var1["fat_g"]


    var3 = var1.to_dict(orient="records")
    return var3
# read food/meal
def get_all_food_names(csv_path=DATA_PATH):
    a1 = pd.read_csv(csv_path)
    a2 = a1["name"].dropna().tolist()
    a2.sort()
    return a2
