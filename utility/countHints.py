def countHints(board):
    return sum(1 for row in board for cell in row if cell != 0 and cell != '0')
