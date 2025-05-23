from contextlib import suppress
import pygame
import ctypes
from pynput import keyboard
from threading import Thread
from typing import Dict, Tuple
import win32api
import win32con
import win32gui

class KeyVisualizer:
    def __init__(self, initial_x=0, initial_y=0):
        # Инициализация pygame
        pygame.init()
        self.width, self.height = 410, 160

        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("KeyPulse")

        self.set_window_always_on_top()
        self.set_window_position(initial_x, initial_y)
        self.remove_window_border()

        # Цвета
        self.bg_color = (40, 40, 40)
        self.key_color = (70, 70, 70)
        self.pressed_color = (255, 80, 80)
        self.text_color = (255, 255, 255)

        # Настройки клавиатуры
        self.key_size = 25
        self.key_gap = 3
        self.key_positions = {}

        # Состояние клавиш
        self.pressed_keys = set()

        # Создаем макет клавиатуры
        self.create_keyboard_layout()

        # Запускаем слушатель клавиш
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release,
            suppress=False)
        self.listener.start()

        # Основной цикл
        self.running = True


    def set_window_always_on_top(self):
        # Получаем handle окна Pygame
        hwnd = pygame.display.get_wm_info()["window"]

        # Устанавливаем стиль окна "Always on top"
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,  # Помещаем поверх всех окон
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )

    def set_window_position(self, x, y):
        """Устанавливает позицию окна на экране"""
        hwnd = pygame.display.get_wm_info()["window"]
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,  # Положение в Z-порядке
            x, y,  # Координаты X и Y
            0, 0,  # Ширина и высота (0 означает не менять)
            win32con.SWP_NOSIZE | win32con.SWP_NOZORDER
        )

    def remove_window_border(self):
        hwnd = pygame.display.get_wm_info()["window"]

        # Получаем текущие стили окна
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)

        # Убираем стандартные рамки и заголовок
        new_style = style & ~win32con.WS_CAPTION & ~win32con.WS_THICKFRAME & ~win32con.WS_MINIMIZEBOX & ~win32con.WS_MAXIMIZEBOX & ~win32con.WS_SYSMENU

        # Применяем новые стили
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, new_style)

        # Обновляем окно, чтобы изменения вступили в силу
        win32gui.SetWindowPos(hwnd, None, 0, 0, 0, 0,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOZORDER | win32con.SWP_FRAMECHANGED)

    def create_keyboard_layout(self):
        """Создаем расположение клавиш на экране"""
        # Первый ряд (Esc, F1-F12)
        first_row = [
            'esc', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6',
            'f7', 'f8', 'f9', 'f10', 'f11', 'f12'
        ]
        for i, key in enumerate(first_row):
            self.key_positions[key] = (10 + i * (self.key_size + self.key_gap), 10)

        # Второй ряд (цифры)
        second_row = [
            '`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'backspace'
        ]
        for i, key in enumerate(second_row):
            width = self.key_size * 1.5 if key == 'backspace' else self.key_size
            self.key_positions[key] = (10 + i * (self.key_size + self.key_gap), 40, width)

        # Третий ряд (буквы)
        third_row =[
            'tab', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', '\\'
        ]
        x_offset = 0
        for i, key in enumerate(third_row):
            width = self.key_size * 1.5 if key == 'tab' else self.key_size
            self.key_positions[key] = (10 + x_offset, 70, width)
            x_offset += width + self.key_gap

        # Четвертый ряд (буквы)
        fourth_row = [
            'caps_lock', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", 'enter'
        ]
        x_offset = 0
        for i, key in enumerate(fourth_row):
            width = self.key_size * 1.5 if key in ['caps_lock', 'enter'] else self.key_size
            self.key_positions[key] = (10 + x_offset, 100, width)
            x_offset += width + self.key_gap

        # Пятый ряд (буквы)
        fifth_row = [
            'shift', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'shift_r'
        ]
        x_offset = 0
        for i, key in enumerate(fifth_row):
            width = self.key_size * 2 if key in ['shift', 'shift_r'] else self.key_size
            self.key_positions[key] = (10 + x_offset, 130, width)
            x_offset += width + self.key_gap

            # Пробел и модификаторы
        self.key_positions['ctrl_l'] = (10, 160, self.key_size * 1.5)
        self.key_positions['cmd'] = (10 + self.key_size * 1.5 + self.key_gap, 160, self.key_size)
        self.key_positions['alt_l'] = (10 + self.key_size * 2.5 + self.key_gap * 2, 160, self.key_size * 1.5)
        self.key_positions['space'] = (10 + self.key_size * 4 + self.key_gap * 3, 160, self.key_size * 6)

    def on_press(self, key):
        """Обработка нажатия клавиши"""
        try:
            key_name = key.char.lower()
        except AttributeError:
            key_name = key.name.lower()

        self.pressed_keys.add(key_name)

    def on_release(self, key):
        """Обработка отпускания клавиши"""
        try:
            key_name = key.char.lower()
        except AttributeError:
            key_name = key.name.lower()

        if key_name in self.pressed_keys:
            self.pressed_keys.remove(key_name)

    def draw_key(self, key_name, x, y, width=None):
        """Рисуем одну клавишу"""
        width = width or self.key_size
        color = self.pressed_color if key_name in self.pressed_keys else self.key_color

        pygame.draw.rect(self.screen, color, (x, y, width, self.key_size))
        pygame.draw.rect(self.screen, (100, 100, 100), (x, y, width, self.key_size), 2)

        # Подписываем клавишу
        font = pygame.font.SysFont('Arial', 14)

        custom_labels = {
            'ctrl_l': 'ctrl',
            'shift': 'shift',
            'shift_r': 'shift',
            'caps_lock': 'caps',
            'enter': 'enter',
            'space': 'space',
            'tab': 'tab',
            'backspace': 'del',
            'cmd': 'win',
            'alt_l': 'alt',
            'esc': 'esc',
        }
        label = custom_labels.get(key_name, key_name.upper() if len(key_name) > 1 else key_name)

        text = font.render(label, True, self.text_color)
        text_rect = text.get_rect(center=(x + width / 2, y + self.key_size / 2))
        self.screen.blit(text, text_rect)

    def run(self):
        """Основной цикл программы"""
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Отрисовка
            self.screen.fill(self.bg_color)

            # Рисуем все клавиши
            for key_name, pos in self.key_positions.items():
                if len(pos) == 3:  # Если указана ширина
                    x, y, width = pos
                    self.draw_key(key_name, x, y, width)
                else:  # Если ширина не указана (по умолчанию)
                    x, y = pos
                    self.draw_key(key_name, x, y)

            pygame.display.flip()
            clock.tick(60)

        # Завершение работы
        self.listener.stop()
        pygame.quit()


if __name__ == "__main__":
    app = KeyVisualizer()
    app.run()