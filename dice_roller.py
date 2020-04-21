import tkinter as tk
from functools import partial
import os

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        
        self.diceBuffer = {} 
        self.modifier = ""
        self.buttonPresets = []
        self.buttonNamesVariables = []
        
        self.load_presets()
        self.create_widgets()

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
            button.grid(column=i%6, row=int(self.gridRows+ 2 + i/6), ipadx=10, padx=5, pady=5)
        
        
        #rolling controls
        button = tk.Button(self)
        button["text"] = "Roll!"
        button.grid(column=0, row=self.gridRows+4, ipadx=10, padx=5, pady=5)
        button["command"] = command=partial(self.copyBufferToClip)
        button = tk.Button(self)
        button["text"] = "Clear!"
        button.grid(column=1, row=self.gridRows+4, ipadx=10, padx=5, pady=5)
        button["command"] = command=partial(self.clearDiceBuffer)
        
        label = tk.Label(self)
        label["text"]
        
        #save presets
        button = tk.Button(self)
        button["text"] = "Save Presets"
        button.grid(column=0, row=self.gridRows+5, ipadx=10, padx=5, pady=5)
        button["command"] = command=self.save_presets


    def copyToClip(self, pos):
        self.master.clipboard_clear()
        self.master.clipboard_append(self.buttonPresets[pos]["value"])
    
    def copyBufferToClip(self):
        self.master.clipboard_clear()
        roll = "/r "
        first= True
        for die, die_occurence in self.diceBuffer.items():
            if first:
                roll += str(die_occurence) + die
                first=False
            else:
                roll += "+" + str(die_occurence) + die
        roll+="+" + self.modifier
        self.master.clipboard_append(roll)

    def clearDiceBuffer(self):
        self.diceBuffer = {}
        
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
        currentValue= self.diceBuffer.get(die, 0)
        self.diceBuffer[die] = currentValue + 1
     
    def append_modifer(self, modifier):
        self.modifier+=str(modifier)
        
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


def yulia_popup(windowCrap):
    print("Love You!")

root = tk.Tk()
root.title("NumbNut's stupid dice roller")
app = Application(master=root)
root.geometry("570x320+600+600")
root.bind('t', yulia_popup)
root.wm_attributes("-topmost", 1)
app.mainloop()