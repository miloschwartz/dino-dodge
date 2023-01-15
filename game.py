"""
-----======= [ EXPLANATION OF DINO DODGE] =======-----

Our game will be called Dino Dodge.

Description:
In our game the player will be a dinosaur that runs side to side at the bottom of the display. The goal of the player is
to avoid the meteors falling from the sky by dodging them. There will be several waves that increase in difficulty.
Waves become more difficult based on the spawn frequency, speed, and duration of each wave, as well as the amount of
extra lives the player is allowed to collect per wave. The player starts with one life and can collect extra lives each
wave. The player's lives do not reset each wave, rather, the current lives carry over. Finally, the player wins by completing
the final wave without running out of lives, and the player loses if they run out of lives before the end of the current wave.

How to play:
Use the left and right arrow keys to move horizontally, and the space bar or up arrow key to jump vertically. The goal of
the game is to complete all waves without dying and with the highest score possible. You will die if you run out of lives.
A live is lost each time that you collide with a falling meteor, and 10 points are deducted from your score. Additional lives
will fall; collecting these extra lives will be important as the waves progress and become more difficult. Additionally,
the collectable lives increase your score by 25 points per live collected. You also get 100 points for successfully completing a wave.

To begin the game, press [RETURN] on your keyboard. The same key will restart the game when you either die or survive.

---- Basic Features ----

User Input:
The player will be able to move horizontally side to side using the left and right arrow keys.
We will implement this through a function that handles player movement which checks for keyboard input and moves the
player's x position accordingly.

Game Over:
The game will end when the player runs out of lives. The player will lose one life for each meteor that hits them.
The game will also end if the player successfully completes all waves and reaches the end.

Graphics/Images:
For the player, we will make a custom animated spite. For each meteor we will also include a custom-made sprite.
Finally, the background will not simply be a solid color, but we will design one that looks like the sky.

---- Additional Features ----

Restart from Game Over:
When the player is out of lives and the game ends, we will allow the player to restart the game by pressing the [return] key.
This will place the player back at wave 1 and reset the score and lives. We will implement this by checking for keyboard input
if the game is not running and will prompt the player to play again if the game is not running.

Sprite Animation:
The player sprite will be an animated dinosaur that walks side to side. To implement this feature, we will design a
custom sprite sheet that contains several frames of a pixel art dino walking. Then we will loop through the sprite
sheet and flip the images depending on in which direction the player is moving.

Collectables:
The player will have the opportunity to collect extra lives in the form of a collectible heart sprite. Collectibles will
be spawned at regular intervals and there will be a limited number per wave. Once a player touches a heart collectible
their lives will be increased by one and their score by 25.

Timer:
There will be a timer on display that counts the amount of seconds left before the wave is over.
By using an accumulator, we can subtract (1 / frame rate) from the duration for each tick to achieve a basic countdown
clock. Once the timer reaches 0, we progress the game to the next wave.

Multiple Levels:
There will be a series of waves that progressively get more difficult as the player successfully progresses. We will
store each wave and its associated settings (duration, meteor speed, etc) in a list of dictionaries which we will
access when we begin a new wave via a function.
"""

import uvage
import random

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
tick_rate = 60
camera = uvage.Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

wave_clock = 0
meteor_spawn_clock = 0
collectable_spawn_clock = 0
frame = 0
score = 0
current_lives = 1
current_wave = 0

health_bar_images = uvage.load_sprite_sheet("healthbar.png", rows=9, columns=1)
dino_images = uvage.load_sprite_sheet("dino.png", rows=1, columns=4)

health_bar = uvage.from_image(SCREEN_WIDTH / 2, 750, health_bar_images[0])
player = uvage.from_image(100, 100, dino_images[0])
ground = uvage.from_image(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50, "ground.png")
background = uvage.from_image(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, "background.png")

is_running = False
facing_right = False

meteors = []
collectables = []
# each wave and their settings in consecutive order
waves = [{"spawn_interval": 0.425, "min_speed": 4, "max_speed": 7, "duration": 30, "max_collectables": 1},
         {"spawn_interval": 0.25, "min_speed": 7, "max_speed": 12, "duration": 30, "max_collectables": 2},
         {"spawn_interval": 0.175, "min_speed": 10, "max_speed": 15, "duration": 30, "max_collectables": 5},
         {"spawn_interval": 0.25, "min_speed": 15, "max_speed": 20, "duration": 30, "max_collectables": 5}]


def spawn_meteor(wave):
    '''
    This function creates a new meteor with a random x (spawn) position, scale, and speed, as well as adds
    the new meteor to the list of all meteors.
    :param wave: The given wave as a dictionary of settings for the wave. This function uses the min_speed and max_speed
    of the given wave to determine a random speed for the meteor.
    :return: This function does not return anything
    '''
    global meteors
    # randomize the x position of the meteor
    x_pos = random.randrange(0, SCREEN_WIDTH)
    y_pos = -60
    # randomize the scale of the meteor
    scale = random.uniform(0.4, 1.5)
    # randomize the speed of the meteor
    speed = random.randrange(wave["min_speed"], wave["max_speed"])
    meteor = uvage.from_image(x_pos, y_pos, "meteor.png")
    meteor.scale_by(scale)
    meteors.append([meteor, speed])


def spawn_collectable():
    '''
    This function creates a new collectable with a random x (spawn) position, as well as adds the new collectable to
    the list of all collectables.
    :return: This function does not return anything
    '''
    global collectables
    # randomize the x position of the collectable
    x_pos = random.randrange(0, SCREEN_WIDTH)
    y_pos = -60
    collectable = uvage.from_image(x_pos, y_pos, "collectable.png")
    collectables.append(collectable)


def clear_meteors():
    '''
    This function clears all the previously spawned meteors by setting the meteors list and meteor_spawn_clock to
    their default values.
    :return: This function does not return anything
    '''
    global meteors, meteor_spawn_clock
    meteors = []
    meteor_spawn_clock = 0


def clear_collectables():
    '''
    This function clears all the previously spawned collectables by setting the collectables list and
    collectable_spawn_clock to their default values.
    :return: This function does not return anything
    '''
    global collectables, collectable_spawn_clock
    collectables = []
    collectable_spawn_clock = 0


def play_wave(wave):
    '''
    This function plays through the given wave for as long as it is called. This function handles the following aspects
    of playing through the current wave:
    1. Display score, timer, and current wave
    2. Spawn meteors and spawn collectables
    3. Make meteors and collectables "fall down" by manipulating their y movement
    4. Handle the event that if a player touches a meteor, they lose a life and their score is reduced
    5. Handle the event that if a player touches a collectable, they gain a life and their score is increased
    :param wave:
    :return:
    '''
    global meteor_spawn_clock, meteors, collectable_spawn_clock, collectables, score, current_lives
    # display the wave timer
    if int(wave["duration"] - wave_clock) > 1 or int(wave["duration"] - wave_clock) == 0:
        camera.draw((str(int(wave["duration"] - wave_clock + 1))) + " seconds left", 35, "white",
                    SCREEN_WIDTH / 2, 80)
    # if there is one second left, make 'seconds' singular
    elif int(wave["duration"] - wave_clock) == 1:
        camera.draw((str(int(wave["duration"] - wave_clock + 1))) + " second left", 35, "white",
                    SCREEN_WIDTH / 2, 80)
    # display the 3-second warning countdown before the wave ends
    if abs(int(wave_clock) - (wave["duration"])) <= 3:
        camera.draw(str(abs(int(wave_clock) - (wave["duration"]))), 150, "white",
                    SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    # display the current wave progress
    camera.draw("Wave: " + str(current_wave + 1) + "/" + str(len(waves)) + "  |  " + "Score: " + str(score), 35,
                "white", SCREEN_WIDTH / 2, 50)

    # spawn a new meteor at a regular interval depending on the given spawn_interval of the current wave
    meteor_spawn_clock += 1 / tick_rate
    if meteor_spawn_clock >= wave["spawn_interval"]:
        meteor_spawn_clock = 0
        spawn_meteor(wave)
    # spawn new collectable at half-way point if max_collectables is set to 1 and the player is not maxed out on lives
    collectable_spawn_clock += 1 / tick_rate
    if wave["max_collectables"] == 1 and collectable_spawn_clock >= wave["duration"] / 2 and current_lives < 9:
        collectable_spawn_clock = 0
        spawn_collectable()
    # spawn a new collectable at regular interval depending on number of max_collectables and player not maxed out lives
    elif wave["max_collectables"] > 1 and collectable_spawn_clock >= (wave["duration"] - 5) / wave["max_collectables"] \
            and current_lives < 9:
        collectable_spawn_clock = 0
        spawn_collectable()

    # move all meteors downward depending on the randomized speed determined when the meteor was originally spawned
    for meteor in meteors:
        meteor[0].y += meteor[1]
        # if player contacts a meteor, reduce lives by one and score by 10
        if player.touches(meteor[0]):
            current_lives -= 1
            meteors.remove(meteor)
            score -= 10
        # destroy the meteor when it leaves the visible area
        if meteor[0].y >= SCREEN_HEIGHT + 200:
            meteors.remove(meteor)
    # move all collectables downward
    for collectable in collectables:
        collectable.y += 4
        # if player contacts a collectable, increase lives by one and score by 25
        if player.touches(collectable):
            collectables.remove(collectable)
            score += 25
            current_lives += 1
        # destroy the collectable when it leaves the visible area
        if collectable.y >= SCREEN_HEIGHT + 200:
            collectables.remove(collectable)


def cycle_waves():
    '''
    This function cycles through each wave in the waves list and plays the current wave for its specified period. This
    function also handles the intermission screen that counts down before beginning a new wave.
    :return: This function does not return anything
    '''
    global waves, wave_clock, current_wave, is_running, player, score
    wave_clock += 1 / tick_rate
    # while the duration of the wave is not over, play the current wave
    if wave_clock <= waves[current_wave]["duration"]:
        play_wave(waves[current_wave])
    # display the intermission screen between waves
    elif wave_clock <= waves[current_wave]["duration"] + 3 and current_wave != len(waves) - 1:
        # move the screen between waves
        camera.clear("black")
        camera.draw("Wave " + str(current_wave + 1) + " of " + str(len(waves)) + " complete!", 50, "white",
                    SCREEN_WIDTH / 2, 150)
        camera.draw("Next wave starting in:", 50, "white", SCREEN_WIDTH / 2, 200)
        camera.draw(str(abs(int(wave_clock) - (waves[current_wave]["duration"] + 3))), 150, "white",
                    SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        camera.draw("+100 pts!", 75, "yellow", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 200)
        camera.draw("Score: " + str(score + 100), 50, "yellow", SCREEN_WIDTH / 2, SCREEN_HEIGHT - 150)
        clear_meteors()
        clear_collectables()
    # move on to the next wave
    else:
        score += 100
        wave_clock = 0
        player.x = SCREEN_WIDTH / 2
        player.y = SCREEN_HEIGHT - 150
        current_wave += 1


def handle_player():
    '''
    This function handles player movement and player animations. Specifically, this function allows the player to move
    horizontally, and when doing so, plays the walk animation. Also, this function handles the vertical movement,
    aka jumping, and plays the jump animation.
    :return: This function does not return anything
    '''
    global player, facing_right, frame
    player_speed = 5
    is_moving = False
    # handle movement to the right
    if uvage.is_pressing("right arrow") or uvage.is_pressing("d"):
        if player.x <= SCREEN_WIDTH:
            player.x += player_speed
            is_moving = True
            if not facing_right:
                facing_right = True
                player.flip()
    # handle movement to the left
    if uvage.is_pressing("left arrow") or uvage.is_pressing("a"):
        if player.x >= 0:
            player.x += -player_speed
            is_moving = True
            if facing_right:
                facing_right = False
                player.flip()

    # handle player jumps
    player.speedy += 1
    if player.touches(ground):
        player.speedy = 0
        player.move_to_stop_overlapping(ground)
        if uvage.is_pressing("space") or uvage.is_pressing("up arrow") or uvage.is_pressing("w"):
            player.speedy = - 10
    else:
        is_moving = True
    player.move_speed()

    # handle player animations for horizontal movement and vertical movement
    if not is_moving:
        player.image = dino_images[0]
    # horizontal, walk, animation
    elif player.touches(ground):
        frame += 12 / tick_rate
        if frame > 3:
            frame = 0
        player.image = dino_images[int(frame)]
    # vertical, jump, animation
    elif not player.touches(ground):
        player.image = dino_images[3]


def handle_health_bar():
    '''
    This function handles the visible element of the health bar at the bottom of the screen by setting the health bar
    image in the sprite sheet to the current amount of lives.
    :return: This function does not return anything
    '''
    global health_bar
    health_bar.image = health_bar_images[current_lives - 1]


def reset_game():
    '''
    This function resets the game to its beginning state by setting global variables to default values, clearing lists,
    and resetting the players position.
    :return: This function does not return anything
    '''
    global current_lives, wave_clock, current_wave, player, score
    current_wave = 0
    wave_clock = 0
    score = 0
    current_lives = 1
    clear_meteors()
    clear_collectables()
    player.x = SCREEN_WIDTH / 2
    player.y = SCREEN_HEIGHT - 150


def tick():
    global is_running
    camera.draw(background)
    if uvage.is_pressing("return") and not is_running:
        reset_game()
        is_running = True

    # player wins/reaches the end
    if current_wave == (len(waves)):
        is_running = False
        camera.draw("YOU SURVIVED", 100, "white", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        camera.draw("+100 pts!", 75, "yellow", SCREEN_WIDTH / 2, 200)
        camera.draw("Final Score: " + str(score), 50, "yellow", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150)
    # player dies
    elif current_lives <= 0:
        is_running = False
        camera.draw("YOU DIED", 100, "white", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
        camera.draw("Final Score: " + str(score), 50, "yellow", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 150)

    # play the game
    if is_running:
        for meteor in meteors:
            camera.draw(meteor[0])
        for collectable in collectables:
            camera.draw(collectable)
        camera.draw(ground)
        handle_player()
        camera.draw(player)
        handle_health_bar()
        camera.draw(health_bar)
        cycle_waves()
    else:
        camera.draw("Press [RETURN] To Play", 50, "white", SCREEN_WIDTH / 2, 50)
    camera.display()


uvage.timer_loop(tick_rate, tick)
