# Falling Block Game
This was originally part of a project for CompSci 687 (Reinforcement Learning) at UMass Amehrst during Fall 2023. My partner and I created a falling block game to use as an environment to train an agent to play games of similar design. The game is written in Python and uses PyGame for the display.

I'm forking to try and polish up the game. Fix glitches, improve display, etc

## How to Install and Play
Install the latest version of Python 3.11 for your platform. Install PyGame using `pip install pygame`. Then run `python3 display.py` to start the game.

The primary goal of the game is to control the falling blocks to form complete rows. When a row is completed, it is removed from the playing field and the blocks above are shifted down. If too many blocks build up without being cleared, the game ends. Alternatively, you win if you clear enough rows.

## Controls
```
←: Move left
→: Move right
z: Rotate counter-clockwise
x: Rotate clockwise
c: Swap w/ stored block
space: Force drop
↓: Fast drop
```

## How to use as RL env
To use as environment for Reinforcement Learning, make sure the latest version of numpy and OpenAI gymnasium are installed. Then in your file simply import our environment with `import block_game_env`, and create an OpenAI gym environment with `gymnasium.make('BlockGame-v0')`.

However, the developers highly recommend you rewrite the environment yourself at the moment. The current environment needs a good portion of elbow grease to be something something. If you are a grader for the class, please pretend you haven't seen this :P

## Copyright
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Credits
- Originally by: Raymond Li, Yi Wei
- Current maintainer: Yi Wei


