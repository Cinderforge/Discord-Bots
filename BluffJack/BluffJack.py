import random

def turn(current):
    global stands, other
    print(f"{current[3]}'s turn")
    decision = int(input("Draw, Use Ability, or Stay: "))
    match decision:
        case 1:
            print("Draw a Card")
            draw(current, 1)
            stands = 0
            turn(current)
        case 2:
            print(f"Arcana: {current[2]}")
            stands = 0
            turn(current)
        case 3:
            print("Stand")
            stands += 1
            if stands > 1:
                end_round()
            else:
                current, other = other, current
                print(current, other)
                turn(current)
        case _:
            print("Invalid Input")
            turn(current)

def end_round():
    a, b = current[1], other[1]
    print(f"{current[3]}'s Score: {a} {other[3]}'s Score: {b}")
    winner = None
    if a == b:
        print("Tie")
    elif a > goal ^ b > goal:
        winner = min(a, b)
    elif a > goal and b > goal:   
        winner = min(a, b)
    else:
        winner = max(a, b)
    if a == winner:
        print(f"{current[3]} wins")
    elif b == winner:
        print(f"{other[3]} wins")

def fool(player):
    print("The Fool: Resets your hand")
    for i in player:
        deck.append(i)
    player[0], player[1] = [], 0
    draw(player, 2)
    tot()

def magician():
    print("The Magician: Swaps last drawn card from each player")
    a, b = current[0][-1], other[0][-1]
    print(a, b)
    del current[0][-1]
    del other[0][-1]
    current[0].append(b)
    other[0].append(a)
    tot()

def devil(other):
    print("The Devil: Force the opponent to draw a card")
    draw(other, 1)

def tot():
    current[1] = sum(current[0])
    other[1] = sum(other[0])
    print(f"Deck: {deck}")
    print(f"{current[3]}: {current}, {other[3]}: {other}")

def draw(player, amount):
    if len(deck) > 0:
        for _ in range(amount):
            drawn = random.choice(deck)
            player[0].append(drawn)
            deck.remove(drawn)
    else:
        print("Empty deck!")
    tot()

if __name__ == "__main__":
    deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    tarot = [fool, magician, devil]
    player1, player2 = [[], 0, [], "Player 1"], [[], 0, [], "Player 2"]
    current = random.choice([player1, player2])
    other = player1 if current is player2 else player2
    stands = 0
    goal = 21
    draw(current, 2)
    draw(other, 2)
    turn(current)