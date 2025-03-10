# black jack in python wth pygame!
import copy
import random
import pygame
import time

pygame.init()

#----------------#
# game variables #
#----------------#

# work with variables to have consistent colors throughout the game
clr_white = (246, 248, 255)
clr_green = (35, 133, 59)
clr_red = (204, 41, 54)
clr_gold = (247, 179, 43)
clr_blue = (52, 138, 167)

# buttons
# adding a sans-serif font for the buttons
btn_font = pygame.font.Font('fonts/NotoSans-bold.ttf', 44)
border_radius = 50

# card background

card_background = pygame.image.load('img/card-template.png')

# load the soundtrack 
# use pygame.mixer.music.load to have a different channel than the sound effects
soundtrack = pygame.mixer.music.load("sounds/epic-soundtrack.mp3")

# to prevent the soundtrack from playing way too loud (distorted), I had to change the volume
pygame.mixer.music.set_volume(0.15)

# play the soundtrack in a continuous loop
pygame.mixer.music.play(loops=-1)

# set play_soundtrack to true in order to make the mute / unmute button work
play_soundtrack = True

# load img for mute_btn

mute_btn = pygame.image.load('img/mute-btn.png')

# sound fx
# use pygame.mixer.Sound to load the effects on another channel than the backing track
deal_sfx = pygame.mixer.Sound("sounds/mix-card.mp3")
hit_sfx = pygame.mixer.Sound("sounds/hit-card.mp3")
win_sfx = pygame.mixer.Sound("sounds/game-win.mp3")
loss_sfx = pygame.mixer.Sound("sounds/game-over.mp3")
stop_sfx = pygame.mixer.Sound("sounds/stop.mp3")

# setup cards (1 suit)
cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
# 1 deck = 4 suits
one_deck = 4 * cards
# play blackjack with 4 decks of cards
decks = 4

#setup the pygame window
WIDTH = 600
HEIGHT = 900
screen = pygame.display.set_mode([WIDTH, HEIGHT])
pygame.display.set_caption('Blackjack!')

fps = 60
timer = pygame.time.Clock()

# load some custom fonts
regular_font = pygame.font.Font('fonts/Atma-Medium.ttf', 44)
smaller_font = pygame.font.Font('fonts/Atma-regular.ttf', 36)

# initially we don't want an active hand when the game starts
active = False

# win, loss, draw/push
records = [0, 0, 0]
player_score = 0
dealer_score = 0
initial_deal = False
my_hand = []
dealer_hand = []
outcome = 0
reveal_dealer = False
hand_active = False
outcome = 0
add_score = False
results = ['', 'PLAYER BUSTED o_O', 'PLAYER WINS! :)', 'DEALER WINS :(', 'TIE GAME!']

#-----------#
# Functions #
#-----------#

# deal cards by selecting randomly from deck, and make function for one card at a time
def deal_cards(current_hand, current_deck):
    card = random.randint(0, len(current_deck))
    current_hand.append(current_deck[card - 1])
    current_deck.pop(card - 1)
    return current_hand, current_deck


# draw scores for player and dealer on screen
def draw_scores(player, dealer):
    screen.blit(smaller_font.render(f'Score[{player}]', True, 'white'), (350, 400))
    if reveal_dealer:
        screen.blit(smaller_font.render(f'Score[{dealer}]', True, 'white'), (350, 100))


# draw cards visually onto screen
def draw_cards(player, dealer, reveal):
    for i in range(len(player)):
        pygame.draw.rect(screen, clr_white, [70 + (70 * i), 460 + (5 * i), 130, 220], 0, 5)
        # overlay card rect with an image, use color variables to improve consistency
        screen.blit(card_background, [70 + (70 * i), 460 + (5 * i), 130, 220])
        screen.blit(regular_font.render(player[i], True, clr_red), (88 + 70 * i, 463 + 5 * i))
        screen.blit(regular_font.render(player[i], True, clr_red), (150 + 70 * i, 613 + 5 * i))

    # if player hasn't finished turn, dealer will hide one card
    for i in range(len(dealer)):
        pygame.draw.rect(screen, clr_white, [70 + (70 * i), 120 + (5 * i), 130, 220], 0, 5)
        # overlay card rect with an image, use color variables to improve consistency
        screen.blit(card_background, [70 + (70 * i), 120 + (5 * i), 130, 220])
        if i != 0 or reveal:
            screen.blit(regular_font.render(dealer[i], True, clr_blue), (88 + 70 * i, 123 + 5 * i))
            screen.blit(regular_font.render(dealer[i], True, clr_blue), (150 + 70 * i, 273 + 5 * i))
        else:
            screen.blit(regular_font.render('???', True, clr_blue), (88 + 70 * i, 123 + 5 * i))
            screen.blit(regular_font.render('???', True, clr_blue), (150 + 70 * i, 273 + 5 * i))


# pass in player or dealer hand and get best score possible
def calculate_score(hand):
    # calculate hand score fresh every time, check how many aces we have
    hand_score = 0
    aces_count = hand.count('A')
    for i in range(len(hand)):
        # for 2,3,4,5,6,7,8,9 - just add the number to total
        for j in range(8):
            if hand[i] == cards[j]:
                hand_score += int(hand[i])
        # for 10 and face cards, add 10 to hand_score
        if hand[i] in ['10', 'J', 'Q', 'K']:
            hand_score += 10
        # for aces start by adding 11, we'll check if we need to reduce afterwards
        elif hand[i] == 'A':
            hand_score += 11
    # determine how many aces need to be 1 instead of 11 to get under 21 if possible
    if hand_score > 21 and aces_count > 0:
        for i in range(aces_count):
            if hand_score > 21:
                hand_score -= 10
    return hand_score


# draw game conditions and buttons
def draw_game(act, record, result):

    # show with how many decks we're playing on the screen
    n_decks_text = smaller_font.render(f'{decks} decks', True, clr_gold)
    screen.blit(n_decks_text, (22, 25))

    button_list = []
    # initially on startup (not active), the only option is a new hand
    if not act:

        # draw add deck button in game
        add_deck = pygame.draw.circle(screen, clr_gold, (50, 95), 15)
        add_deck_text = smaller_font.render('+', True, clr_green)
        screen.blit(add_deck_text, (44, 68))
        button_list.append(add_deck)

        # draw remove deck button in game
        remove_deck = pygame.draw.circle(screen, clr_gold, (88, 95), 15)
        remove_deck_text = smaller_font.render('-', True, clr_red)
        screen.blit(remove_deck_text, (83, 65))
        button_list.append(remove_deck)

        # draw 'deal' button on the screen
        # parameters => target (screen), color (white), [list with X, Y, Width, Height], edge width, border-radius
        deal = pygame.draw.rect(screen, clr_blue, [150, 20, 300, 100], 0, border_radius)
        pygame.draw.rect(screen, clr_white, [150, 20, 300, 100], 2, border_radius)

        # add text to button
        # parameters => text, anti-alias, color
        deal_text = btn_font.render('DEAL HAND', True, clr_white)
        screen.blit(deal_text, (174, 40))
        button_list.append(deal)

    # once game started, shot hit and stand buttons and win/loss records
    else:
        # draw 'HIT' button on the screen
        hit = pygame.draw.rect(screen, clr_green, [40, 720, 240, 80], 0, border_radius)
        pygame.draw.rect(screen, clr_white, [40, 720, 240, 80], 2, border_radius)

        # add text to button
        hit_text = btn_font.render('HIT ME', True, clr_white)
        screen.blit(hit_text, (85, 730))

        button_list.append(hit)

        # draw 'STAND' button on the screen
        stand = pygame.draw.rect(screen, clr_red, [320, 720, 240, 80], 0, border_radius)
        pygame.draw.rect(screen, clr_white, [320, 720, 240, 80], 2, border_radius)

        stand_text = btn_font.render('STAND', True, clr_white)
        screen.blit(stand_text, (370, 730))

        button_list.append(stand)

        score_text = smaller_font.render(f'Wins: {record[0]}   Losses: {record[1]}   Draws: {record[2]}', True, 'white')
        screen.blit(score_text, (15, 840))

    # if there is an outcome for the hand that was played, display a restart button and tell user what happened
    if result != 0:
        screen.blit(smaller_font.render(results[result], True, 'white'), (175, 0))
        deal = pygame.draw.rect(screen, clr_blue, [150, 220, 300, 100], 0, border_radius)
        pygame.draw.rect(screen, clr_gold, [150, 220, 300, 100], 5, border_radius)
        deal_text = btn_font.render('NEW HAND', True, clr_white)
        screen.blit(deal_text, (180, 238))

        button_list.append(deal)

    return button_list


# check endgame conditions function
def check_endgame(hand_act, deal_score, play_score, result, totals, add):
    # check end game scenarios is player has stood, busted or blackjacked
    # result 1- player bust, 2- win, 3- loss, 4- push
    if not hand_act and deal_score >= 17:
        if play_score > 21:
            result = 1

        elif deal_score < play_score <= 21 or deal_score > 21:
            result = 2

        elif play_score < deal_score <= 21:
            result = 3

        else:
            result = 4

        if add:
            # loss
            if result == 1 or result == 3:
                totals[1] += 1
                loss_sfx.play()

            # win
            elif result == 2:
                totals[0] += 1
                win_sfx.play()

            else:
                totals[2] += 1

            add = False

    return result, totals, add


#----------------#
# main game loop #
#----------------#

run = True

while run:
    # run game at our framerate and fill screen with bg-color
    timer.tick(fps)
    # insert background image
    bg_image = pygame.image.load('img/cardgame-background.png')
    screen.blit(bg_image, (0, 0))

    # draw mute button in game
    mute = pygame.draw.circle(screen, clr_white, (535, 70), 35)
    screen.blit(mute_btn, (500, 35))

    # initial deal to player and dealer
    if initial_deal:
        # in the initial deal we want two cards (for me and dealer), hence the for loop
        for i in range(2):
            my_hand, game_deck = deal_cards(my_hand, game_deck)
            dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)

        initial_deal = False

    # once game is activated, and dealt, calculate scores and display cards
    if active:
        player_score = calculate_score(my_hand)
        draw_cards(my_hand, dealer_hand, reveal_dealer)

        if reveal_dealer:
            dealer_score = calculate_score(dealer_hand)

            if dealer_score < 17:
                dealer_hand, game_deck = deal_cards(dealer_hand, game_deck)

        draw_scores(player_score, dealer_score)

    buttons = draw_game(active, records, outcome)

    #----------------#
    # event handling #
    #----------------#

    # if quit pressed, exit game

    for event in pygame.event.get():
        # when close button gets clicked, we get out of the 'run' loop and the game stops
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.MOUSEBUTTONUP:

            # mute / unmute soundtrack

            if mute.collidepoint(event.pos):
                if play_soundtrack:
                    pygame.mixer.music.pause()
                    play_soundtrack = False
                else: 
                    pygame.mixer.music.unpause()
                    play_soundtrack = True

            if not active:
                # add decks by clicking on add button

                # if add_deck button clicked, increase decks by 1
                if buttons[0].collidepoint(event.pos):
                    #according to google you can play blackjack with 1 - 8 decks of cards, 
                    # so you can't increase to more than 8 decks of cards
                    if decks < 8:
                        decks += 1

                # if decrease_deck button clicked, decrease decks by 1
                if buttons[1].collidepoint(event.pos):
                    #it would be impossible to play the game with less than 1 deck of cards ;-)
                    if decks > 1:
                        decks -= 1

                # when game not active, button[0] is 'DEAL' button (buttons list)
                if buttons[2].collidepoint(event.pos):
                    active = True
                    # initial deal is the only time in the game two cards are given
                    initial_deal = True
                    game_deck = copy.deepcopy(decks * one_deck)
                    my_hand = []
                    dealer_hand = []
                    outcome = 0
                    hand_active = True
                    reveal_dealer = False
                    outcome = 0
                    add_score = True
                    deal_sfx.play()
            else:
                # if player can hit, allow them to draw a card
                if buttons[0].collidepoint(event.pos) and player_score < 21 and hand_active:
                    my_hand, game_deck = deal_cards(my_hand, game_deck)
                    hit_sfx.play()
                # allow player to end turn (stand)
                elif buttons[1].collidepoint(event.pos) and not reveal_dealer:
                    reveal_dealer = True
                    hand_active = False
                    stop_sfx.play()
                    # prevent stop_fx.play() and win / loss sound effect from playing simultaneously 
                    time.sleep(1)
                elif len(buttons) == 3:
                    if buttons[2].collidepoint(event.pos):
                        active = True
                        initial_deal = True
                        game_deck = copy.deepcopy(decks * one_deck)
                        my_hand = []
                        dealer_hand = []
                        outcome = 0
                        hand_active = True
                        reveal_dealer = False
                        outcome = 0
                        add_score = True
                        dealer_score = 0
                        player_score = 0
                        deal_sfx.play()


    # if player busts, automatically end turn - treat like a stand
    if hand_active and player_score >= 21:
        hand_active = False
        reveal_dealer = True

    outcome, records, add_score = check_endgame(hand_active, dealer_score, player_score, outcome, records, add_score)

    pygame.display.flip()
pygame.quit()