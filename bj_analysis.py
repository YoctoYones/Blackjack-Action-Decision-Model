import pandas as pd
import scipy.stats as stats
import seaborn as sns
import matplotlib.pyplot as plt
import random
from bj_model_training import train_model
from bj_module import set_game_deck, bj_strat_game


## Training Model
model, feature_columns, X_test, y_test = train_model()

## Analizing Training Data
df = pd.read_csv("bj_training.csv")

# Split into soft and hard hands
df_soft = df[df['player_hand_val'].str.contains("/")]
df_hard = df[~df['player_hand_val'].str.contains("/")]



# Independence chi2 test of "delaer_up_card" and "win"
contingency = pd.crosstab(df["dealer_up_card"], df["win"])
print(contingency)

chi2, p, dof, expected = stats.chi2_contingency(contingency)

print(f'Chi2: {chi2}')
print(f'p-value: {p}')



table = pd.crosstab(df['dealer_up_card'], df['win'], normalize='index')

# Plot the heatmap, brighter squares = higher winrate, plots the chance of losing
plt.figure(figsize=(10, 6))
sns.heatmap(table, annot=True, cmap="YlGnBu", fmt=".2f")

plt.title('Distribution of Outcomes by Dealer Upcard')
plt.xlabel('Win')
plt.ylabel('Dealer Upcard')
plt.show()


#Soft hands plot for each action
actions = df_soft['action'].unique()
for action in actions:
    # Plot heatmap, darker squares = higher winrate
    subset = df_soft[df_soft['action'] == action]
    pivot = subset.groupby(['player_hand_val', 'dealer_up_card'])['win'].mean().unstack()
    sns.heatmap(pivot, annot=True, cmap="YlGnBu")
    plt.title(f"Soft Win Rate Heatmap – Action: {action}")
    plt.xlabel("Dealer Upcard")
    plt.ylabel("Player Total")
    plt.show()

#Hard hands plot for each action
actions = df_hard['action'].unique()
for action in actions:
    # Plot heatmap, darker squares = higher winrate
    subset = df_hard[df_hard['action'] == action]
    pivot = subset.groupby(['player_hand_val', 'dealer_up_card'])['win'].mean().unstack()
    sns.heatmap(pivot, annot=True, cmap="YlGnBu")
    plt.title(f"Hard Hand Win Rate Heatmap – Action: {action}")
    plt.xlabel("Dealer Upcard")
    plt.ylabel("Player Total")
    plt.show()

pivot = df.groupby(['player_hand_val', 'dealer_up_card'])['win'].mean().unstack()

# Plot heatmap for all hands regardless of action
plt.figure(figsize=(12, 8))
sns.heatmap(pivot, annot=True, cmap='YlGnBu', fmt=".2f")

plt.title('Win Rate by Player Total and Dealer Upcard')
plt.xlabel('Dealer Upcard')
plt.ylabel('Player Total')
plt.show()



## Setting Up Stats and Plots
amount_of_games_lst = [10, 100, 1000, 10000]
amount_of_games_lst2 = [10, 20, 30]
all_strats = ["random", "mimic", "generic", "model"]
OG_deck = set_game_deck(6)


# Calculating Winrates for all Strats
for N in amount_of_games_lst:
    balance = 10000000             
    bet = 1

    results = {'random' : [], 'mimic' : [], 'generic' : [], 'model' : []}
    
    for strat in all_strats:
        game_deck = OG_deck.copy()

        increment = random.randint(0,5)
        cut_card_index = round((increment + 20)/100 * len(OG_deck)) 
        

        for i in range(N + 1):
            wins, balance, game_deck, cut_card_index = bj_strat_game(strat, game_deck, OG_deck, cut_card_index, bet, balance, model, feature_columns)
            for win in wins:
                results[strat].append(win)
        winrate = results[strat].count(True) / len(results[strat])
        print(f'Winrate {i} games for {strat}: {winrate}')


# Ploting the course of the Balance for all Strats

for N in amount_of_games_lst2:
    bet = 100

    results = {'random' : [], 'mimic' : [], 'generic' : [], 'model' : []}

    game_list = [num for num in range(N + 1)]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    axes[0].set_title("Balance of 1 Session")
    axes[1].set_title("Median Blanace of 10 Sessions")
    axes[2].set_title("Average Balance of 10 Sessions")
    

    for strat in all_strats:
        game_deck = OG_deck.copy()

        increment = random.randint(0,5)
        cut_card_index = round((increment + 20)/100 * len(OG_deck))

        for a in range(10):
            balance = 1000
            results[strat].append([balance])
            for i in range(N):
                bet = 100
                wins, balance, game_deck, cut_card_index = bj_strat_game(strat, game_deck, OG_deck, cut_card_index, bet, balance, model, feature_columns)
                results[strat][a].append(balance)

            
    

        # Plot 1st balance course (1st list in balance_list)
        axes[0].plot(game_list, results[strat][0], label = strat)

        # Plot median balance
        median_balance_list = []
        for i in range(len(results[strat][0])):
            lst = []
            for balance_list in results[strat]:
                lst.append(balance_list[i])
                
            lst.sort()   
            median_balance_list.append((lst[4] + lst[5]) / 2)

        axes[1].plot(game_list, median_balance_list, label = strat)

        # Plot average balance
        avg_balance_list = []
        
        for i in range(len(results[strat][0])):
            sum = 0
            for balance_list in results[strat]:
                sum += balance_list[i]
            avg_balance_list.append(sum / 10)
            
        axes[2].plot(game_list, avg_balance_list, label = strat)

for axis in axes:
    axis.legend()

plt.tight_layout()
plt.show()