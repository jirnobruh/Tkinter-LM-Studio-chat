import os
import copy
import noGui_app
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import threading
import queue


class Interface:
    def __init__(self):
        self.ModelSelectionScreen = Tk()
        self.AppName = "LM studio model selection"

        # Устанавливаем нормальный размер для окна выбора модели
        self.ModelSelectionScreen.title(self.AppName)
        self.ModelSelectionScreen.geometry("500x400")  # Фиксированный начальный размер
        self.ModelSelectionScreen.minsize(400, 300)  # Минимальный размер

        # Центрируем окно на экране
        screen_width = self.ModelSelectionScreen.winfo_screenwidth()
        screen_height = self.ModelSelectionScreen.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 400) // 2
        self.ModelSelectionScreen.geometry(f"500x400+{x}+{y}")

        self.ModelsFrame = ttk.Frame(self.ModelSelectionScreen, borderwidth=1, relief=SOLID, padding=10)
        self.SelectLabel = ttk.Label(self.ModelsFrame, text="Выберите модель ИИ агента:", font=('Arial', 12, 'bold'))
        self.ErrorLabel = ttk.Label(self.ModelSelectionScreen, foreground='red', wraplength=450)
        self.ModelList = Listbox(self.ModelsFrame, selectmode=SINGLE, height=10, width=50)
        self.BtnFrame = ttk.Frame(self.ModelsFrame)
        self.SelectModelButtton = ttk.Button(self.BtnFrame, text="Выбрать",
                                             command=lambda: self.SelectModel(self.ModelList.get(ACTIVE)))
        self.ReloadModelsButtton = ttk.Button(self.BtnFrame, text="Перезагрузить", command=self.GetAvailableModels)

        # Настройка весов для центрирования
        self.ModelSelectionScreen.columnconfigure(0, weight=1)
        self.ModelSelectionScreen.rowconfigure(0, weight=1)

        self.ModelsFrame.grid(row=0, column=0, sticky=(N, S, E, W), padx=20, pady=20)
        self.ModelsFrame.columnconfigure(0, weight=1)
        self.ModelsFrame.rowconfigure(1, weight=1)

        self.SelectLabel.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        self.ModelList.grid(row=1, column=0, sticky=(N, S, E, W), padx=(0, 10))
        self.BtnFrame.grid(row=1, column=1, sticky=N)
        self.SelectModelButtton.grid(row=0, column=0, pady=(0, 5), sticky=(E, W))
        self.ReloadModelsButtton.grid(row=1, column=0, sticky=(E, W))
        self.ErrorLabel.grid(row=2, column=0, pady=10)

        # Добавляем скроллбар для списка моделей
        scrollbar = ttk.Scrollbar(self.ModelsFrame, orient=VERTICAL, command=self.ModelList.yview)
        self.ModelList.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=0, sticky=(N, S, E), padx=(0, 0))

        self.GetAvailableModels()

    def GetAvailableModels(self):
        try:
            self.ErrorLabel.config(text="")
            _raw_models = noGui_app.get_available_models()
            _models = []

            for i in range(len(_raw_models)):
                _models.append(_raw_models[i]['id'])
            _models = Variable(value=_models)

            if _models:
                self.ModelList.config(listvariable=_models)
                return (_raw_models)
            else:
                self.ErrorLabel.config(
                    text="При получении моделей произошла ошибка:\nСписок моделей оказался пуст\nПроверьте подключение к серверу")
                return []
        except:
            self.ErrorLabel.config(
                text="При получении моделей произошла ошибка:\nНевозможно подключиться к серверу\nПроверьте подключение к сети")
            return []

    def SelectModel(self, model):
        if not model:  # Проверяем, что модель выбрана
            return

        noGui_app.set_model(model)
        try:
            if self.ModelSelectionScreen.winfo_exists():
                self.CreateChatWindow()
                self.ModelSelectionScreen.destroy()
        except:
            self.InsertTextInChat("Модель была изменена на " + model)

    def CreateChatWindow(self):
        self.ChatWindow = Tk()
        self.AppName = "LM studio chat"
        self.MessageStatus = "[Ожидание ответа агента...]"
        self.ChatWindow.title(self.AppName)

        # Устанавливаем нормальный размер для окна чата
        screen_width = self.ChatWindow.winfo_screenwidth()
        screen_height = self.ChatWindow.winfo_screenheight()

        # Занимаем 80% экрана по умолчанию
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        # Минимальный размер окна
        self.ChatWindow.minsize(600, 500)

        # Центрируем окно
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.ChatWindow.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.AttachedFiles = []
        self.queue = queue.Queue()

        #### Виджеты
        # Создаем главное меню
        self.MainMenu = Menu(self.ChatWindow)

        # Создаем подменю для выбора модели
        try:
            _models = self.GetAvailableModels()
            self.ModelsMenu = Menu(self.MainMenu, tearoff=0)
            # Добавляем модели в подменю
            for model in _models:
                self.ModelsMenu.add_command(label=model['id'],
                                            command=lambda model_id=model['id']: self.SelectModel(model_id))
        except:
            pass

        # Добавляем подменю в главное меню
        self.MainMenu.add_cascade(label="Выбор модели", menu=self.ModelsMenu)

        # Устанавливаем главное меню для окна
        self.ChatWindow.config(menu=self.MainMenu)

        # Настройка сетки для растягивания
        self.ChatWindow.columnconfigure(0, weight=1)
        self.ChatWindow.rowconfigure(0, weight=1)  # Чат занимает все доступное пространство
        self.ChatWindow.rowconfigure(1, weight=0)  # StatusFrame не растягивается
        self.ChatWindow.rowconfigure(2, weight=0)  # InputFrame не растягивается

        self.ChatFrame = ttk.Frame(self.ChatWindow)
        self.ChatBox = Text(self.ChatFrame, state="disabled", font=('Arial', 11))
        self.ScrollbarY = ttk.Scrollbar(self.ChatFrame, orient="vertical", command=self.ChatBox.yview)
        self.ChatBox.configure(yscrollcommand=self.ScrollbarY.set)

        self.StatusFrame = ttk.Frame(self.ChatWindow)

        self.InputFrame = ttk.Frame(self.ChatWindow)
        self.InputLine = ttk.Entry(self.InputFrame, font=('Arial', 11))
        self.AttachButton = ttk.Button(self.InputFrame, text="📎", width=4, command=self.AttachFile)
        self.SendButton = ttk.Button(self.InputFrame, text="➤", width=4, command=self.SendMessage)

        # Настройка весов для растягивания внутри фреймов
        self.ChatFrame.columnconfigure(0, weight=1)
        self.ChatFrame.rowconfigure(0, weight=1)

        self.InputFrame.columnconfigure(1, weight=1)

        ## Расстановка элементов интерфейса
        self.ChatFrame.grid(row=0, column=0, sticky=(N, S, E, W), padx=5, pady=(5, 0))
        self.StatusFrame.grid(row=1, column=0, sticky=(E, W), padx=5, pady=5)
        self.InputFrame.grid(row=2, column=0, sticky=(E, W), padx=5, pady=(0, 5))

        # Скрываем StatusFrame изначально
        self.StatusFrame.grid_remove()

        self.ChatBox.grid(row=0, column=0, sticky=(N, S, E, W))
        self.ScrollbarY.grid(row=0, column=1, sticky=(N, S))

        self.AttachButton.grid(row=0, column=0, padx=(0, 5))
        self.InputLine.grid(row=0, column=1, sticky=(E, W), padx=5)
        self.SendButton.grid(row=0, column=2, padx=(5, 0))

        ## Привязка событий
        self.ChatWindow.bind("<Return>", self.SendMessage)
        self.ChatWindow.bind("<Configure>", self.on_window_resize)

        ## Периодическая проверка очереди
        self.CheckQueue()

        # Вызов первоначальной настройки размеров
        self.ChatWindow.after(100, self.update_widget_sizes)

    def DisplayFiles(self):
        ## Удаление старых элементов, если существуют
        if hasattr(self, '_file_frames'):
            for frame in self._file_frames:
                frame.destroy()

        self._file_frames = []
        self._file_labels = []
        self._file_buttons = []

        if self.AttachedFiles:
            self.StatusFrame.grid()
        else:
            self.StatusFrame.grid_remove()
            return

        if not hasattr(self, '_files_container'):
            self._files_container = ttk.Frame(self.StatusFrame)

            self._files_canvas = Canvas(self._files_container, height=35)
            self._files_scrollbar = ttk.Scrollbar(self._files_container, orient="horizontal",
                                                  command=self._files_canvas.xview)
            self._scrollable_frame = ttk.Frame(self._files_canvas)

            self._scrollable_frame.bind(
                "<Configure>",
                lambda e: self._files_canvas.configure(scrollregion=self._files_canvas.bbox("all"))
            )

            self._files_canvas.create_window((0, 0), window=self._scrollable_frame, anchor=NW)
            self._files_canvas.configure(xscrollcommand=self._files_scrollbar.set)

            ## Размещаем виджеты
            self._files_container.grid(row=0, column=0, sticky=(N, S, E, W))
            self._files_canvas.grid(row=0, column=0, sticky=(N, S, E, W))
            self._files_scrollbar.grid(row=1, column=0, sticky=(E, W))

            ## Настройка весов для растягивания
            self._files_container.grid_rowconfigure(0, weight=1)
            self._files_container.grid_columnconfigure(0, weight=1)
            self.StatusFrame.grid_rowconfigure(0, weight=1)
            self.StatusFrame.grid_columnconfigure(0, weight=1)

        for i in range(len(self.AttachedFiles)):
            frame = ttk.Frame(self._scrollable_frame, borderwidth=1, relief=SOLID)
            label = ttk.Label(frame, text=self.AttachedFiles[i].split('/')[-1], wraplength=150)
            button = ttk.Button(frame, text="X", width=3, command=lambda idx=i: self.RemoveFile(idx))

            frame.grid(row=0, column=i, sticky=NS, padx=2, pady=2)
            label.grid(row=0, column=0, padx=5, pady=2, sticky=W)
            button.grid(row=0, column=1, padx=5, pady=2)

            self._file_frames.append(frame)
            self._file_labels.append(label)
            self._file_buttons.append(button)

        ## Обновление региона прокрутки
        self._files_canvas.configure(scrollregion=self._files_canvas.bbox("all"))

        if len(self.AttachedFiles) > 3:
            self._files_scrollbar.grid()
        else:
            self._files_scrollbar.grid_remove()

    def RemoveFile(self, index):
        if 0 <= index < len(self.AttachedFiles):
            self.AttachedFiles.pop(index)
            self.DisplayFiles()

    def AttachFile(self):
        for i in filedialog.askopenfilenames():
            self.AttachedFiles.append(i)
        self.DisplayFiles()

    def InsertTextInChat(self, text):
        self.ChatBox.config(state="normal")
        self.ChatBox.insert(END, "\n" + text)
        self.ChatBox.config(state="disabled")
        self.ChatBox.see(END)

    def ReceiveAnswer(self, message, attached_files):
        try:
            response = "Assistant: " + noGui_app.ask_with_embedded_files(message, attached_files)
        except Exception as ex:
            print(ex)
            response = "Кажется что-то пошло не так"
        self.queue.put(response)

    def CheckQueue(self):
        try:
            while True:
                response = self.queue.get_nowait()
                self.InsertTextInChat(response)
                self.ChatWindow.title(self.AppName)
        except queue.Empty:
            pass

        ## Планируем следующую проверку
        self.ChatWindow.after(100, self.CheckQueue)

    def SendMessage(self, event=None):
        self.ChatWindow.title(self.MessageStatus)
        ## Вывод сообщения пользователя
        message = self.InputLine.get()
        if not message.strip() and not self.AttachedFiles:
            return  # Не отправляем пустое сообщение без файлов

        self.InsertTextInChat("User: " + message)
        for i in range(len(self.AttachedFiles)):
            self.InsertTextInChat("Прикреплённый файл - " + self.AttachedFiles[i].split('/')[-1])

        # Сохраняем копию списка файлов перед очисткой
        attached_files_copy = copy.deepcopy(self.AttachedFiles)

        self.InputLine.delete(0, END)
        self.AttachedFiles.clear()
        self.DisplayFiles()

        ## Вывод ответа агента
        ReceiveThread = threading.Thread(target=self.ReceiveAnswer, args=(message, attached_files_copy),
                                         name="ReceiveThread", daemon=True)
        ReceiveThread.start()

    def on_window_resize(self, event):
        if event.widget == self.ChatWindow:
            self.ChatWindow.after(100, self.update_widget_sizes)

    def update_widget_sizes(self):
        # Получаем текущие размеры окна
        current_width = self.ChatWindow.winfo_width()
        current_height = self.ChatWindow.winfo_height()

        if current_width > 50 and current_height > 50:  # Проверяем, что окно отобразилось
            # Рассчитываем высоту чата на основе высоты окна
            # Чат занимает большую часть окна, оставляя место для статус-бара и ввода
            chat_height = max(10, int((current_height - 150) / 20))

            # Ширина чата и поля ввода
            chat_width = max(40, int(current_width / 10))
            input_width = max(30, int(current_width / 15))

            self.ChatBox.config(width=chat_width, height=chat_height)
            self.InputLine.config(width=input_width)


if __name__ == "__main__":
    app = Interface()
    app.ModelSelectionScreen.mainloop()