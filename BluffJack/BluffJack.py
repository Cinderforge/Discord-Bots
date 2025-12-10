import random
import os

def clear():
    # For Windows
    if os.name == 'nt':
        _ = os.system('cls')
    # For macOS and Linux
    else:
        _ = os.system('clear')

def check():
    clear()
    checker = ""
    while len(checker) == 0:
        checker = input(f"Screen facing {current[3]}? (Any Input): ")

def turn():
    global stands, other, current
    print(f"{current[3]}'s turn")
    print(f"Bet: {bet}, {current[3]}'s Health: {current[6]}, {other[3]}'s Health: {other[6]}")
    selftot()
    print(f"Goal: {goal}")
    decision = (input("Draw (1), Use Ability (2), or Stay (3): "))
    match decision:
        case "1":
            print("Draw a Card")
            draw(current, 1)
            stands = 0
            clear()
            turn()
        case "2":
            print(f"Arcana: {current[2]}")
            stands = 0
            clear()
            turn()
        case "3":
            print("Stand")
            stands += 1
            if stands > 1:
                current, other = other, current
                clear()
                end_round()
            else:
                current, other = other, current
                print(current, other)
                check()
                turn()
        case _:
            print("Invalid Input")
            clear()
            turn()

def end_round():
    global bet, stands
    a, b = current[1], other[1]
    print(f"{current[3]} other {other[3]}")
    print(f"{current[3]}'s Score: {a} {other[3]}'s Score: {b}")
    winner = None
    if a == b:
        print("Tie!")
    elif (a > goal) != (b > goal):
        winner = min(a, b)
    elif a > goal and b > goal:  
        winner = min(a, b)
    else:
        winner = max(a, b)
    if a == winner:
        print(f"{current[3]} wins!")
        current[6] += bet
        other[6] -= bet
    elif b == winner:
        print(f"{other[3]} wins!")
        current[6] -= bet
        other[6] += bet
    if current[6] <= 0 or other [6] <= 0:
        if current[6] > 0:
            print(f"{current[3]} Survives! Sorry {other[3]}, you must die.")
        else:
            print(f"{other[3]} Survives! Sorry {current[3]}, you must die.")
    else:
        print(f"Bet Increase!: {bet} --> {bet + 1}")
        bet += 1
        print(f"Bet: {bet}, {current[3]}'s Health: {current[6]}, {other[3]}'s Health: {other[6]}")
        fool(current)
        fool(other)
        stands = 0
        turn()

def fool(player):
    print("The Fool: Resets your hand")
    for i in player[0]:
        deck.append(i)
    player[0], player[1] = [], 0
    player[4], player[5]= [], 0
    moon(player, 2)
    tot()

def magician():
    print("The Magician: Swaps last drawn card from each player")
    a, b = current[0][-1], other[0][-1]
    print(a, b)
    del current[0][-1]
    del other[0][-1]
    del current[4][-1]
    del other[4][-1]
    current[0].append(b)
    other[0].append(a)
    current[4].append(b)
    other[4].append(a)
    tot()

def empress():
    global goal
    print("The Empress: Set the bust limit to 17")
    goal = 17

def emperor():
    global goal
    print("The Emperor: Set the bust limit to 27")
    goal = 27

def coinSearch(player, num):
    print(f"{num} of Coins: Search the deck for a {num}")
    print("If found, add it to your hand")
    if num not in player[0] and num not in other[0]:
        player[0].append(num)
        deck.remove(num)
    tot()

def swordSearch(player, num):
    print(f"{num} of Swords: Search the deck for a {num}")
    print("If found, add it to your opponent's hand")
    if num not in player[0] and num not in other[0]:
        other[0].append(num)
        deck.remove(num)
    tot()

def devil(other):
    print("The Devil: Force the opponent to draw a card")
    draw(other, 1)

def moon(player, amount):
    print("The Moon: Draw a hidden card")
    if len(deck) > 0:
        for _ in range(amount):
            drawn = random.choice(deck)
            player[0].append(drawn)
            player[4].append(0)
            deck.remove(drawn)
    else:
        print("Empty deck!")
    
def sun():
    print("The Sun: Reveals the opponent's hidden cards")
    other[4] = other[0]

def sutot():
    current[1] = sum(current[0])
    other[1] = sum(other[0])
    current[5] = sum(current[4])
    other[5] = sum(other[4])
    print(f"Deck: {deck}")
    print(f"{current[3]}: {current}, {other[3]}: {other}")

def selftot():
    print(f"{current[3]}: {current[0]} {current[1]}")
    print(f"{other[3]}: {other[4]} ?+{other[5]}")

def tot():
    current[1] = sum(current[0])
    other[1] = sum(other[0])
    current[5] = sum(current[4])
    other[5] = sum(other[4])
    print(f"{current[3]}: {current[4]} {current[5]}, {other[3]}: {other[4]} {other[5]}")

def draw(player, amount):
    if player[1] > goal:
        print("Busted! You may not draw a card")
        print(goal)
    else: 
        if len(deck) > 0:
            for _ in range(amount):
                drawn = random.choice(deck)
                player[0].append(drawn)
                player[4].append(drawn)
                deck.remove(drawn)
        else:
            print("Empty deck!")
    tot()

if __name__ == "__main__":
    with open('rules.txt', 'r') as rules:
        counter = 1
        for line in rules:
            line = line.strip()
            if counter == 1:
                goal = int(line)
                counter += 1
            elif counter == 2:
                life = int(line)
                counter += 1
            elif counter == 3:
                bet = int(line)
                counter += 1
    deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    tarot = [fool, magician, empress, emperor, devil, moon]
    player1, player2 = [[], 0, [], "Player 1", [], 0, life], [[], 0, [], "Player 2", [], 0, life]
    current = random.choice([player1, player2])
    other = player1 if current is player2 else player2
    stands = 0
    moon(current, 2)
    moon(other, 2)
    tot()
    check()
    turn()