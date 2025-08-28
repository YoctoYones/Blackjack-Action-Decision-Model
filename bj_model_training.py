import pandas as pd
import sys
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def train_model():
    '''
    Training a blackjack model with RandomForestClassifier.

    Input: No inputs
    Output: model (RandomForestClassifier Obj), feature_columns (lst of feature column names), X_test (pandas.DataFrame Obj), y_test (pandas.DataFrame Obj)
            None if errors are encountered.
    '''
    try: 
        df = pd.read_csv("bj_training.csv")

        # Convert string "True"/"False" to actual booleans and then to 0/1
        df['win'] = df['win'].astype(bool).astype(int)
        df['ace'] = df['ace'].astype(bool).astype(int)

        features = df[['player_hand_val', 'dealer_up_card', 'ace', 'action']]  
        target = df['win']

        # One-hot encode 'action' 'dealer_up_card' 'player_hand_val'
        df = pd.get_dummies(df, columns=['action', 'dealer_up_card', 'player_hand_val'])

        # Define features and target
        features = df.drop(columns=['win'])  # everything except win
        target = df['win']

        # Training the model
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2)
        feature_columns = X_train.columns.tolist()

        model = RandomForestClassifier()
        model.fit(X_train, y_train)

        return model, feature_columns, X_test, y_test
    except pd.errors.EmptyDataError:
        print('Error Message from "train_model" function in "bj_model_training.py": File "bj_training.csv" does not contain columns.')
        sys.exit()
    except ValueError:
        print('Error Message from "train_model" function in "bj_model_training.py": File "bj_training.csv" does not contain proper training data.')
        sys.exit()
    except FileNotFoundError:
        print('Error Message from "train_model" function in "bj_model_training.py": File "bj_training.csv" does not exist.')
        sys.exit()


# Action for the model
def model_action(model, player_hand, dealer_hand, feature_columns):
    '''
    Decide the opitmal action for a blackjack hand against the dealer's upcard according the trained model from sklearn.

    Input: model (RandomForestClassifier obj), player_hand (Hand obj), dealer_hand (Hand obj), feature_columns (lst)
    Output: actions[best_idx] (str)
    '''

    rows = []
    player_hand_val = str(player_hand)
    dealer_up_card = dealer_hand.hand[0][0]
    if ('A',11) in player_hand.hand:
        ace = 1
    else:
        ace = 0


    if len(player_hand.hand) == 2:
        if player_hand.hand[0] == player_hand.hand[1]:
            actions = ['hit', 'stand', 'double down', 'split']
        else:
            actions = ['hit', 'stand', 'double down']
    else:
        actions = ['hit', 'stand'] 
    

    for action in actions:
        row = {
            'player_hand_val_' + str(player_hand_val): 1,
            'dealer_up_card_' + str(dealer_up_card): 1,
            'ace': ace,
            **{f'action_{a}': int(a == action) for a in actions}
        }
        # Fill missing columns with 0
        full_row = {col: row.get(col, 0) for col in feature_columns}
        rows.append(full_row)

    X = pd.DataFrame(rows)
    probs = model.predict_proba(X)[:, 1]  # Probability of winning
    best_idx = probs.argmax()
    return actions[best_idx]




def main():
    model, feature_column, X_test, y_test = train_model()
    print("Prediction Accuracy:", model.score(X_test, y_test))



if __name__ == '__main__':
    main()