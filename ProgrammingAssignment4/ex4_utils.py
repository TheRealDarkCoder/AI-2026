import random
import time
import re
from matplotlib import pyplot as plt
from matplotlib import ticker as ticker

class Deck:
    """
    Represents a standard deck of 52 playing cards.
    """
    def __init__(self):
        self.cards = []
        suits = ["♥", "♦", "♣", "♠"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        for suit in suits:
            for rank in ranks:
                self.cards.append((rank, suit))
        self.shuffle()

    def draw(self):
        """
        Draws a random card and removes it from the deck.
        """
        if not self.cards:
            return None
        return self.cards.pop(random.randint(0, len(self.cards) - 1))
    
    def shuffle(self):
        random.shuffle(self.cards)

    def reset(self):
        self.__init__()

    def is_empty(self):
        return len(self.cards) <= 1
    
def get_value(rank):
    """
    Converts card rank to its corresponding value.
    """
    if rank == "J":
        return 11
    elif rank == "Q":
        return 12
    elif rank == "K":
        return 13
    elif rank == "A":
        return 14
    else:
        return int(rank)

def play(agent, deck):
    """
    Logic for playing a single game with the given agent and deck.
    """
    over = False
    print(f"You have an initial bet of {agent.winnings}.")
    time.sleep(1)
    print("Welcome to the Double or Nothing card game!")
    print("A random card will be drawn. You can attempt to double your bet by drawing a higher card, or you can quit at any time.")

    while not over:
        if deck.is_empty():
            print("The deck is empty. No more cards to draw.")
            break
        drawn = deck.draw()
        drawn_value = get_value(drawn[0])
        if agent.__class__.__name__ == "RationalAgent" or agent.__class__.__name__ == "RiskAverseAgent":
            agent.drawn = drawn_value

        print(f"Drawn: {drawn[0]}|{drawn[1]}")
        time.sleep(2)
        choice = agent.get_action()
        if choice == 0:
            print("You chose to quit the game.")
            print(f"Your final winnings are: {agent.winnings}. Thank you for playing!")
            break
        elif choice == 1:
            while True:
                your_card = deck.draw()
                your_value = get_value(your_card[0])
                print(f"You drew: {your_card[0]}|{your_card[1]}")
                time.sleep(2)
                if your_value == drawn_value:
                    print("It's a tie! Drawing again...")
                    time.sleep(2)
                    break
                elif your_value > drawn_value:
                    print("You win! You drew a higher card.")
                    agent._winnings *= 2
                    print(f"Your new winnings are: {agent.winnings}")
                    time.sleep(2)
                    break
                else:
                    agent._winnings = 0
                    print("You lose everything.")
                    print(f"Your final winnings are: {agent.winnings}. Thank you for playing!")
                    over = True
                    break
        else:
            raise ValueError(f"Invalid action: {choice}. Choose 'd' to draw or 'q' to quit.")

    if not deck.is_empty():
        update_stats(agent, agent.winnings, 1)
                
def quick_play(agent, deck, runs):
    """
    Logic for quickly playing multiple games with the given agent and deck.
    Also plots the winnings as a histogram and saves statistics to a file.
    """
    winnings = []
    sum_of_winnings = 0

    for i in range(runs):
        deck.reset()
        if agent.__class__.__name__ == "RationalAgent" or agent.__class__.__name__ == "RiskAverseAgent":
            agent.__init__(deck)
        else:
            agent.__init__()
        over = False
        while not over:
            if deck.is_empty():
                return
            drawn = deck.draw()
            drawn_value = get_value(drawn[0])
            if agent.__class__.__name__ == "RationalAgent" or agent.__class__.__name__ == "RiskAverseAgent":
                agent.drawn = drawn_value
            choice = agent.get_action()
            if choice == 0:
                winnings.append(agent.winnings)
                sum_of_winnings += agent.winnings
                over = True
                break
            elif choice == 1:
                while True:
                    your_card = deck.draw()
                    your_value = get_value(your_card[0])
                    if your_value == drawn_value:
                        break
                    elif your_value > drawn_value:
                        agent._winnings *= 2
                        break
                    else:
                        agent._winnings = 0
                        winnings.append(agent.winnings)
                        over = True
                        break
            else:
                raise ValueError(f"Invalid action: {choice}. Choose 'd' to draw or 'q' to quit.")
    
    update_stats(agent, sum_of_winnings, runs)
    print_stats(agent)

    # Plot the winnings as a histogram
    plt.figure(figsize=(18, 6))
    unique_winnings = len(set(winnings))
    plt.xlim(0, 1200000)
    plt.ylim(1, 1000000)
    plt.yscale('log')
    plt.hist(winnings, bins=1000, range=(0, 1200000), edgecolor='blue')
    plt.title(f"{agent.__class__.__name__} winnings over {runs} runs")
    plt.xlabel("Winnings")
    plt.ylabel("Frequency (log scale)")
    plt.grid(True)
    plt.gca().xaxis.set_major_formatter(ticker.StrMethodFormatter('{x:.0f}'))
   
def update_stats(agent, sum_of_winnings, runs):
    """
    Utility for updating the statistics file for the given agent.
    """
    agent_name = agent.__class__.__name__
    file_map = {
        "PlayerAgent": "player_stats.txt",
        "CrazyRiskSeekerAgent": "risk_seeker_stats.txt",
        "QuitterAgent": "quitter_stats.txt",
        "RationalAgent": "rational_stats.txt",
        "RiskAverseAgent": "risk_averse_stats.txt"
    }
    file = file_map.get(agent_name)
    if not file:
        raise ValueError(f"Unknown agent type: {agent_name}")

    try:
        with open(file, "r") as f_read:
            contents = re.split(r":|\n", f_read.read().strip())
            contents = [c.strip() for c in contents if c.strip()]
            prev_winnings = int(contents[1])
            prev_runs = int(contents[3])
            total_winnings = prev_winnings + sum_of_winnings
            total_runs = prev_runs + runs
    except FileNotFoundError:
        total_winnings = sum_of_winnings
        total_runs = runs
    finally:
        with open(file, "w") as f_write:
            f_write.write(
                f"Winnings: {total_winnings}\n"
                f"Runs: {total_runs}\n"
                f"Average winnings: {round(total_winnings / total_runs)}"
            )

def print_stats(agent):
    """
    Utility for printing the statistics of the given agent.
    """
    agent_name = agent.__class__.__name__
    file_map = {
        "PlayerAgent": "player_stats.txt",
        "CrazyRiskSeekerAgent": "risk_seeker_stats.txt",
        "QuitterAgent": "quitter_stats.txt",
        "RationalAgent": "rational_stats.txt",
        "RiskAverseAgent": "risk_averse_stats.txt"
    }
    file = file_map.get(agent_name)
    if not file:
        raise ValueError(f"Unknown agent type: {agent_name}")

    try:
        with open(file, "r") as f_read:
            contents = f_read.read().strip()
            print(contents)
    except FileNotFoundError:
        print(f"No statistics found for {agent_name}.")