import pygame 
from pygame.sprite import Group 

from snake_register import Register


class Game_view:
    pygame.init()
    s_screen = pygame.display.set_mode((1120, 700))
    pygame.display.set_caption("Snake")
    pygame.display.flip()

    #颜色设定(待定   
    def __init__(self): 
        
        #暂定放缩是10
        self.screen = self.s_screen
        self.scale = 10
        self.screen_rect = self.screen.get_rect()
        self.text_color = (255, 250, 250)#白色
        self.board_color = (105, 105, 105)
        self.body_color = (102, 205, 0)
        self.head_color = (255, 0, 0)

        self.font = pygame.font.Font("font.ttf", 24)
        self.wall_image = pygame.image.load('images/wall.png')
        self.apple_image = pygame.image.load('images/apple.bmp')
        self.map_image = pygame.image.load('images/map1.bmp')
        self.end_image = pygame.image.load('images/end.bmp')
        


    def scale_pos(self,pos):
        """得到坐标放缩后的对应点"""
        x, y = pos
        r_x = x * self.scale
        r_y = y * self.scale
        return (r_x, r_y)


    def draw_head(self, head):
        """画出蛇头"""
        h_x, h_y = self.scale_pos(head)
        head_rect = pygame.Rect(h_x, h_y, self.scale, self.scale)
        pygame.draw.rect(self.screen, self.head_color, head_rect)


    def draw_snake_body(self, body):
        """画蛇身"""
        for pos in body:
            #snake = Snake_body(self.screen, pos)
            #self.body.add(snake)
        #self.body.draw(self.screen)
        #self.body.empty()
            b_x, b_y = self.scale_pos(pos)
            pos_rect = pygame.Rect(b_x, b_y, self.scale, self.scale)
            pygame.draw.rect(self.screen, self.body_color, pos_rect)


    def draw_walls(self,walls):
        """墙体贴图"""
        for pos in walls:
            w_x, w_y = self.scale_pos(pos)            
            self.screen.blit(self.wall_image, (w_x, w_y))

    def draw_apples(self, apples):
        """贴苹果"""
        for pos in apples:
            a_x, a_y = self.scale_pos(pos)
            self.screen.blit(self.apple_image, (a_x, a_y))

    def draw_bg_1(self):
        """登录注册界面"""
        filename='music/bgm.mp3'
        #播放bgm
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(-1,0)
        pygame.mixer.music.set_volume(0.5)

        bg_1_image = pygame.image.load('images/bg_1.bmp')
        self.screen.blit(bg_1_image, (0,0))
        pygame.display.flip()
        flag = True
        while flag:
            button_pos = (371, 728, 524, 578)
            x_1, x_2, y_1, y_2 = button_pos
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = pygame.mouse.get_pos()
                    if (x > x_1) and (x < x_2) and (y > y_1) and (y < y_2):
                        login = Register()
                        print("sign success")
                        if login.user_name != '':
                            return(login.user_name)
                        
        
    def draw_bg_2(self):
        """菜单界面"""
        bg_2_image = pygame.image.load('images/bg_2.bmp')
        self.screen.blit(bg_2_image, (0,0))

    def draw_bg_3(self):
        """游戏规则界面"""
        bg_3_image = pygame.image.load('images/bg_3.bmp')
        self.screen.blit(bg_3_image, (0,0))

    def draw_map_all(self):
        """游戏背景整体地图界面"""
        for x in range(17,112):
            for y in range(70):
                pos_m = self.scale_pos((x,y))
                self.screen.blit(self.map_image, pos_m)

    def draw_map_piece(self,pos):
        """画一小块地图"""
        if pos != None:
            pos_m = self.scale_pos(pos)
            self.screen.blit(self.map_image, pos_m)


    def draw_board(self):
        board = pygame.Rect(0, 0, 170, 700)
        pygame.draw.rect(self.screen, self.board_color, board)


    def draw_text(self,text,pos):
        """渲染文字, 并画出来"""
        x,y = pos
        text_image = self.font.render(text, True, self.text_color, self.board_color)
        text_rect = text_image.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        self.screen.blit(text_image, text_rect)


    def draw_text_1(self,text,pos):
        """结束文字"""
        x,y = pos
        text_image = self.font.render(text, True, self.text_color)
        text_rect = text_image.get_rect()
        text_rect.centerx = x
        text_rect.top = y
        self.screen.blit(text_image, text_rect)


    def draw_end(self):
        self.end_image.set_alpha(100)
        self.screen.blit(self.end_image, (0,0))