import os.path
import json
import ast
import itertools
import time
from binascii import hexlify
script_path = (os.path.dirname(os.path.realpath(__file__)))

def my_random_int(start, end):
    # a very simple randomizer
    end = end + 1
    rand = int(hexlify(os.urandom(16)), 16)
    return rand % (end - start) + start
def rand_item(list):
    start = 0
    end = len(list) - 1
    return list[my_random_int(start, end)]
def say_hello():
    print("========================= Welcome to crossnuls game =========================")
    print("========================= version 2.0               =========================")
    print("========================= tested for python 3.7.5   =========================")
    print("=== You can setup the game ether you want ")
    print("=== Players count")
    print("=== Size of field")
    print("=== What kind of symbol you will place")
    print("=== AI has a simple learning algorythm")
    print("=== Warning! don't set a high amount of cells or players!")
    print("=== It may cause issues!")
    print("=== go to main() func to uncoment some rows and run game in circle")

## reading map
def get_map(side_len, players_count):
    #getting map from file or build new if not exists
    map_path = "\\cn_map_" + str(side_len) + "_" + str(players_count) + ".txt"
    map_path = script_path + map_path
    print("checking map " + map_path)
    try:
        with open(map_path, 'r', encoding="utf-8")as cn_file:
            return json.load(cn_file)
    except Exception:
        print("can't load map, creating empty")
        return {}

def save_map(price_map, side_len, players_count):
    #saving condi map to file
    map_path = "\\cn_map_" + str(side_len) + "_" + str(players_count) + ".txt"
    map_path = script_path + map_path
    with open(map_path, "w+") as cn_file:
        json.dump(price_map, cn_file)

                
def show_field(cs, side_len, players_signs):
    # return
    # display game field in console
    # supports squares only
    
    # prepare vars that are not going to be changed
    cells_in_side = range(side_len)
    p1 = "-"*(side_len*6 +1) ## row separator
    p2 = "|" + "     |"*side_len # empty string for bigger cells
    cell_delim = "  | " #cell separator

    # exact build text view
    print (p1)
    for i in cells_in_side: ## rows
        cell_vals = []
        for j in cells_in_side: ## columns
            cv = int(cs[i*side_len + j])
            if cv == 0:
                cv = str(i*side_len + j + 1)
            else:
                cv = players_signs[cv - 1]
            cv = ' '*(2 - len(cv)) + cv
            cell_vals.append(cv)
        cell_string = "| " + cell_delim.join(cell_vals) + "  |"
        print (p2)
        print (cell_string)
        print (p2)
        print (p1)
    print ("\n")

def get_field_string(condition, cell_count, players_count):
    ## gets condition in dec num sys, returns string in num system of players_count
    num_system = condi_stringify(condition, players_count + 1)
    return '0'*(cell_count - len(num_system)) + num_system

def condi_stringify(condition, cc):
    ost = condition % cc
    int_del =  condition // cc
    if int_del == 0 :
        return str(condition)
    else:
        if(ost > 9):
            ost = chr(87 + ost)
        return condi_stringify(int_del, cc) + str(ost)


def get_options():
    options_path = script_path + "\\options.txt"
    try:
        with open(options_path, 'r') as opt_file:
            options = json.load(opt_file)
    except Exception:
        print("error on read options, creating new")
        options = {'side_len': 3, 'players_count': 2, 'players_is_ai': [False, False], 'signs': ['X', 'O', 'T', 'A']}
        save_options(options)
    print("current options:")
    print(options)
    return options

def save_options(options):
    options_path = script_path + "\\options.txt"
    try:
        with open(options_path, 'w') as opt_file:
            json.dump(options, opt_file, indent=4)
    except Exception:
        print("cannot write options")
    

def get_user_options(options):
    # Set options via write like [option]=[value]
    print("current options:")
    print(options)

    opts_quit = False
    while not opts_quit:
        player_input = input("Set options via write like [option]=[value]\n")
        if player_input == "quit":
            opts_quit = True
        else:
            try:
                opt = player_input.split('=')
                opt[0] = opt[0].strip()
                opt[1] = opt[1].strip()
                options[opt[0]] = opt[1]
                if(opt[0] == 'players_is_ai'):
                    try:
                        options['players_is_ai'] = json.loads(opt[1])
                    except Exception:
                        print("cant read your option players_is_ai. please write value like in json [false, false]")
                elif opt[0] == 'players_count': 
                    options['players_is_ai'] = [False for _ in range(int(opt[0])+1)]
            except Exception:
                print("error on accepting option")
        print("current options:")
        print(options)
    save_options(options)
    return options

def run_game(options, current_map):
    # dev stage
    players_count = int(options['players_count'])
    side_len = int(options['side_len'])
    players_is_ai = options['players_is_ai']
    players_signs = options['signs']
    size = side_len*side_len
    condition = 0
    cs = get_field_string(condition, size, players_count)
    win = False
    stopped = False
    draw = False
    turns = []
    win_cases = build_win_cases(side_len)
    #print(win_cases)
    while (not win) & (not stopped):
        for current_player in range(players_count):
            show_field(cs, side_len, players_signs)
            if players_is_ai[current_player] == True:
                condition = get_ai_step(condition, options, current_player, current_map)
            else:
                condition = get_player_step(condition, options, current_player)
            
            if not condition: 
                stopped = True
            else:
                turns.append(condition)
                cs = get_field_string(condition, size, players_count)
                winner = check_win(cs, win_cases, side_len, players_count)
            
            if not winner is False:
                if winner == 'draw':
                    draw = True
                else:
                    winner = players_signs[winner]
                win = True
            if win | stopped:
                break
       
    show_field(cs, side_len, players_signs) 
    print("made turns\n", turns)

    if draw:
        print("Draw!")
    elif win:
        print("Congratulations, " + winner + "! You Win!")
    elif stopped:
        print("Game was stopped!")

    if not draw:
        current_map = update_map(current_map, players_count, turns, players_signs.index(winner))
    return current_map

def update_map(current_map, players_count, turns, p_w):
    k = 0
    for turn in turns:
        k = k + 1
        success_case = [-0.01*k, 0, 0.01*k, 1] 
        new_turn = []
        for p in range(players_count):
            ## i_success - index of success:
            ## 0 - not last turn and not winner
            ## 1 - last turn and not winner
            ## 2 - not last turn and winner
            ## 3 - last turn and winner
            i_success = int(p == p_w)*2 + int(k == len(turns))
            new_turn.append(success_case[i_success])

        t_str = str(turn)
        if not (t_str in current_map):
            current_map[t_str] = [0 for _ in range(players_count)]
        current_map[t_str] = [x + y for [x, y] in zip(current_map[t_str], new_turn)]
    return current_map


def build_win_cases(side_len):
    # returns list of list of indexes to win
    horrs = [[] for _ in range(side_len)]
    verts = [[] for _ in range(side_len)]
    diags = [[], []]
    for i in range(side_len):
        for j in range(side_len):
            if i == 0:
                diags[0].append(j*side_len + j)
                diags[1].append((side_len-j)*side_len - (side_len-j))
            horrs[j].append(j*side_len + i)
            verts[i].append(j*side_len + i)
    win_cases = horrs + verts + diags
    return win_cases

def check_win(cs, win_cases, side_len, players_count):
    # dev stage
    # side_len = len(win_cases[0])
    inwin = list(map((lambda win_case: ''.join([cs[i] for i in win_case])), win_cases))
    # print(inwin)
    for p in range(players_count):
        win_string = str(p+1)*side_len
        # print(win_string)
        if win_string in inwin:
            return p
    if "0" not in cs: 
        return 'draw'
    return False
    
def get_ai_step(condition, options, current_player, current_map):
    # dev stage
    side_len = int(options['side_len'])
    players_count = int(options['players_count'])
    size = side_len*side_len
    cs = get_field_string(condition, size, players_count)
    size = len(cs)
    empty_cells = [(size - i-1) for i in range(size) if cs[i] == '0']
    add_vals = [(current_player+1) * ((players_count+1)**cell) for cell in empty_cells]
    av_conds = [condition + add_val for add_val in add_vals]

    max_price = 0
    for cc in av_conds:
        if str(cc) in current_map:
            if current_map[str(cc)][current_player] > max_price:
                chosen = cc
                max_price = current_map[str(cc)][current_player]

    for_learning = my_random_int(1, 10)
    if (max_price == 0) | (for_learning < 3):
        print("chosen random")
        chosen = rand_item(av_conds)
    return chosen

    
def get_player_step(condition, options, current_player):
    # dev stage
    side_len = int(options['side_len'])
    players_count = int(options['players_count'])
    players_signs = options['signs']
    size = side_len*side_len
    cs = get_field_string(condition, size, players_count)
    accepted = False
    while not accepted:
        try:
            cell = int(input("turn " + players_signs[current_player] + "\n"))
            if not cell in range(1, size + 1):
                print("current field size is " + size)
            elif cs[cell-1] != '0':
                print("this cell is busy")
            else:
                accepted = True
                cell = size - cell
                add_val = (current_player+1) * ((players_count+1)**cell)
        except ValueError:
            print("invalid input")
    return condition + add_val


def main():
    say_hello()
    commands = ["quit", "opts", "play"]
    options = get_options()

    # just edit options.txt and uncomment rows below to run game in circle
    # run_game_circle(options, 1000)
        
    game_quit = False
    while not game_quit:
        print("Available commands:")
        print(commands)
        player_input = input("Enter your command\n")
        if player_input == "quit":
            game_quit = True
        elif player_input == "opts":
            options = get_user_options(options)
        elif player_input == "play":
            run_game_circle(options, 1)
        else:
            print("unknown command")
    print("Thanks for using this app!")


def run_game_circle(options, c_count):
    players_count = int(options['players_count'])
    side_len = int(options['side_len'])
    current_map = get_map(side_len, players_count)
    for _ in range(c_count):
        current_map = run_game(options, current_map)
    save_map(current_map, side_len, players_count)


main()
