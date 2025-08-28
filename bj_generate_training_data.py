import random
import csv
import os

import bj_module as bjm


def add_bj_data(win, dealer_up_card, player_hand_val, action, ace):
    '''
    Adds data from a blackjack game into bj_training.csv.
    The input data is win, dealer upper card, player_start_hand, action, ace (str)

    Rough example of the .csv file:
    win,dealer_up_card,player_hand_val,action,ace
    yes,T,4 / 14,hit,yes 

    Output: None
    '''

    file_exist = os.path.isfile("bj_training.csv")   #boolean value

    with open('bj_training.csv', 'a', newline = '') as bj_training_data:
        fieldnames=["win", "dealer_up_card", "player_hand_val", "action", "ace"]
        writer = csv.DictWriter(bj_training_data, fieldnames=fieldnames)

        if file_exist == False or os.stat("bj_training.csv").st_size == 0:
            writer.writeheader()

        writer.writerow({"win": win, "dealer_up_card": dealer_up_card, "player_hand_val": player_hand_val, "action": action, "ace": ace})

    return None


def bj_game(game_deck, OG_deck, cut_card_index, inp_player_hand = None, inp_dealer_hand = None, split_count = 0):
    '''
    Generates a blackjack game and stores the data in bj_training_data.csv with the function "add_bj_data".
    Note: Splitting hands in succession won't get stored as data, but the odds for tha possibility to do that in a real game is slim.

    Input: game_deck (list), OG_deck (list), cut_card_index (int), inp_player_hand, inp_dealer_hand (Hand Obj) set to None as default, split_count (int) set to 0 as default. 
    Output: game_deck (list), OG_deck (list), cut_card_index (int)
    '''

    # Check for Reshuffling the Deck
    if cut_card_index >= len(game_deck):
                game_deck = OG_deck.copy()
                increment = random.randint(0,5)
                cut_card_index = round((increment + 20)/100 * len(OG_deck))

    # Setting Up Player & Dealer
    if inp_player_hand == None and inp_dealer_hand == None:
        player_hand = bjm.Hand(game_deck)
        dealer_hand = bjm.dealer_action(bjm.D_Hand(game_deck), game_deck)  #dealer hand done with all moves
        split = False
    else:
        player_hand = inp_player_hand  #this hand originates from a split hand
        split = True
        dealer_hand = inp_dealer_hand
        split_count += 1


    if int(str(dealer_hand)) > 21:   #checking if dealer has busted
        dealer_hand.bust == True

    dealer_up_card = dealer_hand.hand[0][0]


    # Player Hand actions
    actions_done = []

    while player_hand.stand == False and player_hand.bust == False:
        if len(player_hand.hand) == 2:
            if player_hand.hand[0] == player_hand.hand[1]:
                possible_actions = ["hit", "stand", "double down", "split"]
                rng = random.randint(0, len(possible_actions) - 1)

                action = possible_actions[rng]
                actions_done.append(action)

                player_hand = bjm.make_action(action, player_hand, game_deck)

            else:
                possible_actions = ["hit", "stand", "double down"]
                rng = random.randint(0, len(possible_actions) - 1)

                action = possible_actions[rng]
                actions_done.append(action)

                player_hand = bjm.make_action(action, player_hand, game_deck)
        else:
            possible_actions = ["hit", "stand"]
            rng = random.randint(0, len(possible_actions) - 1)
            
            action = possible_actions[rng]
            

            player_hand = bjm.make_action(action, player_hand, game_deck)


        if isinstance(player_hand, tuple) == True: #hand got split
            bj_game(game_deck, OG_deck, cut_card_index, player_hand[0], dealer_hand, split_count)
            bj_game(game_deck, OG_deck, cut_card_index, player_hand[1], dealer_hand, split_count)
            return game_deck, OG_deck, cut_card_index

        # check if player busted
        try:
            if int(str(player_hand)) > 21:
                player_hand.bust = True
        except ValueError:
            pass

        #checking for need of reshuffling
        if cut_card_index >= len(game_deck):
                game_deck = OG_deck.copy()
                increment = random.randint(0,5)
                cut_card_index = round((increment + 20)/100 * len(OG_deck))

    actions_done.reverse()

    # Evaluating who won
    if split == True: #HAND STEMS FROM A SPLIT HAND
        if player_hand.bust == True: #player busts and hand.stand = False and hand.bust = True
            win = "False"
            player_hand.stand = False
            #storing the split hand 
            if ('A',11) == player_hand.hand[0]:
                ace = "True"
                for i in range(split_count):
                    add_bj_data(win, dealer_up_card, "2 / 12", "split", ace)
            else:
                ace = "False"
                for i in range(split_count):
                    add_bj_data(win, dealer_up_card, str(2 * player_hand.hand[0][1]), "split", ace)

            #sotring the rest
            for action in actions_done:
                player_hand.hand.pop(-1)

                if ('A',11) in player_hand.hand:
                    ace = "True"
                    add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                else:
                    ace = "False"
                    add_bj_data(win, dealer_up_card, str(player_hand), action, ace)

        elif int(str(player_hand)) <= int(str(dealer_hand)) and dealer_hand.bust == False: #player loses/tie and hand.stand = False 
            win = "False"
            player_hand.stand = False
            #storing the split hand 
            if ('A',11) == player_hand.hand[0]:
                ace = "True"
                for i in range(split_count):
                    add_bj_data(win, dealer_up_card, "2 / 12", "split", ace)
            else:
                ace = "False"
                for i in range(split_count):
                    add_bj_data(win, dealer_up_card, str(2 * player_hand.hand[0][1]), "split", ace)

            #sotring the rest
            for action in actions_done:
                if action == "double down": #hand action is double down
                    player_hand.hand.pop(-1)  #remove the card that was added when doubled down
                    if ('A',11) in player_hand.hand:
                        ace = "True"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    else:
                        ace = "False"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                else:
                    if ('A',11) in player_hand.hand:
                        ace = "True"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    else:
                        ace = "False"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    player_hand.hand.pop(-1)


        else:  #player wins and hand.stand = True
            win = "True"
            player_hand.stand = False
            #storing the split hand 
            if ('A',11) == player_hand.hand[0]:
                ace = "True"
                for i in range(split_count):
                    add_bj_data(win, dealer_up_card, "2 / 12", "split", ace)
            else:
                ace = "False"
                for i in range(split_count):
                    add_bj_data(win, dealer_up_card, str(2 * player_hand.hand[0][1]), "split", ace)

            #sotring the rest
            for action in actions_done:
                if action == "double down": #hand action is double down
                    player_hand.hand.pop(-1)  #remove the card that was added when doubled down
                    if ('A',11) in player_hand.hand:
                        ace = "True"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    else:
                        ace = "False"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                else:
                    if ('A',11) in player_hand.hand:
                        ace = "True"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    else:
                        ace = "False"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    player_hand.hand.pop(-1)


    else: #HAND NOT STEMMING FROM A SPLIT HAND
        if player_hand.bust == True: #player busts and hand.stand = False and hand.bust = True
            win = "False"
            player_hand.stand = False
            for action in actions_done:
                player_hand.hand.pop(-1)  #remove the card that busted the hand

                if ('A',11) in player_hand.hand:
                    ace = "True"
                    add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                else:
                    ace = "False"
                    add_bj_data(win, dealer_up_card, str(player_hand), action, ace)

        elif int(str(player_hand)) <= int(str(dealer_hand)) and dealer_hand.bust == False: #player loses/tie and hand.stand = True
            win = "False"
            player_hand.stand = False
            for action in actions_done:
                if action == "double down": #hand action is double down
                    player_hand.hand.pop(-1)  #remove the card that was added when doubled down
                    if ('A',11) in player_hand.hand:
                        ace = "True"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    else:
                        ace = "False"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                else:
                    if ('A',11) in player_hand.hand:
                        ace = "True"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    else:
                        ace = "False"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    player_hand.hand.pop(-1)

        else:  #player wins and hand.stand = True
            win = "True"
            player_hand.stand = False
            for action in actions_done:
                if action == "double down": #hand action is double down
                    player_hand.hand.pop(-1)  #remove the card that was added when doubled down
                    if ('A',11) in player_hand.hand:
                        ace = "True"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    else:
                        ace = "False"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                else:
                    if ('A',11) in player_hand.hand:
                        ace = "True"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    else:
                        ace = "False"
                        add_bj_data(win, dealer_up_card, str(player_hand), action, ace)
                    player_hand.hand.pop(-1)



    
    return game_deck, OG_deck, cut_card_index
    
        
def generate_data(N):
    '''
    Generates data from blackjack games and stores it in bj_training.csv N times.
    This is done with the function "bj_game".

    Input: N (int)
    Output: None
    '''

    
    OG_deck = bjm.set_game_deck(6)
    game_deck = OG_deck.copy()

    increment = random.randint(0,5)
    cut_card_index = round((increment + 20)/100 * len(OG_deck))

    for i in range(N):
        game_deck, OG_deck, cut_card_index = bj_game(game_deck, OG_deck, cut_card_index)

    return None

    

generate_data(100000)

   