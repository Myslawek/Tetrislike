import typing

import pygame
import random
import numpy
import dataclasses


colors = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "MAGENTA": (255, 0, 255),
    "CYAN": (0, 255, 255),
    "BLACK": (0, 0, 0),
    "GRAY": (128, 128, 128),
    "WHITE": (255, 255, 255)
}


def index_to_color(color_index: int) -> typing.Tuple:
    try:
        return colors.get(list(colors)[int(color_index)])
    except:
        print(f'Failed at provided: {type(color_index)}, with value {color_index}')

@dataclasses.dataclass
class Position:
    x: int
    y: int

class Figure:
    __next_color_index: int = 0
    BOUNDING_BOX_WIDTH: int = 4
    BOUNDING_BOX_HEIGHT: int = 4

    # Draw field indexes:
    # 0 , 1 , 2, 3
    # 4 , 5 , 6, 7
    # 8 , 9 ,10,11
    # 14, 13,14,15

    # https://en.wikipedia.org/wiki/Tetromino#One-sided_tetrominoes
    # "(type, rotation)"
    __bounding_box_filled_indexes = {
        "I": numpy.array(
            [
                [1, 5, 9, 13],
                [4, 5, 6, 7]
            ]
        ),
        "O": numpy.array(
            [
                [1, 2, 5, 6]
            ]
        ),
        "T": numpy.array(
            [
                [1, 4, 5, 6],
                [1, 5, 6, 9],
                [4, 5, 6, 9],
                [1, 4, 5, 9]
            ]
        ),
        "J": numpy.array(
            [
                [1, 5, 8, 9],
                [0, 4, 5, 6],
                [1, 2, 5, 9],
                [4, 5, 6, 10]
            ]
        ),
        "L": numpy.array(
            [
                [1, 5, 9, 10],
                [4, 5, 6, 2],
                [0, 1, 5, 9],
                [8, 4, 5, 6]
            ]
        ),
        "S": numpy.array(
            [
                [6, 7, 9, 10],
                [1, 5, 6, 10]
            ]
        ),
        "Z": numpy.array(
            [
                [4, 5, 9, 10],
                [2, 5, 6, 9]
            ]
        )
    }

    def __init__(self, bounding_box_current_position: Position, rotation: int = 0, shape_symbol: str = None):
        self.bounding_box_position = bounding_box_current_position
        if shape_symbol is not None and shape_symbol in list(Figure.__bounding_box_filled_indexes.keys()):
            self.__shape_symbol = shape_symbol
        else:
            self.__shape_symbol = random.choice(list(Figure.__bounding_box_filled_indexes.keys()))
        self.possible_rotations: int = Figure.__bounding_box_filled_indexes.get(self.__shape_symbol).shape[0]
        self.rotation = rotation % self.possible_rotations
        self.color_index: int = Figure.__next_color_index
        Figure.__next_color_index = (Figure.__next_color_index + 1) % (len(
            colors) - 3)  # -3 so to avoid using BLACK, GRAY and WHITE

    def rotate(self):
        self.rotation = (self.rotation + 1) % self.possible_rotations

    def filled_points(self):
        return Figure.__bounding_box_filled_indexes.get(self.__shape_symbol)[self.rotation]

    def get_absolute_occupied_positions(self) -> typing.List[Position]:
        points = []
        for filled_index in Figure.__bounding_box_filled_indexes.get(self.__shape_symbol)[self.rotation]:
            bounding_box_occupied_row = int(filled_index / 4)
            bounding_box_occupied_column = filled_index % 4
            points.append(Position(self.bounding_box_position.x + bounding_box_occupied_column,
                                   self.bounding_box_position.y + bounding_box_occupied_row))
        return points
        
class GameArea:
    EMPTY_CELL_VALUE: int = -1

    def __init__(self, height: int = 20, width: int = 10, horizontal_padding: int = 100, vertical_padding: int = 20):
        self.height = height
        self.width = width
        self.area: numpy.ndarray = numpy.full((height, width), fill_value=GameArea.EMPTY_CELL_VALUE)
        self.horizontal_padding = horizontal_padding
        self.vertical_padding = vertical_padding

    def override_target_row_with_upper(self, row_index_to_override: int):
        self.area[row_index_to_override] = self.area[row_index_to_override - 1]

    def move_rows_down(self, bottom_row_index: int):
        row: numpy.ndarray
        for i in range(bottom_row_index, 1, -1):
            self.override_target_row_with_upper(i)

    def is_row_solid(self, target_row_index: int) -> bool:
        for cell in self.area[target_row_index]:
            if cell == GameArea.EMPTY_CELL_VALUE:
                return False
        return True

class Tetrislike:
    def __init__(self, game_area: GameArea = None):
        if game_area is None:
            self.game_area = GameArea(height=20, width=10)
        else:
            self.game_area = game_area
        self.speed: float = 1
        self.controlled_figure: Figure = None
        self.score: int = 0
        self.spawn_new_figure()
        self.game_over: bool = False
        self.level: int = 0
        self.next_level_threshold: int = 20
        self.move_down_scalar: float = 0.3

    def spawn_new_figure(self):
        self.controlled_figure: Figure = Figure(Position(int(self.game_area.width / 2), 0))

    def is_figure_colliding(self, figure_to_check: Figure) -> bool:
        for occupied_position in figure_to_check.get_absolute_occupied_positions():
            # check if exceeding vertically
            if occupied_position.y > self.game_area.height - 1:
                return True

            # check if exceeding horizontally
            if occupied_position.x < 0 or occupied_position.x > self.game_area.width - 1:
                return True

            # check if occupied by another figure (or part of it)
            if self.game_area.area[occupied_position.y, occupied_position.x] != GameArea.EMPTY_CELL_VALUE:
                return True

        return False

    def handle_settle(self, figure_to_settle: Figure):
        for occupied_position in figure_to_settle.get_absolute_occupied_positions():
            self.game_area.area[occupied_position.y, occupied_position.x] = figure_to_settle.color_index

    def collect_lines(self):
        collected_lines_amount: int = 0
        for i in range(self.game_area.height):  # from bottom, to top
            if self.game_area.is_row_solid(i):
                collected_lines_amount += 1
                self.game_area.move_rows_down(i)
        self.score += collected_lines_amount * self.game_area.width

    def refresh_area(self):
        self.handle_settle(self.controlled_figure)
        self.collect_lines()
        self.spawn_new_figure()
        if self.is_figure_colliding(self.controlled_figure):
            self.game_over = True # gameover


    def __move(self, horizontal_displacement: int):
        self.controlled_figure.bounding_box_position.x += horizontal_displacement
        if self.is_figure_colliding(self.controlled_figure):
            self.controlled_figure.bounding_box_position.x -= horizontal_displacement

    def fig_move_right(self):
        self.__move(1)

    def fig_move_left(self):
        self.__move(-1)

    def fig_move_down(self):
        self.controlled_figure.bounding_box_position.y += 1
        if self.is_figure_colliding(self.controlled_figure):
            self.controlled_figure.bounding_box_position.y -= 1
            self.refresh_area()

    def fig_rotate(self):
        prev_rotation: int = self.controlled_figure.rotation
        self.controlled_figure.rotate()
        if self.is_figure_colliding(self.controlled_figure):
            self.controlled_figure.rotation = prev_rotation


def draw_figure(target_screen, x_pad: int, y_pad: int, scale: int, target_figure: Figure):
    target_color = index_to_color(target_figure.color_index)
    for abs_pos in target_figure.get_absolute_occupied_positions():
        pygame.draw.rect(target_screen, target_color,
                         [x_pad + scale * (abs_pos.x) + 1,
                          y_pad + scale * (abs_pos.y) + 1,
                          scale - 2, scale - 2])