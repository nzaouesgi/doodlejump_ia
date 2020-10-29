import random
import time

X = 0
Y = 1

GAME_WIDTH = 400
GAME_HEIGHT = 10000

# 60 frames per second
FRAME_TIME_MS = 1000  // 60

PLATFORM_WIDTH = 50
AGENT_WIDTH = 40

# maximum height of a single jump
JUMP_MAX_HEIGHT = 50

ACTION_LEFT = 1
ACTION_RIGHT = 2
ACTION_NONE = 3

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
        self.current_jump_height = 0

        self.dead = False
        self.has_won = False

    def update_y (self, time_elapsed):

        while time_elapsed > 0:

            if self.is_jumping:
                
                self.location = (self.location[X], self.location[Y] + 1)
                self.current_jump_height += 1
                
                if self.current_jump_height >= JUMP_MAX_HEIGHT:
                    
                    self.is_jumping = False
                    self.current_jump_height = 0

            else:
                self.location = (self.location[X], self.location[Y] - 1)
            
            i = 0

            for platform in self.environment.platforms:

                if self.location[Y] - 1 == platform[Y]:
                    
                    if self.location[X] < platform[X] + PLATFORM_WIDTH:

                        if self.location[X] > platform[X]:

                            self.is_jumping = True
                            self.current_jump_height = 0

                            self.current_platform = i
                i += 1
            

            time_elapsed -= 25

    def update_x (self, action, time_elapsed):

        while time_elapsed > 0:

            if action == ACTION_LEFT:
                self.location = (self.location[X] + 1, self.location[Y])
            
            elif action == ACTION_RIGHT:
                self.location = (self.location[X] - 1, self.location[Y])

            if self.location[X] > GAME_WIDTH:
                self.location = (0 - AGENT_WIDTH, self.location[Y])
            
            elif self.location[X] < (-AGENT_WIDTH):
                self.location = (GAME_WIDTH, self.location[Y])

            time_elapsed -= 25

    def update(self, action, time_elapsed):

        self.update_x(action, time_elapsed)
        self.update_y(time_elapsed)

        if self.location[Y] >= GAME_HEIGHT:
            self.has_won = True

        if self.location[Y] < self.environment.platforms[self.current_platform][Y]:
            self.dead = True


class Environment:
    
    def __init__(self):
        
        self.platforms = self.generate_platforms()
        

    def generate_platforms(self):

        platforms = []

        current_height = 0

        while current_height <= GAME_HEIGHT:

            platform_x = random.randint(
                0, 
                GAME_WIDTH - PLATFORM_WIDTH
            )
            platform_y = random.randint(
                current_height, 
                current_height + (JUMP_MAX_HEIGHT - 10)
            )

            current_height = platform_y

            platform = (platform_x, platform_y)

            platforms.append(platform)

        return platforms


def get_time_ms():
    return int(round(time.time() * 1000))

def get_current_frame_time(last_frame_time):
    return get_time_ms() - last_frame_time

if __name__ == "__main__":

    environment = Environment()
    agent = Agent(environment)

    last_frame_time = get_time_ms()

    # Main loop
    while agent.dead == False and agent.has_won == False:

        time_elapsed = get_current_frame_time(last_frame_time)

        # Wait for next frame and optimize with sleep
        while time_elapsed < FRAME_TIME_MS:
            time.sleep((FRAME_TIME_MS / 2) / 1000)
            time_elapsed = get_current_frame_time(last_frame_time)

        action = ACTION_NONE

        agent.update(action, time_elapsed)

        last_frame_time = get_time_ms()

    print("Game finished. Agent %s!" % ("Lost" if agent.has_won else "Won"))