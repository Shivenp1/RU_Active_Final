import pandas as pd

def calculate_nutrition(height_in_inches, weight_in_pounds, age, activity_level, goal):
    # Convert height and weight to metric for BMR calculation
    height_cm = height_in_inches * 2.54
    weight_kg = weight_in_pounds * 0.453592

    # Calculate BMR using Mifflin-St Jeor Equation
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5  # +5 for males, -161 for females (adjust as needed)
    
    # Adjust calories based on activity level
    if activity_level == 'sedentary':
        calories = bmr * 1.2
    elif activity_level == 'active':
        calories = bmr * 1.55
    else:
        calories = bmr * 1.9  # Very active

    # Adjust calories and protein based on goal
    if goal == 'muscle_gain':
        calories += 500  # Add for muscle gain
        protein = weight_in_pounds * 1.0  # 1.0g of protein per pound
    elif goal == 'weight_loss':
        calories -= 500  # Subtract for weight loss
        protein = weight_in_pounds * 1.2  # 1.2g of protein per pound
    else:  # maintenance
        protein = weight_in_pounds * 1.0  # 1.0g of protein per pound

    # Calculate carbohydrates and fats
    carbs = (calories * 0.5) / 4  # 50% of calories from carbs, 4 kcal per gram
    fats = (calories * 0.25) / 9  # 25% of calories from fats, 9 kcal per gram

    # Create a DataFrame for better display
    data = {
        "Nutrient": ["Calories (kcal)", "Protein (g)", "Carbohydrates (g)", "Fats (g)"],
        "Suggested Intake": [round(calories), round(protein), round(carbs), round(fats)]
    }
    df = pd.DataFrame(data)
    return df