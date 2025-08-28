
# Blackjack Action Decision Model

A Python machine learning model (RandomForestClassifier) that recommends the best action in Blackjack.

## Table of Contents
- [How to use](#how-to-use)
- [Purpose of Project](#purpose-of-project)

## How to use

User guide on following .py files.   


### [bj_module.py](./bj_module.py)

A module of classes and functions that are imported into the other scripts. The function `generic_strat` depends on `generic_bj_strat.csv`.


### [bj_generate_training_data.py](./bj_generate_training_data.py)

Generates Blackjack training data:
- Dynamic deck that reshuffles
- Stores data in `bj_training.csv` with the following features:

| Feature          | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `win`            | True/False — whether the player won                                         |
| `dealer_up_card` | Dealer’s visible card                                                       |
| `player_hand_val`| Total value of the player’s hand                                            |
| `action`         | Randomly chosen player action                                               |
| `ace`            | True/False — whether the player’s hand contains an Ace                      |


Use `generate_data(N)` on `line 296` to generate `N` blackjack games and store them in `bj_training.csv`.

If `bj_training.csv` isn't found `bj_generate_training_data.py` will create it.

Use `set_game_deck(amount)` on `line 283` to dynamically generate blackjack games with `amount` decks. Recommended value 6 to 8.


### [bj_model_training.py](./bj_model_training.py)  

This script trains a RandomForestClassifier model based on data from `bj_training.csv`. 

The script also contains the function `model_action` which is used to make the model recommend the best possible action for a blackjack hand. The aforementioned function is imported into `bj_analysis.py`. 


### [bj_analysis.py](./bj_analysis.py)  

Analyzes the trained model’s performance vs. other Blackjack strategies such as randomly picking actions, mimicking the dealer and a [generic strategy](https://www.blackjackapprenticeship.com/blackjack-strategy-charts/). 

Featured Outputs:
- Win rates over up to 10,000 games  
- Balance, median balance and average balance progression up to 30 games    

Use `set_game_deck(amount)` on `line 86` to dynamically analyze blackjack games with `amount` decks. Recommended value 6 to 8.

## Purpose of Project

This project was created as a way to learn machine learning concepts through the fun application of blackjack.
