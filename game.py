import pygame
import random
import time
from support import *
from settings import *

import threading

# import pyttsx3

from solution import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.shuffle_time = 0
        self.start_shuffle = False
        self.previous_choice = ""
        self.start_game = False
        self.start_timer = False
        self.elapsed_time = 0
        self.high_score = float(self.get_high_scores()[0])

        # Dictionary to map numbers to alphabets
        self.number_to_alphabet = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E",
            6: "F",
            7: "G",
            8: "H",
            9: "I",
            10: "J",
            11: "K",
            12: "L",
            13: "M",
            14: "N",
            15: "O",
            16: "P",
        }

    def get_high_scores(self):
        with open("high_score.txt", "r") as file:
            scores = file.read().splitlines()
        return scores

    def save_score(self):
        with open("high_score.txt", "w") as file:
            file.write(str("%.3f\n" % self.high_score))

    def create_game(self):
        grid = [
            [x + y * GAME_SIZE for x in range(1, GAME_SIZE + 1)]
            for y in range(GAME_SIZE)
        ]
        grid[-1][-1] = 0
        return grid

    def shuffle(self):
        possible_moves = []
        for row, tiles in enumerate(self.tiles):
            for col, tile in enumerate(tiles):
                if tile.text == "empty":
                    if tile.right():
                        possible_moves.append("right")
                    if tile.left():
                        possible_moves.append("left")
                    if tile.up():
                        possible_moves.append("up")
                    if tile.down():
                        possible_moves.append("down")
                    break
            if len(possible_moves) > 0:
                break

        if self.previous_choice == "right":
            (
                possible_moves.remove("left")
                if "left" in possible_moves
                else possible_moves
            )
        elif self.previous_choice == "left":
            (
                possible_moves.remove("right")
                if "right" in possible_moves
                else possible_moves
            )
        elif self.previous_choice == "up":
            (
                possible_moves.remove("down")
                if "down" in possible_moves
                else possible_moves
            )
        elif self.previous_choice == "down":
            possible_moves.remove("up") if "up" in possible_moves else possible_moves

        choice = random.choice(possible_moves)

        self.previous_choice = choice
        if choice == "right":
            self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = (
                self.tiles_grid[row][col + 1],
                self.tiles_grid[row][col],
            )
        elif choice == "left":
            self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = (
                self.tiles_grid[row][col - 1],
                self.tiles_grid[row][col],
            )
        elif choice == "up":
            self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = (
                self.tiles_grid[row - 1][col],
                self.tiles_grid[row][col],
            )
        elif choice == "down":
            self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = (
                self.tiles_grid[row + 1][col],
                self.tiles_grid[row][col],
            )

    def draw_tiles(self):
        self.tiles = []
        for row, x in enumerate(self.tiles_grid):
            self.tiles.append([])
            for col, tile in enumerate(x):
                if tile != 0:
                    # Convert numbers to alphabets
                    tile_text = self.number_to_alphabet[tile]
                    self.tiles[row].append(Tile(self, col, row, tile_text))
                else:
                    self.tiles[row].append(Tile(self, col, row, "empty"))

    def new(self):
        self.all_sprites = pygame.sprite.Group()
        self.tiles_grid = self.create_game()
        self.tiles_grid_completed = self.create_game()
        self.elapsed_time = 0
        self.start_timer = False
        self.start_game = False
        self.buttons_list = []
        self.buttons_list.append(Button(500, 100, 200, 50, "Shuffle", WHITE, BLACK))
        self.buttons_list.append(Button(500, 170, 200, 50, "Reset", WHITE, BLACK))
        self.buttons_list.append(Button(500, 240, 200, 80, "Solve", WHITE, BLACK))
        self.draw_tiles()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        if self.start_game:
            if self.tiles_grid == self.tiles_grid_completed:
                self.start_game = False
                if self.high_score > 0:
                    self.high_score = (
                        self.elapsed_time
                        if self.elapsed_time < self.high_score
                        else self.high_score
                    )
                else:
                    self.high_score = self.elapsed_time
                self.save_score()

            if self.start_timer:
                self.timer = time.time()
                self.start_timer = False
            self.elapsed_time = time.time() - self.timer

        if self.start_shuffle:
            self.shuffle()
            self.draw_tiles()
            self.shuffle_time += 1
            if self.shuffle_time > 120:
                self.start_shuffle = False
                self.start_game = True
                self.start_timer = True

        self.all_sprites.update()

    def draw_grid(self):
        for row in range(-1, GAME_SIZE * TILESIZE, TILESIZE):
            pygame.draw.line(
                self.screen, LIGHTGREY, (row, 0), (row, GAME_SIZE * TILESIZE)
            )
        for col in range(-1, GAME_SIZE * TILESIZE, TILESIZE):
            pygame.draw.line(
                self.screen, LIGHTGREY, (0, col), (GAME_SIZE * TILESIZE, col)
            )

    def draw(self):
        self.screen.fill(BGCOLOUR)
        self.all_sprites.draw(self.screen)
        self.draw_grid()
        for button in self.buttons_list:
            for button in self.buttons_list:
                button.draw(self.screen)
        UIElement(550, 35, "%.3f" % self.elapsed_time).draw(self.screen)
        UIElement(
            430,
            350,
            "High Score - %.3f" % (self.high_score if self.high_score > 0 else 0),
        ).draw(self.screen)
        pygame.display.flip()

    def move_tile(self, direction):
        for row, tiles in enumerate(self.tiles_grid):
            for col, tile in enumerate(tiles):
                if tile == 0:
                    if direction == "right" and col < GAME_SIZE - 1:
                        self.tiles_grid[row][col], self.tiles_grid[row][col + 1] = (
                            self.tiles_grid[row][col + 1],
                            self.tiles_grid[row][col],
                        )
                        self.draw_tiles()
                        return
                    elif direction == "left" and col > 0:
                        self.tiles_grid[row][col], self.tiles_grid[row][col - 1] = (
                            self.tiles_grid[row][col - 1],
                            self.tiles_grid[row][col],
                        )
                        self.draw_tiles()
                        return
                    elif direction == "up" and row > 0:
                        self.tiles_grid[row][col], self.tiles_grid[row - 1][col] = (
                            self.tiles_grid[row - 1][col],
                            self.tiles_grid[row][col],
                        )
                        self.draw_tiles()
                        return
                    elif direction == "down" and row < GAME_SIZE - 1:
                        self.tiles_grid[row][col], self.tiles_grid[row + 1][col] = (
                            self.tiles_grid[row + 1][col],
                            self.tiles_grid[row][col],
                        )
                        self.draw_tiles()
                        return

    def solve_puzzle(self, *args):

        ans_list = args

        print(len(ans_list))

        i = 1

        visited = []

        for direction in ans_list:

            if direction in visited:
                continue

            visited.append(direction)

            if i <= 10:
                direction = direction[1:]
            else:
                direction = direction[2:]

            print(str(i) + direction)

            i = i + 1

           
            time.sleep(0.5)
        
    print("Solution completed successfully")

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for row, tiles in enumerate(self.tiles):
                    for col, tile in enumerate(tiles):
                        if tile.click(mouse_x, mouse_y):
                            if tile.right() and self.tiles_grid[row][col + 1] == 0:
                                (
                                    self.tiles_grid[row][col],
                                    self.tiles_grid[row][col + 1],
                                ) = (
                                    self.tiles_grid[row][col + 1],
                                    self.tiles_grid[row][col],
                                )
                                print("L")

                            if tile.left() and self.tiles_grid[row][col - 1] == 0:
                                (
                                    self.tiles_grid[row][col],
                                    self.tiles_grid[row][col - 1],
                                ) = (
                                    self.tiles_grid[row][col - 1],
                                    self.tiles_grid[row][col],
                                )
                                print("R")

                            if tile.up() and self.tiles_grid[row - 1][col] == 0:
                                (
                                    self.tiles_grid[row][col],
                                    self.tiles_grid[row - 1][col],
                                ) = (
                                    self.tiles_grid[row - 1][col],
                                    self.tiles_grid[row][col],
                                )
                                print("D")

                            if tile.down() and self.tiles_grid[row + 1][col] == 0:
                                (
                                    self.tiles_grid[row][col],
                                    self.tiles_grid[row + 1][col],
                                ) = (
                                    self.tiles_grid[row + 1][col],
                                    self.tiles_grid[row][col],
                                )
                                print("U")

                            self.draw_tiles()

                for button in self.buttons_list:
                    if button.click(mouse_x, mouse_y):
                        if button.text == "Shuffle":
                            self.shuffle_time = 0
                            self.start_shuffle = True
                        if button.text == "Reset":
                            self.new()
                        if button.text == "Solve":
                            int_tiles_grid = []
                            for row in self.tiles_grid:
                                int_row = []
                                for tile in row:
                                    if isinstance(tile, int):
                                        int_row.append(tile)
                                    else:
                                        int_row.append(int(tile.text))
                                int_tiles_grid.append(int_row)
                            ans_list = solve_robo(int_tiles_grid)

                            solve_thread = threading.Thread(
                                target=self.solve_puzzle, args=(*ans_list,)
                            )
                            solve_thread.start()


game = Game()

while True:
    game.new()
    game.run()
