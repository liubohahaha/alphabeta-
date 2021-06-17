from enum import IntEnum
import pygame
from pygame.locals import *
import pygame.gfxdraw
from pygame import *
GAME_VERSION = 'V1.0'

REC_SIZE = 50
CHESS_RADIUS = REC_SIZE // 2 - 2
CHESS_LEN = 15
MAP_WIDTH = CHESS_LEN * REC_SIZE
MAP_HEIGHT = CHESS_LEN * REC_SIZE

INFO_WIDTH = 200
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 50

SCREEN_WIDTH = MAP_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT

Inside_Width=6
Stone_Radius=REC_SIZE//2+3
Up_x=REC_SIZE*CHESS_LEN+REC_SIZE//2
Up_y=REC_SIZE
Down_x = REC_SIZE * CHESS_LEN + REC_SIZE // 2
Down_y = REC_SIZE+Stone_Radius*2+10
BLACK_COLOR=(0,0,0)
WHITE_COLOR=(255,255,255)
GREY_COLOE=(200,200,200)
RED_COLOR= (200, 30, 30)


class MAP_ENTRY_TYPE(IntEnum):
    MAP_EMPTY = 0,
    MAP_PLAYER_ONE = 1,
    MAP_PLAYER_TWO = 2,
    MAP_NONE = 3,  # out of map range


class Map():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.map = [[0 for x in range(self.width)] for y in range(self.height)]
        self.steps = []

        self.black_win_count = 0
        self.white_win_count = 0
        self.playerInMap=MAP_ENTRY_TYPE.MAP_PLAYER_ONE
    def reset(self):
        for y in range(self.height):
            for x in range(self.width):
                self.map[y][x] = 0
        self.steps = []
        self.playerInMap=MAP_ENTRY_TYPE.MAP_PLAYER_ONE
    def regret(self):
        if self.playerInMap==MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            self.steps.pop()
            self.steps.pop()
        else:
            return
    def black_count_add(self):
        self.black_win_count+=1
    def white_count_add(self):
        self.white_win_count+=1
    def reverseTurn(self, turn):
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            return MAP_ENTRY_TYPE.MAP_PLAYER_TWO
        else:
            return MAP_ENTRY_TYPE.MAP_PLAYER_ONE
    def reverseTurnInMap(self,turn):
        if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
            return MAP_ENTRY_TYPE.MAP_PLAYER_TWO
        else:
            return MAP_ENTRY_TYPE.MAP_PLAYER_ONE
    def getMapUnitRect(self, x, y):
        map_x = x * REC_SIZE
        map_y = y * REC_SIZE

        return (map_x, map_y, REC_SIZE, REC_SIZE)

    def MapPosToIndex(self, map_x, map_y):
        x = map_x // REC_SIZE
        y = map_y // REC_SIZE
        return (x, y)

    def isInMap(self, map_x, map_y):
        if (map_x <= 0 or map_x >= MAP_WIDTH or
                map_y <= 0 or map_y >= MAP_HEIGHT):
            return False
        return True

    def isEmpty(self, x, y):
        return (self.map[y][x] == 0)

    def click(self, x, y, type):
        self.map[y][x] = type.value
        self.steps.append((x, y))
        #print(self.steps)
    def drawChess(self, screen):
        player1 = WHITE_COLOR
        player2 = BLACK_COLOR
        player_color = [player1, player2]

        font = pygame.font.SysFont(None, REC_SIZE * 2 // 3)
        for i in range(len(self.steps)):
            x, y = self.steps[i]
            map_x, map_y, width, height = self.getMapUnitRect(x, y)
            pos, radius = (map_x + width // 2, map_y + height // 2), CHESS_RADIUS
            turn = self.map[y][x]
            if turn == 1:
                op_turn = 2
            else:
                op_turn = 1
            pygame.draw.circle(screen, player_color[turn - 1], pos, radius)

            image = font.render(str(i), True, player_color[op_turn - 1], player_color[turn - 1])
            image_rect = image.get_rect()
            image_rect.center = pos
            screen.blit(image, image_rect)

        if len(self.steps) > 0:
            last = self.steps[-1]
            map_x, map_y, width, height = self.getMapUnitRect(last[0], last[1])
            purple_color = (255, 0, 0)
            last_Rect = [(map_x, map_y), (map_x + width, map_y),
                          (map_x + width, map_y + height), (map_x, map_y + height)]
            pygame.draw.lines(screen, purple_color, True, last_Rect, 1)

    def print_text(self,screen, font, x, y, text, fcolor):
        imgText = font.render(text, True, fcolor)
        screen.blit(imgText, (x, y))

    def draw_chessman_pos(self,screen, pos, stone_color):
        pygame.gfxdraw.aacircle(screen, pos[0], pos[1], Stone_Radius, stone_color)
        pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], Stone_Radius, stone_color)
    def drawBackground(self, screen):
        color = (0, 0, 0)
        pygame.draw.rect(screen, color, (REC_SIZE//2-Inside_Width, REC_SIZE//2-Inside_Width,
                                         REC_SIZE*(self.width-1)+Inside_Width*2, REC_SIZE*(self.height-1)+Inside_Width*2), 4)
        self.draw_chessman_pos(screen,[Up_x,Up_y],(255,255,255))
        self.draw_chessman_pos(screen,[Down_x,Down_y],(45,45,45))

        font=pygame.font.Font('HGDGY_CNKI.TTF',50)
        self.print_text(screen,font,Up_x+Stone_Radius*2-15,REC_SIZE//2,'玩家',BLACK_COLOR)
        self.print_text(screen, font, Up_x + Stone_Radius * 2 - 15,REC_SIZE // 2+Stone_Radius*2+10, '电脑', BLACK_COLOR)

        self.draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius, SCREEN_HEIGHT - int(Stone_Radius * 4.5)),
                               WHITE_COLOR)
        self.draw_chessman_pos(screen, (SCREEN_HEIGHT + Stone_Radius, SCREEN_HEIGHT - Stone_Radius * 2),
                           BLACK_COLOR)

        self.print_text(screen, font, SCREEN_HEIGHT + Stone_Radius * 3,SCREEN_HEIGHT - int(Stone_Radius * 5.5) ,
                      f'{self.white_win_count} 胜',
                        WHITE_COLOR)
        self.print_text(screen, font, SCREEN_HEIGHT + Stone_Radius*3, SCREEN_HEIGHT - Stone_Radius * 3, f'{self.black_win_count} 胜',
                   BLACK_COLOR)

        for y in range(self.height):
            # draw a horizontal line
            start_pos, end_pos = (REC_SIZE // 2, REC_SIZE // 2 + REC_SIZE * y), (
            MAP_WIDTH - REC_SIZE // 2, REC_SIZE // 2 + REC_SIZE * y)
            if y == (self.height) // 2:
                width = 2
            else:
                width = 1
            pygame.draw.line(screen, color, start_pos, end_pos, width)

        for x in range(self.width):
            # draw a horizontal line
            start_pos, end_pos = (REC_SIZE // 2 + REC_SIZE * x, REC_SIZE // 2), (
            REC_SIZE // 2 + REC_SIZE * x, MAP_HEIGHT - REC_SIZE // 2)
            if x == (self.width) // 2:
                width = 2
            else:
                width = 1
            pygame.draw.line(screen, color, start_pos, end_pos, width)

        rec_size = 8
        pos = [(3, 3), (3,7),(11,7),(11, 3), (3, 11), (11, 11), (7, 7)]
        for (x, y) in pos:
            pygame.draw.rect(screen, color, (
            REC_SIZE // 2 + x * REC_SIZE - rec_size // 2, REC_SIZE // 2 + y * REC_SIZE - rec_size // 2, rec_size,
            rec_size))
