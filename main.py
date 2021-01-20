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

class Figure:
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
        