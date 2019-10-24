
from tkinter import *
from tkinter import messagebox


class Register():
    user_name = ''

    def __init__(self):
        #创建一个窗口
        self.window = Tk()
        self.window.title("Resigter")
        self.window.wm_attributes('-topmost',1)
        self.window.geometry('450x300')

        #获取屏幕尺寸以计算布局参数，使窗口居屏幕中央
        screenwidth = self.window.winfo_screenwidth()  
        screenheight = self.window.winfo_screenheight() 
        alignstr = '%dx%d+%d+%d' % (450, 300, (screenwidth-450)/2, (screenheight-300)/2)
        self.window.geometry(alignstr)


        #画布放置图片
        canvas=Canvas(self.window,height=300,width=500)
        imagefile=PhotoImage(file='images/sign.png')
        image=canvas.create_image(0,0,anchor='nw',image=imagefile)
        canvas.pack(side='top')

        #创建并添加一个框架
        label_1 = Label(self.window, text="用户名：").place(x=100,y=150)
        self.name = StringVar()
        entryName = Entry(self.window, textvariable=self.name).place(x=160,y=150)
        bt_exit = Button(self.window, text="退出", 
                         command=self.process_exit).place(x=280,y=230)
        bt_sign = Button(self.window, text="注册",
                      command=self.process_sign).place(x=140,y=230)
       
        #循环事件检测
        self.window.mainloop()

    def process_sign(self):
        messagebox.showinfo('欢迎','注册成功')
        self.user_name = self.name.get()

    def process_exit(self):
        self.window.destroy()

