import noGui_app
from tkinter import *
from tkinter import ttk

class Interface:
    def __init__(self):
        self.ChatWindow = Tk()
        self.ChatWindow.title("LM studio chat")
        self.ScreenWidth = self.ChatWindow.winfo_screenwidth()
        self.ScreenHeight = self.ChatWindow.winfo_screenheight()

        # Базовые размеры для расчета
        self.ChatWidthRatio = 0.8  
        self.ChatHeightRatio = 0.7 
        self.InputWidthRatio = 0.9

        # Расчет размеров виджетов
        ChatWidth = int(self.ScreenWidth * self.ChatWidthRatio / 10)
        ChatHeight = int(self.ScreenHeight * self.ChatHeightRatio / 20)
        InputWidth = int(self.ScreenWidth * self.InputWidthRatio / 10)

        self.ChatFrame = ttk.Frame(self.ChatWindow)
        self.ChatBox = Text(self.ChatFrame, width = ChatWidth, height = ChatHeight, state = "disabled")
        self.ScrollbarY = ttk.Scrollbar(self.ChatFrame, orient = "vertical", command = self.ChatBox.yview)

        self.InputFrame = ttk.Frame(self.ChatWindow)
        self.InputLine = ttk.Entry(self.InputFrame, width = InputWidth)
        self.AttachButton = ttk.Button(self.InputFrame, text = "§", width = 4)
        self.SendButton = ttk.Button(self.InputFrame, text = ">", width = 4, command=self.SendMessage)
        self.StatusLabel = ttk.Label(self.InputFrame)

        ## Настройка весов для растягивания
        self.ChatWindow.columnconfigure(0, weight=1)
        self.ChatWindow.rowconfigure(0, weight=1)  
        self.ChatWindow.rowconfigure(1, weight=0)  
        
        self.ChatFrame.columnconfigure(0, weight=1)
        self.ChatFrame.rowconfigure(0, weight=1)
        
        self.InputFrame.columnconfigure(1, weight=1)
        
        ## Расстановка элементов интерфейса
        self.ChatFrame.grid(row=0, column=0, sticky=NSEW, padx=5, pady=5)
        self.InputFrame.grid(row=1, column=0, sticky=EW, padx=5, pady=5)

        self.ChatBox.grid(row=0, column=0, sticky=NSEW)
        self.ScrollbarY.grid(row=0, column=1, sticky=NS)

        self.StatusLabel.grid(row=0, column=0, columnspan=3, sticky=W)
        self.AttachButton.grid(row=1, column=0, padx=(0, 5))
        self.InputLine.grid(row=1, column=1, sticky=EW, padx=5)
        self.SendButton.grid(row=1, column=2, padx=(5, 0))

        ## Привязка событий
        self.ChatWindow.bind("<Return>", self.SendMessage)
        self.ChatWindow.bind("<Configure>", self.on_window_resize)

        ## Переменные для отслеживания размера
        self.LastWidth = self.ChatWindow.winfo_width()
        self.LastHeight = self.ChatWindow.winfo_height()
        
        ## Запускаем первоначальное обновление после отображения окна
        self.ChatWindow.after(100, self.initial_resize)
        
    def InsertTextInChat(self, text):
        self.ChatBox.config(state = "normal")
        self.StatusLabel.config(text = "Сообщение отправляется...")
        self.ChatBox.insert(END, "\n"+text)
        self.StatusLabel.config(text = "")
        self.ChatBox.config(state = "disabled")
        self.ChatBox.see(END)

    def SendMessage(self, event=None):
        message = self.InputLine.get()
        self.InsertTextInChat("User: "+message)
        self.InputLine.delete(0, END)
        try:
            response = "Assistant: "+noGui_app.ask(message)
        except:
            response = "Кажется что-то пошло не так"
        self.InsertTextInChat(response)

    def initial_resize(self):
        self.update_widget_sizes()
        
    def on_window_resize(self, event):
        if event.widget == self.ChatWindow:
            CurrentWidth = event.width
            CurrentHeight = event.height
            
            ## Обновляем только при значительном изменении размера (более 10 пикселей)
            if (abs(self.LastWidth - CurrentWidth) > 10 or 
                abs(self.LastHeight - CurrentHeight) > 10):
                
                self.LastWidth = CurrentWidth
                self.LastHeight = CurrentHeight
                self.update_widget_sizes()
    
    def update_widget_sizes(self):
        ## Получаем текущий размер окна
        WindowWidth = self.ChatWindow.winfo_width()
        WindowHeight = self.ChatWindow.winfo_height()
        
        if WindowWidth > 1 and WindowHeight > 1:  # Проверяем, что окно уже отобразилось
            ## Пересчитываем размеры на основе текущего размера окна
            new_ChatWidth = max(20, int(WindowWidth / 18))
            new_ChatHeight = max(10, int(WindowHeight / 25))
            new_InputWidth = max(20, int(WindowWidth / 20))
            
            ## Обновляем размеры виджетов
            self.ChatBox.config(width=new_ChatWidth, height=new_ChatHeight)
            self.InputLine.config(width=new_InputWidth)


app = Interface()
