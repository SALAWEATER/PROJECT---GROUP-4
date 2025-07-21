import flet as ft
import requests
from datetime import datetime

def main(page: ft.Page):
    # Light mode settings
    page.title = "Mental Health Tracker"
    page.vertical_alignment = "stretch"
    page.horizontal_alignment = "center"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme=ft.ColorScheme(
            primary=ft.Colors.BLUE_400,
            secondary=ft.Colors.BLUE_200,
            surface=ft.Colors.WHITE,
            on_surface=ft.Colors.BLACK,
        )
    )
    page.update()

    # State variables
    current_user = ft.TextField(visible=False)
    current_password = ft.TextField(visible=False)
    
    # UI Components
    # Mood Tracking
    mood_slider = ft.Slider(min=1, max=10, divisions=9, width=300)
    mood_notes = ft.TextField(label="Notes", multiline=True, width=300, height=100)
    mood_history = ft.ListView(expand=True)
    
    # Activity Tracking
    activity_input = ft.TextField(label="Activity", width=250)
    activity_duration = ft.TextField(label="Minutes", width=100)
    activities_list = ft.ListView(expand=True)
    
    # Journal
    journal_entry = ft.TextField(label="Journal", multiline=True, width=300, height=150)
    journal_entries = ft.ListView(expand=True)

    # Navigation Rail (Left sidebar)
    nav_rail = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.NONE,
        min_width=70,
        min_extended_width=150,
        leading=ft.Container(
            height=50,
            content=ft.Icon(ft.Icons.MOOD, size=30),
            margin=ft.margin.only(bottom=20)
        ),
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.MOOD_OUTLINED,
                selected_icon=ft.Icons.MOOD,
                label="Mood"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.DIRECTIONS_RUN_OUTLINED,
                selected_icon=ft.Icons.DIRECTIONS_RUN,
                label="Activities"
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.BOOK_OUTLINED,
                selected_icon=ft.Icons.BOOK,
                label="Journal"
            ),
        ],
        on_change=lambda e: change_tab(e.control.selected_index)
    )

    # Content area
    content_column = ft.Column(
        [
            ft.Text("How are you feeling today?", size=20),
            mood_slider,
            mood_notes,
            ft.ElevatedButton("Log Mood", on_click=lambda e: submit_mood(e)),
            ft.Divider(),
            ft.Text("Recent Entries", size=16),
            mood_history
        ],
        alignment="center",
        horizontal_alignment="center",
        expand=True
    )

    # Main layout
    main_content = ft.Row(
        [
            nav_rail,
            ft.VerticalDivider(width=1),
            ft.Container(content=content_column, expand=True, padding=20)
        ],
        expand=True
    )

    def submit_mood(e):
        if not mood_slider.value:
            show_snackbar("Please select a mood score!")
            return

        try:
            response = requests.post(
                "http://localhost:8000/mood",
                data={
                    "username": current_user.value,
                    "password": current_password.value,
                    "score": int(mood_slider.value),
                    "notes": mood_notes.value
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                show_snackbar("Mood logged successfully!", ft.Colors.GREEN)
                mood_history.controls.insert(0, ft.ListTile(
                    title=ft.Text(f"Mood: {mood_slider.value}"),
                    subtitle=ft.Text(f"Notes: {mood_notes.value or 'None'}"),
                    trailing=ft.Text(datetime.now().strftime("%H:%M"))
                ))
                mood_slider.value = 5
                mood_notes.value = ""
                page.update()
            else:
                show_snackbar(f"Error: {response.json().get('detail', 'Failed to log mood')}")
        except Exception as e:
            show_snackbar(f"Connection error: {str(e)}")

    def add_activity(e):
        if not activity_input.value or not activity_duration.value:
            show_snackbar("Please enter activity and duration!")
            return
        
        activities_list.controls.insert(0, ft.ListTile(
            title=ft.Text(activity_input.value),
            subtitle=ft.Text(f"{activity_duration.value} minutes"),
            trailing=ft.Text(datetime.now().strftime("%H:%M"))
        ))
        activity_input.value = ""
        activity_duration.value = ""
        page.update()

    def add_journal_entry(e):
        if not journal_entry.value:
            show_snackbar("Journal entry cannot be empty!")
            return
        
        journal_entries.controls.insert(0, ft.ListTile(
            title=ft.Text(datetime.now().strftime("%b %d, %H:%M")),
            subtitle=ft.Text(journal_entry.value),
        ))
        journal_entry.value = ""
        page.update()

    def change_tab(index):
        content_column.controls.clear()
        
        if index == 0:  # Mood
            content_column.controls.extend([
                ft.Text("How are you feeling today?", size=20),
                mood_slider,
                mood_notes,
                ft.ElevatedButton("Log Mood", on_click=lambda e: submit_mood(e)),
                ft.Divider(),
                ft.Text("Recent Mood Entries", size=16),
                mood_history
            ])
        
        elif index == 1:  # Activities
            content_column.controls.extend([
                ft.Text("Track Your Activities", size=20),
                ft.Row([activity_input, activity_duration]),
                ft.ElevatedButton("Add Activity", on_click=add_activity),
                ft.Divider(),
                ft.Text("Today's Activities", size=16),
                activities_list
            ])
        
        elif index == 2:  # Journal
            content_column.controls.extend([
                ft.Text("Journal Entry", size=20),
                journal_entry,
                ft.ElevatedButton("Save Entry", on_click=add_journal_entry),
                ft.Divider(),
                ft.Text("Previous Entries", size=16),
                journal_entries
            ])
        
        page.update()

    def show_snackbar(message, color=ft.Colors.RED):
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()

    # Login view
    login_username = ft.TextField(label="Username")
    login_password = ft.TextField(label="Password", password=True)
    
    def login(e):
        try:
            response = requests.post(
                "http://localhost:8000/login",
                data={
                    "username": login_username.value,
                    "password": login_password.value
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                current_user.value = login_username.value
                current_password.value = login_password.value
                show_snackbar("Login successful!", ft.Colors.GREEN)
                page.go("/dashboard")
        except Exception as e:
            show_snackbar(f"Error: {str(e)}")

    # Registration view
    register_username = ft.TextField(label="Username")
    register_password = ft.TextField(label="Password", password=True)
    register_email = ft.TextField(label="Email (optional)")
    
    def register(e):
        if not register_username.value or not register_password.value:
            show_snackbar("Username and password are required!")
            return

        try:
            response = requests.post(
                "http://localhost:8000/register",
                data={
                    "username": register_username.value,
                    "password": register_password.value,
                    "email": register_email.value
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                show_snackbar("Registration successful! Please login.", ft.Colors.GREEN)
                page.go("/login")
            else:
                show_snackbar(f"Error: {response.json().get('detail', 'Registration failed')}")
        except Exception as e:
            show_snackbar(f"Connection error: {str(e)}")

    # Registration view
    register_view = ft.View(
        "/register",
        [
            ft.Column(
                [
                    ft.Text("Register", size=24),
                    register_username,
                    register_password,
                    register_email,
                    ft.ElevatedButton("Register", on_click=register),
                    ft.TextButton("Back to Login", on_click=lambda _: page.go("/login"))
                ],
                alignment="center",
                horizontal_alignment="center"
            )
        ]
    )

    # Dashboard view with new layout
    dashboard_view = ft.View(
        "/dashboard",
        [
            ft.AppBar(
                title=ft.Text(f"Welcome, {current_user.value}"),
                actions=[ft.TextButton("Logout", on_click=lambda _: page.go("/login"))]
            ),
            main_content
        ],
        padding=0
    )

    # Login view
    login_view = ft.View(
        "/login",
        [
            ft.Column(
                [
                    ft.Text("Login", size=24),
                    login_username,
                    login_password,
                    ft.ElevatedButton("Login", on_click=login),
                    ft.TextButton("Register", on_click=lambda _: page.go("/register"))
                ],
                alignment="center",
                horizontal_alignment="center"
            )
        ]
    )

    def route_change(e):
        page.views.clear()
        if page.route == "/login":
            page.views.append(login_view)
        elif page.route == "/register":
            page.views.append(register_view)
        elif page.route == "/dashboard":
            if current_user.value:
                page.views.append(dashboard_view)
            else:
                page.go("/login")
        page.update()

    page.on_route_change = route_change
    page.go("/login")

ft.app(target=main)