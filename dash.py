import flet as ft  # Import Flet library for building the frontend UI
import requests  # Import requests library to handle HTTP requests
from time import sleep  # Import sleep function to introduce delays

# State variable for mode
is_manual_mode = True  # Initialize control mode as manual

# Colors for UI design
PRIMARY_COLOR = "#6A5ACD"  # Slate Blue for primary elements
SECONDARY_COLOR = "#483D8B"  # Dark Slate Blue for secondary elements
ACCENT_COLOR = "#9370DB"  # Medium Purple for accents
BACKGROUND_COLOR = "#F5F5F5"  # Light background color
CARD_COLOR = "#FFFFFF"  # White for card backgrounds
TEXT_COLOR = "#333333"  # Dark text color

# Function to update the UI with the latest status values
# Fetches sensor data and updates the UI components
def update_status(page):
    try:
        response = requests.get('http://localhost:5000/status', timeout=5)  # Request data from Flask server
        if response.status_code == 200:  # Check if response is successful
            data = response.json()  # Parse JSON data
            # Update UI controls with received data
            page.controls['light_level'].value = f'{data["light_level"]}'
            page.controls['distance'].value = f'{data["distance"]} cm'
            page.controls['led_status'].value = 'ON' if data["led_status"] else 'OFF'
            page.controls['fan_speed'].value = f'{data["fan_speed"]}'
            page.controls['temperature'].value = f'{data["temperature"]}°C'

            # Update LED toggle and fan slider controls
            page.controls['led_toggle'].value = data["led_status"]
            page.controls['fan_slider'].disabled = not is_manual_mode  # Disable slider in automatic mode
            page.controls['fan_slider'].value = data["fan_speed"]

            # Change LED indicator color based on status
            page.controls['led_indicator'].bgcolor = ft.Colors.GREEN if data["led_status"] else ft.Colors.RED

            page.update()  # Apply updates to the page
    except requests.exceptions.RequestException as e:
        print(f"Error updating status: {e}")
        sleep(2)  # Wait for 2 seconds before retrying
        update_status(page)

# Function to control LED based on user input
def control_led(page, status):
    try:
        response = requests.post('http://localhost:5000/control_led', json={'status': status}, timeout=3)
        if response.status_code == 200:
            update_status(page)
    except requests.exceptions.RequestException as e:
        print(f"Error controlling LED: {e}")

# Function to control Fan speed (Servo motor)
# Only works in manual mode
def control_fan(page, speed):
    if is_manual_mode:
        try:
            response = requests.post('http://localhost:5000/control_fan', json={'speed': speed}, timeout=3)
            if response.status_code == 200:
                update_status(page)
        except requests.exceptions.RequestException as e:
            print(f"Error controlling Fan: {e}")

# Toggle control mode between Manual and Automatic
def toggle_mode(page):
    global is_manual_mode
    is_manual_mode = not is_manual_mode  # Switch mode
    # Update button text and color based on mode
    page.controls['mode_button'].text = f"Switch to {'Automatic' if is_manual_mode else 'Manual'} Mode"
    page.controls['mode_button'].bgcolor = ft.Colors.GREEN_500 if is_manual_mode else ft.Colors.BLUE_500
    page.controls['fan_slider'].disabled = not is_manual_mode  # Disable fan slider in automatic mode
    page.update()

# Function to create a consistent status card
def create_status_card(title, value, icon, key=None):
    return ft.Card(
        elevation=5,
        content=ft.Container(
            content=ft.Column([
                ft.ListTile(
                    leading=ft.Icon(icon, color=PRIMARY_COLOR),
                    title=ft.Text(title, weight=ft.FontWeight.BOLD),
                    subtitle=ft.Text(value, key=key, size=18) if key else ft.Text(value, size=18),
                )
            ], spacing=0),
            padding=15, width=250),
        color=CARD_COLOR
    )

# Main function to set up the Flet application
def main(page: ft.Page):
    # Configure page settings
    page.title = 'Smart Room Controller'
    page.window_width = 800
    page.window_height = 900
    page.padding = 30
    page.bgcolor = BACKGROUND_COLOR
    page.fonts = {"Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap"}
    page.theme = ft.Theme(font_family="Roboto")

    # Header component
    header = ft.Container(
        content=ft.Column([
            ft.Text("Smart Room", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("Controller Dashboard", size=18, color=ft.Colors.WHITE70)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=5),
        bgcolor=PRIMARY_COLOR, padding=20, border_radius=15, width=700, alignment=ft.alignment.center)

    # Status grid displaying sensor data
    status_grid = ft.GridView(
        runs_count=2, max_extent=300, child_aspect_ratio=2, spacing=20, run_spacing=20,
        controls=[
            create_status_card("Light Level", "Loading...", ft.Icons.LIGHTBULB, "light_level"),
            create_status_card("Distance", "Loading...", ft.Icons.STRAIGHTEN, "distance"),
            create_status_card("Temperature", "Loading...", ft.Icons.THERMOSTAT, "temperature"),
            create_status_card("Fan Speed", "Loading...", ft.Icons.AIR, "fan_speed")
        ])

    # Main layout structure
    main_column = ft.Column([
        header,  # Add header
        ft.Text("Room Status", size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
        status_grid  # Add status grid
    ], spacing=30, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # Scrollable container for main content
    scrollable = ft.Container(
        content=ft.Column([main_column], scroll=ft.ScrollMode.AUTO),
        expand=True)

    # Add main layout to page
    page.add(scrollable)

    # Periodic update loop to fetch data
    def update_loop():
        while True:
            update_status(page)
            sleep(2)

    # Run update loop in separate thread
    import threading
    threading.Thread(target=update_loop, daemon=True).start()

# Run Flet app
ft.app(target=main)
