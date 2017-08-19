import tkinter as tk

import piece as p

root = tk.Tk()

images = {}
for color in ['black','white',]:
    for piece in ['P','R','N','B','K','Q',]:
        for floor in ['Bisque','White']:
            path = color + piece + floor
            images[path] = tk.PhotoImage(file=path+'.png')
images['White'] = tk.PhotoImage(file='White.png')
images['Bisque'] = tk.PhotoImage(file='Bisque.png')  # 26 total images


def swap_pieces(start, target): # characters [0:6] piece [6:] tile
    target['text'] = start['text'][0:6] + target['fg']
    start['text'] = start['fg']
    start['image'] = images[start['text']]
    target['image'] = images[target['text']]


def promotion(pawn):
    pawn['text'] = pawn['text'][0:5] + 'Q' + pawn['text'][6:]
    pawn['image'] = images[pawn['text']]


def passant_capture(pawn):
    pawn['image'] = images[pawn['fg']]


class Game(tk.Frame):
    selected_tile  = None
    white = True # white's turn
    ep_col = -1 # column allowing en passant, -1 means none
    P1_moved = [0,0,0] # columns for queen's rook, king, and king's rook
    P2_moved = [0,0,0] # 1 means piece has moved, can't castle
    K1 = None
    K2 = None
    board = [] # stores tile objects, used for getting piece locations

    def __init__(self, master = None, expand=True):
        super().__init__(master)
        self.pack()
        self.set_board()

    def highlight(self, tile):
        if not (self.selected_tile or p.is_empty(tile)):
            tile['bg'] = 'gold'
        elif self.selected_tile:
            self.selected_tile['bg'] = self.selected_tile['fg']

    def execute_castle(self, king, end):
        king_index = self.board.index(king)
        end_index  = self.board.index(end)
        rook_index = end_index + 1 if end_index > king_index else end_index - 2
        rook_end   = end_index - p.shift(end_index > king_index)
        swap_pieces(king, end)
        swap_pieces(self.board[rook_index], self.board[rook_end])

    def pawn_conds(self, pawn, row, col, end_row):
        if 'P' in pawn['text']:
            if abs(row - end_row) == 2:
                self.ep_col = col
            if end_row == 0 or end_row == 7:
                promotion(pawn)

    def king_conds(self, tile, row, col):
        if 'K' in tile['text']:
            if self.white:
                self.P1_moved[1] = 1
                self.K1 = tile
            else:
                self.P2_moved[1] = 1
                self.K2 = tile
        elif 'R' in tile['text']:
            if row == 0:
                index = 0 if col == 0 else 2
                self.P1_moved[index] = 1
            else:
                index = 2 if col == 0 else 0
                self.P2_moved[index] = 1

    def in_check(self, king):
        pos = p.get_pos(self.board, king)
        return p.in_check(self.board, king, pos[0], pos[1])

    def finalize_move(self, end, king):
        temp_end = end['text']
        temp_start = self.selected_tile['text']
        swap_pieces(self.selected_tile, end)
        if self.in_check(king) or \
            ('K' in end['text'] and self.in_check(end)):  # K in end
                end['text'] = temp_end
                end['image'] = images[temp_end]
                self.selected_tile['text'] = temp_start
                self.selected_tile['image'] = images[temp_start]
                return False
        return True

    def validate_move(self, start, end, row, col, end_row, end_col):
        moved = self.P1_moved if self.white else self.P2_moved
        king = self.K1 if self.white else self.K2
        if p.valid_move(self.board, start, end, row, col,
                        end_row, end_col, self.ep_col, moved):
            if p.is_castle(self.board, start, row, col,
                           end_row, end_col, moved):
                self.execute_castle(start, end)
                return True
            elif p.is_ep(start, end, row, col, end_row, end_col, self.ep_col):
                target = self.board[8 * row + self.ep_col]
                passant_capture(target)
            return self.finalize_move(end, king)

    def game_manager(self, event):
        tile = event.widget
        self.highlight(tile)
        if not (self.selected_tile or p.is_empty(tile)):
            self.selected_tile = tile
        elif self.selected_tile:
            if self.selected_tile is not tile:
                color = ('white' in self.selected_tile['text'])
                if self.white == color:
                    pos = p.get_pos(self.board, self.selected_tile)
                    end = p.get_pos(self.board, tile)
                    if self.validate_move(self.selected_tile, tile, pos[0],
                                          pos[1], end[0], end[1]):
                        self.pawn_conds(tile, pos[0], pos[1], end[0])
                        self.king_conds(tile, pos[0], pos[1])
                        self.white = not self.white
            self.selected_tile = None

    def set_board(self):
        barracks = ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P',
                    'R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for row in range(8):
            for col in range(8):
                rank = side = ''
                if row < 2 or row > 5:
                    side = 'black' if row < 2 else 'white'
                    piece_col = 8 * (row == 0 or row == 7) + col
                    rank = barracks[piece_col]
                floor = 'White' if (row + col) % 2 == 0 else 'Bisque'
                pic = images[side+rank+floor]
                tile = tk.Button(self, image=pic, activebackground='gold',
                                 fg=floor, bg=floor, text=side+rank+floor)
                tile.bind("<Button>", self.game_manager)
                tile.grid(row=row, column=col, ipadx=13, ipady=13)
                self.board.append(tile)
        self.K1 = self.board[60]
        self.K2 = self.board[4]

Game(root).mainloop()
