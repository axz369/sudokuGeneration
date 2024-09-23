class AddHintToLineSymmetry:
    def __init__(self, board, boardA):
        self.board = board
        self.boardA = boardA  # 解盤面Aを追加
        self.size = len(board)
        self.possibleValues = list(range(1, self.size + 1))
        self.maxAttempts = 1000  # 再トライの最大回数を設定

    def addSymmetries(self):
        # 4つの対称性に基づいた盤面をリストで返却
        boards = []
        boards.append(self.addHorizontalSymmetry())
        boards.append(self.addVerticalSymmetry())
        boards.append(self.addDiagonalSymmetry())
        boards.append(self.addAntiDiagonalSymmetry())
        return boards

    def addHorizontalSymmetry(self):  # 横対称
        board_copy = [row[:] for row in self.board]  # 現在の盤面のコピーを作成
        for row in range(self.size):
            for col in range(self.size):
                oppositeRow = self.size - 1 - row  # 下側の対称位置を計算
                self.addToOppositePosition(board_copy, row, col, oppositeRow, col)
        return board_copy

    def addVerticalSymmetry(self):  # 縦対称
        board_copy = [row[:] for row in self.board]  # 現在の盤面のコピーを作成
        for row in range(self.size):
            for col in range(self.size):
                oppositeCol = self.size - 1 - col  # 右側の対称位置を計算
                self.addToOppositePosition(board_copy, row, col, row, oppositeCol)
        return board_copy

    def addDiagonalSymmetry(self):  # 右上がり
        board_copy = [row[:] for row in self.board]  # 現在の盤面のコピーを作成
        for row in range(self.size):
            for col in range(self.size):
                oppositeRow = self.size - 1 - col  # 対称位置の行を計算
                oppositeCol = self.size - 1 - row  # 対称位置の列を計算
                self.addToOppositePosition(board_copy, row, col, oppositeRow, oppositeCol)
        return board_copy

    def addAntiDiagonalSymmetry(self):  # 右下がり
        board_copy = [row[:] for row in self.board]  # 現在の盤面のコピーを作成
        for row in range(self.size):
            for col in range(self.size):
                oppositeRow = col  # 対称位置の行を計算
                oppositeCol = row  # 対称位置の列を計算
                self.addToOppositePosition(board_copy, row, col, oppositeRow, oppositeCol)
        return board_copy

    def addToOppositePosition(self, board_copy, row, col, oppositeRow, oppositeCol):
        # 現在の位置に値があり、かつ対称位置に値が入っていない場合
        if board_copy[row][col] != 0 and board_copy[oppositeRow][oppositeCol] == 0:
            # 解盤面Aの値を対称位置に配置
            board_copy[oppositeRow][oppositeCol] = self.boardA[oppositeRow][oppositeCol]

    def getSymmetricBoards(self):
        # 4つの対称性に基づいた盤面を返す
        return self.addSymmetries()
