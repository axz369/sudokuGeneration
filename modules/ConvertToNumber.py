import random
import string


class ConvertToNumber:
    def __init__(self, board, maxNumber):
        self.board = board
        self.maxNumber = maxNumber
        self.charToNumberMap = {}
        self.numberToCharMap = {}
        self.boardConvertedToNumber = [
            [0 for _ in range(maxNumber)] for _ in range(maxNumber)]
        self.convert()

    def convert(self):
        # 数値に変換後の配列を作る
        for row in range(len(self.board)):  # 行の繰り返し
            for col in range(len(self.board[row])):  # 列の繰り返し
                cellValue = self.board[row][col]

                # もし0ならスキップ
                if cellValue == "0":
                    continue

                # もしすでに見つかっている文字であればスキップ
                if cellValue in self.charToNumberMap:
                    continue

                # 左上から順に探索して見つかった順に数値を割り当てる
                self.charToNumberMap[cellValue] = len(self.charToNumberMap) + 1
                self.numberToCharMap[len(self.charToNumberMap)] = cellValue

        # 配列の要素数がmaxNumberに達していないなら別のランダムな文字を割り振る
        if len(self.charToNumberMap) < self.maxNumber:
            # charToNumberMapがmaxNumberの値と同じになるまで繰り返し
            while len(self.charToNumberMap) != self.maxNumber:
                # 既に割り当てられている以外の値をcharToNumberMapに入れていく
                randomUppercaseLetter = random.choice(string.ascii_uppercase)
                if randomUppercaseLetter in self.charToNumberMap:
                    continue
                self.charToNumberMap[randomUppercaseLetter] = len(
                    self.charToNumberMap) + 1
                self.numberToCharMap[len(
                    self.charToNumberMap)] = randomUppercaseLetter

        # 盤面を数値に変換する
        for row in range(len(self.board)):  # 行の繰り返し
            for col in range(len(self.board[row])):  # 列の繰り返し
                cellValue = self.board[row][col]
                if cellValue == "0":
                    self.boardConvertedToNumber[row][col] = 0
                else:
                    self.boardConvertedToNumber[row][col] = self.charToNumberMap[cellValue]

    def getConvertedData(self):
        return {
            "charToNumberMap": self.charToNumberMap,
            "boardConvertedToNumber": self.boardConvertedToNumber
        }

    # 数値から元の文字に変換する
    def convertBack(self, numberBoard):
        boardConvertedToChar = []
        for row in numberBoard:
            convertedRow = []
            for num in row:
                if num == 0:
                    convertedRow.append("0")
                else:
                    convertedRow.append(self.numberToCharMap[num])
            boardConvertedToChar.append(convertedRow)
        return boardConvertedToChar
