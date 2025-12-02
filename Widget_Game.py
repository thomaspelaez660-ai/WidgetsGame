from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
import random

# Player widget
class Player(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, 50)
        with self.canvas:
            Color(0, 1, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

# Falling obstacle
class Obstacle(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size = (50, 50)
        self.x = random.randint(0, 350)
        self.y = 400
        with self.canvas:
            Color(1, 0, 0)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class GameArea(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player = Player(pos=(175, 20))
        self.add_widget(self.player)
        self.obstacles = []
        self.score = 0
        self.running = False
        self.double_points = False
        self.progress = None  # will link from App

    def start_game(self):
        self.running = True
        self.score = 0
        self.clear_obstacles()
        Clock.schedule_interval(self.update, 1/30)

    def stop_game(self):
        self.running = False
        Clock.unschedule(self.update)

    def clear_obstacles(self):
        for obs in self.obstacles:
            self.remove_widget(obs)
        self.obstacles = []

    def update(self, dt):
        # Add new obstacle occasionally
        if random.randint(0, 20) == 0:
            obs = Obstacle()
            self.add_widget(obs)
            self.obstacles.append(obs)

        # Move obstacles down
        for obs in self.obstacles[:]:
            obs.y -= 5
            if obs.y < 0:
                self.remove_widget(obs)
                self.obstacles.remove(obs)
                points = 2 if self.double_points else 1
                self.score += points
                if self.progress:
                    self.progress.value = self.score

            # Check collision
            if (self.player.x < obs.x + obs.width and
                self.player.x + self.player.width > obs.x and
                self.player.y < obs.y + obs.height and
                self.player.y + self.player.height > obs.y):
                self.stop_game()
                if self.progress:
                    self.progress.value = 0
                print(f"Game Over! Score: {self.score}")

class SliderDodgeApp(App):
    def build(self):
        root = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Player name input
        self.name_input = TextInput(multiline=False, hint_text="Enter your name")
        root.add_widget(self.name_input)

        # Double points checkbox
        self.checkbox_label = Label(text="Double Points: Off", size_hint_y=None, height=30)
        self.checkbox = CheckBox()
        self.checkbox.bind(active=self.update_checkbox)
        cb_layout = BoxLayout(size_hint_y=None, height=30)
        cb_layout.add_widget(self.checkbox_label)
        cb_layout.add_widget(self.checkbox)
        root.add_widget(cb_layout)

        # Start/stop switch
        self.switch_label = Label(text="Game: Stopped", size_hint_y=None, height=30)
        self.switch = Switch()
        self.switch.bind(active=self.toggle_game)
        sw_layout = BoxLayout(size_hint_y=None, height=30)
        sw_layout.add_widget(self.switch_label)
        sw_layout.add_widget(self.switch)
        root.add_widget(sw_layout)

        # Game area
        self.game_area = GameArea(size_hint_y=0.6)
        root.add_widget(self.game_area)

        # Slider to move player
        self.slider = Slider(min=0, max=350, value=175)
        self.slider.bind(value=self.move_player)
        root.add_widget(self.slider)

        # ProgressBar for score
        self.progress = ProgressBar(max=100, value=0)
        self.game_area.progress = self.progress
        root.add_widget(self.progress)

        return root

    def move_player(self, instance, value):
        self.game_area.player.x = value

    def update_checkbox(self, instance, value):
        self.game_area.double_points = value
        self.checkbox_label.text = "Double Points: On" if value else "Double Points: Off"

    def toggle_game(self, instance, value):
        if value:
            self.switch_label.text = "Game: Running"
            self.game_area.start_game()
        else:
            self.switch_label.text = "Game: Stopped"
            self.game_area.stop_game()

if __name__ == "__main__":
    SliderDodgeApp().run()