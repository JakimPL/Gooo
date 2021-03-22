import math
from queue import*
import pygame, sys
from pygame.locals import*
pygame.init()

FPS = 60
clock = pygame.time.Clock()

n = 3	    # liczba samochodów gracza
N = n + 1   # rozmiar planszy

turn = 0	    # tura gracza (0 - niebieski, 1 - czerwony)
game_end = 0	    # czy koniec gry?
board_width = N	    # szerokość planszy
board_height = N    # wysokość planszy
x_offset = 16	    # offset x rysowania planszy
y_offset = 16	    # offset y rysowania planszy
size = 64	    # wielkość pola (w pikselach)
rim = 2		    # wielkość obwódki pola
panel = 600	    # szerokość panelu
frames = 0
nodes_per_frame = 1600
states_per_frame = 3200
to_compute = Queue()
to_analyze = []
refresh_frames = 3
refresh_counter = 1
computing = True
analyzing = True

node = None
node_analyze = None

# rozmiar okna
game_width = 2*x_offset + size * board_width + panel
game_height = 2*y_offset + size * board_width

counter = 0	    # licznik węzłów
depth_global = -1   # głębia szukania
points = 0	    # punkty w grze

# stan gry
player = [[0 for i in range(N)] for j in range(2)]
player[0][0] = -1
player[1][0] = -1

# kolory
TURN    = [(64,64,128), (128,64,64)]
COLOR   = [[(180,192,180) for i in range(N)] for j in range(N)]
LT_GREY = (210, 210, 210)
DK_GREY = (112, 112, 112)
BLACK   = (  0,   0,   0)
RIM     = [[(220, 220, 220) for i in range(N)] for j in range(N)]

# sprite
spr_car = [pygame.image.load("car" + str(i+1) + ".png") for i in range(2)]

# plansza N x N
board = [[0 for i in range(N)] for j in range(N)]

# font
font = pygame.font.SysFont("Lucida Console", 14)

# ustaw kolory
for i in range(n):
    COLOR[0][1+i] = (112,112,255)
    RIM[0][1+i] = (192,192,255)
    COLOR[1+i][0] = (255,112,112)
    RIM[1+i][0] = (255,192,192)
    board[0][i+1] = 1
    board[i+1][0] = 2

# display
DISPLAYSURF = pygame.display.set_mode((game_width,game_height),0,32)

### progress_calc wylicza postęp gry jako sumę ruchów wszystkich graczy
def progress_calc(temp_player):
    val = 2 # uwzględnij -1,-1 w stanie gry
    for j in range(2):
        for i in range(N):
            val += temp_player[j][i]
    return val	

### check_moves na podstawie stanu gry wyznacza możliwe ruchy do wykonania
def check_moves(list):
    moves = []		# utwórz listę możliwych ruchów
    player0 = list[0]	# pobierz stan gracza 1
    player1 = list[1]	# pobierz stan gracza 2
    if list[2] == 0:	# jeżeli tura gracza 1
        for i in range(1,N):
            if player0[i] + 1 == N: # jeżeli samochód może opuścić planszę
                moves += [i]
            elif player0[i] + 1 < N:
                if player1[player0[i] + 1] != i: # jeżeli gracz nie opuszcza planszy i nie jest blokowany przez drugiego gracza
                    moves += [i]
    else:
        for j in range(1,N):
            if player1[j] + 1 == N:
                moves += [j]
            elif player1[j] + 1 < N:
                if player0[player1[j] + 1] != j:
                    moves += [j]
    return moves

### state_chain_step dokonuje wyszukiwania ścieżek niekończących gry z ustalonego stanu początkowego
def state_chain_step(temp_player, temp_turn, temp_progress, temp_points, temp_game_end, state_move, depth, parent):
    global queue, leaves
    (temp_turn, temp_player, temp_points, temp_game_end, depth) = turn_next(temp_turn, state_move, temp_points, temp_player, depth)
    # print(temp_turn, temp_player, temp_progress, temp_points, temp_game_end, state_move)
    if temp_game_end == 0:
        state_new = game_state([temp_player[0], temp_player[1]], temp_turn, temp_points, parent) # utwórz nowy stan gry odpowiadający możliwemu ruchowi
        queue += [[state_new, depth]] # dodaj do kolejki możliwy stan
    else:
        leaves += [parent]  # jeżeli gra się kończy, oznacz stan jako liść.
    return temp_points	    # zwróć liczbę punktów po wykonaniu tego ruchu

### state_chain dokonuje wyszukania możliwych ścieżek ruchów z ustaloną głębią i stanem początkowym
def state_chain(state, depth):
    global queue, counter, frames, to_compute, node
    node = state
    frames += 1 
    if frames < nodes_per_frame:
        queue = []      # kolejka nowych stanów
        if depth == 0:  # zakończ szukanie, jeżeli przekroczono głębię
            to_compute.put(state)
            return -1
        list = state.to_list()	# konwertuj stan do listy
        moves = check_moves(list)	# sprawdź możliwe ruchy
        minmax = [] 		# utwórz tabelę minmax
        for m in range(len(moves)): # dla każdego możliwego ruchu
            pts = state_chain_step([[list[t][s] for s in range(N)] for t in range(2)], list[2], list[3], list[4], 0, moves[m], depth, state) # wykonaj krok
            minmax += [(moves[m], pts)] # dodaj do minmax (ruch, punkt)
            # jeżeli ruch gracza 1, wyznacz maksimum, minimum w przeciwnym razie
        if list[2] == 0:
            extr = max([item[1] for item in minmax])
        else:
            extr = min([item[1] for item in minmax])
        for item in queue:
            if item[0].points == extr:	    # omiń nieopłacalne ścieżki
                counter += 1            
            state_chain(item[0], item[1])   # dokonaj szukania dla nowego stanu       
        return state
    else:
        to_compute.put(state)
        return -1
    
def state_reset(state):
    state.minmax_old = state.minmax
    state.minmax = None
    for child in state.children:
        state_reset(child)

### state_analyze wyznacza minmax dla całych możliwych ścieżek, sprawdzając ich korzystność
def state_analyze(state):
    global frames, to_analyze
    frames += 1
    if frames < states_per_frame:
        if len(state.children) == 0:
            state.minmax = state.points
        else:
            for child in state.children:
                if child.minmax == None:
                    to_analyze += [state]
                    state_analyze(child)                
            count = len([item for item in state.children if item.turn == state.turn])
            if len([item for item in state.children if item.minmax != None]) == len(state.children):
                if count > 0:
                    if state.turn == 1:
                        state.minmax = max([item.minmax for item in state.children if item.turn == state.turn])                
                    else:
                        state.minmax = min([item.minmax for item in state.children if item.turn == state.turn])
                else:
                    if state.turn == 0:
                        state.minmax = max([item.minmax for item in state.children if item.turn != state.turn])
                    else:
                        state.minmax = min([item.minmax for item in state.children if item.turn != state.turn])
        return 0
    else:
        to_analyze += [state]
        return -1
             
### game_state reprezentuje stan gry złożonego z pozycji graczy, aktualnej tury, punktów w grze oraz poprzedni ruch (parent)
class game_state:
    def __init__(self, player, turn, points, parent = None, progress = -1):
        self.children = []
        self.player = player
        self.turn = turn
        if progress == -1:
            self.progress = progress_calc(self.player)
        else:
            self.progress = progress
        self.points = points        
        self.parent = parent
        self.minmax = None
        self.minmax_old = None
        if parent != None:
            parent.children += [self]
    def to_list(self): # zwróć listę stanu gry
        return [self.player[0], self.player[1], self.turn, self.progress, self.points, self.minmax]

### mouse_in sprawdza, czy kursos myszy jest w ustalonym regionie
def mouse_in(pos, i, j):
    if pos[0] > x_offset + i*size + 1 and pos[0] <= x_offset + (i+1)*size and pos[1] > y_offset + j*size + 1 and pos[1] <= y_offset + (j+1)*size:
        return True
    return False

### turn_next wykonuje następny ruch oraz sprawdza, czy drugi gracz ma możliwość ruchu oraz czy gra nie została skończona
def turn_next(var, k, points, temp_player, depth = depth_global):
    game_end = 0
    turn = var
    temp_player[var][k] += 1 # dodaj 1 do k-tej pozycji gracz
    test = (len(check_moves([temp_player[0], temp_player[1], 1 - var])) != 0) # czy są ruchy
    if test:
        turn = 1 - var	    # jeżeli tak, zmień turę
    else:        
        points += 1 - 2*var # jeżeli nie, dodaj punkty graczowi blokującemu
    if win_check(var, temp_player):
        game_end = 1 + var
    if test:
        return (turn, temp_player, points, game_end, depth - 1)
    else:
        return (turn, temp_player, points, game_end, depth)

### win_check sprawdza, czy któryś z graczy zakończył swoją grę
def win_check(var, temp_player):
    if var == 0:
        for i in range(1,N):
            if temp_player[0][i] < N:
                return False
        return True
    else:
        for j in range(1,N):
            if temp_player[1][j] < N:
                return False
        return True

'''def clear(queue):
    while not queue.empty():
        queue.get()'''
    
### reset zeruje tablice stanów gry (ale nie kasuje instancji obiektów!)
def reset(temp_player, turn, points):    
    global initial_state, counter, leaves, node
    counter = 0
    initial_state = game_state(temp_player, turn, points)
    leaves = []
    node = state_chain(initial_state, depth_global)
    for child in initial_state.children:
        state_analyze(child)
    print(initial_state.minmax)
    
'''def draw_status(initial_state):
    print([child.minmax for child in initial_state.children])
    for child in initial_state.children:
        if len(child.children) != 0:
            print(sum([childs.minmax for childs in child.children])/len(child.children))'''

reset(player, turn, points)

while True:
    frames = 0
    while not to_compute.empty():
        computing = True
        node = to_compute.get()
        if frames < nodes_per_frame:
            state_chain(node, depth_global)
        else:
            to_compute.put(node)
            break
    frames = 0
    if refresh_counter >= refresh_frames and len(to_analyze) == 0:
        previous = computing
        if to_compute.empty():
            computing = False
        if computing or previous != computing:
            state_reset(initial_state)
            state_analyze(initial_state)
            refresh_counter = 0
    else:
        refresh_counter += 1
    analyzing = False
    while not len(to_analyze) == 0:
        analyzing = True
        node_analyze = to_analyze.pop(-1)
        if frames < states_per_frame:
            state_analyze(node_analyze)
        else:
            to_analyze = to_analyze + [node_analyze]
            break
    if game_end == 0:
        pygame.draw.rect(DISPLAYSURF, TURN[turn], (0, 0, game_width, game_height))
    else:
        pygame.draw.rect(DISPLAYSURF, DK_GREY, (0, 0, game_width, game_height))
    for i in range(board_width):
        for j in range(board_height):
            pygame.draw.rect(DISPLAYSURF, RIM[i][j], (x_offset + i*size + 1, y_offset + j*size + 1, size - 2, size - 2))            
            if mouse_in(pygame.mouse.get_pos(),i,j):
                color = LT_GREY
                if pygame.mouse.get_pressed()[0] and game_end == 0:
                    if turn == 0:
                        if board[i][j] == 1:
                            flag = False
                            if i + 1 < N:
                                if board[i+1][j] == 0:
                                    board[i][j] = 0
                                    board[i+1][j] = 1
                                    flag = True
                            else:
                                board[i][j] = 0
                                flag = True
                            if flag:
                                (turn, player, points, game_end, dummy) = turn_next(0, j, points, player)
                                for child in initial_state.children:
                                    if child.player == player:
                                        initial_state = child
                                        break
                    else:
                        if board[i][j] == 2:
                            flag = False
                            if j + 1 < N:
                                if board[i][j+1] == 0:
                                    board[i][j] = 0
                                    board[i][j+1] = 2
                                    flag = True
                            else:
                                board[i][j] = 0
                                flag = True
                            if flag:
                                (turn, player, points, game_end, dummy) = turn_next(1, i, points, player)
                                for child in initial_state.children:
                                    if child.player == player:
                                        initial_state = child
                                        break
            else:
                color = COLOR[i][j]
            if game_end == 0:
                pygame.draw.rect(DISPLAYSURF, color, (x_offset + i*size + rim,y_offset + j*size + rim, size - 2*rim, size - 2*rim))
            if board[i][j] == 1:
                DISPLAYSURF.blit(spr_car[0], (x_offset + i*size + 1, y_offset + j*size + 1))
            elif board[i][j] == 2:
                DISPLAYSURF.blit(spr_car[1], (x_offset + i*size + 1, y_offset + j*size + 1))
    if points > 1:
        text = "Blue player wins by " + str(points) + " points."
    elif points == 1:
        text = "Blue player wins by " + str(points) + " point."
    elif points == 0:
        text = "Draw."
    elif points == -1:
        text = "Red player wins by " + str(-points) + " point."
    else:
        text = "Red player wins by " + str(-points) + " points."
    label = font.render(text, 1, (255,255,255))
    DISPLAYSURF.blit(label, (game_width - panel, y_offset))
    DISPLAYSURF.blit(font.render("Position: " + str(player), 1, (255,255,255)), (game_width - panel, 2*y_offset))
    DISPLAYSURF.blit(font.render("Searching: " + str(node.player), 1, (255,255,255)), (game_width - panel, 3*y_offset))
    DISPLAYSURF.blit(font.render("Analyzing: " + str(node_analyze.player), 1, (255,255,255)), (game_width - panel, 4*y_offset))
    DISPLAYSURF.blit(font.render("Minmax: " + str([child.minmax_old for child in initial_state.children]), 1, (255,255,255)), (game_width - panel, 5*y_offset))
    DISPLAYSURF.blit(font.render("Computing? " + str(computing), 1, (255,255,255)), (game_width - panel, 6*y_offset))
    DISPLAYSURF.blit(font.render("Analyzing? " + str(analyzing), 1, (255,255,255)), (game_width - panel, 7*y_offset))
    DISPLAYSURF.blit(font.render("Counter: " + str(counter), 1, (255,255,255)), (game_width - panel, 8*y_offset))
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                reset(player, turn, points)
    clock.tick(FPS)
    pygame.display.update()
