import random
import csv
from bj_model_training import model_action

# DEFINING HAND CLASSES
class Hand:
    '''Class for blackjack hands'''

    def __init__(self, game_deck, bet = 0):
        '''
        Input: game_deck (lst), bet (int)

        Deal 2 cards, the start of a blackjack game.
        '''

        self.hand = []
        for i in range(2):
            rng = random.randint(0,len(game_deck)-1)
            self.hand.append(game_deck[rng])
            game_deck.pop(rng)
        self.stand = False   # checking if a hand has double downed/stand
        self.bet = bet # amount of money that is bet on the hand
        self.bust = False # losing


    def deal(self, game_deck):
        '''
        Deal 1 card to the existing hand.
        
        Input: game_deck (lst)
        '''
        if self.stand == False:
            rng = random.randint(0,len(game_deck)-1)
            self.hand.append(game_deck[rng])
            game_deck.pop(rng)
        else:
            print("hand_Obj.deal(self) won't deal since self.stand = False")


    def __str__(self):
        '''Shows the hand's total card value'''

        value = 0
        values = [0,0] #first value is when ace is 1 and the second value is when ace is 11
        if ('A',11) in self.hand:  #there is an Ace or more in hand
            for card in self.hand:
                value += card[1] 
            for card in self.hand:                   
                values[0] += card[1]
                values[1] += card[1]
            for i in range(self.hand.count(('A',11))):
                values[0] -= 10  #all aces is worth 1 for values[0]
                values[1] -= 10  #all aces except for one is worth 1 for values[1]
            values[1] += 10
            if values[1] > 21:
                value = values[0]
                return f'{value}'
            elif self.stand == True:
                value = values[1]
                return f'{value}'
            else:
                return f'{values[0]} / {values[1]}'                   
        else:
            for card in self.hand:
                value += card[1] 
            return f'{value}'
       

    def __repr__(self):
        '''Show what cards there are in the hand'''
        out = ''
        for card in self.hand:
            out += card[0]
            out += ' '
        return out
    
class D_Hand(Hand):
    '''
    Dealer Hand subclass of Hand
    '''

    def __init__(self, game_deck):
        super().__init__(game_deck)

    
    def __str__(self):
        '''The Dealer Hand's value'''
        value = 0
        values = [0,0] #first value is when ace is 1 and the second value is when ace is 11
        if ('A',11) in self.hand:  #there is an Ace or more in hand
            for card in self.hand:                   
                values[0] += card[1]
                values[1] += card[1]
            for i in range(self.hand.count(('A',11))):
                values[0] -= 10  #all aces is worth 1 for values[0]
                values[1] -= 10  #all aces except for one is worth 1 for values[1]
            values[1] += 10
            if values[1] <= 21:
                return f'{values[1]}'
            elif values[1] > 21:
                return f'{values[0]}'
        else:
            for card in self.hand:
                value += card[1] 
            return f'{value}'
        
    def __repr__(self):
        '''Show what cards there are in the hand'''
        super().__repr__(self)
            
    

# HAND ACTIONS
def make_action(action, hand, game_deck):
    '''
    Makes an action for a hand
    Input: action (str), hand (Hand obj), game_deck (lst)
    Output: The hand with a recieved action (Hand obj) or 2 hands in a tuple if the action is split    
    '''

    if action == 'hit':
        hand.deal(game_deck)
        return hand
    elif action == 'stand':
        hand.stand = True
        return hand
    elif action == 'double down':
        hand.deal(game_deck)
        hand.bet *= 2
        hand.stand = True
        return hand
    elif action == 'split':
        hand_a = Hand(game_deck, hand.bet/2)
        hand_b = Hand(game_deck, hand.bet/2)
        hand_a.hand[0] = hand.hand[0]
        hand_b.hand[0] = hand.hand[0]
        return (hand_a, hand_b)
    

def dealer_action(dealer_hand, game_deck):
    '''
    Algorithm for the dealer's action during his turn.
    Input: dealer_hand (D_Hand obj), game_deck (lst)
    Output: dealer_hand (D_Hand obj), the hand has now finished all dealer moves during the dealer's turn
    '''

    while len(str(dealer_hand)) > 2:
        values_list = str(dealer_hand).split()  #format: '1 / 11' -> ['1','/','11']
        values = [int(values_list[0]),int(values_list[-1])] #format: [1,11]

        while values[0] < 17 or values[-1] < 17:
            dealer_hand.deal(game_deck)
            values_list = str(dealer_hand).split()  #format: '1 / 11' -> ['1','/','11']
            values[0] += int(values_list[0]) 
            values[-1] += int(values_list[-1])


    while int(str(dealer_hand)) < 17:
        dealer_hand.deal(game_deck)
        if int(str(dealer_hand)) > 21:
            dealer_hand.bust = True
            return dealer_hand
        
    return dealer_hand




# STRATEGIES
def random_strat(player_hand, game_deck, balance, dealer_hand = None, model = None, feature_columns = None):
    '''
    Randomly chooses an action for a player hand.

    Input:  player_hand (Hand obj), game_deck (lst), balance (int), dealer_hand (Hand obj), model, feature_columns (None, won't be used)
    Output: player_hand (Hand obj), action (str)
    '''

    possible_actions = ["hit", "stand"]

    if len(player_hand.hand) == 2:
        if balance >= player_hand.bet:
            possible_actions.append("double down")
            if player_hand.hand[0] == player_hand.hand[1]:
                possible_actions.append("split")    
        
    rng = random.randint(0, len(possible_actions) - 1)
        
    action = possible_actions[rng]

    player_hand = make_action(action, player_hand, game_deck)

    return player_hand, action


def mimic_dealer_strat(player_hand, game_deck, balance = 0, dealer_hand = None, model = None, feature_columns = None):
    '''
    Mimic how dealer plays.

    Input: player_hand (Hand obj), game_deck (lst), balance (int), dealer_hand (Hand obj), model, feature_columns (None, won't be used)
    Output: player_hand (Hand obj), action (str)
    '''

    if str(player_hand) == '11 / 21':
        player_hand.stand = True
        action = 'stand'
    elif '/' in str(player_hand):
        player_hand.deal(game_deck)
        action = 'hit'
    else:
        try:
            if int(str(player_hand)) <= 16:
                player_hand.deal(game_deck)
                action = 'hit'
            else:
                player_hand.stand = True
                action = 'stand'
        except ValueError:   #The hand is a soft hand if this occurs
            player_hand.deal(game_deck)
            action = 'hit'


    return player_hand, action 


def generic_strat(player_hand, game_deck, balance, dealer_hand, model = None, feature_columns = None):
    '''
    This is a generic blackjack strategy.

    Input: player_hand (Hand obj), game_deck (lst), balance (int), dealer_hand (Hand obj), model, feature_columns (None, won't be used)
    Output: player_hand (Hand obj), action (str)
    '''

    action = ''

    splittable = "False"
    player_hand_val = str(player_hand)
    dealer_up_card = str(dealer_hand.hand[0][1])

    if len(player_hand.hand) == 2 and player_hand.hand[0] == player_hand.hand[1]:
        splittable = "True"

    try:
        with open('generic_bj_strat.csv') as options:
            reader = csv.reader(options)
            for row in reader:
                    if row[0] == player_hand_val and row[1] == dealer_up_card and row[3] == splittable:
                        action = row[2]
                        break
    except FileNotFoundError:
        print('Error Message from "generic_strat" function in "bj_module.py": File "generic_bj_strat.csv" does not exist.')

    if action == 'double down':
        if balance < player_hand.bet or len(player_hand.hand) != 2:
            action = 'hit'

    player_hand = make_action(action, player_hand, game_deck)

    return player_hand, action


def model_strat(player_hand, game_deck, balance, dealer_hand, model, feature_columns):
    '''
    Decide the opitmal action for a blackjack hand against the dealer's upcard according the trained model from sklearn.

    Input: player_hand (Hand obj), game_deck (lst), balance (int), dealer_hand (Hand obj), model (RandomForestClassifier obj), feature_columns (lst)
    Output: player_hand (Hand obj)
    '''

    action = model_action(model, player_hand, dealer_hand, feature_columns)

    if action == 'double down':
        if balance < player_hand.bet or len(player_hand.hand) != 2:
            action = 'hit'

    player_hand = make_action(action, player_hand, game_deck)

    return player_hand, action



def set_game_deck(amount = 6):
    '''
    Creates the intended amount of decks for a blackjack game.

    Input: amount (int)
    Output: OG_deck (list)
    '''

    deck = (('A',11), ('2',2), ('3',3), ('4',4), ('5',5), ('6',6), ('7',7), ('8',8), ('9',9), ('T',10), ('J',10), ('Q',10), ('K',10))
    OG_deck = []
    
    for i in range(4 * amount):
        for card in deck:
            OG_deck.append(card)

    

    return OG_deck


# Function that plays a Blackjack Game with a given Strategy
def bj_strat_game(strat, game_deck, OG_deck, cut_card_index, bet = 0, balance = 0, model = None, feature_columns = None):
    '''
    Plays a blackjack game where the player plays a given strategy and deck.

    Input:  strat (str), acceptable inputs are "random", "mimic", "generic" and "model"
            game_deck (lst)
            OG_deck (lst)
            cut_card_index (int)
            bet (int)
            balance (int)
            model (RandomForestClassifier obj)
            feature_columns (lst of str)         
    Output: wins (lst of bool)
            balance (int)
            game_deck (lst)
            cut_card_index (int)
    '''

    # All Strats
    all_strats = {'random' : random_strat, 'mimic' : mimic_dealer_strat, 'generic' : generic_strat, 'model' : model_strat}

    # Check for Need to Reshuffle Deck
    if cut_card_index >= len(game_deck):
                game_deck = OG_deck.copy()
                increment = random.randint(0,5)
                cut_card_index = round((increment + 20)/100 * len(OG_deck)) 


    # Setting Up Player & Dealer
    player_hand = Hand(game_deck, bet)
    balance -= player_hand.bet
    all_player_hands = [player_hand]
    dealer_hand = dealer_action(D_Hand(game_deck), game_deck)

    # Hand Actions
    index_hand = 0
    while index_hand <= len(all_player_hands)-1:
        while all_player_hands[index_hand].stand == False and all_player_hands[index_hand].bust == False:
            player_hand, action = all_strats[strat](all_player_hands[index_hand], game_deck, balance, dealer_hand, model, feature_columns)

            if action == 'double down':
                balance -= player_hand.bet
            
            if isinstance(player_hand, tuple) == True:  #Hand got split
                all_player_hands[index_hand] = player_hand[0]
                all_player_hands.insert(index_hand + 1, player_hand[1])

            # Check if Hand has Busted
            try:
                if int(str(player_hand)) > 21:
                    player_hand.bust = True
            except ValueError:
                pass


        if cut_card_index >= len(game_deck):
                game_deck = OG_deck.copy()
                increment = random.randint(0,5)
                cut_card_index = round((increment + 20)/100 * len(OG_deck)) 

        index_hand += 1
        
    # Determine win/loss
    wins = []
    winnings = 0
    
    for P_hand in all_player_hands:
        
        if P_hand.bust == True:
            wins.append(False)
        elif int(str(P_hand)) <= int(str(dealer_hand)) and dealer_hand.bust == False:
            wins.append(False)
        else:
            wins.append(True)
            if len(P_hand.hand) == 2 and str(P_hand) == '21': #Blackjack payout 3:2
                winnings +=  2.5 * P_hand.bet
            else:
                winnings += 2 * P_hand.bet
    
    balance += winnings

    return wins, balance, game_deck, cut_card_index



