# coding=UTF-8

from Tkinter import *
import ttk

import pywifi

import random
from threading import Timer

# Channel Data From https://zh.wikipedia.org/wiki/WLAN%E4%BF%A1%E9%81%93%E5%88%97%E8%A1%A8

freq_24 = {  # 14 Channel
    1:2412,
    2:2417,
    3:2422,
    4:2427,
    5:2432,
    6:2437,
    7:2442,
    8:2447,
    9:2452,
    10:2457,
    11:2462,
    12:2467,
    13:2472,
    14:2484
}

china_deny_24 = [14]

temp_dict = {v : k for k, v in freq_24.items()}
freq_24 = temp_dict

freq_5 = {  # 27 Channel
    34:5170,
    36:5180,
    38:5190,
    40:5200,
    42:5210,
    44:5220,
    46:5230,
    48:5240,
    52:5260,
    56:5280,
    60:5300,
    64:5320,
    100:5500,
    104:5520,
    108:5540,
    112:5560,
    116:5580,
    120:5600,
    124:5620,
    128:5640,
    132:5660,
    136:5680,
    140:5700,
    149:5745,
    153:5765,
    157:5785,
    161:5805,
    165:5825
}

china_deny_5 = [34,100,104,108,112,116,120,124,128,132,136,140]

temp_dict = {v : k for k, v in freq_5.items()}
freq_5 = temp_dict

# 2.4GHz mode = False , 5GHz mode = True
# freq_flag = False
# freq_cur =  freq_24 if not freq_flag else freq_5

# freq_list = freq_cur.values()
# freq_list.sort()

def random_RGB():
    while 1:
        RGB_list = []
        for i in range(3):
            RGB_list.append(random.randint(0,255))
        sum = 0
        for i in RGB_list:
            sum += i
        if sum > 180:    # 统计RGB值加起来是否大于180 因为背景为黑色 防止颜色太深看起来不清楚 
            RGB = '#'
            for i in RGB_list:
                shex = str(hex(i))[2:]
                # print shex
                if len(shex) == 1:
                    RGB += '0'
                RGB += shex
            # print RGB
            return RGB
    

root = Tk()
root.resizable(False, False)
root.configure(bg='black')

w = pywifi.PyWiFi()
il = w.interfaces()
# interface = il[0]
color_reg = {}

def start_print():
    global freq_cur
    global freq_list

    freq_cur =  freq_24 if not freq_flag else freq_5
    freq_list = freq_cur.values()
    freq_list.sort()

    root_width = len(freq_cur)*30+(len(freq_cur)-1)*10+20+2
    root.geometry(str(root_width)+"x452")

    if not freq_flag:
        root.title('WiFiAnalyzer - 2.4GHz')
    else:
        root.title('WiFiAnalyzer - 5GHz')

    print_bg()
    print_item()
    cv.pack()


def select_24():
    global freq_flag
    freq_flag = False

    global interface
    interface = il[Hs['values'].index(Hs.get())]

    Hf.destroy()
    start_print()

def select_5():
    global freq_flag
    freq_flag = True

    global interface
    interface = il[Hs['values'].index(Hs.get())]

    Hf.destroy()
    start_print()

def print_Home():
    root.geometry("572x452")
    root.title('WiFiAnalyzer')

    global Hf
    Hf = Frame(root,bg='black')
    Hf.pack(expand=True)
    Ht = Label(Hf,fg='white',bg='black',text='WiFiAnalyzer',font=('Helvetica','30'))
    Ht.pack()
    global Hs
    Hs = ttk.Combobox(Hf, width=30, font=("Times New Roman", 20), justify=CENTER)
    Hs.configure(state='readonly')
    Hs.configure(values = [i.name() for i in il])
    if len(Hs['values']) != 0:
        Hs.current(0)
    Hs.pack()
    Hb24 = Button(Hf, text='2.4GHz', command=select_24, bg='black',fg='white', font=('Helvetica','20'))
    Hb5 = Button(Hf, text='5GHz', command=select_5, bg='black',fg='white', font=('Helvetica','20'))
    Hb24.pack(side=LEFT,pady=10,padx=60)
    Hb5.pack(side=LEFT,pady=10,padx=60)


def print_bg():
    global cv
    cv_width = len(freq_cur)*30+(len(freq_cur)-1)*10+20
    cv = Canvas(root,bg='black',width=cv_width,height=450)

    china_deny = china_deny_24 if not freq_flag else china_deny_5

    cv.create_line(10,30,cv_width-10,30,fill='white')
    for freq_no in range(len(freq_list)):
        x = 10*(freq_no+1)+30*freq_no+15
        freq_channel = freq_list[freq_no]
        color = 'white'
        if freq_channel in china_deny:
            color = 'red'
        cv.create_text(x,15,fill=color,text=str(freq_channel),font=('Helvetica','14'))


def print_item():
    interface.scan()
    r = interface.scan_results()

    cv.delete("item")

    for ap in r:

        # | flag | <= 2484000 | pass |
        # | ---- | ---------- | ---- |
        # |   0  |      1     |   1  |
        # |   0  |      0     |   0  |
        # |   1  |      1     |   0  |
        # |   1  |      0     |   1  |

        # XOR NB 666!
        if freq_flag ^ (ap.freq <= 2484000):

            freq_channel = freq_cur[int(ap.freq)/1000]
            freq_no = freq_list.index(freq_channel)

            x = 10*(freq_no+1)+30*freq_no
            y = 450-ap.signal*(-4)

            global color_reg
            if color_reg.has_key(ap.bssid):
                color = color_reg[ap.bssid]
            else:
                color = random_RGB()
                color_reg[ap.bssid] = color
            
            cv.create_rectangle(x,31,x+30,y,outline=color,tags='item')
            cv.create_text(x+15,y+5,fill=color,text=ap.ssid,tags='item')

    global t
    t = Timer(2, print_item, ())
    t.start()


def freq_switch(event):
    t.cancel()
    cv.destroy()

    global freq_flag
    freq_flag = not freq_flag

    start_print()

root.bind_all('<Tab>', freq_switch)

def break_Home(event):
    t.cancel()
    cv.destroy()

    print_Home()

root.bind_all('<Escape>', break_Home)


def closeWindow():
    try:
        t.cancel()
    except NameError:
        pass
    root.destroy()

print_Home()
root.protocol('WM_DELETE_WINDOW', closeWindow)
root.mainloop()