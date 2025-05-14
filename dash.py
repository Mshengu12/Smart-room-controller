import flet as ft
import requests
from time import sleep

# State variable for mode
is_manual_mode = True

# Colors
PRIMARY_COLOR = "#6A5ACD"  # Slate Blue
SECONDARY_COLOR = "#483D8B"  # Dark Slate Blue
ACCENT_COLOR = "#9370DB"  # Medium Purple
BACKGROUND_COLOR = "#F5F5F5"
CARD_COLOR = "#FFFFFF"
TEXT_COLOR = "#333333"

# Function to update the UI with the latest status values
def update_status(page):
    """Fetch and update all status values from the backend"""
    try:
        # Send a GET request to the backend to retrieve the latest sensor data
        response = requests.get('http://localhost:5000/status', timeout=5)
        if response.status_code == 200:
            data = response.json()
            
            # Update UI with received data
            page.controls['light_level'].value = f'{data["light_level"]}'
            page.controls['distance'].value = f'{data["distance"]} cm'
            page.controls['led_status'].value = 'ON' if data["led_status"] else 'OFF'
            page.controls['fan_speed'].value = f'{data["fan_speed"]}'
            page.controls['temperature'].value = f'{data["temperature"]}°C'

            # Update controls
            page.controls['led_toggle'].value = data["led_status"]
            page.controls['fan_slider'].disabled = not is_manual_mode
            page.controls['fan_slider'].value = data["fan_speed"]

            # Update LED indicator color
            page.controls['led_indicator'].bgcolor = ft.Colors.GREEN if data["led_status"] else ft.Colors.RED
            
            page.update()
    except requests.exceptions.RequestException as e:
        print(f"Error updating status: {e}")
        # Retry after 2 seconds if there's an error
        sleep(2)
        update_status(page)

# Function to control LED
def control_led(page, status):
    try:
        response = requests.post('http://localhost:5000/control_led', 
                               json={'status': status}, 
                               timeout=3)
        if response.status_code == 200:
            update_status(page)
    except requests.exceptions.RequestException as e:
        print(f"Error controlling LED: {e}")

# Function to control Fan (Servo motor)
def control_fan(page, speed):
    if is_manual_mode:
        try:
            response = requests.post('http://localhost:5000/control_fan', 
                                    json={'speed': speed}, 
                                    timeout=3)
            if response.status_code == 200:
                update_status(page)
        except requests.exceptions.RequestException as e:
            print(f"Error controlling Fan: {e}")

# Function to toggle control mode (Manual/Automatic)
def toggle_mode(page):
    global is_manual_mode
    is_manual_mode = not is_manual_mode
    page.controls['mode_button'].text = f"Switch to {'Automatic' if is_manual_mode else 'Manual'} Mode"
    page.controls['mode_button'].bgcolor = ft.Colors.GREEN_500 if is_manual_mode else ft.Colors.BLUE_500
    page.controls['fan_slider'].disabled = not is_manual_mode
    page.update()

def create_status_card(title, value, icon, key=None):
    """Helper function to create consistent status cards"""
    return ft.Card(
        elevation=5,
        content=ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Icon(icon, color=PRIMARY_COLOR),
                        title=ft.Text(title, weight=ft.FontWeight.BOLD),
                        subtitle=ft.Text(value, key=key, size=18) if key else ft.Text(value, size=18),
                    )
                ],
                spacing=0,
            ),
            padding=15,
            width=250,
        ),
        color=CARD_COLOR,
    )

def main(page: ft.Page):
    # Set page properties
    page.title = 'Smart Room Controller'
    page.window_width = 800
    page.window_height = 900
    page.padding = 30
    page.bgcolor = BACKGROUND_COLOR
    page.fonts = {
        "Roboto": "https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap"
    }
    page.theme = ft.Theme(font_family="Roboto")

    # Header
    header = ft.Container(
        content=ft.Column(
            [
                ft.Text("Smart Room", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ft.Text("Controller Dashboard", size=18, color=ft.Colors.WHITE70),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        ),
        bgcolor=PRIMARY_COLOR,
        padding=20,
        border_radius=15,
        width=700,
        alignment=ft.alignment.center,
    )

    # Status Grid
    status_grid = ft.GridView(
        runs_count=2,
        max_extent=300,
        child_aspect_ratio=2,
        spacing=20,
        run_spacing=20,
        controls=[
            create_status_card("Light Level", "Loading...", ft.Icons.LIGHTBULB, "light_level"),
            create_status_card("Distance", "Loading...", ft.Icons.STRAIGHTEN, "distance"),
            create_status_card("Temperature", "Loading...", ft.Icons.THERMOSTAT, "temperature"),
            create_status_card("Fan Speed", "Loading...", ft.Icons.AIR, "fan_speed"),
        ]
    )

    # LED Control Card
    led_card = ft.Card(
        elevation=5,
        content=ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.LIGHT_MODE, color=PRIMARY_COLOR),
                        title=ft.Text("LED Control", weight=ft.FontWeight.BOLD),
                    ),
                    ft.Row(
                        [
                            ft.Container(
                                width=20,
                                height=20,
                                border_radius=20,
                                bgcolor=ft.Colors.RED,
                                key="led_indicator"
                            ),
                            ft.Switch(
                                key='led_toggle',
                                label="Toggle LED",
                                active_color=ACCENT_COLOR,
                                value=False,
                                on_change=lambda e: control_led(page, e.control.value)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        spacing=20
                    )
                ],
                spacing=10,
            ),
            padding=20,
            width=700,
        ),
        color=CARD_COLOR,
    )

    # Fan Control Card
    fan_card = ft.Card(
        elevation=5,
        content=ft.Container(
            content=ft.Column(
                [
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.AIR, color=PRIMARY_COLOR),
                        title=ft.Text("Fan Control", weight=ft.FontWeight.BOLD),
                    ),
                    ft.Slider(
                        key='fan_slider',
                        min=0,
                        max=255,
                        divisions=10,
                        label="{value}",
                        active_color=ACCENT_COLOR,
                        inactive_color=ft.Colors.GREY_300,
                        on_change=lambda e: control_fan(page, e.control.value)
                    ),
                    ft.ElevatedButton(
                        text="Switch to Automatic Mode",
                        key='mode_button',
                        icon=ft.Icons.SWITCH_ACCESS_SHORTCUT,
                        on_click=lambda e: toggle_mode(page),
                        bgcolor=ft.Colors.BLUE_500,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=20
                        )
                    )
                ],
                spacing=20,
            ),
            padding=20,
            width=700,
        ),
        color=CARD_COLOR,
    )

    # Main layout
    main_column = ft.Column(
        [
            header,
            ft.Text("Room Status", size=20, weight=ft.FontWeight.BOLD, color=TEXT_COLOR),
            status_grid,
            led_card,
            fan_card,
        ],
        spacing=30,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Add scroll to the main column
    scrollable = ft.Container(
        content=ft.Column([main_column], scroll=ft.ScrollMode.AUTO),
        expand=True
    )

    # Add the main column to the page
    page.add(scrollable)

    # Start periodic updates
    def update_loop():
        while True:
            update_status(page)
            sleep(2)  # Update every 2 seconds

    # Run the update loop in a separate thread
    import threading
    threading.Thread(target=update_loop, daemon=True).start()

# Run the Flet application
ft.app(target=main)