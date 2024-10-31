import streamlit as st
import database
from workout import suggest_progressive_overload
from nutrition import calculate_nutrition
import plotly.express as px
import plotly.graph_objects as go

# Initialize database
database.create_tables()

def main_app():
    """Main application."""
    st.set_page_config(page_title="RU Active", layout="wide")
    st.title("RU Active - Your Fitness Companion")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Home", "Workout Suggestions", "Nutritional Suggestions", "Login", "Sign Up", "Profile", "Progress", "Friends"])

    if page == "Home":
        st.header("Welcome to RU Active!")
        st.write("Please use the navigation menu to explore the app.")

    elif page == "Workout Suggestions":
        st.header("Workout Suggestions")
        current_weight = st.number_input("Current Weight Lifted (kg):", min_value=0.0, step=0.5)
        current_reps = st.number_input("Current Reps:", min_value=0, step=1)
        current_sets = st.number_input("Current Sets:", min_value=1, max_value=5, step=1)

        if st.button("Get Suggestion"):
            suggestion_df = suggest_progressive_overload(current_weight, current_reps, current_sets)
            st.write("Suggested Workout for Next Week:")
            st.table(suggestion_df)
            fig = px.bar(suggestion_df, x=suggestion_df.index, y="Next Week", title="Workout Progression")
            st.plotly_chart(fig)

    elif page == "Nutritional Suggestions":
        st.header("Nutritional Suggestions")

        if 'logged_in_user' in st.session_state:
            user_data = database.get_user_profile(st.session_state.logged_in_user)
            if user_data:
                # Ensure default values if any field is None
                height_in_inches = user_data['height'] or 0
                weight_in_pounds = user_data['weight'] or 0
                age = user_data['age'] or 0
                activity_level = user_data['activity_level'] or 'sedentary'
                goal = user_data['goal'] or 'maintenance'

                nutrition_df = calculate_nutrition(height_in_inches, weight_in_pounds, age, activity_level, goal)
                st.write("Suggested Daily Nutritional Intake:")
                st.table(nutrition_df)

                # Expanded pie chart with additional nutrients
                fig = px.pie(nutrition_df, values='Suggested Intake', names='Nutrient', title='Nutritional Breakdown')
                st.plotly_chart(fig)
            else:
                st.error("User profile data not found.")
        else:
            st.error("Please log in to view nutritional suggestions.")

    elif page == "Login":
        st.header("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if database.verify_user(username, password):
                st.session_state.logged_in_user = username
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password")

    elif page == "Sign Up":
        st.header("Create a New Account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        if st.button("Sign Up"):
            if database.add_user(new_username, new_password):
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username already exists. Please choose a different username.")

    elif page == "Profile":
        if 'logged_in_user' in st.session_state:
            st.header("Profile Management")
            user_data = database.get_user_profile(st.session_state.logged_in_user)
            if user_data:
                # Display user stats
                st.subheader("Your Stats")
                st.write(f"Height: {user_data['height']} inches")
                st.write(f"Weight: {user_data['weight']} pounds")
                st.write(f"Age: {user_data['age']}")
                st.write(f"Activity Level: {user_data['activity_level']}")
                st.write(f"Goal: {user_data['goal']}")

                # Display badges
                st.subheader("Badges")
                badges = database.get_user_badges(user_data['id'])
                for badge in badges:
                    st.write(f"- {badge['name']}: {badge['description']}")

                # Leaderboard
                st.subheader("Leaderboard")
                leaderboard_data = database.get_leaderboard(user_data['id'])
                st.table(leaderboard_data)

                # Existing profile management code...
                height = st.number_input("Height (inches):", value=user_data['height'] or 0)
                weight = st.number_input("Weight (pounds):", value=user_data['weight'] or 0)
                age = st.number_input("Age:", value=user_data['age'] or 0)
                activity_level = st.selectbox("Activity Level:", ["sedentary", "active", "very active"], index=["sedentary", "active", "very active"].index(user_data['activity_level'] or "sedentary"))
                goal = st.selectbox("Fitness Goal:", ["muscle_gain", "weight_loss", "maintenance"], index=["muscle_gain", "weight_loss", "maintenance"].index(user_data['goal'] or "maintenance"))

                if st.button("Update Profile"):
                    database.update_user_profile(st.session_state.logged_in_user, height, weight, age, activity_level, goal)
                    st.success("Profile updated successfully!")
            else:
                st.error("User data not found.")
        else:
            st.error("Please log in to view your profile.")

    elif page == "Progress":
        if 'logged_in_user' in st.session_state:
            st.header("Track Your Progress")
            exercise = st.text_input("Exercise")
            weight = st.number_input("Weight (kg):", min_value=0.0, step=0.5)
            reps = st.number_input("Reps:", min_value=0, step=1)
            date = st.date_input("Date")

            if st.button("Add Progress"):
                database.add_workout_progress(st.session_state.logged_in_user, exercise, weight, reps, date)
                st.success("Progress added successfully!")

            # Fetch and display progress
            progress_data = database.get_user_progress(st.session_state.logged_in_user)
            if progress_data is not None and not progress_data.empty:
                st.write("Your Progress:")
                st.table(progress_data)

                # Visualize progress with dual y-axes
                fig = go.Figure()

                # Add weight data to the primary y-axis
                for exercise in progress_data['exercise'].unique():
                    exercise_data = progress_data[progress_data['exercise'] == exercise]
                    fig.add_trace(go.Scatter(
                        x=exercise_data['date'],
                        y=exercise_data['weight'],
                        mode='lines+markers',
                        name=f"{exercise} Weight",
                        yaxis='y1'
                    ))

                # Add reps data to the secondary y-axis
                for exercise in progress_data['exercise'].unique():
                    exercise_data = progress_data[progress_data['exercise'] == exercise]
                    fig.add_trace(go.Scatter(
                        x=exercise_data['date'],
                        y=exercise_data['reps'],
                        mode='lines+markers',
                        name=f"{exercise} Reps",
                        yaxis='y2'
                    ))

                # Update layout to include secondary y-axis
                fig.update_layout(
                    title='Progress Over Time',
                    xaxis_title='Date',
                    yaxis=dict(
                        title='Weight (kg)',
                        side='left'
                    ),
                    yaxis2=dict(
                        title='Reps',
                        overlaying='y',
                        side='right'
                    )
                )

                st.plotly_chart(fig)
            else:
                st.info("No progress data available.")
        else:
            st.error("Please log in to track your progress.")

    elif page == "Friends":
        if 'logged_in_user' in st.session_state:
            st.header("Your Friends")
            user_data = database.get_user_profile(st.session_state.logged_in_user)
            if user_data:
                friends = database.get_friends(user_data['id'])
                if friends:
                    st.write("Your Friends:")
                    for friend in friends:
                        st.write(f"- {friend}")
                else:
                    st.info("You have no friends added.")

                # Add friend functionality
                st.subheader("Add a Friend")
                friend_username = st.text_input("Friend's Username")
                if st.button("Add Friend"):
                    if database.add_friend(user_data['id'], friend_username):
                        st.success("Friend added successfully!")
                    else:
                        st.error("Could not add friend. Please check the username.")
            else:
                st.error("User data not found.")
        else:
            st.error("Please log in to view your friends.")

# Run the main application
main_app()