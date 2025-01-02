from eval7 import equity, cards, handrange

def Equity(hero_cards, villain_dist, board, num_iter):
    #print(f"{hero_cards[0]}{hero_cards[1]}")
    hero_dist = handrange.HandRange(f"{hero_cards[0]}{hero_cards[1]}")
    #print(f"villain_dist: {villain_dist}")
    villain_dist = handrange.HandRange(villain_dist)
    return equity.py_all_hands_vs_range(hero_dist, villain_dist, board, num_iter)[(cards.Card(str(hero_cards[0])), cards.Card(str(hero_cards[1])))]