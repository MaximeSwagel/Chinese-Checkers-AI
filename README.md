# 02180_intro_to_ai_group_28
#This project was done in a group of 3 people for an assignment in course 02180 Intro to AI at DTU. Our goal was to implement an AI capable of playing a board game and implement the board game. 

We implemented the board game Chinese Checkers and AI agent capable of playing the game against a human player.

#The full assignment can be found in the Board_game_assignment_2025.pdf file

# How to run the game
First, install the necessary packages:
```bash
pip install -r requirements.txt
```
Then, you can play the game using:
```bash
python .\main.py
```

# How to play the game
You the human is player 1 (RED)

During your turn you can click on one of the red pieces, valid moves are shown with a yellow ring, click on a valid position to move.
After that please wait for the AI to move, this can take a couple of seconds depending on your hardware and whether or not you decide to use the c version.

You win by geting all your pieces from the top to the buttom.


# Optional
We originally used c code for two select BMI2 instructions as they weren't natively supported in python.
To avoid the complications of having to compile the c code we made a python fallback.
This python fallback works the same but is slower, but we decide it was best that it was the default option.

If you wish to use the c code, follow the steps below:

## compile c code

### Linux and macos
You should be able to just run this command to compile the code:
```bash
gcc -mbmi2 -shared -o bmi2_bitops.so -fPIC bmi2_bitops.c
```

### Windows
The windows compilation is a bit more involved.

We have provided a pre-compiled "bmi2_bitops.so" that maybe works right out of the box.

If not you can follow the steps provided:

Go to
https://winlibs.com/

And download the latest version

add the bin (likely C:\mingw64\bin) to path 
https://www.java.com/en/download/help/path.html

1. Use terminal
2. navigate to to root folder:
```bash
cd /path/to/02180_intro_to_ai_group_28
```
3. use this command:
```bash
gcc -mbmi2 -shared -o bmi2_bitops.so -fPIC bmi2_bitops.c
```

After compiling the c code remember to change the "use_python_bmi2" variable in "config.py" to False to use the c code.
