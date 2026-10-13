import tkinter as tk
import random

# ================= НАСТРОЙКИ ИГРЫ =================
COLS = 10
ROWS = 20
BLOCK_SIZE = 30
WIDTH = COLS * BLOCK_SIZE
HEIGHT = ROWS * BLOCK_SIZE
GAME_SPEED = 500 # Скорость падения в миллисекундах (чем меньше, тем быстрее)
# ==================================================

# Фигуры и их цвета (классические)
SHAPES = [
    [[1, 1, 1, 1]],                             # I (Голубой)
    [[1, 1], [1, 1]],                           # O (Желтый)
    [[0, 1, 0], [1, 1, 1]],                     # T (Фиолетовый)
    [[0, 1, 1], [1, 1, 0]],                     # S (Зеленый)
    [[1, 1, 0], [0, 1, 1]],                     # Z (Красный)
    [[1, 0, 0], [1, 1, 1]],                     # J (Синий)
    [[0, 0, 1], [1, 1, 1]]                      # L (Оранжевый)
]
COLORS = ["cyan", "yellow", "purple", "green", "red", "blue", "orange"]

class Tetris:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Тетрис")
        self.root.resizable(False, False)
        
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="black")
        self.canvas.pack()
        
        self.score = 0
        self.score_text = self.canvas.create_text(10, 10, text="Счет: 0", anchor="nw", fill="white", font=("Arial", 14, "bold"))
        self.game_over_text = self.canvas.create_text(WIDTH//2, HEIGHT//2, text="", fill="red", font=("Arial", 24, "bold"))
        
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.current_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_color = ""
        self.is_game_over = False
        self.game_loop_id = None
        
        self.root.bind("<KeyPress>", self.key_press)
        
        self.new_piece()
        self.game_loop()
        self.root.mainloop()

    def new_piece(self):
        idx = random.randint(0, len(SHAPES) - 1)
        self.current_piece = [row[:] for row in SHAPES[idx]] # Копия фигуры
        self.current_color = COLORS[idx]
        self.current_x = COLS // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        
        if self.check_collision(self.current_x, self.current_y, self.current_piece):
            self.is_game_over = True
            self.canvas.itemconfig(self.game_over_text, text="ИГРА ОКОНЧЕНА\nНажми 'R' для рестарта")

    def check_collision(self, x, y, piece):
        for r, row in enumerate(piece):
            for c, cell in enumerate(row):
                if cell:
                    new_x = x + c
                    new_y = y + r
                    if new_x < 0 or new_x >= COLS or new_y >= ROWS:
                        return True
                    if new_y >= 0 and self.board[new_y][new_x]:
                        return True
        return False

    def merge_piece(self):
        for r, row in enumerate(self.current_piece):
            for c, cell in enumerate(row):
                if cell:
                    if self.current_y + r >= 0:
                        self.board[self.current_y + r][self.current_x + c] = self.current_color

    def clear_lines(self):
        lines_cleared = 0
        new_board = [row for row in self.board if any(cell == 0 for cell in row)]
        lines_cleared = ROWS - len(new_board)
        
        for _ in range(lines_cleared):
            new_board.insert(0, [0 for _ in range(COLS)])
            
        self.board = new_board
        
        if lines_cleared > 0:
            self.score += lines_cleared * 100
            self.canvas.itemconfig(self.score_text, text=f"Счет: {self.score}")

    def rotate_piece(self):
        # Транспонирование и реверс строк для поворота на 90 градусов
        rotated = [list(row) for row in zip(*self.current_piece[::-1])]
        if not self.check_collision(self.current_x, self.current_y, rotated):
            self.current_piece = rotated

    def move(self, dx, dy):
        if self.is_game_over:
            return
        if not self.check_collision(self.current_x + dx, self.current_y + dy, self.current_piece):
            self.current_x += dx
            self.current_y += dy
        elif dy > 0: # Если движение вниз заблокировано
            self.merge_piece()
            self.clear_lines()
            self.new_piece()

    def draw(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black")
        
        # Рисуем доску
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r][c]:
                    self.draw_block(c, r, self.board[r][c])
                    
        # Рисуем текущую фигуру
        if self.current_piece and not self.is_game_over:
            for r, row in enumerate(self.current_piece):
                for c, cell in enumerate(row):
                    if cell:
                        self.draw_block(self.current_x + c, self.current_y + r, self.current_color)
                        
        self.canvas.itemconfig(self.score_text, text=f"Счет: {self.score}")
        if self.is_game_over:
            self.canvas.itemconfig(self.game_over_text, text="ИГРА ОКОНЧЕНА\nНажми 'R' для рестарта")

    def draw_block(self, x, y, color):
        x1 = x * BLOCK_SIZE
        y1 = y * BLOCK_SIZE
        x2 = x1 + BLOCK_SIZE
        y2 = y1 + BLOCK_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1)

    def key_press(self, event):
        if self.is_game_over:
            # Проверка клавиши R в любой раскладке
            keysym = event.keysym.lower()
            if keysym in ['r', 'cyrillic_er', 'к']:
                self.restart()
            return

        if event.keysym == "Left":
            self.move(-1, 0)
        elif event.keysym == "Right":
            self.move(1, 0)
        elif event.keysym == "Down":
            self.move(0, 1)
        elif event.keysym == "Up" or event.keysym == "space":
            self.rotate_piece()
            
        self.draw()

    def game_loop(self):
        if not self.is_game_over:
            self.move(0, 1)
            self.draw()
            self.game_loop_id = self.root.after(GAME_SPEED, self.game_loop)

    def restart(self):
        if self.game_loop_id:
            self.root.after_cancel(self.game_loop_id)
        self.board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.is_game_over = False
        self.canvas.itemconfig(self.game_over_text, text="")
        self.new_piece()
        self.game_loop()

if __name__ == "__main__":
    game = Tetris()