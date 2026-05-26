import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QHeaderView
from PyQt6.QtGui import QIcon, QPixmap
import pygame as pg

# иницилизация Qt дизайна
# была вынесена в другой файл для быстрого изменения или добавление чего-то нового в структуре дизайна
from ui_file_1 import MainWindow
from choose_screen import ChooseWindow
from practice_screen import PracticeWindow

# Константы
STYLE = False

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

        if STYLE:  # Светлая тема
            style_file = "styles/light.qss"
        else:  # Темная тема
            style_file = "styles/dark.qss"

        with open(style_file, "r") as f:
            self.setStyleSheet(f.read())

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
        reply = QMessageBox.question(
            self,
            "Закрыть приложение",
            "Вы действительно хотите уйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
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

        if STYLE:  # Светлая тема
            style_file = "styles/light.qss"
        else:  # Темная тема
            style_file = "styles/dark.qss"

        with open(style_file, "r") as f:
            self.setStyleSheet(f.read())

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
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(val).capitalize()))

        # регулируем ширину столбцов
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # убираем возможность изменять таблицу
        self.tableWidget.setEnabled(False)

        # функционал кнопок
        self.search_button.clicked.connect(self.filter)
        self.start_button.clicked.connect(self.run)
        self.set_style_button.clicked.connect(self.change_style)
        self.exit_button.clicked.connect(self.exit)

        self.search_line.returnPressed.connect(self.filter)
        self.song_id.returnPressed.connect(self.run)

        self.style = STYLE
        self.set_style_button.setIcon(QIcon('sun.png'))
        self.search_button.setIcon((QIcon('Lupa.png')))

    def exit(self):
        self.ex = Learn_The_Guitar()
        self.ex.choose_window = self
        self.ex.show()
        self.close()

    def change_style(self):
        global STYLE
        self.style = not self.style
        STYLE = self.style

        if self.style:  # Светлая тема
            style_file = "styles/light.qss"
            self.set_style_button.setIcon(QIcon('moon.png'))
        else:  # Темная тема
            style_file = "styles/dark.qss"
            self.set_style_button.setIcon(QIcon('sun.png'))

        with open(style_file, "r") as f:
            self.setStyleSheet(f.read())

    def filter(self):
        cur = self.con.cursor()
        search_text = self.search_line.text().strip().lower()

        try:
            if (not search_text):
                result = cur.execute("SELECT * FROM Tracks").fetchall()
            else:
                query = f"SELECT * FROM Tracks WHERE LOWER(singer) LIKE ? OR LOWER(track_title) LIKE ?"
                search_pattern = f"%{search_text}%"
                result = cur.execute(query, (search_pattern, search_pattern)).fetchall()

            self.tableWidget.setRowCount(len(result))

            if (not result):
                self.statusBar().showMessage("Nothing found")
                return

            for i, elem in enumerate(result):
                for j, val in enumerate(elem):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val).capitalize()))

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
                singer = str(result[song_id - 1][1]).capitalize()
                song = str(result[song_id - 1][2]).capitalize()
                self.statusBar().showMessage("Запуск трека")

                self.ex = practice_screen(str(song_id), singer, song)
                self.ex.choose_window = self

                self.ex.show()

                self.close()
            else:
                self.statusBar().showMessage("Трека с таким ID нет в базе данных", 3000)
        except sqlite3.Error as e:
            self.statusBar().showMessage(f"Ошибка БД: {e}", 3000)


class practice_screen(QMainWindow, PracticeWindow):

    def __init__(self, song_id, singer, song):
        super(practice_screen, self).__init__()
        self.setupUi(self)

        self.singer_label.setText(singer)
        self.track_label.setText(song)

        # соберём данные с песни
        with open(f'songs_texts/{song_id}.txt', encoding='utf-8') as file:
            self.song_text.setPlainText(file.read())
        with open(f'songs_settings/{song_id}.txt', encoding='utf-8') as file:
            text = file.readlines()

        pixmap = QPixmap(f'pics/{song_id}.png')
        self.image_label.setPixmap(pixmap)

        # данные о бое
        with open(f'battle/{text[0].strip()}.txt', encoding='utf-8') as file:
            self.battle = file.readline()
        # print(self.battle)

        # данный об аккордах
        self.accords = []
        for accord in text[1].split():
            with open(f'accords/{accord}.txt', encoding='utf-8') as file:
                self.accords.append(file.read())
        # print(*self.accords, sep='\n')

        # загружаем трек
        pg.mixer.init(22100)
        pg.mixer.music.load(f'songs_audios/{song_id}.mp3')
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play()
        pg.mixer.music.pause()
        self.play = False
        self.start_pos = 0

        # длинна песни
        con = sqlite3.connect("tracks.sqlite")
        cur = con.cursor()
        res = cur.execute(f"""
        SELECT duration FROM Tracks
        WHERE id = '{song_id}'""").fetchall()
        self.song_lenth = res[0][0].split(':')
        self.song_lenth = int(self.song_lenth[0]) * 60 + int(self.song_lenth[1])
        # print(self.song_lenth)

        # запускаем основную иницилизацию
        self.initUI()

    def initUI(self):
        # Настройка окна и иконочки)
        self.setFixedSize(1000, 800)
        self.setWindowTitle('Практика')
        self.setWindowIcon(QIcon('icon.png'))

        if STYLE:  # Светлая тема
            style_file = "styles/light.qss"
        else:  # Темная тема
            style_file = "styles/dark.qss"

        with open(style_file, "r") as f:
            self.setStyleSheet(f.read())

        # делаем неизменяемыми все текстовые поля
        self.song_text.setReadOnly(True)
        self.battle_text.setReadOnly(True)
        self.accords_text.setReadOnly(True)

        # функционал кнопок
        self.show_battle_button.clicked.connect(self.show_battle)
        self.show_accords_button.clicked.connect(self.show_accords)
        self.hide_battle_button.clicked.connect(self.hide_battle)
        self.hide_accords_button.clicked.connect(self.hide_accords)
        self.back_button.clicked.connect(self.back_to_choice)
        self.pause_button.clicked.connect(self.pause_play)
        self.plus_button.clicked.connect(self.plus_time)
        self.minus_button.clicked.connect(self.minus_time)

        # функционал слайдеров
        self.sound_slider.valueChanged.connect(self.change_volume)

        # покажем бой и аккорды изначально
        self.show_battle()
        self.show_accords()

    # Показать бой
    def show_battle(self):
        self.battle_text.setPlainText(self.battle)

    # скрыть бой
    def hide_battle(self):
        self.battle_text.setPlainText('')

    # Показать аккорды
    def show_accords(self):
        self.accords_text.setPlainText('\n'.join(self.accords))

    # скрыть аккорды
    def hide_accords(self):
        self.accords_text.setPlainText('')

    # вернуться к выбору трека
    def back_to_choice(self):
        pg.mixer.music.stop()
        self.ex = choose_screen()
        self.ex.choose_window = self
        self.ex.show()
        self.close()

    def change_volume(self):
        pg.mixer.music.set_volume(self.sound_slider.value() / 100)
        # print(pg.mixer.music.get_volume())

    def pause_play(self):
        self.play = not self.play
        if self.play:
            self.pause_button.setText('⏸')
            pg.mixer.music.unpause()
        else:
            self.pause_button.setText('▶')
            pg.mixer.music.pause()

    # перемотка вперед
    def plus_time(self):
        # текущее место в треке в секундах
        cur_pos = pg.mixer.music.get_pos() / 1000

        # от момента начала + сколько прошло + 5 сек
        self.start_pos += cur_pos + 5

        # если больше длины самого трека, то он начинается с начала
        if self.start_pos > self.song_lenth:
            self.start_pos = 0
        pg.mixer.music.play(0, self.start_pos, 0)

        # если на паузе, то не играем
        if not self.play:
            pg.mixer.music.pause()

    # перемотку назад
    def minus_time(self):
        # текущее место в треке в секундах
        cur_pos = pg.mixer.music.get_pos() / 1000

        # от момента начала + сколько прошло - 5 сек
        self.start_pos += cur_pos - 5

        # если результат меньше нуля (трек начинается с отрицательной секунды), то начинать трек с 0
        if self.start_pos < 0:
            self.start_pos = 0
        pg.mixer.music.play(0, self.start_pos, 0)

        # если на паузе, то не играем
        if not self.play:
            pg.mixer.music.pause()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Learn_The_Guitar()
    ex.show()
    sys.exit(app.exec())
