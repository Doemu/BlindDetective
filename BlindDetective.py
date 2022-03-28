import random
import time
import os
from collections import deque

clear = lambda: os.system('cls')

# игровые параметры
ROW = 8
COL = 8
MAX_TURNS = 30
MAX_EPISODES = 25000
# гиперпараметры
EPSILON = 0.5
LYAMBDA = 0.4
# инициализация необходимых переменных
# state = [up, right, bottom, left, mid, prev_mid, prev_mid2]
Q = {}
episode = 1
turn = 1
deaths = 0
# для сбора информации
total_score_deque = deque()     # будут храниться последние 10 результатов
total_score_deque.append(0)
#total_score = 0


#RED_TEXT = '\033[91m'
RED_TEXT = ''
#RESET_TEXT = '\033[0m'
RESET_TEXT = ''

def print_matrix(A):
    print('\n'.join([''.join(['{:4}'.format(item) for item in row])
                     for row in A]))


class Detective:
    def __init__(self):
        self.i = random.randint(0, ROW - 1)
        self.j = random.randint(0, COL - 1)
        self.score = 0
        self.prev_result = 0

        self.state = [0, 0, 0, 0, 0,   None, None]
        self.prev_state = [None, None, None, None, None,   None, None]

        self.prev_action = 0

        self.is_alive = True
        #self.observe() #?

    def action(self):
        global EPSILON
        if random.random() > EPSILON:   # следуем стратегии
            action_list = Q[self.state.__str__()]
            max_val = max(action_list)
            max_idx = action_list.index(max_val)

            if max_idx == 0:
                self.i = self.i - 1
                self.prev_action = 0
            elif max_idx == 1:
                self.j = self.j + 1
                self.prev_action = 1
            elif max_idx == 2:
                self.i = self.i + 1
                self.prev_action = 2
            elif max_idx == 3:
                self.j = self.j - 1
                self.prev_action = 3

        else:   # исследуем случайным оразом
            moved = False
            while moved is False:
                rnd = random.random()
                if rnd < 0.25:              # up
                    if self.i-1 >= 0:
                        self.i = self.i - 1
                        moved = True
                        self.prev_action = 0
                elif rnd < 0.5:             # right
                    if self.j+1 < COL:
                        self.j = self.j + 1
                        moved = True
                        self.prev_action = 1
                elif rnd < 0.75:            # bottom
                    if self.i+1 < ROW:
                        self.i = self.i + 1
                        moved = True
                        self.prev_action = 2
                else:  # <1                 # left
                    if self.j-1 >= 0:
                        self.j = self.j - 1
                        moved = True
                        self.prev_action = 3

    #depr
    def move_safely(self, case):
        if case == 'up':
            pass
        elif case == 'right':
            pass
        elif case == 'bottom':
            pass
        else:       #4
            pass

    def observe(self, culprit):
        if turn != 1:
            self.prev_state = self.state.copy()

        if turn != 1:
            if turn != 2:
                self.state[6] = self.state[5]
            self.state[5] = self.state[4]

        # если детектив не вышел за границы, то сохраняем наблюдения
        if not (self.i < 0 or self.i == ROW or self.j < 0 or self.j == COL):
            if self.i-1 >= 0: self.state[0] = grid[self.i-1][self.j]
            else: self.state[0] = None
            if self.j+1 < COL: self.state[1] = grid[self.i][self.j+1]
            else: self.state[1] = None
            if self.i+1 < ROW: self.state[2] = grid[self.i+1][self.j]
            else: self.state[2] = None
            if self.j-1 >= 0: self.state[3] = grid[self.i][self.j-1]
            else: self.state[3] = None
            self.state[4] = grid[self.i][self.j]

            # победа, конец игры
            if grid[self.i][self.j] == 100:
                culprit.is_caught = True

        else:   # смерть, конец игры
            self.is_alive = False
            global deaths
            deaths = deaths + 1

    # manually
    def get_reward(self):
        score = 0
        if not self.is_alive: #self.i<0 or self.i == ROW or self.j<0 or self.j == COL:
            score = score - 1000
        else:
            score = score - 6                     # наказание, чтобы агент торопился победить и не эксплойтил награды
            score = score + grid[self.i][self.j]  # награда за нахождение подсказки или поимки преступника

        self.prev_result = score
        self.score = self.score + score


class Culprit:
    def __init__(self):
        self.i = random.randint(0, ROW - 1)
        self.j = random.randint(0, COL - 1)
        self.is_caught = False

    def fill_the_evidence(self):
        # himself
        grid[self.i][self.j] = 100
        # 5
        if self.j != 0:
            grid[self.i][self.j - 1] = 5
            if self.i != 0: grid[self.i - 1][self.j - 1] = 5
            if self.i != ROW - 1: grid[self.i + 1][self.j - 1] = 5
        if self.i != 0: grid[self.i - 1][self.j] = 5
        if self.i != ROW - 1: grid[self.i + 1][self.j] = 5
        if self.j != COL - 1:
            grid[self.i][self.j + 1] = 5
            if self.i != 0: grid[self.i - 1][self.j + 1] = 5
            if self.i != ROW - 1: grid[self.i + 1][self.j + 1] = 5
        # 3
        if self.i-2 >= 0 and self.j-2 >= 0: grid[self.i-2][self.j-2] = 3
        if self.i-2 >= 0 and self.j+2 < COL: grid[self.i-2][self.j+2] = 3
        if self.i+2 < ROW and self.j-2 >= 0: grid[self.i+2][self.j-2] = 3
        if self.i+2 < ROW and self.j+2 < COL: grid[self.i+2][self.j+2] = 3
        # 1
        if self.j-4 >= 0:
            grid[self.i][self.j-4] = 1
            if self.i-2 >= 0: grid[self.i-2][self.j-4] = 1
            if self.i-4 >= 0: grid[self.i-4][self.j-4] = 1
            if self.i+2 < ROW: grid[self.i+2][self.j-4] = 1
            if self.i+4 < ROW: grid[self.i+4][self.j-4] = 1
        if self.j+4 < COL:
            grid[self.i][self.j+4] = 1
            if self.i-2 >= 0: grid[self.i-2][self.j+4] = 1
            if self.i-4 >= 0: grid[self.i-4][self.j+4] = 1
            if self.i+2 < ROW: grid[self.i+2][self.j+4] = 1
            if self.i+4 < ROW: grid[self.i+4][self.j+4] = 1
        if self.i-4 >= 0:
            grid[self.i-4][self.j] = 1
            if self.j-2 >= 0: grid[self.i-4][self.j-2] = 1
            if self.j+2 < COL: grid[self.i-4][self.j+2] = 1
        if self.i+4 < ROW:
            grid[self.i+4][self.j] = 1
            if self.j-2 >= 0: grid[self.i+4][self.j-2] = 1
            if self.j+2 < COL: grid[self.i+4][self.j+2] = 1


# то, чем гордиться не приходится
def q_init():
    mas = [None, 0, 1, 3, 5, 100]
    for a in range(0, 6):
        for r in range(0, 6):
            for t in range(0, 6):
                for w in range(0, 6):
                    for o in range(0, 6):
                        for R in range(0, 5):
                            for k in range(0, 5):
                                arr = [mas[a], mas[r], mas[t], mas[w], mas[o], mas[R], mas[k]]
                                Q[arr.__str__()] = [random.random(), random.random(), random.random(), random.random()]

def q_update(detective):
    global Q
    Q[detective.prev_state.__str__()][detective.prev_action] = Q[detective.prev_state.__str__()][detective.prev_action] + EPSILON * (detective.prev_result + LYAMBDA * max(Q[detective.state.__str__()]) - Q[detective.prev_state.__str__()][detective.prev_action])


def place(string, i, j, letter):
    # ()*() \избавиться от плюсов и минусов\ + ()*() \избавиться от решёток и пробелов\ +
    # (2) \поправка для середины клетки\ + () \перемещение в нужный столбец\ + () + (1) \знаки перехода на новую строку\
    position = ((COL + 1 + 3 * COL) * (i + 1) + (COL + 1 + 3 * COL) * (i) + 2 + (j * 4) + (1 + i * 2) + 1)
    string = string[:position] + letter + string[position + 1:]
    return string


def draw(detective, culprit):
    if episode >= MAX_EPISODES-5:
        #clear()

        print('Turn: ' + turn.__str__())
        #print('PrevScore: ' + detective.prev_score.__str__())
        print('Score: ' + detective.score.__str__())
        #print(detective.prev_state)
        #print(detective.state)
        print(detective.prev_result)

        sep = '\n' + '+---' * COL + '+\n'
        str = sep + ('|   ' * COL + '|' + sep) * ROW
        str = place(str, culprit.i, culprit.j, 'C')

        for i in range(0, ROW):
            for j in range(0, COL):
                if grid[i][j] != 0 and grid[i][j] != 100: str = place(str, i, j, grid[i][j].__str__())

        str = place(str, detective.i, detective.j, 'D')
        print(str)
        time.sleep(0.3)





q_init()

for j in range (0, MAX_EPISODES):
    print('Episode: ' + episode.__str__())
    print('Avg total score: ' + (sum(total_score_deque) / len(total_score_deque)).__str__())
    print('Epsilon: ' + str(EPSILON))

    grid = [[0] * COL for i in range(ROW)]
    culprit = Culprit()
    culprit.fill_the_evidence()
    detective = Detective()

    i = 0
    while i < MAX_TURNS and detective.is_alive and not culprit.is_caught:
        detective.observe(culprit)
        if detective.is_alive:
            draw(detective, culprit)
        detective.get_reward()
        q_update(detective)
        if detective.is_alive:
            detective.action()

        turn = turn + 1
        i = i + 1

    if not detective.is_alive:
        draw(detective, culprit)
        print(RED_TEXT + 'Detective checked how hard the wall is')
    elif culprit.is_caught:
        draw(detective, culprit)
        print(RED_TEXT + 'Detective won')
    else:
        print(RED_TEXT + 'Ran out of time')

    if episode >= MAX_EPISODES-5:
        time.sleep(1)

    print(RESET_TEXT)

    #print('Score:' + detective.score.__str__())
    #print('deq:' + total_score_deque.__str__())
    if len(total_score_deque) == 10:
        total_score_deque.popleft()
    total_score_deque.append(detective.score)

#    total_score = total_score + detective.score
    episode = episode + 1
    if episode < MAX_EPISODES - 5:
        EPSILON = EPSILON - 0.5 / MAX_EPISODES  # со временем больше шансов следовать стратегии
    else:
        EPSILON = 0

    turn = 1


