from .countHints import countHints


def printBoard(board):
    size = len(board)
    print(f"ヒント数: {countHints(board)}")

    # 盤面に2桁の数字が含まれているかチェック
    has_two_digit = any(any(isinstance(val, (int, str)) and len(str(val)) > 1 and val != '0' for val in row) for row in board)

    if has_two_digit:
        # 2桁の数字がある場合の処理
        print("+" + "----+" * size)
        for i, row in enumerate(board):
            print("|", end="")
            for val in row:
                if val != 0 and val != '0':
                    print(f" {val:>2} ", end="|")
                else:
                    print("    ", end="|")
            print()
            if i < size - 1:
                print("+" + "----+" * size)
        print("+" + "----+" * size)
    else:
        # 1桁の数字のみの場合の処理
        print("+" + "---+" * size)
        for i, row in enumerate(board):
            print("|", end="")
            for val in row:
                print(f" {val if val != 0 and val != '0' else ' '} ", end="|")
            print()
            if i < size - 1:
                print("+" + "---+" * size)
        print("+" + "---+" * size)
