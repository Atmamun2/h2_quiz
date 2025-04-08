import random
import time
import csv
import os
import re


"""Hangman Game with Time and Score Features

This module implements a text-based Hangman game with the following features:
- Multiple difficulty levels (easy, medium, hard)
- Time-based gameplay with countdown
- Score tracking system
- Custom word support via CSV files
- Save/load game functionality
- Hint system that activates after multiple incorrect guesses

The game uses a procedural programming approach with functions and dictionaries to manage game state, rather than classes and objects.
"""

# Add clear screen function
def clear_screen():
    """Clear the terminal screen in a cross-platform way."""
    # For windows
    if os.name == 'nt':
        os.system('cls') 
    # For mac and Linux
    else:
        os.system('clear')

# Constants
MAX_SCORE = 100
INITIAL_TIME = 30
MAX_INCORRECT_GUESSES = 10
HINT_THRESHOLD = 3
CUSTOM_WORD_FILE = "custom_words.csv"
DIFFICULTY_PARAMS = {
    "easy": (4, 5),
    "medium": (6, 7),
    "hard": (8, 20)
}

def create_game_state(word="", guessed_letters=None, score=MAX_SCORE, time_left=INITIAL_TIME):
    """Create a new game state dictionary"""
    return {
        "word": word.lower(),
        "guessed_letters": set(guessed_letters) if guessed_letters else set(),
        "score": score,
        "time_left": time_left,
        "incorrect_guesses": 0,
        "hint_used": False
    }

def update_time(state, elapsed):
    """Update the remaining time and return if time is still avaliable"""
    state["time_left"] -= int(elapsed)
    return state["time_left"] > 0

def add_guess(state, guess):
    """Add a guess to the state and return if it was correct"""
    state["guessed_letters"].add(guess)
    return guess in state["word"]

def get_valid_input(prompt, validator, error_msg):
    while True:
        response = input(prompt).strip().lower()
        if validator(response):
            return response # if the response isn't returned
        print(error_msg) # it will print out this error message, due to the return being the final output of the function

def load_word_list(filename):
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, "r") as file:


            # loads the word list, and for the first element in the csv file, if the row exists every string character is apart of the alphabet .strip() while along having no spaces in the word (singular word) then it will return that word.
            return [row[0].lower() for row in csv.reader(file)
                    if row and row[0].strip().isalpha()]

    except Exception as e:
        print(f"Error loading words from {filename}: {e} ") # catches the exception that it had an erorr printing the word from filename e.
        return []

def save_game_state(filename, state):
    # Replace any invalid filname characters with underscores
    filename = re.sub(r'[^a-zA-Z0-9\s\.]', "_", filename)

    # Add .save extension if not already present
    if not filename.endswith(".save"): # used ".save" instead of '.save'
        filename += ".save" # denoted same as filename = filename + '.save'
    
    # if the player hasn't already saved the filename by endinf with .save, you add it to the end of the filename saving accordingly write the try and except:

    try:
        with open(filename, "w") as file:
            file.write(f"{state['word']} \n")
            file.write(f"{','.join(state['guessed_letters'])}\n")
            file.write(f"{state['time_left']}\n")
        print(f"Game saved successful as {filename}!")
    
    except Exception as e:
        print(f"Error saving game: {e} ")

def load_game_state(filename):
    # Add .save extension if not already present
    if not filename.endswith(".save"):
        filename += ".save"

    # every time you load the game it adds the .save extension
    try:
        with open(filename, "r") as file:
            lines = [line.strip() for line in file]
            return create_game_state(
                word=lines[0],
                guessed_letters=lines[1].split(",") if lines[1] else [],
                score=int(lines[2]),
                time_left = int(lines[3])

                # goes through each section of the line file, takes the word from the 1st element, guessed letters from the 2nd
                # score from the third, and the time duration left from the third as a numerical value.
            )
        
    except Exception as e:
        print(f"Error loading game: {e}")
        return None
    

def new_game():
    difficulty = get_valid_input(
        "Choose difficulty (easy/medium/hard): ",
        lambda d: d in DIFFICULTY_PARAMS, 
        "Invalid difficulty! Please choose from easy/medium/hard."
    )

    min_len, max_len = DIFFICULTY_PARAMS[difficulty]
    words = [
        word for word in
        load_word_list(CUSTOM_WORD_FILE) +
        load_word_list(f"{difficulty}_words.csv")
        if min_len <= len(word) <= max_len # making sure the word is in between the set number of characters
    ]

    if not words:
        print("No words avaliable for this difficulty. ")
        return None
    
    return create_game_state(word=random.choice(words)) # takes a word randomly from words

def game_loop(state):
    while True:
        print(f"\n Current word: {' '.join([l if l in state["guessed_letters"]
    else "_" for l in state["word"]])}")
        print(f"Guessed letters: {", ".join(sorted(state["guessed_letters"]))}")
        print(f"Score: {state["score"]} Time remaining: {state["time_left"]}s")

        start_time = time.time()
        guess = input("Guess a letter/word or type 'save' to quit: ").strip().lower()


        if guess == "save":
            filename = input("Enter save filename (spaces allowed): ").strip()
            save_game_state(filename, state)
            print("Game saved. Goodbye!")
            return False # Return False to indicate player doesn't want to continue
        
        elapsed = time.time() - start_time
        if not update_time(state, elapsed):
            print("Time's up! You lost!")
            print(f"The word was: {state['word']}")
            return ask_continue() # Ask if player wants to continue
        
        if guess == state["word"]:
            print(f"Congratulations! You guessed the word: {state["word"]}")
            print(f"Final Score: {state["score"]}")
            return ask_continue() # Ask if player wants to continue
        
        if len(guess) == 1 and guess.isalpha():
            if guess in state["guessed_letters"]:
                print("You already guessed that latter!")
                continue
        
        correct = add_guess(state, guess) 
        if not correct:
            state["incorrect_guesses"] -= 1
            state["score"] -= 10
            print(f"Wrong guess! {guess} is not in the word. ")
        
        else:
            print("Invalid input! Please enter a single letter or the full word. ")

            state["incorrect_guesses"] += 1
            state["score"] -= 10

        if all(l in state["guessed_letters"] for l in state["word"]):
            print(f"Congratulations! You guessed the word: {state["word"]}")
            print(f"Final Score: {state["score"]}")
            return ask_continue() # Ask if player wants to continue
        
        if state["score"] <= 0:
            print("You scored 0 points. Game over!")
            print(f"The word was: {state["word"]}")
            return ask_continue() # Ask if player wants to continue
        
        if state["incorrect_guesses"] >= HINT_THRESHOLD and not state["hint_used"]:
            missing = [l for l in state["word"] if l not in state["guessed_letters"]]

            if missing:
                state["hint_used"] = True
                print(f"*Hint: The letter '{random.choice(missing)}' is in the word! ")

def ask_continue():
    """Ask if the player wants to continue and return their choice."""
    response = get_valid_input(
        "\nDo you want to play again? (y/n): ",
        lambda x: x in {"y", "n"},
        "Please enter y or n: "

    )
    return response == "y"

def list_save_files():
    """List all avaliable save files in the current directory"""
    save_files = []
    try:
        for file in os.listdir():
            if file.endswith(".save"):
                save_files.append(file) # saves the files into save_files list
        return save_files
    except Exception as e:
        print(f"Error listing save files: {e}")
        return []
    
def hangman():
    clear_screen() # Clears screen when starting game
    print("\n=== New Game ===")
    while True:   # Main game loop for continuous play
        if get_valid_input("Load saved game? (y/n)  ", lambda x: x in {"y", "n"},
                           "Please enter y/n: ") == "y":
                            save_files = list_save_files() # finds the values from list save files

                            if not save_files:
                                print("No saved games found. ")
                                print("Starting new game instead. ")
                                state = new_game()
                            else:
                                print("\n Avaliable saved games: ")
                                for i, file in enumerate(save_files, 1):
                                    print(f"{i}. {file}")
                                print(f"0. Return to main menu")

                            choice = get_valid_input(
                                f"Choose a save file (0-{len(save_files)}): ",
                                lambda x: x.isdigit() and 0 <= int(x) <= len(save_files),
                                f"Please enter a number betweeen 0 and {len(save_files)}"
                            )
                            
                            choice = int(choice)
                            if choice == 0:
                                print("Returning to main menu...")
                                return
                            
                            filename = save_files[choice - 1]
                            print(f"Loading {filename} ...")

                            state = load_game_state(filename)
                            if not state:
                                print("Starting new game instead.")
                                state = new_game()
        
        else:
            state = new_game()
        
        if not state:
            print("Failed to start game - no valid words avaliable!")
            return
        
        # Play the game and check if player wants to continue
        continue_game = game_loop(state)
        if not continue_game:
            break # Return to main menu if player doesn't want to continue

    
def add_custom_words():
    clear_screen()   # Clear screen when adding custom words
    if not os.path.exists(CUSTOM_WORD_FILE):
        open(CUSTOM_WORD_FILE, "a").close()

    while True:
        word = input("Enter a word (4-10 letters) or 'done': ").lower().strip()
        
        if word == "done":
            break

        if not word.isalpha():
            print("Only alphabetic characters allowed!")
            continue

        if len(word) < 4 or len(word) > 20:
            print("Word must be between 4-20 letters!")
            continue

        existing = load_word_list(CUSTOM_WORD_FILE)
        if word in existing:
            print(f"'{word}' already exists! ")
            continue

        try:
            with open(CUSTOM_WORD_FILE, "a", newline="") as file:
                csv.writer(file).writerow([word])
            print(f"Added '{word}' to custom words!")

        except Exception as e:
            print(f"Error saving word: {e}")
        
def main():
    clear_screen()  # Clear screen at startup
    while True:
        print("\n 1. Play Game \n 2. Add Custom Words \n 3. Exit")
        choice = get_valid_input(
            "Choose option: ",
            lambda x: x in {"1", "2", "3"},
            "Please enter 1, 2, or 3"
        )

        if choice == "1":
            hangman()
            clear_screen()   # Clear screen when returning to main menu
        
        elif choice == "2":
            add_custom_words()
            clear_screen()   # Clear screeen when returning to main menu
        
        else:
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()


