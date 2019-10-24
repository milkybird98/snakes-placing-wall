import pygame 
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
        self.font = pygame.font.SysFont(None, 48)

        #无关紧要的颜色
        self.white = (255, 250, 250)
        self.green = (102, 205, 0)
        self.red = (255, 0, 0)
        self.blue = (100, 149, 237)


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
        pygame.draw.rect(self.screen, self.red, head_rect)


    def draw_snake_body(self, body):
        """画蛇身"""
        for pos in body:
            b_x, b_y = self.scale_pos(pos)
            pos_rect = pygame.Rect(b_x, b_y, self.scale, self.scale)
            pygame.draw.rect(self.screen, self.green, pos_rect)


    def draw_walls(self,walls):
        """墙体贴图"""
        for pos in walls:
            w_x, w_y = self.scale_pos(pos)
            wall_image = pygame.image.load('images/wall.bmp')
            self.screen.blit(wall_image, (w_x, w_y))

    def draw_apples(self, apples):
        """贴苹果"""
        for pos in apples:
            a_x, a_y = self.scale_pos(pos)
            apple_image = pygame.image.load('images/apple.bmp')
            self.screen.blit(apple_image, (a_x, a_y))

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

    def draw_map_bg(self):
        """游戏背景地图界面"""
        map_bg_image = pygame.image.load('images/map_bg.bmp')
        self.screen.blit(map_bg_image, (0,0))


    def draw_text(self,text,pos_y):
        """渲染文字, 并画出来"""
        text_image = self.font.render(text, True, self.text_color)
        text_rect = text_image.get_rect()
        text_rect.centerx = 172/2
        text_rect.top = pos_y
        self.screen.blit(text_image, text_rect)

