import random
import time
import arcade

X = 0
Y = 1

GAME_WIDTH = 400
GAME_HEIGHT = 10000

VIEWPORT_WIDTH = 600
VIEWPORT_HEIGHT = 1000

PLATFORM_WIDTH = 50

# Gravity
GRAVITY = 1500

# Damping - Amount of speed lost per second
DEFAULT_DAMPING = 1.0
PLAYER_DAMPING = 0.4

# Friction between objects
PLAYER_FRICTION = 1.0
WALL_FRICTION = 0.7

# Mass (defaults to 1)
PLAYER_MASS = 1

# Keep player from going too fast
PLAYER_MAX_HORIZONTAL_SPEED = 450
PLAYER_MAX_VERTICAL_SPEED = 1600

# Force applied when moving left/right in the air
PLAYER_MOVE_FORCE_IN_AIR = 900

# Strength of a jump
PLAYER_JUMP_IMPULSE = 1800

# Force applied while on the ground
PLAYER_MOVE_FORCE_ON_GROUND = 8000

class Game(arcade.Window):

    def __init__ (self):
        
        super().__init__(VIEWPORT_WIDTH, VIEWPORT_HEIGHT, "Doodle Jump")

        self.environment = Environment()
        self.agent = Agent(self.environment)

        self.platform_sprites_list = None
        self.player_sprite = None

        self.left_pressed = False
        self.right_pressed = False

        self.physics_engine = None

        arcade.set_background_color(arcade.csscolor.FLORAL_WHITE)

    def setup(self):

        self.platform_sprites_list = arcade.SpriteList(use_spatial_hash=True)
        
        self.player_sprite = arcade.Sprite("resources/doodle_left.png", 0.5)

        self.player_sprite.left = self.agent.location[X]
        self.player_sprite.bottom = self.agent.location[Y]

        for platform in self.environment.platforms:

            platform_sprite = arcade.Sprite("resources/platform.png", 1)

            platform_sprite.left = platform[X]
            platform_sprite.top = platform[Y]

            self.platform_sprites_list.append(platform_sprite)

    def on_draw (self):

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        self.platform_sprites_list.draw()
        self.player_sprite.draw()

    def on_key_press(self, key, modifiers):

        if key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):

        if key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False

    def on_update(self, delta_time):

        if self.left_pressed and not self.right_pressed:

            print(delta_time)
            
        elif self.right_pressed and not self.left_pressed:

            print(delta_time)



class Agent:

    def __init__(self, environment):

        self.environment = environment

        # Agent startup location is the lowest platform.
        self.location = (
            environment.platforms[0][X] + (PLATFORM_WIDTH / 2), 
            environment.platforms[0][Y] + 5
        )

        self.current_platform = 0

        self.is_jumping = False

        self.dead = False
        self.has_won = False


class Environment:
    
    def __init__(self):
        
        self.platforms = self.generate_platforms()
        

    def generate_platforms(self):

        current_height = 50

        decay = 150

        platforms = [
            ((GAME_WIDTH / 2) - PLATFORM_WIDTH / 2, current_height)
        ]

        while current_height <= GAME_HEIGHT:

            platform_x = random.randint(
                0, 
                GAME_WIDTH - PLATFORM_WIDTH
            )
            platform_y = random.randint(
                current_height + 30, 
                current_height + (decay - 10)
            )

            current_height = platform_y

            platform = (platform_x, platform_y)

            platforms.append(platform)

        return platforms

if __name__ == "__main__":

    window = Game()
    window.setup()
    arcade.run()