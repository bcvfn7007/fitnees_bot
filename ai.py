def generate_menu(data):
    goal = data["goal"]

    if goal == "lose":
        return (
            "🥣 Breakfast: oatmeal + berries\n"
            "🍗 Lunch: chicken + vegetables\n"
            "🥗 Dinner: protein salad"
        )

    if goal == "gain":
        return (
            "🍳 Breakfast: eggs + toast\n"
            "🍝 Lunch: pasta with meat\n"
            "🍚 Dinner: rice + protein"
        )

    return (
        "🥣 Breakfast: porridge\n"
        "🍲 Lunch: balanced meal\n"
        "🥙 Dinner: light protein"
    )
