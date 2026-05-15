import sys
import sqlite3
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QApplication, QMainWindow, QInputDialog, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QPainter, QColor, QIcon
from PyQt6.QtCore import QPointF, Qt, pyqtSignal
import pygame as pg
import math as m

# иницилизация Qt дизайна
# была вынесена в другой файл для быстрого изменения или добавление чего-то нового в структуре дизайна
from ui_file_1 import MainWindow
from ui_file_2 import ChooseWindow
from ui_file_3 import PracticeWindow

# Константы
DRAW_COLOR = QColor(123, 200, 246)
WHITE = QColor(255, 255, 255)
FI = 2 * m.pi / 5

# иницилизация пайгейма для музыки
pg.init()


class Learn_The_Guitar(QMainWindow, MainWindow):
    def __init__(self):
        super(Learn_The_Guitar, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        # Настройка окна и иконочки)
        self.setFixedSize(500, 470)
        self.setWindowTitle('Learn the guitar')
        self.setWindowIcon(QIcon('icon.png'))

        # поле инструкции к приложению
        # загруска текста
        with open('help_text.txt', encoding='utf-8') as file:
            text = file.read()
        self.help_text.setPlainText(text)
        self.help_text.setReadOnly(True)
        self.help_text.hide()

        # кнопка возвращения в главное меню
        self.back_button.hide()

        # настройка всех кнопок
        self.exit_button.clicked.connect(self.close_app)
        self.help_button.clicked.connect(self.show_help_text)
        self.back_button.clicked.connect(self.back_to_lobby)
        self.start_button.clicked.connect(self.run)

    def paintEvent(self, event):
        self.design()

    # функия загрузки украшений окна
    def design(self):
        qp = QPainter()
        qp.begin(self)

        # добавим окно белого цвета - часто используемый дизайн, популярен и прост
        qp.setPen(WHITE)
        qp.drawRoundedRect(30, 140, 440, 270, 20, 20)

        # добавим пару голубых звездочек для красоты
        qp.setPen(DRAW_COLOR)
        self.draw_star(qp, 50, 45, 20)
        self.draw_star(qp, 450, 45, 20)

        qp.end()

    # функция для рисования звездочки
    def draw_star(self, qp, x, y, r):
        # самостоятельно придумывал точки из геометрии звезды
        pnts = [QPointF(x + r * m.cos(-m.pi / 2 - FI * i), y + r * m.sin(-m.pi / 2 - FI * i)) for i in range(0, 10, 2)]
        qp.drawPolygon(pnts)

    # показать инструкцию
    def show_help_text(self):
        self.help_text.show()
        self.back_button.show()

    # вернутся на главный экран
    def back_to_lobby(self):
        self.back_button.hide()
        self.help_text.hide()

    # функция закрытия приложение через приложение
    def close_app(self):
        # не разобрался с Dialog.CloseEvent =(
        res, ok_pressed = QInputDialog.getItem(
            self, "Закрыть приложение", "Вы действительно хотите уйти?",
            ("Да", "Нет"), 0, False)

        if ok_pressed and res == 'Да':
            app.quit()

    # основная функция приложения
    def run(self):
        self.ex = choose_screen()
        self.ex.show()
        self.close()  

class choose_screen(QMainWindow, ChooseWindow):
    def __init__(self):
        super(choose_screen, self).__init__()
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        # Настройка окна и иконочки)
        self.setFixedSize(800, 600)
        self.setWindowTitle('Выбор трека')
        self.setWindowIcon(QIcon('icon.png'))

        # подключаемся к базе данных для выбора трека, которого собираемся тренировать
        self.con = sqlite3.connect("tracks.sqlite")
        cur = self.con.cursor()
        result = cur.execute("SELECT * FROM Tracks").fetchall()

        # добавляем удобные для понимая заголовки и заполняем таблицу
        self.titles = ['Id', 'Исполнитель', 'Название трека', 'Продолжительность', 'Сложность']
        self.tableWidget.setRowCount(len(result))
        self.tableWidget.setColumnCount(len(result[0]))
        self.tableWidget.setHorizontalHeaderLabels(self.titles)
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

        # регулируем ширину столбцов
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # убираем возможность изменять таблицу
        self.tableWidget.setEnabled(False)

        # создадим список для фильтрации
        fl = ['Id', 'singer', 'track_title', 'duration', 'complexity']
        self.alph = {self.titles[i]: fl[i] for i in range(len(self.titles))}

        # функционал кнопок
        self.search_button.clicked.connect(self.filter)
        self.start_button.clicked.connect(self.run)

    def filter(self):
        cur = self.con.cursor()
        search_text = self.search_line.text().strip()
        column = self.alph.get(self.search_filter.currentText())

        if (not column):
            self.statusBar().showMessage("Error: Choose category for search")
            return 
        try:
            if (not search_text):
                result = cur.execute("SELECT * FROM Tracks").fetchall()
            else:
                query = f"SELECT * FROM Tracks WHERE {column} LIKE ?"
                search_pattern = f"%{search_text}%"
                result = cur.execute(query, (search_pattern,)).fetchall()
            
            self.tableWidget.setRowCount(len(result))

            if (not result):
                self.statusBar().showMessage("Nothing found")
                return

            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

            # Настройка ширины столбцов
            header = self.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

            self.statusBar().showMessage(f"Нашел {len(result)} треков")

        except sqlite3.Error as e:            
            self.statusBar().showMessage(F"Ошибка: {e}")

    def run(self):
        try:
            song_id = int(self.song_id.text())
        except ValueError:
            self.statusBar().showMessage("Ошибка: ID должен быть числом", 3000)
            return 
        
        try:
            cur = self.con.cursor()
            result = cur.execute("SELECT * FROM Tracks").fetchall()

            if (1 <= song_id <= len(result)):
                self.statusBar().showMessage("Запуск трека")

                self.ex = practice_screen(str(song_id))
                self.ex.choose_window = self

                self.ex.show()

                self.close()
            else:
                self.statusBar().showMessage("Трека с таким ID нет в базе данных", 3000)
        except sqlite3.Error as e:
            self.statusBar().showMessage(f"Ошибка БД: {e}", 3000)

class ClickableProgressBar(QtWidgets.QProgressBar):
    clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimum(0)
        self.setMaximum(100) 
        self.setValue(0)
        self.dragging = False
        self.setStyleSheet("""
            QProgressBar {
                border: 1px solid #888;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1E90FF;
                border-radius: 5px;
            }
        """)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.maximum() == 0:
            return
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        ratio = self.value() / self.maximum()
        x = int(ratio * self.width())
        y = self.height() // 2
        radius = 8
        color = QtGui.QColor(30, 144, 255) if not self.dragging else QtGui.QColor(0, 100, 200)
        painter.setBrush(color)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.drawEllipse(QtCore.QPoint(x, y), radius, radius)
        painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.white, 2))
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QtCore.QPoint(x, y), radius, radius)
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragging = True
            self.update()
            self._set_value_from_pos(event.position().x() if hasattr(event, 'position') else event.x())

    def mouseMoveEvent(self, event):
        if self.dragging:
            self._set_value_from_pos(event.position().x() if hasattr(event, 'position') else event.x())

    def mouseReleaseEvent(self, event):
        if self.dragging and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.dragging = False
            self.update()
            self.clicked.emit(self.value())

    def _set_value_from_pos(self, x):
        width = self.width()
        if width > 0:
            ratio = max(0.0, min(1.0, x / width))
            new_val = int(ratio * self.maximum())
            if new_val != self.value():
                self.setValue(new_val)
                self.clicked.emit(new_val)
        

class practice_screen(QMainWindow, PracticeWindow):
    def animation_button(self, button):
        original_style = button.styleSheet()
        button.setStyleSheet("background-color: #1E90FF;")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, lambda: button.setStyleSheet(original_style))

    def closeEvent(self, event):
        if hasattr(self, 'timer'): self.timer.stop()
        if self.audio_loaded: pg.mixer.music.stop()
        if (self.choose_window is not None): self.choose_window.show()
        event.accept()  

    def __init__(self, song_id):
        super(practice_screen, self).__init__()
        self.setupUi(self)
        self.audio_loaded = False
        self.play = False
        self.start_pos = 0
        self.song_id = song_id
        self.choose_window = None

        # Текст
        try:
            with open(f'songs_texts/{song_id}.txt', encoding='utf-8') as file:
                self.song_text.setPlainText(file.read())
        except FileNotFoundError:
            self.song_text.setPlainText("[Текст песни не найден]")
        except Exception as e:
            self.song_text.setPlainText(f"[Ошибка: {e}]")

        # Настройки (бой и аккорды) 
        battle_file = None
        accords_list = []
        try:
            with open(f'songs_settings/{song_id}.txt', encoding='utf-8') as file:
                lines = file.readlines()
            if len(lines) >= 2:
                battle_file = lines[0].strip()
                accords_list = lines[1].split()
        except FileNotFoundError:
            self.statusBar().showMessage("Файл настроек не найден", 3000)
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка настроек: {e}", 3000)

        # Бой
        self.battle = ""
        if battle_file:
            try:
                with open(f'battle/{battle_file}.txt', encoding='utf-8') as file:
                    self.battle = file.readline().strip()
            except FileNotFoundError:
                self.battle = "[Бой не найден]"

        # Аккорды
        self.accords = []
        for accord in accords_list:
            try:
                with open(f'accords/{accord}.txt', encoding='utf-8') as file:
                    self.accords.append(file.read())
            except FileNotFoundError:
                self.accords.append(f"[Аккорд {accord} не найден]")

        # Аудио
        try:
            pg.mixer.init(22100)
            pg.mixer.music.load(f'songs_audios/{song_id}.mp3')
            pg.mixer.music.set_volume(0.5)
            pg.mixer.music.play()
            pg.mixer.music.pause()
            self.audio_loaded = True
        except pg.error as e:
            self.statusBar().showMessage(f"Не удалось загрузить аудио: {e}", 3000)

        # Длительность трека
        self.song_length = 0
        try:
            con = sqlite3.connect("tracks.sqlite")
            cur = con.cursor()
            res = cur.execute("SELECT duration FROM Tracks WHERE id = ?", (song_id,)).fetchall()
            if res:
                dur_parts = res[0][0].split(':')
                self.song_length = int(dur_parts[0]) * 60 + int(dur_parts[1])
            con.close()
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка получения длительности: {e}", 3000)

        self.initUI()
        self.setup_progress_bar()

    def initUI(self):
        self.setFixedSize(800, 500)
        self.setWindowTitle('Практика')
        self.setWindowIcon(QIcon('icon.png'))

        self.pause_button.move(380, 410)      
        self.plus_button.move(440, 420)      
        self.minus_button.move(340, 420)     
        self.back_button.move(50, 420)
        self.label_2.move(580, 420)     
        self.sound_slider.move(620, 430) 

        self.song_text.setReadOnly(True)
        self.battle_text.setReadOnly(True)
        self.accords_text.setReadOnly(True)

        # Кнопки с анимацией
        self.show_battle_button.clicked.connect(lambda: [self.animation_button(self.show_battle_button), self.show_battle()])
        self.show_accords_button.clicked.connect(lambda: [self.animation_button(self.show_accords_button), self.show_accords()])
        self.hide_battle_button.clicked.connect(lambda: [self.animation_button(self.hide_battle_button), self.hide_battle()])
        self.hide_accords_button.clicked.connect(lambda: [self.animation_button(self.hide_accords_button), self.hide_accords()])
        self.back_button.clicked.connect(lambda: [self.animation_button(self.back_button), self.back_to_choice()])
        self.pause_button.clicked.connect(lambda: [self.animation_button(self.pause_button), self.pause_play()])
        self.plus_button.clicked.connect(lambda: [self.animation_button(self.plus_button), self.plus_time()])
        self.minus_button.clicked.connect(lambda: [self.animation_button(self.minus_button), self.minus_time()])

        self.sound_slider.valueChanged.connect(self.change_volume)

        self.show_battle()
        self.show_accords()

    def seek_to_position(self, value_msec):
        if (not self.audio_loaded): return

        new_pos_sec = value_msec / 1000.0

        if (new_pos_sec < 0): new_pos_sec = 0
        if (new_pos_sec > self.song_length): new_pos_sec = self.song_length

        self.start_pos = new_pos_sec
        pg.mixer.music.play(0, self.start_pos)

        if (not self.play): pg.mixer.music.pause()

        minutes = int(new_pos_sec // 60)
        seconds = int(new_pos_sec % 60)
        self.statusBar().showMessage(f"Перемотка на {minutes}:{seconds:02d}", 1000)

    def setup_progress_bar(self):
        self.progress_bar = ClickableProgressBar(self.centralwidget)
        self.progress_bar.setGeometry(QtCore.QRect(10, 380, 780, 16))
        self.progress_bar.setRange(0, int(self.song_length * 1000))
        self.progress_bar.setValue(0)
        self.progress_bar.clicked.connect(self.seek_to_position) 

        self.time_label = QtWidgets.QLabel(self.centralwidget)
        self.time_label.setGeometry(QtCore.QRect(10, 405, 100, 20))
        self.time_label.setText("0:00")

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

    def update_progress(self):
        if not self.audio_loaded:
            return
        pos = pg.mixer.music.get_pos()
        if pos == -1:
            pos = 0
        total_pos = self.start_pos * 1000 + pos
        self.progress_bar.setValue(int(total_pos))
        current_seconds = int(total_pos // 1000)
        minutes = current_seconds // 60
        seconds = current_seconds % 60
        self.time_label.setText(f"{minutes}:{seconds:02d}")

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key.Key_Space:
            self.pause_play()
        elif key == QtCore.Qt.Key.Key_Left:
            self.minus_time()
        elif key == QtCore.Qt.Key.Key_Right:
            self.plus_time()
        else:
            super().keyPressEvent(event)

    def show_battle(self):
        self.battle_text.setPlainText(self.battle)

    def hide_battle(self):
        self.battle_text.setPlainText('')

    def show_accords(self):
        self.accords_text.setPlainText('\n'.join(self.accords))

    def hide_accords(self):
        self.accords_text.setPlainText('')

    def back_to_choice(self):
        if (hasattr(self, 'timer')):
            self.timer.stop()
        if (self.audio_loaded):
            pg.mixer.music.stop()
        if (self.choose_window is not None):
            self.choose_window.show()
        self.close()

    def change_volume(self):
        if not self.audio_loaded:
            return
        pg.mixer.music.set_volume(self.sound_slider.value() / 100)

    def pause_play(self):
        if not self.audio_loaded:
            return
        self.play = not self.play
        if self.play:
            self.pause_button.setText('⏸')
            pg.mixer.music.unpause()
        else:
            self.pause_button.setText('▶')
            pg.mixer.music.pause()

    def plus_time(self):
        if (not self.audio_loaded): return

        cur_rel_pos = pg.mixer.music.get_pos() / 1000.0
        new_abs_pos = self.start_pos + cur_rel_pos + 5

        if (new_abs_pos > self.song_length): new_abs_pos = self.song_length

        self.start_pos = new_abs_pos
        pg.mixer.music.play(0, self.start_pos)

        if (not self.play): pg.mixer.music.pause()
        self.statusBar().showMessage("⏩ +5 секунд", 1000)


    def minus_time(self):
        if (not self.audio_loaded): return

        cur_rel_pos = pg.mixer.music.get_pos() / 1000.0
        new_abs_pos = self.start_pos + cur_rel_pos - 5

        if (new_abs_pos < 0): new_abs_pos = 0

        self.start_pos = new_abs_pos
        pg.mixer.music.play(0, self.start_pos)

        if (not self.play): pg.mixer.music.pause()
        self.statusBar().showMessage("⏪ -5 секунд", 1000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Learn_The_Guitar()
    ex.show()
    sys.exit(app.exec())
