import random


# Класс исключения
class BoardOutException(Exception):
    def __init__(self, msg="Выстрел вышел за пределы игрового поля!"):
        self.msg = msg
        Exception.__init__(self, self.msg)


# Класс точек на поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Метод проверки точек на равенство
    def __eq__(self, other):
        if isinstance(other, Dot):
            return self.x == other.x and self.y == other.y
        return False


# Класс корабль
class Ship:
    def __init__(self, length, tip, direction):
        self.length = length
        self.tip = tip
        self.direction = direction
        self.lives = length

    # Метод возвращающий список всех точек коробля
    def dots(self):
        ship_dots = []
        if self.direction == "Вертикаль":
            for i in range(self.length):
                ship_dots.append(Dot(self.tip.x, self.tip.y + i))
        else:
            for i in range(self.length):
                ship_dots.append(Dot(self.tip.x + i, self.tip.y))
        return ship_dots


# Класс доска
class Board:
    def __init__(self, size, hid=True):
        self.alive_ships = 0
        self.hid = hid
        self.size = size
        self.ships = []
        self.grid = [[' '] * size for _ in range(size)]

    # Метод который ставит корабль на доску
    def add_ships(self, ship):
        for dot in ship.dots():
            if self.out(dot) or self.grid[dot.x][dot.y] != ' ':
                raise ValueError("Здесь невозможно разместить корабль!")
        for dot in ship.dots():
            self.grid[dot.x][dot.y] = 'O'
            self.ships.append(ship)
        self.alive_ships += 1

    # Метод который обводит корабль по контуру
    def contour(self, ship):
        for dot in ship.dots():
            for x in range(max(0, self.size - 1), min(self.size, dot.x + 2)):
                for y in range(max(0, self.size - 1), min(self.size, dot.y + 2)):
                    if self.grid[x][y] == ' ':
                        self.grid[x][y] = "X"

    # Методы, который выводит доску в консоль в зависимости от параметра hid
    def is_hidden(self):
        self.hid = True

    def is_not_hidden(self):
        self.hid = False

    # Метод отображение игрового поля
    def display(self):
        print("  | " + "   ".join(str(i) for i in range(self.size)))
        print("--+" + "----" * 1 * self.size)
        for i, row in enumerate(self.grid):
            row_str = " | ".join(cell if not self.hid or cell != 'O' else ' ' for cell in row)
            print(f"{i} | {row_str}")

    # Метод, который делает выстрел по доске
    def shot(self, dot):
        if self.out(dot):
            raise ValueError("Выстрел за пределы поля!")
        if not self.grid[dot.x][dot.y] != 'T':
            raise ValueError("Вы уже производиле выстрел по этим координатам")

        hit_ship = None
        for ship in self.ships:
            if dot in ship.dots():
                ship.lives -= 1
                if ship.lives == 0:
                    self.alive_ships -= 1
                    self.contour(ship)
                hit_ship = ship
                break

        if hit_ship:
            self.grid[dot.x][dot.y] = 'X'
            return True
        else:
            self.grid[dot.x][dot.y] = 'T'
            return False

    # Метод out, который для точки (объекта класса Dot) возвращает True, если точка выходит за пределы поля,
    # и False, если не выходит
    def out(self, dot):
        return not (0 <= dot.x < self.size and 0 <= dot.y < self.size)


# Класс родитель игроков
class Player:
    def __init__(self, own_board, enemy_board):
        self.own_board = own_board
        self.enemy_board = enemy_board

    # Метод, который «спрашивает» игрока, в какую клетку он делает выстрел
    @staticmethod
    def ask():
        raise NotImplementedError("Этот метод должен быть реализован дочерними классами!")

    # Метод, который делает ход в игре
    def move(self):
        while True:
            try:
                target = self.ask()
                if self.enemy_board.shot(target):
                    return self.enemy_board.alive_ships > 0
            except ValueError as e:
                print(e)


# Класс реального игрока
class User(Player):
    @staticmethod
    def ask():
        while True:
            try:
                x = int(input("Введите координату X: "))
                y = int(input("Введите координату Y: "))
                shot_dot = Dot(x, y)
                return shot_dot
            except ValueError:
                print("Неверные координаты, введите корректные координаты!")


# Класс игорка компьютера
class AI(Player):
    def ask(self):
        x = random.randint(0, self.enemy_board.size - 1)
        y = random.randint(0, self.enemy_board.size - 1)
        return Dot(x, y)


# Класс игры
class Game:
    def __init__(self):
        self.user_board = Board(10, hid=False)
        self.ai_board = Board(10, hid=True)
        self.user = User(self.user_board, self.ai_board)
        self.ai = AI(self.ai_board, self.user_board)

    # Метод генерирует случайную доску
    @staticmethod
    def random_board(board):
        ship_lengths = [3, 2, 2, 1, 1, 1, 1]

        for length in ship_lengths:
            while True:
                direction = random.choice(['Вертикаль', 'Горизонталь'])
                x = random.randint(0, board.size - 1)
                y = random.randint(0, board.size - 1)
                tip = Dot(x, y)

                try:
                    ship = Ship(length, tip, direction)
                    board.add_ships(ship)
                    break
                except ValueError:
                    continue

    # Метод с самим игровым циклом
    def loop(self):
        while self.user_board.alive_ships > 0 and self.ai_board.alive_ships > 0:
            self.user_board.display()
            self.ai_board.display()

            user_repeat = self.user.move()
            ai_repeat = self.ai.move()
            if not user_repeat:
                self.user_board.display()
                self.ai_board.display()
                print("Поздравляю вы выиграли!!!")
                break
            if not ai_repeat:
                self.user_board.display()
                self.ai_board.display()
                print("Увы, вы проиграли!")
                break

            if self.user_board.alive_ships == 0:
                break

            elif self.ai_board.alive_ships == 0:
                break

    # Метод запуска игры
    def start(self):
        self.random_board(self.user_board)
        self.random_board(self.ai_board)
        self.loop()


print("Добро пожаловать в игру 'Морсокй бой'")
game = Game()
game.start()