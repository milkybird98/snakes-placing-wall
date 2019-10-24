from snake_view import Game_view
import pygame
from snake_client import Game_model
from snake_control import Game_control


def run():
    #登录界面
    view = Game_view()
    pygame.display.flip()

    name = view.draw_bg_1()
    user = Game_model('http://127.0.0.1:5000', name)
    control = Game_control(user, view)

    #进菜单
    view.draw_bg_2()

    while True:

        control.check_events()
    
        pygame.display.flip()


if __name__ == "__main__":
    run()