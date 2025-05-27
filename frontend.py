import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Task Manager", layout="centered")
st.title("Task Manager with FastAPI")

menu = st.sidebar.selectbox("Choose an action", ["Signup", "Login", "Add Task", "View Tasks", "Logout", "Delete User"])

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False
    st.session_state.username = None
    st.session_state.password = None

if menu == "Signup":
    st.subheader("Create a New Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        res = requests.post(f"{API_URL}/signup", params={"username": username, "password": password})
        if res.status_code == 200:
            st.success("Signup successful")
        else:
            st.error("Signup failed")

elif menu == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        res = requests.post(f"{API_URL}/users/login", params={"username": username, "password": password})
        if res.json().get("message") == "Login successful":
            st.success("Login successful")
            st.session_state.is_logged_in = True
            st.session_state.username = username
            st.session_state.password = password
        else:
            st.error("Login failed")

elif menu == "Add Task":
    if st.session_state.is_logged_in:
        st.subheader("Add a New Task")
        title = st.text_input("Task Title")
        description = st.text_area("Task Description")
        if st.button("Add Task"):
            res = requests.post(f"{API_URL}/adding/tasks", params={
                "username": st.session_state.username,
                "title": title,
                "description": description
            })
            st.success("Task added successfully")
    else:
        st.warning("Please login first.")

elif menu == "View Tasks":
    if st.session_state.is_logged_in:
        st.subheader("Your Tasks")
        res = requests.get(f"{API_URL}/users/tasks", params={"username": st.session_state.username})
        if res.status_code == 200:
            tasks = res.json()
            for task in tasks:
                with st.expander(f"{task[2]}"):
                    st.markdown(f"**Description:** {task[3]}")
                    if st.button("Delete Task", key=f"del_{task[0]}"):
                        delete_res = requests.delete(f"{API_URL}/delete/tasks/{task[0]}")
                        if delete_res.status_code == 200:
                            result = delete_res.json()
                            if result.get("message") == "Task deleted successfully":
                                st.success("Task deleted successfully.")
                                st.experimental_rerun()  
                            else:
                                st.error(result.get("message", "Failed to delete task."))
                        else:
                            st.error("Server error during deletion.")
        else:
            st.error("Failed to fetch tasks.")
    else:
        st.warning("Please login first.")

elif menu == "Logout":
    if st.session_state.is_logged_in:
        res = requests.post(f"{API_URL}/users/logout", params={
            "username": st.session_state.username,
            "password": st.session_state.password
        })
        if "successfully" in res.text:
            st.success("Logged out successfully")
            st.session_state.is_logged_in = False
            st.session_state.username = None
            st.session_state.password = None
        else:
            st.error(res.text)
    else:
        st.warning("You are not logged in.")

elif menu == "Delete User":
    if st.session_state.is_logged_in:
        if st.button("Delete User"):
            username=st.session_state.username
            res = requests.delete(f"{API_URL}/delete/users/{username}")
            st.write(res.text)