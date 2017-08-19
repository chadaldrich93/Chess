def shift(predicate):
    return 1 if predicate else -1


def get_pos(board, tile): # position -> row, column
    index = board.index(tile)
    row = index // 8
    col = index % 8
    return [row, col]


def is_empty(button):  # Button with piece has name/color/tile color in text
    return len(button['text']) < 7 # shorter text holds tile color only


def are_enemies(start, end):
    if not (is_empty(start) or is_empty(end)):
        return ('black' in start['text']) != ('black' in end['text'])


def P_attack(start, end, row, col, end_row, end_col, ep): # ep -> en passant
    row_shift = shift('black' in start['text'])
    if are_enemies(start, end) or ep:
        return abs(col - end_col) == 1 and end_row - row == row_shift


def P_move(pawn, row, col, end_row, end_col):
    if ('P' in pawn['text']) and col == end_col:
        return (end_row - row == shift('black' in pawn['text']) or
                ((row == 1 or row == 6) and abs(row - end_row) == 2))


def R_move(row, col, end_row, end_col):
    return row == end_row or col == end_col


def N_move(row, col, end_row, end_col):
    dr = abs(row - end_row) # delta row
    dc = abs(col - end_col) # delta column
    return (dr == 2 and dc == 1) or (dr == 1 and dc == 2)


def B_move(row, col, end_row, end_col):
    return abs(row - end_row) == abs(col - end_col)


def Q_move(row, col, end_row, end_col):
    return R_move(row,col,end_row,end_col) or B_move(row,col,end_row,end_col)


def K_move(row, col, end_row, end_col):
    return abs(row - end_row) <= 1 and abs(col - end_col) <= 1


def attack(board, start, end, row, col, end_row, end_col):
    rank = start['text'][5]
    if free_file(board, rank, start, end, row, col, end_row, end_col):
        if rank == 'P':
            return P_attack(start, end, row, col, end_row, end_col, False)
        return eval(rank + "_move(row, col, end_row, end_col)")


def free_file(board, rank, start, end, row, col, end_row, end_col):
    if rank == 'N':
        return is_empty(end) or are_enemies(start, end)
    if rank == 'K' and col - end_col == 2: # queenside castle
        end_col -= 1
    if rank == 'P' and col == end_col and not is_empty(end):
        return False
    while not (row == end_row and col == end_col):
        if row != end_row:
            row += shift(row < end_row)
        if col != end_col:
            col += shift(col < end_col)
        current = board[row * 8 + col]
        if not is_empty(current):
            return row == end_row and col == end_col and \
                   are_enemies(start, current)
    return True


def in_check(board, king, king_row, king_col):
    for tile in board:
        pos = get_pos(board, tile)
        if are_enemies(tile, king) and \
           attack(board, tile, king, pos[0], pos[1], king_row, king_col):
            return True


def is_castle(board, king, king_row, king_col, end_row, end_col, moved):
    step = shift(end_col > king_col)
    rook_index = end_col + step if step > 0 else end_col + 2 * step
    rook = board[rook_index]
    index = shift(end_col > king_col) + 1
    if (('K' in king['text']) and ('R' in rook['text']) and
         abs(end_col - king_col) == 2 and king_row == end_row and
         not (moved[1] or moved[index])):  # 1 -> king
            for num in range(3):
                if in_check(board, king, king_row, king_col + num * step):
                    return False
            return True


def is_ep(pawn, end, row, col, end_row, end_col, ep_col): # en passant
    ep_row = 4 if 'black' in pawn['text'] else 3
    if 'P' in pawn['text'] and end_col == ep_col and row == ep_row:
        return P_attack(pawn, end, row, col, end_row, end_col, True)


def valid_move(board, start, end, row, col, end_row, end_col, ep_col, moved):
    rank = start['text'][5]
    if ((attack(board, start, end, row, col, end_row, end_col)       or
        P_move(start, row, col, end_row, end_col)                   or
        is_ep(start, end, row, col, end_row, end_col, ep_col)       or
        is_castle(board, start, row, col, end_row, end_col, moved)) and
            free_file(board, rank, start, end, row, col, end_row, end_col)):
            return True
