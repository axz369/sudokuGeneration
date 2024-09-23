import random
from utility.printBoard import printBoard


class UnifiedNumberOfHints:
    def __init__(self, boards, boardA, targetHintCount):
        self.boards = boards
        self.boardA = boardA
        self.size = len(boards[0])
        self.targetHintCount = targetHintCount

    def countHints(self, board):
        return self.size * self.size - sum(row.count(0) for row in board)

    def unifyHints(self):
        hintCounts = [self.countHints(board) for board in self.boards]
        maxHints = max(hintCounts)
        targetHints = max(maxHints, self.targetHintCount)

        for i, board in enumerate(self.boards):
            currentHintCount = self.countHints(board)
            if currentHintCount < targetHints:
                print(f"\n盤面 {i + 1} のヒント追加処理開始:")
                symmetry_type = ['horizontal', 'vertical', 'diagonal_up', 'diagonal_down'][i]
                self.addHints(board, targetHints - currentHintCount, symmetry_type)

        return self.boards

    def addHints(self, board, hintsToAdd, symmetry_type):
        positions = [(r, c) for r in range(self.size) for c in range(self.size) if board[r][c] == 0]
        random.shuffle(positions)

        totalNumberOfhintsAdded = 0
        isRandomAdditionOrder = 1
        lastAddedPosition = None

        while totalNumberOfhintsAdded < hintsToAdd:
            if not positions:
                break

            if isRandomAdditionOrder:
                r, c = positions.pop()
                board[r][c] = self.boardA[r][c]
                print(f"ランダム追加: 位置 ({c + 1}, {r + 1}) にヒント {board[r][c]} を追加")
                totalNumberOfhintsAdded += 1
                lastAddedPosition = (r, c)
                isRandomAdditionOrder = 0
            else:
                symR, symC = self.getSymmetricPosition(lastAddedPosition[0], lastAddedPosition[1], symmetry_type)
                if (symR, symC) in positions:
                    board[symR][symC] = self.boardA[symR][symC]
                    positions.remove((symR, symC))
                    print(f"対称追加 ({symmetry_type}): 位置 ({symC + 1}, {symR + 1}) にヒント {board[symR][symC]} を追加")
                    totalNumberOfhintsAdded += 1
                isRandomAdditionOrder = 1

            self.printBoardStatus(board)

    def getSymmetricPosition(self, r, c, symmetry_type):
        if symmetry_type == 'horizontal':
            return self.size - 1 - r, c
        elif symmetry_type == 'vertical':
            return r, self.size - 1 - c
        elif symmetry_type == 'diagonal_up':
            return self.size - 1 - c, self.size - 1 - r  # 修正
        elif symmetry_type == 'diagonal_down':
            return c, r

    def printBoardStatus(self, board):
        print("更新後の盤面:")
        printBoard(board)
        print(f"現在のヒント数: {self.countHints(board)}")
        print("--------------------")
