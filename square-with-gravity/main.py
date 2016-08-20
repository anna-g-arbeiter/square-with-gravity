### Author: yela @cyela4t
### Description: Gravity makes squares falling down. Try to erase the colorful evil squares before it is too late!
### Category: Game
### License: MIT
### Appname : SQUARE WITH GRAVITY

## https://github.com/annaeg/square-with-gravity

import ugfx
import pyb
import buttons

# IMU is the Inertial Measurement Unit combines accelerometer and gyroscope.
# This uses the https://github.com/emfcamp/Mk3-Firmware/blob/master/lib/imu.py
from imu import IMU

SCREEN_WIDTH = 320
SCREEN_HEIGHT = 240
# More delay will be a more cear background, but the falling is not so nice anymore
# Delay should be always 10*VELOCITY. This feels nice.
# If you double the delay, then set the square spawn time half
VELOCITY = 15 # how fast a square falls down
DELAY = VELOCITY*10 # delay between two rounds
SQR_SPAWN = 15 # spawn a square every x rounds
SQR_MIN = 20 # min size of a square
SQR_MAX = 45 # max size of a square
SIMILARITY = 35 # how similar a square color has to be compared to the BG color to vanish
DYING_COUNTER = 6 # how long a dead square will be visible

imu = IMU()
ugfx.init()
buttons.init()
class Color:
    def __init__(self):
        self.red = pyb.rng() % (0xFF + 1)
        self.blue = pyb.rng() % (0xFF + 1)
        self.green = pyb.rng() % (0xFF + 1)

    def get_color(self):
        return (self.red<<16) + (self.blue<<8) + (self.green)

    def change(self, color, intensity):
        # intensity can be negative
        color += intensity
        if(color < 0):
            color = 0
        if(color > 0xFF):
            color = 0xFF
        return color

    def more_red(self, intensity):
        self.red = self.change(self.red, intensity)
        self.green = self.change(self.green, intensity *-1)
        self.blue = self.change(self.blue, intensity *-1)

    def more_green(self, intensity):
        self.green = self.change(self.green, intensity)
        self.red = self.change(self.red, intensity *-1)
        self.blue = self.change(self.blue, intensity *-1)

    def more_blue(self, intensity):
        self.blue = self.change(self.blue, intensity)
        self.red = self.change(self.red, intensity *-1)
        self.green = self.change(self.green, intensity *-1)

    def rotate(self):
        red = self.red
        blue = self.blue
        green = self.green
        self.red = blue
        self.blue = green
        self.green = red

    def similar_to(self, color):
        if(abs(self.red-color.red) < SIMILARITY and abs(self.blue-color.blue) < SIMILARITY and abs(self.green-color.green) < SIMILARITY):
            return True
        return False

    def draw(self):
        ugfx.clear(ugfx.html_color(self.get_color()))

class Square:
    def __init__(self):
        self.width = (pyb.rng() % (SQR_MAX - SQR_MIN + 1)) + SQR_MIN
        self.x = (int) (SCREEN_WIDTH/2 - self.width/2)
        self.y = (int) (SCREEN_HEIGHT/2 - self.width/2)
        self.color = Color()
        self.build = False
        self.dead = False
        self.dead_counter = 0

    # Checks if there is a collision:
    def collides(self, square):
        if(self is square):
            return False
        if(self.x + self.width < square.x):
            return False
        if(self.x > square.x + square.width):
            return False
        if(self.y + self.width < square.y):
            return False
        if(self.y > square.y + square.width):
            return False
        return True

    def fall(self, acc, squares, x_boost, y_boost):
        if(self.build):
            return
        # (the boost can have values between 5 and -5)
        # x and y will have values between 10 and -10:
        x = (int) (acc['x'] * VELOCITY)
        y = (int) (acc['y'] * VELOCITY)
        self.x = self.x + x + x_boost
        self.y = self.y + y + y_boost
        for s in squares:
            if(self.collides(s)):
                self.build = True
        if(self.y + self.width >= SCREEN_HEIGHT):
            self.y = SCREEN_HEIGHT - self.width
            self.build = True
        elif(self.y < 0):
            self.y = 0
            self.build = True
        if(self.x + self.width >= SCREEN_WIDTH):
            self.x = SCREEN_WIDTH - self.width
            self.build = True
        elif(self.x < 0):
            self.x = 0
            self.build = True

    def draw(self):
        if(self.dead):
            self.dead_counter = self.dead_counter + 1
            if(self.dead_counter % 2 == 1):
                ugfx.area(self.x, self.y, self.width, self.width, ugfx.BLACK)
            else:
                ugfx.area(self.x, self.y, self.width, self.width, ugfx.WHITE)
        else:
            ugfx.area(self.x, self.y, self.width, self.width, ugfx.html_color(self.color.get_color()))

def init():
    ugfx.clear(ugfx.BLUE)
    ugfx.set_default_font(ugfx.FONT_TITLE)
    ugfx.text(95, 50, "SQUARE", ugfx.YELLOW)
    ugfx.text(60, 80, "WITH GRAVITY", ugfx.YELLOW)
    ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
    ugfx.text(70, 180, "PRESS A TO START", ugfx.YELLOW)
    ugfx.text(70, 200, "PRESS B FOR HELP", ugfx.YELLOW)
    ugfx.area(260, 95, 25, 25, ugfx.RED)
    ugfx.area(240, 120, 30, 30, ugfx.YELLOW)
    ugfx.area(250, 150, 60, 60, ugfx.html_color(0xFF00FF))
    pyb.delay(1000)

def repaint(squares, color, score):
    color.draw()
    for s in squares:
        s.draw()
    ugfx.text(10, 10, "SCORE: " + str(score), ugfx.YELLOW)

def game_over(score):
    ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
    ugfx.text(100, 120, "GAME OVER!", ugfx.YELLOW)
    ugfx.set_default_font(ugfx.FONT_SMALL)
    ugfx.text(10, 220, "Press Menu for a new game", ugfx.YELLOW)

def new_game():
    color = Color()
    squares = []
    # Influence the falling of the square with the joystic. This will set the boost:
    x_boost = 0
    y_boost = 0
    start_square = Square()
    squares.append(start_square)
    score = start_square.width
    counter = 0
    while not buttons.is_pressed("BTN_MENU"):
        pyb.delay(DELAY)
        acc = imu.get_acceleration()
        x = acc['x'] # RED
        y = acc['y'] # GREEN
        z = acc['z'] # BLUE
        if(abs(x) > abs(y) and abs(x) > abs(z)):
            color.more_red((int) (x * 10))
        elif(abs(y) > abs(x) and abs(y) > abs(z)):
            color.more_blue((int) (y * 10))
        elif(abs(z) > abs(x) and abs(z) > abs(y)):
            color.more_green((int) (y * 10))
        if buttons.is_pressed("BTN_A"):
            color.rotate()
        if buttons.is_pressed("BTN_B"):
            for s in squares:
                s.color.rotate()
        if buttons.is_pressed("JOY_UP"):
            y_boost = -5
        if buttons.is_pressed("JOY_DOWN"):
            y_boost = 5
        if buttons.is_pressed("JOY_LEFT"):
            x_boost = -5
        if buttons.is_pressed("JOY_RIGHT"):
            x_boost = 5
        for s in squares:
            if(s.dead):
                if(s.dead_counter >= DYING_COUNTER):
                    squares.remove(s)
            else:
                s.fall(acc, squares, x_boost, y_boost)
                if(color.similar_to(s.color)):
                    s.dead = True
        x_boost = 0
        y_boost = 0
        repaint(squares, color, score)
        counter = counter + 1
        if(counter == SQR_SPAWN):
            s = Square()
            squares.append(s)
            for s2 in squares:
                if(s.collides(s2)): # GAME OVER
                    game_over(score)
                    while not buttons.is_pressed("BTN_MENU"):
                        pyb.delay(DELAY)
                    return
            score = score + s.width
            counter = 0

init()
while not buttons.is_pressed("BTN_MENU"):
    if buttons.is_pressed("BTN_A"):
        new_game()
        init()
    if buttons.is_pressed("BTN_B"):
        ugfx.clear(ugfx.BLUE)
        ugfx.set_default_font(ugfx.FONT_SMALL)
        ugfx.text(10, 10, "* The BG color changes based on orientation", ugfx.YELLOW)
        ugfx.text(10, 30, "* A rotates BG color, B rotates square colors", ugfx.YELLOW)
        ugfx.text(10, 50, "* Squares always fall down", ugfx.YELLOW)
        ugfx.text(10, 70, "* Control the falling square with the joystick", ugfx.YELLOW)
        ugfx.text(10, 90, "* A square vanishes,", ugfx.YELLOW)
        ugfx.text(50, 110, "if the background color is the same", ugfx.YELLOW)
        ugfx.text(10, 130, "* Game is over,", ugfx.YELLOW)
        ugfx.text(50, 150, "if a new square has not enough space", ugfx.YELLOW)
        ugfx.set_default_font(ugfx.FONT_MEDIUM_BOLD)
        ugfx.text(70, 180, "PRESS A TO START", ugfx.YELLOW)
        while not buttons.is_pressed("BTN_A"):
            pyb.delay(DELAY)
        new_game()
        init()
    pyb.delay(DELAY)
