import noGui_app
from tkinter import *
from tkinter import ttk

class Interface:
    def __init__(self):
        self.ChatWindow = Tk()
        self.ChatWindow.title("LM studio chat")
        self.ScreenWidth = self.ChatWindow.winfo_screenwidth()
        self.ScreenHeight = self.ChatWindow.winfo_screenheight()

        self.ChatFrame = ttk.Frame()
        self.ChatBox = Text(self.ChatFrame, width = int(self.ScreenWidth/20), state = "disabled")
        self.ScrollbarY = ttk.Scrollbar(self.ChatFrame, orient = "vertical", command = self.ChatBox.yview)

        self.InputFrame = ttk.Frame()
        self.InputLine = ttk.Entry(self.InputFrame, width = int(self.ScreenWidth/17))
        self.AttachButton = ttk.Button(self.InputFrame, text = "§", width = 4)
        self.SendButton = ttk.Button(self.InputFrame, text = ">", width = 4, command=self.SendMessage)
        self.AttachedFiles = ttk.Label(self.InputFrame)
        
        ## Расстановка элементов интерфейса
        self.ChatFrame.grid(row = 0, column = 0)
        self.InputFrame.grid(row = 1, column = 0)

        self.ChatBox.grid(row = 0, column = 0)
        self.ScrollbarY.grid(row = 0, column = 1, sticky = NS)

        self.AttachedFiles.grid(row = 0, column = 0, columnspan = 3)
        self.AttachButton.grid(row = 1, column = 0)
        self.InputLine.grid(row = 1, column = 1)
        self.SendButton.grid(row = 1, column = 2)

    def InsertTextInChat(self, text):
        self.ChatBox.state = "normal"
        self.ChatBox.insert(END, "\n"+text)
        self.ChatBox.state = "disabled"

    def SendMessage(self):
        message = self.InputLine.get()
        response = noGui_app.ask(message)
        self.InsertTextInChat(response)


app = Interface()
