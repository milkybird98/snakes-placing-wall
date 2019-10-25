import sys
import pygame


class Game_control:
    #user为本地用户

    def __init__(self, client, view):
        self.client = client#model类的实体化
        self.view = view#view类的实体化
        self.flag_2 = True#bg_2
        self.flag_start = False#游戏界面
        self.direction = ''
        self.sound = 0.5#初始音量为5


    #按键\鼠标 响应控制

    def check_keydown_events(self,event):
        """解析按键响应"""
        
        if event.key == pygame.K_ESCAPE:
            #跳转到bg_2
            #self.stop_bgm()
            pygame.mouse.set_visible(True)#显示光标
            self.flag_start = False
            self.flag_2 = True
            self.view.draw_bg_2()

        if self.flag_start:
            #如果在游戏过程中
            #移动蛇
            if event.key == pygame.K_UP:
                self.direction = 'n'
                self.client.move_snake('n')
            elif event.key == pygame.K_DOWN:
                self.direction = 's'
                self.client.move_snake('s')
            elif event.key == pygame.K_LEFT:
                self.direction = 'w'
                self.client.move_snake('w')
            elif event.key == pygame.K_RIGHT:
                self.direction = 'e'
                self.client.move_snake('e')       
            #放墙
            elif event.key == pygame.K_w:
                self.client.place_wall('n')
            elif event.key == pygame.K_s:
                self.client.place_wall('s')
            elif event.key == pygame.K_a:
                self.client.place_wall('w')
            elif event.key == pygame.K_d:
                self.client.place_wall('e')     
        #调整音乐声音
        if event.key == pygame.K_e:
                self.adjust_sound("up")
        elif event.key == pygame.K_c:
                self.adjust_sound("down")


    def check_click_events(self, click_pos):
        """根据点击的点位置和flag状态判断事件"""
     
        if self.flag_2:
            button_1_pos = (100, 303, 184, 306)#游戏规则
            button_2_pos = (412, 678, 232, 393)#开始游戏           
            button_3_pos = (776, 978, 179, 301)#退出游戏
            if self.check_click_button(click_pos, button_1_pos):
                self.flag_2 = False
                self.view.draw_bg_3()
            elif self.check_click_button(click_pos, button_2_pos):
                self.flag_2 = False
                self.flag_start = True
                pygame.mouse.set_visible(False)#隐藏光标
                self.game_start()#进入游戏界面
            elif self.check_click_button(click_pos, button_3_pos):
                self.flag_2 = False
                sys.exit()

          
    def check_events(self):
        """响应按键和鼠标事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.check_click_events((mouse_x, mouse_y))


    def check_click_button(self, click_pos, button_pos):
        """检测是否点到按钮里"""
        x, y = click_pos
        x_1, x_2, y_1, y_2 = button_pos
        if (x > x_1) and (x < x_2) and (y > y_1) and (y < y_2):
            return True
        else:
            return False


    #绘画控制

    def snake_head_pos(self,player):
        """指令画蛇头，向view传输蛇头的点"""
        head_pos = player['snake']['head']
        self.view.draw_head((head_pos['x'], head_pos['y']))


    def snake_body_pos(self, player):
        """指令画蛇身，向view传输蛇身的点"""
        body_pos = []
        for body in player['snake']['body']:
            body_pos.append((body['x'], body['y']))
        self.view.draw_snake_body(body_pos)

    
    def walls_pos(self):
        """指令画墙，向view传输所需要的墙的点"""
        walls = []
        for pos in self.client.game_map['walls']:
            walls.append((pos['x'], pos['y']))
        self.view.draw_walls(walls)


    def apple_pos(self):
        """指令画苹果，向view传输所需要的苹果的点"""
        apples = []
        for pos in self.client.game_map['apples']:
            apples.append((pos['x'], pos['y']))
        self.view.draw_apples(apples)


    def show_board(self):
        """显示右侧信息板"""
        #分数
        text_1 = "Score"
        score_str = str(self.client.user['score'])
        pos_text_1 = 150
        pos_score = 200
        self.view.draw_text(text_1, pos_text_1)
        self.view.draw_text(score_str, pos_score)
        #用户姓名
        text_2 = "Player"
        name = self.client.user['name']
        pos_text_2 = 350
        pos_name = 400
        self.view.draw_text(text_2, pos_text_2)
        self.view.draw_text(name, pos_name)


    #bgm

    def adjust_sound(self, key):
        """调整bgm音量"""
        if key == "up" and self.sound < 1.0:
            self.sound += 0.1
        if key == "down" and self.sound > 0.0:
            self.sound -= 0.1
        pygame.mixer.music.set_volume(self.sound)


    #游戏开始控制

    def game_start(self):
        """开始游戏界面"""
        self.client.join_game()
        self.client.wait_game_start()
        res = self.client.birth_snake()
        clock = pygame.time.Clock()

        self.client.sync_world()

        #判断初始蛇头方向

        if res['data']['dire'] == 1:
            self.direction = 'n'
        elif res['data']['dire'] == 3:
            self.direction = 's'
        elif res['data']['dire'] == 2:
            self.direction = 'e'
        elif res['data']['dire'] == 4:
            self.direction = 'w'
   
        while self.flag_start:       
            clock.tick(10)
            self.view.draw_map_bg()
            #self.apple_pos()
            self.snake_body_pos(self.client.user)
            self.snake_head_pos(self.client.user)
            for player in self.client.players:
                self.snake_body_pos(player)
                self.snake_head_pos(player)
            self.walls_pos() 
            self.show_board()

            pygame.display.update()
            self.check_events()
            self.client.move_snake(self.direction)
            self.client.sync_world()


        