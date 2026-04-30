class UserProfile:
    def __init__(self, goal, calorie_limit, budget, min_protein, max_sugar, w1, w2, w3):
        self.goal = goal
        self.calorie_limit = calorie_limit
        self.budget = budget
        self.min_protein = min_protein
        self.max_sugar = max_sugar
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3

    @property
    def goal_label(self):
        if self.goal == "weight_loss":
            return "Weight Loss"
        if self.goal == "muscle_gain":
            return "Muscle Gain"
        if self.goal == "balanced":
            return "Balanced"
        return self.goal





def build_profile(goal, calorie_limit, budget, min_protein, max_sugar):
    if goal == "weight_loss":
        var1 = 0.4
        var2 = 0.4
        var3 = 0.2
    elif goal == "muscle_gain":
        var1 = 0.6
        var2 = 0.2
        var3 = 0.2
    else:
        var1 = 0.33
        var2 = 0.33
        var3 = 0.33
    return UserProfile(goal, calorie_limit, budget, min_protein, max_sugar, var1, var2, var3)
