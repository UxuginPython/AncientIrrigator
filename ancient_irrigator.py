DRY_COLOR='#806000'
WET_COLOR='#804000'
WATER_COLOR='#0000ff'
AIR_COLOR='#000000'
YOUNG_COLOR='#00ff00'
GROWN_COLOR='#ffff00'
import enum
import json
import os
import random
from tkinter import *
from tkinter import messagebox
LandState=enum.IntEnum('LandState', ['NULL', 'DRY', 'WET', 'YOUNG', 'GROWN'])
def generate_gamedata():
    land=[[None for y in range(16)] for x in range(16)]
    water=[[None for y in range(16)] for x in range(16)]
    land_state=[[None for y in range(16)] for x in range(16)]
    for x in range(16):
        for y in range(16):
            if 6<=x<=9:
                land[x][y]=2
                water[x][y]=4
                land_state[x][y]=LandState.WET
            else:
                land[x][y]=6
                water[x][y]=0
                land_state[x][y]=LandState.DRY
    data={'land': land, 'water': water, 'land_state': land_state}
    #return json.dumps(data)
    return data
#weighted_average function copied from Snowbotics39131/FLL-Pre-Season-Code
def weighted_average(values, weights=None):
    if weights is None:
        return sum(values)/len(values)
    else:
        values=[i[0]*i[1] for i in zip(values, weights)]
        return sum(values)/sum(weights)
def get_color(x, y):
    if land_state[x][y]==LandState.YOUNG:
        return YOUNG_COLOR
    if land_state[x][y]==LandState.GROWN:
        return GROWN_COLOR
    def prepare_color(color):
        color=color.replace('#', '')
        red=color[0:1]
        green=color[2:3]
        blue=color[4:5]
        red=int(red, 16)
        green=int(green, 16)
        blue=int(blue, 16)
        return red, green, blue
    land_=land[x][y]
    water_=water[x][y]
    match land_state[x][y]:
        case LandState.DRY:
            land_r, land_g, land_b=prepare_color(DRY_COLOR)
        case LandState.WET:
            land_r, land_g, land_b=prepare_color(WET_COLOR)
    water_r, water_g, water_b=prepare_color(WATER_COLOR)
    air_r, air_g, air_b=prepare_color(AIR_COLOR)
    r=round(weighted_average((land_r, water_r, air_r), (land_, water_, 8-(land_+water_))))
    g=round(weighted_average((land_g, water_g, air_g), (land_, water_, 8-(land_+water_))))
    b=round(weighted_average((land_b, water_b, air_b), (land_, water_, 8-(land_+water_))))
    return f'#{hex(r)[2:]}{hex(g)[2:]}{hex(b)[2:]}'
data=generate_gamedata()
land=data['land']
water=data['water']
land_state=data['land_state']
window=Tk()
tool='place'
dirt_number=0
seed_number=1
def update_water():
    x_list=list(range(16))
    random.shuffle(x_list)
    for x in x_list:
        y_list=list(range(16))
        random.shuffle(y_list)
        for y in y_list:
            if water[x][y]<=0:
                continue
            here=water[x][y]+land[x][y]
            up=water[x][y-1]+land[x][y-1] if y>0 else 999
            down=water[x][y+1]+land[x][y+1] if y<15 else 999
            left=water[x-1][y]+land[x-1][y] if x>0 else 999
            right=water[x+1][y]+land[x+1][y] if x<15 else 999
            if up<here:
                water[x][y-1]+=1
                water[x][y]-=1
            elif down<here:
                water[x][y+1]+=1
                water[x][y]-=1
            elif left<here:
                water[x-1][y]+=1
                water[x][y]-=1
            elif right<here:
                water[x+1][y]+=1
                water[x][y]-=1
            #thingstodo=[
            #    'if up<here:\n    water[x][y-1]+=1\n    water[x][y]-=1\n    keepgoing=False',
            #    'if down<here:\n    water[x][y+1]+=1\n    water[x][y]-=1\n    keepgoing=False',
            #    'if left<here:\n    water[x-1][y]+=1\n    water[x][y]-=1\n    keepgoing=False',
            #    'if right<here:\n    water[x+1][y]+=1\n    water[x][y]-=1\n    keepgoing=False'
            #]
            #random.shuffle(thingstodo)
            #keepgoing=True
            #for i in thingstodo:
            #    if keepgoing:
            #        exec(i)
    for x in range(16):
        for y in range(16):
            if water[x][y]>0:
                land_state[x][y]=LandState.WET
#click_func partially copied from UxuginPython/BuildIT
def click_func(event):
    global dirt_number, seed_number
    tile=event.widget
    column=tile.grid_info()['column']
    row=tile.grid_info()['row']
    match tool:
        case 'place':
            def can_place():
                if land[column][row]+1>8-water[column][row]:
                    return False
                if dirt_number<=0:
                    return False
                return True
            if can_place():
                #land[column][row]=min(land[column][row]+1, 8-water[column][row])
                land[column][row]+=1
                dirt_number-=1
        case 'break':
            def can_break():
                if land[column][row]-1<0:
                    return False
                return True
            if can_break():
                #land[column][row]=max(land[column][row]-1, 0)
                land[column][row]-=1
                dirt_number+=1
        case 'sow':
            def can_sow():
                if water[column][row]>0:
                    return False
                if land[column][row]<1:
                    return False
                if land_state[column][row]!=LandState.WET:
                    return False
                return True
            if can_sow():
                land_state[column][row]=LandState.YOUNG
                seed_number-=1
        case 'reap':
            match land_state[column][row]:
                case LandState.YOUNG:
                    seed_number+=1
                    land_state[column][row]=LandState.WET
                case LandState.GROWN:
                    seed_number+=2
                    land_state[column][row]=LandState.DRY
tile_frame=Frame(window)
tiles=[[Label(tile_frame, text='      ') for y in range(16)] for x in range(16)]
for x, column in enumerate(tiles):
    for y, label in enumerate(column):
        label.bind('<Button-1>', click_func)
        label.grid(column=x, row=y)
tile_frame.grid(column=0, row=0)
tool_select=Frame(window)
seeds=Label(tool_select, text='#')
def sow_func():
    global tool
    tool='sow'
sow=Button(tool_select, text='Sow', command=sow_func)
def reap_func():
    global tool
    tool='reap'
reap=Button(tool_select, text='Reap', command=reap_func)
def place_func():
    global tool
    tool='place'
place=Button(tool_select, text='Place', command=place_func)
def break_func():
    global tool
    tool='break'
break_=Button(tool_select, text='Break', command=break_func)
dirt=Label(tool_select, text='#')
seeds.grid(column=0, row=0)
sow.grid(column=1, row=0)
reap.grid(column=2, row=0)
place.grid(column=3, row=0)
break_.grid(column=4, row=0)
dirt.grid(column=5, row=0)
tool_select.grid(column=0, row=1)
while True:
    #for i in range(5, 9):
    #    water[i][0]=6-land[0][i]
    #    water[i][15]=0
    for x in range(16):
        for y in range(16):
            if land_state[x][y]==LandState.YOUNG:
                if random.randrange(1000)==391:
                    land_state[x][y]=LandState.GROWN
    update_water()
    for x, column in enumerate(tiles):
        for y, label in enumerate(column):
            label.config(bg=get_color(x, y))
    dirt.config(text=dirt_number)
    seeds.config(text=seed_number)
    window.update()
    window.update_idletasks()
