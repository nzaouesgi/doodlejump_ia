import random
import time
import arcade

X = 0
Y = 1

GAME_WIDTH = 400
GAME_HEIGHT = 30000

VIEWPORT_WIDTH = 600
VIEWPORT_HEIGHT = 1000

PLATFORM_WIDTH = 50

MOVE_X = 10
MOVE_Y = 20

MAX_JUMP_HEIGHT = 250

GRAVITY = 0.60


def load_texture_pair(filename):
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class Game(arcade.Window):

    def __init__(self):

        super().__init__(VIEWPORT_WIDTH, VIEWPORT_HEIGHT, "Doodle Jump")

        self.environment = Environment()
        self.agent = Agent(self.environment)

        self.left_pressed = False
        self.right_pressed = False

        self.game_height = 0

        self.background = arcade.load_texture("resources/bck.png")

    def setup(self):

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.agent.sprite,
                                                             arcade.SpriteList(
                                                                 use_spatial_hash=True),
                                                             GRAVITY)
        self.physics_engine.disable_multi_jump()

    def on_draw(self):

        # Clear the screen to the background color
        arcade.start_render()

        (left, _right, bottom, _top) = arcade.get_viewport()

        arcade.draw_lrwh_rectangle_textured(left, bottom,
                                    VIEWPORT_WIDTH, VIEWPORT_HEIGHT,
                                    self.background)

        # Draw our sprites
        self.environment.platform_sprites.draw()
        self.agent.sprite.draw()

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

    def set_effective_platforms(self):

        effective_platforms = arcade.SpriteList(use_spatial_hash=True)

        for platform in self.environment.platform_sprites:

            if platform.top <= self.agent.sprite.bottom:

                effective_platforms.append(platform)

        self.physics_engine.platforms = effective_platforms

    def move_left(self):
        self.agent.sprite.change_x = -MOVE_X
        self.agent.sprite.set_texture(0)

    def move_right(self):
        self.agent.sprite.change_x = MOVE_X
        self.agent.sprite.set_texture(1)

    def scroll_viewport(self):

        (_left, _right, bottom, top) = arcade.get_viewport()

        new_bottom = bottom
        new_top = top

        if bottom < self.game_height:
            new_bottom = bottom + 10
        if new_top < VIEWPORT_HEIGHT + self.game_height:
            new_top = top + 10

        arcade.set_viewport(
                0,
                VIEWPORT_WIDTH,
                new_bottom,
                new_top
            )

    def on_update(self, delta_time):

        self.set_effective_platforms()

        if self.left_pressed:
            self.move_left()
        elif self.right_pressed:
            self.move_right()
        else:
            self.agent.sprite.change_x = 0

        if self.agent.sprite.change_y <= 0.0:

            if self.physics_engine.can_jump():

                self.game_height = self.agent.sprite.bottom - \
                    self.environment.platform_sprites[0].height

                self.physics_engine.jump(MOVE_Y)

        self.physics_engine.update()

        if self.agent.sprite.right < 0:
            self.agent.sprite.left = VIEWPORT_WIDTH
        elif self.agent.sprite.left > VIEWPORT_WIDTH:
            self.agent.sprite.right = 0
        
        self.scroll_viewport()


class Agent:

    def __init__(self, environment):

        self.environment = environment

        first_platform = environment.platform_sprites[0]

        filename = "resources/doodle_left.png"

        self.sprite = arcade.Sprite(scale=0.5)
        for t in load_texture_pair(filename):
            self.sprite.append_texture(t)
        self.sprite.set_texture(0)
        self.sprite.center_x = first_platform.center_x
        self.sprite.bottom = first_platform.bottom + first_platform.height

        self.is_jumping = False
        self.current_jump_height = 0

        self.dead = False
        self.has_won = False


class Environment:

    def __init__(self):

        self.platform_sprites = arcade.SpriteList(use_spatial_hash=True)

        for coordinates in self.generate_platforms_coordinates():

            sprite = arcade.Sprite("resources/platform.png", 1)

            sprite.center_x = coordinates[X]
            sprite.center_y = coordinates[Y]

            self.platform_sprites.append(sprite)

    def generate_platforms_coordinates(self):

        current_height = 50

        platforms = [
            ((GAME_WIDTH / 2), current_height)
        ]

        min_decay = 30
        max_decay = 60

        while current_height <= GAME_HEIGHT:

            platform_x = random.randint(
                0,
                GAME_WIDTH - PLATFORM_WIDTH
            )
            platform_y = random.randint(
                current_height + min_decay,
                current_height + MAX_JUMP_HEIGHT
            )

            if random.choice([ True, False ]):
                if min_decay < max_decay:
                    min_decay += 1

            current_height = platform_y

            platform = (platform_x, platform_y)

            platforms.append(platform)

        return platforms


if __name__ == "__main__":

    window = Game()
    window.setup()
    arcade.run()
