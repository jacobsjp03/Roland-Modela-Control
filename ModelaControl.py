# -*- coding: utf-8 -*-
"""
Created on Wed Jan  1 2020
@author: John
"""

import serial
import tkinter as tk
import tkinter.filedialog
import threading
import time

############  Window Setup ################
#Setup the window and frames
window = tk.Tk()
window.title("MDX-15 Controller")
#window.minsize(567,369)
window.resizable(False, False)

padding = 10

leftframe = tk.Frame(window, padx=padding, pady=padding, borderwidth=1, relief=tk.RAISED)
leftframe.pack(side=tk.LEFT, expand=1, fill=tk.BOTH)

settingsframe = tk.Frame(leftframe, padx=padding, pady=padding, borderwidth=1, relief=tk.RAISED)
settingsframe.pack(side=tk.TOP, expand=1, fill=tk.BOTH)

buttonframe = tk.Frame(leftframe, padx=padding, pady=padding, borderwidth=1, relief=tk.RAISED)
buttonframe.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)

rightframe = tk.Frame(window, padx=padding, pady=padding, borderwidth=1, relief=tk.RAISED)
rightframe.pack(side=tk.RIGHT, expand=1, fill=tk.BOTH)

loadframe = tk.Frame(rightframe, padx=padding, pady=padding) #, borderwidth=1, relief=tk.RAISED)
loadframe.pack(side=tk.TOP, expand=1, fill=tk.BOTH)

coordframe = tk.Frame(rightframe, padx=padding, pady=padding) #, borderwidth=1, relief=tk.RAISED)
coordframe.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)


############  Serial Port Setup ################
#COM Port drop down variables
com_port = tk.StringVar()
com_choices = ['COM1','COM2','COM3','COM4','COM5','COM6','COM7','COM8','COM9']

#Read default COM port from defaults.txt
try:
    with open("./defaults.txt", "r") as f:
        data = f.readline()
        if data[:3] =="COM":
            com_port.set(data)
        else:
            com_port.set('COM3')
        f.close()
except:
    com_port.set('COM3')


#com_port.set('COM5')
ser = serial.Serial()

#COM Port Connection
def ConnectToCOM():
    global ser  
    if ser.isOpen() == False:
        #Serial Port Setup
        ser = serial.Serial(
            port=com_port.get(), #'COM5', 
            baudrate=9600,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=False,
            dsrdtr=True
            )
    
        if ser.isOpen()==True:
            ResetZZero()
            MoveHome()
            EnableButtons()
            buttonComConnect.configure(state=tk.DISABLED, text="Close Cover")
            
    else:
        ser.close()
  
    
#Close serial port before we exit. Otherwise, the port will be locked for others.
def exit_handler():
    print("closing")
    ser.close()
    window.destroy()



############  Global Variable Setup ################
#global XYZ and movement variables
g_X = 0.0
g_Y = 0.0
g_Z = 0.0
g_ZOffset = 0.0
scale = 40
move_by = 5
move_by_choices = ['0.01','0.10','1.00','5.00','10.00']
move_by_choice = tk.StringVar()
move_by_choice.set('5.00')

#MIN and MAX coordinates
MIN_X = 0
MAX_X = 152.4
MIN_Y = 0
MAX_Y = 101.6
MIN_Z = -60.5
MAX_Z = 0

#Text box variables
txtX = tk.StringVar()
txtY = tk.StringVar()
txtZ = tk.StringVar()
txtZ0 = tk.StringVar()
txtX.set(str(g_X))
txtY.set(str(g_Y))
txtZ.set(str(g_Z))
txtZ0.set(str(g_ZOffset))

#Spindle checkbox variable
spindle = tk.IntVar()

#Flag to stop the thread which sends the file
stop_thread = "RUN"



############  Main Button Functions ################
def MoveHome():
    global g_X
    global g_Y
    global g_Z
    g_X = 0.0
    g_Y = 0.0
    g_Z = 0.0
    txtX.set(str(g_X))
    txtY.set(str(g_Y))
    txtZ.set(str(g_Z))
    move_to_coords(g_X, g_Y, g_Z)
    
def MoveUp():
    global g_Z
    if g_Z + g_ZOffset + move_by <= MAX_Z:
        g_Z = round(g_Z + move_by,2)
        txtZ.set(str(g_Z))
    else:
        g_Z = round(MAX_Z - g_ZOffset,2)
        txtZ.set(str(g_Z))
    move_to_coords(g_X, g_Y, g_Z)
    
    
def MoveDn():
    global g_Z
    if g_Z + g_ZOffset - move_by >= MIN_Z:
        g_Z = round(g_Z - move_by,2)
        txtZ.set(str(g_Z))
    else:
        g_Z = round(MIN_Z - g_ZOffset,2)
        txtZ.set(str(g_Z))
    move_to_coords(g_X, g_Y, g_Z)
        

def MoveLt():
    global g_X
    if g_X - move_by >= MIN_X:
        g_X = round(g_X - move_by,2)
        txtX.set(str(g_X))
    else:
        g_X = MIN_X
        txtX.set(str(g_X))
    move_to_coords(g_X, g_Y, g_Z)
        
    
def MoveRt():
    global g_X
    if g_X + move_by <= MAX_X:
        g_X = round(g_X + move_by,2)
        txtX.set(str(g_X))
    else:
        g_X = MAX_X
        txtX.set(str(g_X))
    move_to_coords(g_X, g_Y, g_Z)
        

def MoveFwd():
    global g_Y
    if g_Y - move_by >= MIN_Y:
        g_Y = round(g_Y - move_by,2)
        txtY.set(str(g_Y))
    else:
        g_Y = MIN_Y
        txtY.set(str(g_Y))
    move_to_coords(g_X, g_Y, g_Z)
    
def MoveBk():
    global g_Y
    if g_Y + move_by <= MAX_Y:
        g_Y = round(g_Y + move_by,2)
        txtY.set(str(g_Y))
    else:
        g_Y = MAX_Y
        txtY.set(str(g_Y))
    move_to_coords(g_X, g_Y, g_Z)
    
def SetZZero():
    global g_ZOffset
    global g_Z
    g_ZOffset=float(zbox.get())+g_ZOffset
    txtZ0.set(str(g_ZOffset))
    g_Z = 0.0
    txtZ.set(str(g_Z))
    cmd = "^DF;!ZO" + format(g_ZOffset*scale, '.3f') +";"
    ser.write(cmd.encode())

def ResetZZero():
    global g_ZOffset
    global g_Z
    g_ZOffset = 0.0
    g_Z = 0.0
    txtZ0.set(str(g_ZOffset))
    txtZ.set(str(g_Z))
    cmd = "^IN;!MC0;^PA;!ZO0;;;^IN;!MC0;"
    ser.write(cmd.encode())
    
def GoToCoordsBtn():
    global g_X
    global g_Y
    global g_Z
    g_X = float(xbox.get())
    g_Y = float(ybox.get())
    g_Z = float(zbox.get())
    move_to_coords(g_X, g_Y, g_Z)
    
def LoadFile():
    global serial_thread
    global stop_thread
    filename = tk.filedialog.askopenfilename(initialdir="/", title="Select File", filetypes=(("PRN Files","*.prn"),("All Files","*.*")))
    #print(filename)
    buttonPauseFile.configure(state=tk.NORMAL)
    buttonCancelFile.configure(state=tk.NORMAL)
    DisableButtons()
    stop_thread = "RUN"
    serial_thread = threading.Thread(target=SendFileOverSerial, args=(filename,))
    serial_thread.start()
    

def SendFileOverSerial(filename):
    global stop_thread
    with open(filename, "r") as f:
        data = f.read().splitlines()
        for line in data:
            if stop_thread == "STOP":
                break
            elif stop_thread == "PAUSE":
                while stop_thread == "PAUSE":
                    time.sleep(0.01)
            else:
                ser.write(line.encode())
                #print(line.encode())

def PauseFile():
    global stop_thread
    if serial_thread.isAlive():
        #serial_thread.terminate()
        print("Thread is alive")
        if stop_thread == "RUN":
            stop_thread = "PAUSE"
            buttonPauseFile.configure(text = "Resume")
        elif stop_thread == "PAUSE":
            stop_thread = "RUN"
            buttonPauseFile.configure(text = "Pause")
    else:
        print("Thread is not alive")

def CancelFile():
    global stop_thread
    if serial_thread.isAlive():
        #serial_thread.terminate()
        print("Thread is alive")
        stop_thread = "STOP"
        EnableButtons()
    else:
        print("Thread is not alive")
        EnableButtons()

def DisableButtons():
    buttonHome.configure(state=tk.DISABLED)
    buttonUp.configure(state=tk.DISABLED)
    buttonLt.configure(state=tk.DISABLED)
    buttonRt.configure(state=tk.DISABLED)
    buttonDn.configure(state=tk.DISABLED)
    buttonBk.configure(state=tk.DISABLED)
    buttonFwd.configure(state=tk.DISABLED)
    buttonSetZ.configure(state=tk.DISABLED)
    buttonReset.configure(state=tk.DISABLED)
    buttonGo.configure(state=tk.DISABLED)
    buttonLoadFile.configure(state=tk.DISABLED)
    buttonComConnect.configure(state=tk.DISABLED)

def EnableButtons():
    buttonHome.configure(state=tk.NORMAL)
    buttonUp.configure(state=tk.NORMAL)
    buttonLt.configure(state=tk.NORMAL)
    buttonRt.configure(state=tk.NORMAL)
    buttonDn.configure(state=tk.NORMAL)
    buttonBk.configure(state=tk.NORMAL)
    buttonFwd.configure(state=tk.NORMAL)
    buttonSetZ.configure(state=tk.NORMAL)
    buttonReset.configure(state=tk.NORMAL)
    buttonGo.configure(state=tk.NORMAL)
    buttonLoadFile.configure(state=tk.NORMAL)
    buttonComConnect.configure(state=tk.NORMAL)

#def sliderCallback(value):
#    values = [0.01,0.1,1,5,10]
#    newvalue = min(values, key=lambda x:abs(x-float(value)))
#    movebySlider.set(newvalue)
    
#Function to send the serial commands
def move_to_coords(x,y,z):
    if spindle.get() == 1:
        cmd = "^DF;!MC1;!PZ0,0;V15.0;Z" + format(x*scale, '.3f') + "," + format(y*scale, '.3f') + "," + format(z*scale, '.3f') + ";!MC0;"
    else:
        cmd = "^DF;!MC0;!PZ0,0;V15.0;Z" + format(x*scale, '.3f') + "," + format(y*scale, '.3f') + "," + format(z*scale, '.3f') + ";!MC0;"
    ser.write(cmd.encode())
    
def move_by_change(index, value, op):
    global move_by
    move_by = float(move_by_choice.get())
    
    
############  Left Frame Buttons ################
buttonHome = tk.Button(buttonframe, text="Home", command=MoveHome, width=10, state=tk.DISABLED)
buttonHome.grid(row=1, column=2, sticky=tk.W)

buttonframe.grid_rowconfigure(2, minsize=20)

buttonBk = tk.Button(buttonframe, text="Move Back", command=MoveBk, width=10, state=tk.DISABLED)
buttonBk.grid(row=3, column=2, sticky=tk.W)

buttonLt = tk.Button(buttonframe, text="Move Left", command=MoveLt, width=10, state=tk.DISABLED)
buttonLt.grid(row=4, column=1, sticky=tk.W)

buttonRt = tk.Button(buttonframe, text="Move Right", command=MoveRt, width=10, state=tk.DISABLED)
buttonRt.grid(row=4, column=3, sticky=tk.W)

buttonFwd = tk.Button(buttonframe, text="Move Foward", command=MoveFwd, width=10, state=tk.DISABLED)
buttonFwd.grid(row=5, column=2, sticky=tk.W)

buttonframe.grid_rowconfigure(6, minsize=20)

buttonUp = tk.Button(buttonframe, text=" Move Up ", command=MoveUp, width=10, state=tk.DISABLED)
buttonUp.grid(row=7, column=2, sticky=tk.W)

buttonDn = tk.Button(buttonframe, text="Move Down", command=MoveDn, width=10, state=tk.DISABLED)
buttonDn.grid(row=8, column=2, sticky=tk.W)

buttonframe.grid_rowconfigure(9, minsize=20)

checkSpindle = tk.Checkbutton(buttonframe, text="Spindle On", variable=spindle)
checkSpindle.grid(row=10, column=2, sticky=tk.W)



############  Coordinates Frame Buttons ################
tk.Label(coordframe, text="Coords (mm):").grid(row=1)
tk.Label(coordframe, text="X:").grid(row=2)
xbox = tk.Entry(coordframe, width=10, textvariable=txtX)
xbox.grid(row=2, column=1)

tk.Label(coordframe, text="Y:").grid(row=3)
ybox = tk.Entry(coordframe, width=10, textvariable=txtY)
ybox.grid(row=3, column=1)

tk.Label(coordframe, text="Z:").grid(row=4)
zbox = tk.Entry(coordframe, width=10, textvariable=txtZ)
zbox.grid(row=4, column=1)

tk.Label(coordframe, text="Z Zero:").grid(row=5)
z0box = tk.Entry(coordframe, width=10, textvariable=txtZ0)
z0box.grid(row=5, column=1)

buttonSetZ = tk.Button(coordframe, text="Set Z Zero", command=SetZZero, width=10, state=tk.DISABLED)
buttonSetZ.grid(row=5, column=2, sticky=tk.W)

buttonReset = tk.Button(coordframe, text="Reset Z Zero", command=ResetZZero, width=10, state=tk.DISABLED)
buttonReset.grid(row=6, column=2, sticky=tk.W)

coordframe.grid_rowconfigure(7, minsize = 25)

buttonGo = tk.Button(coordframe, text="Move To Coords", command=GoToCoordsBtn, width=14, state=tk.DISABLED)
buttonGo.grid(row=8, column=1, sticky=tk.W)


############  Settings Frame Buttons ################
tk.Label(settingsframe, text="COM Port").grid(row=1)
comSelection = tk.OptionMenu(settingsframe, com_port, *com_choices)
comSelection.grid(row=1, column=2, sticky=tk.W)

buttonComConnect = tk.Button(settingsframe, text="Connect", command=ConnectToCOM, width=10)
buttonComConnect.grid(row=1, column=3, sticky=tk.W)

tk.Label(settingsframe, text="Move By (mm):").grid(row=2)
movebySelection = tk.OptionMenu(settingsframe, move_by_choice, *move_by_choices)
movebySelection.grid(row=2, column=2, sticky=tk.W)
move_by_choice.trace('w',move_by_change)

#movebySlider = tk.Scale(settingsframe, from_=0.01, to=10, command=sliderCallback, orient="horizontal", resolution=0.01, length = 150)
#movebySlider.grid(row=2, column=2, columnspan=2, sticky=tk.W)

############  Load File Frame Buttons ################
buttonLoadFile = tk.Button(loadframe, text="Send File ...", command=LoadFile, width = 10, state=tk.DISABLED)
buttonLoadFile.grid(row=1, column = 1, sticky=tk.W)

buttonPauseFile = tk.Button(loadframe, text="Pause", command=PauseFile, width=10, state=tk.DISABLED)
buttonPauseFile.grid(row=1, column = 3, sticky=tk.W)

buttonCancelFile = tk.Button(loadframe, text="Cancel/End", command=CancelFile, width=10, state=tk.DISABLED)
buttonCancelFile.grid(row=1, column = 4, sticky=tk.W)


############  Main Loop ################
window.protocol("WM_DELETE_WINDOW", exit_handler)
window.mainloop()