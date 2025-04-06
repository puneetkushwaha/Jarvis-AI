from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QHBoxLayout, QPushButton, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat, QTextCursor
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint
import sys
import os
from dotenv import dotenv_values

try:
    env_vars = dotenv_values(".env")
    Assistantname = env_vars.get("Assistantname", "Jarvis")
except Exception:
    Assistantname = "Jarvis"

current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphisDirPath = os.path.join(current_dir, "Frontend", "Graphics")

os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphisDirPath, exist_ok=True)

def initialize_files():
    files = {
        os.path.join(TempDirPath, "Mic.data"): "False",
        os.path.join(TempDirPath, "Status.data"): "Ready",
        os.path.join(TempDirPath, "Responses.data"): ""
    }
    for file_path, default_content in files.items():
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding='utf-8') as file:
                file.write(default_content)

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modifier_answer = '\n'.join(non_empty_lines)
    return modifier_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    
    if not query_words:
        return ""
        
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    try:
        with open(os.path.join(TempDirPath, "Mic.data"), "w", encoding='utf-8') as file:
            file.write(Command)
    except Exception as e:
        print(f"Error writing microphone status: {e}")

def GetMicrophoneStatus():
    try:
        with open(os.path.join(TempDirPath, "Mic.data"), "r", encoding='utf-8') as file:
            Status = file.read()
        return Status
    except Exception as e:
        print(f"Error reading microphone status: {e}")
        return "False"

def SetAssistantStatus(Status):
    try:
        with open(os.path.join(TempDirPath, "Status.data"), "w", encoding='utf-8') as file:
            file.write(Status)
    except Exception as e:
        print(f"Error writing assistant status: {e}")

def GetAssistantStatus():
    try:
        with open(os.path.join(TempDirPath, "Status.data"), "r", encoding='utf-8') as file:
            Status = file.read()
        return Status
    except Exception as e:
        print(f"Error reading assistant status: {e}")
        return "Ready"

def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphisDirPath, Filename)

def TempDirectoryPath(Filename):
    return os.path.join(TempDirPath, Filename)

def ShowTextToScreen(Text):
    try:
        with open(os.path.join(TempDirPath, "Responses.data"), "w", encoding='utf-8') as file:
            file.write(Text)
    except Exception as e:
        print(f"Error writing response: {e}")

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 40, 40, 100)
        layout.setSpacing(10)
        
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.chat_text_edit.setFrameStyle(QTextEdit.NoFrame)
        self.chat_text_edit.setStyleSheet("background-color: black; color: white;")
        
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        
        layout.addWidget(self.chat_text_edit)
        
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        
        gif_path = GraphicsDirectoryPath("Jarvis.gif")
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
            max_gif_size = 350
            movie.setScaledSize(QSize(max_gif_size, max_gif_size))
            self.gif_label.setMovie(movie)
            movie.start()
        else:
            self.gif_label.setStyleSheet("background-color: blue; border-radius: 50%;")
            self.gif_label.setFixedSize(350, 350)
            
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        bottom_layout.addWidget(self.gif_label, alignment=Qt.AlignRight)
        
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 24px; margin-right: 345px; border: none;")
        self.label.setAlignment(Qt.AlignRight)
        bottom_layout.addWidget(self.label, alignment=Qt.AlignRight)
        
        layout.addWidget(bottom_container)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.LoadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(250)
        
        self.setStyleSheet("""
        QScrollBar:vertical {
            border: none;
            background: #222;
            width: 10px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: white;
            min-height: 20px;
            border-radius: 5px;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            background: none;
            height: 0px;
        }
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        """)

    def LoadMessages(self):
        global old_chat_message
        
        try:
            with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as file:
                messages = file.read()
            
            if messages and messages != old_chat_message:
                self.addMessage(message=messages, color='White')
                old_chat_message = messages
                self.chat_text_edit.verticalScrollBar().setValue(
                    self.chat_text_edit.verticalScrollBar().maximum()
                )
        except Exception as e:
            print(f"Error loading messages: {e}")

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding="utf-8") as file:
                status = file.read()

                if status:
                    self.label.setText(status)
    
                    self.label.repaint()
        except Exception as e:
            print(f"Error reading status: {e}")

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        char_format = QTextCharFormat()
        char_format.setForeground(QColor(color))
        
        block_format = QTextBlockFormat()
        block_format.setTopMargin(10)
        
        cursor.movePosition(QTextCursor.End)
        cursor.setCharFormat(char_format)
        cursor.setBlockFormat(block_format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        content_layout = QVBoxLayout(self)
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        gif_label = QLabel()
        gif_path = GraphicsDirectoryPath('Jarvis.gif')
        
        if os.path.exists(gif_path):
            movie = QMovie(gif_path)
    
            gif_size = screen_width // 4
            movie.setScaledSize(QSize(gif_size, gif_size))
            gif_label.setMovie(movie)
            movie.start()
        else:
            gif_label.setStyleSheet("background-color: blue; border-radius: 100px;")

            gif_label.setFixedSize(400, 400)
        
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        self.icon_label = QLabel()
        mic_path = GraphicsDirectoryPath('Mic_on.png')
        if os.path.exists(mic_path):
            self.load_icon(mic_path)
        else:
            self.icon_label.setText("🎤")
            self.icon_label.setStyleSheet("color: white; font-size: 40px; background-color: #333; border-radius: 30px; padding: 10px;")
            self.icon_label.setFixedSize(65, 65)
            
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.mousePressEvent = self.toggle_icon
        self.toggled = True
        
        self.label = QLabel("Ready")
    
        self.label.setStyleSheet("color: white; font-size: 24px;")
        self.label.setAlignment(Qt.AlignCenter)
        
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        center_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        center_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        
        content_layout.addWidget(center_widget, alignment=Qt.AlignCenter)
        
        self.setStyleSheet("background-color: black;")
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)

        self.timer.start(250)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), 'r', encoding='utf-8') as file:
                status = file.read()
                if status:
                    self.label.setText(status)
                    self.label.repaint()
        except Exception as e:
            print(f"Error reading status: {e}")

    def load_icon(self, path, width=60, height=60):
        try:
            pixmap = QPixmap(path)
            new_pixmap = pixmap.scaled(width, height)
            self.icon_label.setPixmap(new_pixmap)
            self.icon_label.setFixedSize(65, 65)
        except Exception as e:
            print(f"Error loading icon: {e}")
            self.icon_label.setText("🎤")
            self.icon_label.setStyleSheet("color: white; font-size: 40px;")

    def toggle_icon(self, event=None):
        mic_on_path = GraphicsDirectoryPath('Mic_on.png')
        mic_off_path = GraphicsDirectoryPath('Mic_off.png')
        
        if self.toggled:
            if os.path.exists(mic_on_path):
                self.load_icon(mic_on_path, 60, 60)
            else:
                self.icon_label.setText("🎤")
                self.icon_label.setStyleSheet("color: green; font-size: 40px; background-color: #333; border-radius: 30px; padding: 10px;")
            MicButtonInitialed()
        else:
            if os.path.exists(mic_off_path):
                self.load_icon(mic_off_path, 60, 60)
            else:
                self.icon_label.setText("🎤")
                self.icon_label.setStyleSheet("color: red; font-size: 40px; background-color: #333; border-radius: 30px; padding: 10px;")
            MicButtonClosed()
        self.toggled = not self.toggled

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        
        self.setStyleSheet("background-color: black;")

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.offset = None
        self.parent_window = parent
        self.stacked_widget = stacked_widget
        
        self.maximize_button = QPushButton()
        
        max_icon_path = GraphicsDirectoryPath("Maximize.png")
        min_icon_path = GraphicsDirectoryPath("Minimize.png")
        
        if os.path.exists(max_icon_path) and os.path.exists(min_icon_path):
            self.maximize_icon = QIcon(max_icon_path)
            self.restore_icon = QIcon(min_icon_path)
        else:
            self.maximize_button.setText("□")
            self.maximize_icon = None
            self.restore_icon = None
        
        self.initUI()

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        
        title_text = f"{Assistantname.capitalize() if Assistantname else 'Jarvis'} AI"
        title_label = QLabel(title_text)
        title_label.setStyleSheet("color: black; font-size: 18px; font-weight: bold;")
        
        home_button = QPushButton("Home")
        home_button.setIcon(QIcon(GraphicsDirectoryPath("Home.png")) if os.path.exists(GraphicsDirectoryPath("Home.png")) else QIcon())
        home_button.setStyleSheet("QPushButton { height: 40px; background-color: #e0e0e0; border-radius: 5px; padding: 5px 10px; } "
                                 "QPushButton:hover { background-color: #d0d0d0; }")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        message_button = QPushButton("Chat")
        message_button.setIcon(QIcon(GraphicsDirectoryPath("Chats.png")) if os.path.exists(GraphicsDirectoryPath("Chats.png")) else QIcon())
        message_button.setStyleSheet("QPushButton { height: 40px; background-color: #e0e0e0; border-radius: 5px; padding: 5px 10px; } "
                                    "QPushButton:hover { background-color: #d0d0d0; }")
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        minimize_button = QPushButton()
        if os.path.exists(GraphicsDirectoryPath("Minimize.png")):
            minimize_button.setIcon(QIcon(GraphicsDirectoryPath("Minimize.png")))
        else:
            minimize_button.setText("_")
        minimize_button.setStyleSheet("QPushButton { background-color: #e0e0e0; border-radius: 5px; min-width: 30px; } "
                                     "QPushButton:hover { background-color: #d0d0d0; }")
        minimize_button.clicked.connect(self.minimizeWindow)
        
        if self.maximize_icon:
            self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setStyleSheet("QPushButton { background-color: #e0e0e0; border-radius: 5px; min-width: 30px; } "
                                         "QPushButton:hover { background-color: #d0d0d0; }")
        self.maximize_button.setCheckable(True)
        self.maximize_button.clicked.connect(self.maximizeWindow)
        
        close_button = QPushButton()
        if os.path.exists(GraphicsDirectoryPath("Close.png")):
            close_button.setIcon(QIcon(GraphicsDirectoryPath("Close.png")))
        else:
            close_button.setText("×")
            close_button.setStyleSheet("QPushButton { background-color: #ff5555; color: white; font-weight: bold; "
                                      "border-radius: 5px; min-width: 30px; } "
                                      "QPushButton:hover { background-color: #ff0000; }")
        close_button.clicked.connect(self.closeWindow)
        
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addSpacing(10)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
        self.draggable = True

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent_window.showMinimized()
    
    def maximizeWindow(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            if self.maximize_icon:
                self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent_window.showMaximized()
            if self.restore_icon:
                self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent_window.close()

    def mousePressEvent(self, event):
        if self.draggable and event.button() == Qt.LeftButton:
            self.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.draggable and self.offset and event.buttons() == Qt.LeftButton:
            if self.parent_window.isMaximized():
                self.maximizeWindow()
                screen_width = QApplication.desktop().screenGeometry().width()
                window_width = self.parent_window.width()
                ratio = window_width / screen_width
                self.offset = QPoint(int(event.pos().x() * ratio), event.pos().y())
            new_pos = event.globalPos() - self.offset
            self.parent_window.move(new_pos)
    
    def mouseReleaseEvent(self, event):
        self.offset = None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
        
    def initUI(self):
        initialize_files()
        
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        
        self.setGeometry(
            int(screen_width * 0.1),
            int(screen_height * 0.1),
            int(screen_width * 0.8),
            int(screen_height * 0.8)
        )
        
        self.setStyleSheet("background-color: black;")
        
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()