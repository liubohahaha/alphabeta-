import pygame
from pygame.locals import *
from GameMap import *
from ChessAI import *
from GameMap import Up_x,Up_y,Down_x,Down_y,RED_COLOR

class Button():
    def __init__(self, screen, text, x, y, color, enable):
        self.screen = screen
        self.width = BUTTON_WIDTH
        self.height = BUTTON_HEIGHT
        self.button_color = color
        self.text_color = (0,0,0)
        self.enable = enable
        self.font = pygame.font.Font('HGDGY_CNKI.TTF', 30)
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.topleft = (x, y)
        self.text = text
        self.init_msg()

    def init_msg(self):
        if self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
        else:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw(self):
        if self.enable:
            self.screen.fill(self.button_color[0], self.rect)
        else:
            self.screen.fill(self.button_color[1], self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)


class StartButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [WHITE_COLOR,GREY_COLOE], True)

    def click(self, game):
        if self.enable:
            game.start()
            game.winner = None
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True


class GiveupButton(Button):
    def __init__(self, screen, text, x, y):
        super().__init__(screen, text, x, y, [WHITE_COLOR,GREY_COLOE], False)

    def click(self, game):
        if self.enable:
            game.is_play = False
            if game.winner is None:
                game.winner = game.map.reverseTurn(game.player)
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
            self.enable = False
            return True
        return False

    def unclick(self):
        if not self.enable:
            self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[0])
            self.enable = True
# class RegretButton(Button):
#     def __init__(self,screen,text,x,y):
#         super().__init__(screen,text,x,y,[WHITE_COLOR,GREY_COLOE],False)
#
#     def click(self,game):
#         if self.enable:
#
#             self.msg_image = self.font.render(self.text, True, self.text_color, self.button_color[1])
#             self.enable = False
#             return True
#         return False
#     def unclick(self):
#         if not self.enable:
#             self.msg_image = self.font.render(self.text,True,self.text_color,self.button_color[0])
#             self.enable=True


class Game():
    def __init__(self, caption):
        pygame.init()
        self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        self.map = Map(CHESS_LEN, CHESS_LEN)
        self.buttons = []
        self.buttons.append(StartButton(self.screen, '开始', MAP_WIDTH + 30, Down_y+REC_SIZE+10))
        #self.buttons.append(RegretButton(self.screen, '悔棋', MAP_WIDTH + 30,BUTTON_HEIGHT  +Down_y+REC_SIZE+20))
        self.buttons.append(GiveupButton(self.screen, '认输', MAP_WIDTH + 30, BUTTON_HEIGHT  + Down_y + REC_SIZE + 30 ))

        self.is_play = False
        self.has_add=False


        self.action = None
        self.AI = Computer(CHESS_LEN)
        self.useAI = False
        self.winner = None

    def start(self):
        self.is_play = True
        self.player = MAP_ENTRY_TYPE.MAP_PLAYER_ONE
        self.map.reset()
        self.has_add=False
    def print_text(self,screen, font, x, y, text, fcolor):
        imgText = font.render(text, True, fcolor)
        screen.blit(imgText, (x, y))
    def play(self):
        self.clock.tick(60)
        font2 = pygame.font.Font('HGDGY_CNKI.TTF', 100)
        chess_bg_color = (0xE3, 0x92, 0x65)
        pygame.draw.rect(self.screen, chess_bg_color, pygame.Rect(0, 0, MAP_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, chess_bg_color, pygame.Rect(MAP_WIDTH, 0, INFO_WIDTH, SCREEN_HEIGHT))

        for button in self.buttons:
            button.draw()

        if self.is_play and not self.isOver():
            if self.useAI:
                x, y = self.AI.find_Best_Position(self.map.map, self.player)
                self.checkClick(x, y, True)
                self.useAI = False

            if self.action is not None:
                self.checkClick(self.action[0], self.action[1])
                self.action = None

            if not self.isOver():
                self.changeMouseShow()
        self.map.drawBackground(self.screen)
        self.map.drawChess(self.screen)
        if self.isOver():
            if self.winner == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
                if not self.has_add:
                    self.map.white_count_add()
                    self.has_add=True

                self.print_text(self.screen,font2, (SCREEN_WIDTH )//10, (SCREEN_HEIGHT )//2-REC_SIZE,'You Win! :)',RED_COLOR)
            else:
                if not self.has_add:
                    self.map.black_count_add()
                    self.has_add=True
                self.print_text(self.screen,font2, (SCREEN_WIDTH )//10, (SCREEN_HEIGHT )//2-REC_SIZE,'You Lose... :(',RED_COLOR)

    def changeMouseShow(self):
        map_x, map_y = pygame.mouse.get_pos()
        x, y = self.map.MapPosToIndex(map_x, map_y)
        if self.map.isInMap(map_x, map_y) and self.map.isEmpty(x, y):
            pygame.mouse.set_visible(False)
            red = (255,0,0)
            pos, radius = (map_x, map_y), CHESS_RADIUS
            pygame.draw.circle(self.screen, red, pos, radius)
        else:
            pygame.mouse.set_visible(True)

    def checkClick(self, x, y, isAI=False):
        self.map.click(x, y, self.player)
        if self.AI.isWin(self.map.map, self.player):
            self.winner = self.player
            self.click_button(self.buttons[1])
        else:
            self.player = self.map.reverseTurn(self.player)
            self.map.reverseTurnInMap(self.player)
            if not isAI:
                self.useAI = True

    def mouseClick(self, map_x, map_y):
        if self.is_play and self.map.isInMap(map_x, map_y) and not self.isOver():
            x, y = self.map.MapPosToIndex(map_x, map_y)
            if self.map.isEmpty(x, y):
                self.action = (x, y)

    def isOver(self):
        return self.winner is not None

    def click_button(self, button):
        if button.click(self):
            for tmp in self.buttons:
                if tmp != button:
                    tmp.unclick()

    def check_buttons(self, mouse_x, mouse_y):
        for button in self.buttons:
            if button.rect.collidepoint(mouse_x, mouse_y):
                self.click_button(button)
                break


game = Game("Developed By Dzk and Lb")
while True:
    game.play()
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            game.mouseClick(mouse_x, mouse_y)
            game.check_buttons(mouse_x, mouse_y)
