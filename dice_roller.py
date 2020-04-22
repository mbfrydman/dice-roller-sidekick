import tkinter as tk
from functools import partial
import os
import discord
from dotenv import load_dotenv
import multiprocessing as mp

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        
        self.diceBuffer = {} 
        self.modifier = ""
        self.buttonPresets = []
        self.buttonNamesVariables = []
        
        self.rollWithAdvantage = tk.IntVar()
        self.rollWithDisadvantage = tk.IntVar()
        self.currentBuffer = tk.StringVar()
        
        self.load_presets()
        self.create_widgets()
        self.messageQueue = None
       
    def create_widgets(self):
        
        #Generic Buttons
        self.gridColumns = 6
        self.gridRows = int ( len(self.buttonPresets) / self.gridColumns )

        for i, buts in enumerate(self.buttonPresets):

                button = tk.Button(self)
                button["textvariable"] = self.buttonNamesVariables[i]
                button.grid(column=i%6, row=int(i/6), ipadx=10, padx=5, pady=5)
                button["command"] = command=partial(self.copyToClip, i)
                button.bind('<Button-3>', partial(self.changeButton, i ) )
         
        #dice buttons
        dice_files=[
        {'file' : 'd4.png', 'value' : 'd4'},
        {'file' : 'd6.png', 'value' : 'd6'},
        {'file' : 'd8.png', 'value' : 'd8'},
        {'file' : 'd10.png', 'value' : 'd10'},
        {'file' : 'd20.png', 'value' : 'd20'},
        {'file' : 'd100.png', 'value' : 'd100'},
]
        for pos, die in enumerate(dice_files):
            photo = tk.PhotoImage(file = "rsrc\\" + die["file"])
            photoimage = photo.subsample(6, 6)
            button = tk.Button(self, image=photoimage)
            button.photo=photoimage
            button["command"] = command=partial(self.add_die, die["value"])
            button.grid(column=pos, row=self.gridRows+1)
        
        #modifiers
        for i in range(0,10):
            button = tk.Button(self)
            button["text"] = "+" + str(i)
            button["command"] = command=partial(self.append_modifer, i)
            button.grid(column=i%self.gridColumns, row=int(self.gridRows+ 2 + i/self.gridColumns), ipadx=10, padx=5, pady=5)
        
        
        tk.Checkbutton(self.master, text="Advantage d20?", variable=self.rollWithAdvantage).grid(row=5)
        tk.Checkbutton(self.master, text="Disadvantage d20?", variable=self.rollWithDisadvantage).grid()

        
        
        #rolling controls
        button = tk.Button(self)
        button["text"] = "Roll!"
        button.grid(column=0, row=self.gridRows+4, ipadx=10, padx=5, pady=5)
        button["command"] = command=partial(self.copyBufferToClip)
        button = tk.Button(self)
        button["text"] = "Clear!"
        button.grid(column=1, row=self.gridRows+4, ipadx=10, padx=5, pady=5)
        button["command"] = command=partial(self.clearDiceBuffer)
        
        tk.Label(self.master, textvariable=self.currentBuffer).grid()
        
        #save presets
        button = tk.Button(self)
        button["text"] = "Save Presets"
        button.grid(column=0, row=self.gridRows+5, ipadx=10, padx=5, pady=5)
        button["command"] = command=self.save_presets
        
        alwaysTopCheckbox = tk.IntVar()
        alwaysTopCheckbox.set(1)
        tk.Checkbutton(self.master, text="Always on top?", variable=alwaysTopCheckbox, command = partial(self.toggle_always_on_top, alwaysTopCheckbox)).grid(row=self.gridRows+5)

    def toggle_always_on_top(self, toggle):
        if toggle.get() == 1 : 
            self.master.wm_attributes("-topmost", 1)
        else:
            self.master.wm_attributes("-topmost", 0)
    
    def copyToClip(self, pos):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.buttonPresets[pos]["value"])
        self.messageQueue.put(self.buttonPresets[pos]["value"])
        
    def copyBufferToClip(self):
        self.master.clipboard_clear()
        
        roll = self.get_current_buffer()
            
        self.master.clipboard_append(roll)
        self.messageQueue.put(roll)
        self.clearDiceBuffer()
        self.rollWithDisadvantage.set(0)
        self.rollWithAdvantage.set(0)

    def clearDiceBuffer(self):
        self.diceBuffer = {}
        self.modifier = ""
        self.currentBuffer.set("")
        
    def changeButton(self ,pos , buttonCrap):
        popup = tk.Toplevel(self.master)
        popup.wm_title("Change Button")
        popup.tkraise(self.master) # This just tells the message to be on top of the root window.
        x_pos = self.master.winfo_x()
        y_pos = self.master.winfo_y()
        popup.geometry("+" + str(x_pos + 185) + "+" + str(y_pos + 129))
        
        tk.Label(popup, text="New Name for Button:").grid(column=0,row=0)
        textName=tk.Entry(popup)
        textName.grid(column=1,row=0)
        tk.Label(popup, text="New Value for Button:").grid(column=0,row=1)
        textValue=tk.Entry(popup)
        textValue.grid(column=1,row=1)
        tk.Button(popup, text="Save", command = partial(self.saveToButtons, pos, textName, textValue, popup)).grid(column=1,row=2)
        
    def saveToButtons(self, pos, buttonName, buttonValue, popup):
        self.buttonPresets[pos]["name"] = buttonName.get()
        self.buttonPresets[pos]["value"] = buttonValue.get()
        self.buttonNamesVariables[pos].set(buttonName.get())

        popup.destroy()
        
    def add_die(self, die):
        currentValue = self.diceBuffer.get(die, 0)
        self.diceBuffer[die] = currentValue + 1
        self.currentBuffer.set(self.get_current_buffer())
     
    def append_modifer(self, modifier):
        self.modifier+=str(modifier)
        self.currentBuffer.set(self.get_current_buffer())
        
    def load_presets(self):
        try:
            with open("presets\\defaults.txt", 'r') as fp:
                line = fp.readline()
                while line:
                    line = line.strip()
                    line = line.strip("\n")
                    name, value = line.split(";")
                    self.buttonPresets.append({"name":name, "value":value})
                    sVar = tk.StringVar()
                    sVar.set(name)
                    self.buttonNamesVariables.append(sVar)
                    line = fp.readline()
        except IOError as error:
            for i in range(16):
                self.buttonPresets.append({str(i):""})
                sVar = tk.StringVar()
                sVar.set(str(i))
                self.buttonNamesVariables.append(sVar)
                
    def save_presets(self):
        try:
            os.remove("presets\\defaults.txt")
        except:
            pass
            
  
        with open("presets\\defaults.txt", 'w') as fp:
            for button in self.buttonPresets:
                fp.write(button["name"]+";"+button["value"]+"\n")
                
                
    def get_current_buffer(self):
        roll = "/r "
        first= True
        for die, die_occurence in self.diceBuffer.items():
            if die == "d20":
                if self.rollWithAdvantage.get():
                    die = "d20k1"
                    die_occurence = 2
                elif self.rollWithDisadvantage.get():                
                    die = "d20kl1"
                    die_occurence = 2
            if first:
                roll += str(die_occurence) + die
                first=False
            else:
                roll += "+" + str(die_occurence) + die
                
        if self.modifier != "":
            roll+="+" + self.modifier
            
        return roll
     
     
def discord_process(messageQueue):
    load_dotenv()
    TOKEN = os.getenv('USER_TOKEN')
    discord_client = discord.Client()
    
    @discord_client.event
    async def on_ready():
        dice_channel = discord_client.get_channel(694244882125946990)
        while True:
            message = messageQueue.get()
            
            if message == "DIE":
                await discord_client.logout()
                break
            else:
                await dice_channel.send(message)
        
    #discord_client.run(TOKEN)
    discord_client.run(USERTOKEN, bot=False)
    
def on_app_close():
    messageQueue.put("DIE")
    root.destroy()

if __name__ == '__main__':
    mp.freeze_support()
    root = tk.Tk()
    root.title("Frak's stupid dice roller")
    app = Application(master=root)
    root.geometry("+300+300")
    root.wm_attributes("-topmost", 1)
    root.protocol("WM_DELETE_WINDOW", on_app_close)
    
    ctx = mp.get_context('spawn')
    messageQueue = ctx.Queue()
    discordProcess = ctx.Process(target=discord_process, args=(messageQueue,))
    discordProcess.start()
    app.messageQueue = messageQueue
    
    app.mainloop()