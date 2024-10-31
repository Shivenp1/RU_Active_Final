import pandas as pd

def suggest_progressive_overload(current_weight, current_reps, current_sets):
    # Suggest increasing weight by 5% if reps are met
    if current_reps >= 8:  # Assume a minimum of 8 reps to increase
        new_weight = current_weight * 1.05  # Increase by 5%
        new_reps = current_reps
    else:
        new_weight = current_weight
        new_reps = current_reps + 1  # Increase reps if weight is not increased

    # Suggest increasing sets if current sets are less than 3
    new_sets = current_sets if current_sets >= 3 else current_sets + 1

    # Create a DataFrame for better display
    data = {
        "Current": [current_weight, current_reps, current_sets],
        "Next Week": [round(new_weight, 2), new_reps, new_sets]
    }
    df = pd.DataFrame(data, index=["Weight (kg)", "Reps", "Sets"])
    return df