import sys
import pygame

import operator


class Game_control:
    #user为本地用户

    def __init__(self, client, view):
        self.client = client#model类的实体化
        self.view = view#view类的实体化
        
        self.flag_2 = True#bg_2
        self.flag_start = False#游戏界面
        self.place_wall = False
        self.change_move = False
        self.live = True
        self.end_choose = False

        self.direction = ''
        self.wall_dir = ''
        
        self.sound = 0.5#初始音量为5
        self.last_b = []
        self.last_n = []
        self.player_b = []
        


    #按键\鼠标 响应控制
    
    def check_keyup_events(self, event):
        #放墙
        if self.flag_start:
            if event.key == pygame.K_w or event.key == pygame.K_s or event.key == pygame.K_a or  event.key == pygame.K_d:
                self.place_wall = False

    def check_keydown_events(self,event):
        """解析按键响应"""
        
        if event.key == pygame.K_ESCAPE:
            #跳转到bg_2
            #self.stop_bgm()
            pygame.mouse.set_visible(True)#显示光标
            self.flag_start = False
            self.flag_2 = True
            self.view.draw_bg_2()

        if self.live == False:
            if event.key == pygame.K_F1:
                sys.exit()

        if self.flag_start and self.live:
            #如果在游戏过程中
            #移动蛇
            if event.key == pygame.K_UP:
                self.direction = 'n'
            elif event.key == pygame.K_DOWN:
                self.direction = 's'
            elif event.key == pygame.K_LEFT:
                self.direction = 'w'
            elif event.key == pygame.K_RIGHT:
                self.direction = 'e'
            #放墙
            elif event.key == pygame.K_w:
                self.wall_dir = 'n'
                self.place_wall = True
            elif event.key == pygame.K_s:
                self.wall_dir = 's'
                self.place_wall = True
            elif event.key == pygame.K_a:
                self.wall_dir = 'w'
                self.place_wall = True
            elif event.key == pygame.K_d:
                self.wall_dir = 'e' 
                self.place_wall = True
                
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
                res = self.client.join_game()
                if res['res'] == 'suc':
                    self.client.wait_game_start()
                    print(self.client.players)
                    self.flag_2 = False
                    self.flag_start = True
                    pygame.mouse.set_visible(False)#隐藏光标
                    self.client.sync_world()
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
            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)
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

    def snake_head_pos(self,player,flag):
        """指令画蛇头，向view传输蛇头的点"""
        head_pos = player['snake']['head']
        self.view.draw_head((head_pos['x'], head_pos['y']))
        if flag == 2:
            self.player_b.append((head_pos['x'], head_pos['y']))
        #self.client.sync_world()


    def snake_body_pos(self, player,flag):
        """指令画蛇身，向view传输蛇身的点"""
        body_pos = []
        for body in player['snake']['body']:
            body_pos.append((body['x'], body['y']))
            if flag == 2:
                self.player_b.append((body['x'], body['y']))
        self.last_n.append(body_pos[-2])
        self.last_n.append(body_pos[-1])
        self.view.draw_snake_body(body_pos)
        #self.client.sync_world()
        

    
    def walls_pos(self):
        """指令画墙，向view传输所需要的墙的点"""
        walls = []
        for pos in self.client.game_map['walls']:
            walls.append((pos['x'], pos['y']))
        self.view.draw_walls(walls)
        #self.client.sync_world()


    def apple_pos(self):
        """指令画苹果，向view传输所需要的苹果的点"""
        apples = []
        for pos in self.client.game_map['apples']:
            apples.append((pos['x'], pos['y']))
        self.view.draw_apples(apples)
        #self.client.sync_world()

    #更改 初始化的墙删除
    #更改，对玩家成绩进行排序
    def rank_player(self):

        temp = self.client.players[:]
        temp.append(self.client.user)
        rank = sorted(temp, key=operator.itemgetter('score'))  
        return rank

    #改动
    def show_board(self):
        """显示信息板"""
      
        #用户姓名+分数
        x = 85
        y = 30
        self.view.draw_text("排名:", (x, y))
        rank = self.rank_player()
        for player in rank:
            name = player['name']
            score = str(player['score'])
            text = name+"：\n"+score
            y += 30
            self.view.draw_text(text, (x, y))
        

        #test = "apple" + str()
    
        y = 420
        text_w = "wall:\n" + str(self.client.game_map['walls_count'])
        self.view.draw_text(text_w, (x, y))

        y += 30
        text_l = "length:\n" + str(self.client.user['snake']['len'])
        self.view.draw_text(text_l, (x, y))

        y += 30
        score = "score: " + str(self.client.user['score'])
        self.view.draw_text(score, (x, y))

        y += 30
        process = "process:\n" + str(len(self.client.game_map['walls'])/10) +"%"
        self.view.draw_text(process, (x, y))

        if self.live == False:
            text = " 游戏结束，你可以继续观看游戏，若要退出游戏请按F1 " 
            x,y = 560, 0
            self.view.draw_text_1(text, (x, y))

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
        self.client.birth_snake()
        clock = pygame.time.Clock()
        temp = 0
        self.view.draw_map_all()
        self.view.draw_board()

        #判断初始蛇头方向
        h_x = self.client.user['snake']['head']['x']
        h_y = self.client.user['snake']['head']['y']
        body_init = self.client.user['snake']['body'][0]
        b_x = body_init['x']
        b_y = body_init['y']
        if h_x == b_x and h_y < b_y:
            self.direction = 'n'
        elif h_x == b_x and h_y > b_y:
            self.direction = 's'
        elif h_x < b_x and h_y == b_y:
            self.direction = 'w'
        elif h_x > b_x and h_y == b_y:
            self.direction = 'e'
   
        while self.flag_start:  
            clock.tick(60)
            temp += 1
            flag = temp % 6
            flag_sync = temp % 3

            
            self.check_events()
            if flag_sync == 0:
                self.client.sync_world()

            if flag == 0 and self.place_wall:
                self.client.place_wall(self.wall_dir)
            if self.client.user['snake']['len'] >= 0 and flag == 0:
                res = self.client.move_snake(self.direction)

            self.apple_pos()

            #蛇死亡判断
            lens = self.client.user['snake']['len']
            if lens >= 0:
                self.live = True
            else:
                self.live = False

            if flag == 0 and ( res['res'] == 'suc' or res['res'] == 'fdie' ):
                    self.view.draw_map_piece((res['data']['pos']['x'],res['data']['pos']['y']))
            if flag == 0 and self.live:
                self.snake_body_pos(self.client.user,1)
                self.snake_head_pos(self.client.user,1)

            for pos in self.player_b:
                self.view.draw_map_piece(pos)
            self.player_b.clear()

            for player in self.client.players:
                if player['snake']['len'] > 2:
                    self.snake_body_pos(player,2)
                    self.snake_head_pos(player,2)

            self.walls_pos() 
            self.show_board()

            #if self.live == False:
                #self.view.draw_end()

            pygame.display.update()
            pygame.display.flip()
                    


        