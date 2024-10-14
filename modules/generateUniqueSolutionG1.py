import time
import gurobipy as gp
import random  # ランダムな選択のために追加

from utility.printBoard import printBoard


def generateUniqueSolutionG1(board, maxSolutions):
    startTime = time.time()
    numberOfHintsAdded = 0  # 追加したヒントの数をカウントする変数
    numberOfGeneratedBoards = []  # 生成された解の数を保存するリスト

    print("唯一解生成開始")
    size = len(board)
    maxSolutions = maxSolutions  # 生成する解の最大数

    # 解盤面を保存するリスト
    solutions = []

    # 111~999の連続した配列 (0-indexedなので実際は[0][0][0]から[8][8][8])
    occurrenceCount = [
        [[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]

    # 数独の制約問題を定義
    model = gp.Model("Sudoku")

    # 出力をオフにする
    model.setParam('OutputFlag', 0)

    # 決定変数の作成
    isValueInCell = model.addVars(range(size), range(size), range(
        1, size + 1), vtype=gp.GRB.BINARY, name="IsValueInCell")

    # 制約条件の追加（同じまま）
    # 1. 各マスには1つの数字のみが入る
    for i in range(size):
        for j in range(size):
            model.addConstr(gp.quicksum(
                isValueInCell[i, j, k] for k in range(1, size + 1)) == 1)

    # 2. 各行には1から9の数字が1つずつ入る
    for i in range(size):
        for k in range(1, size + 1):
            model.addConstr(gp.quicksum(
                isValueInCell[i, j, k] for j in range(size)) == 1)

    # 3. 各列には1から9の数字が1つずつ入る
    for j in range(size):
        for k in range(1, size + 1):
            model.addConstr(gp.quicksum(
                isValueInCell[i, j, k] for i in range(size)) == 1)

    # 4. 各3x3ブロックには1から9の数字が1つずつ入る
    blockSize = int(size ** 0.5)
    for bi in range(blockSize):
        for bj in range(blockSize):
            for k in range(1, size + 1):
                model.addConstr(gp.quicksum(isValueInCell[i, j, k]
                                            for i in range(bi * blockSize, (bi + 1) * blockSize)
                                            for j in range(bj * blockSize, (bj + 1) * blockSize)) == 1)

    # 5. 初期値（ヒント）の設定
    for i in range(size):
        for j in range(size):
            if board[i][j] != 0:
                model.addConstr(isValueInCell[i, j, board[i][j]] == 1)

    # 解の生成フェーズ
    solutionCount = 0
    while solutionCount < maxSolutions:
        currentTime = time.time()
        if currentTime - startTime > 1800:  # 30分（1800秒）を超えた場合
            print("30分を超えたため処理を終了します。")
            return None, numberOfHintsAdded, numberOfGeneratedBoards  # numberOfGeneratedBoardsも返す

        # 問題を解く
        model.setObjective(0, gp.GRB.MINIMIZE)  # ダミーの目的関数
        model.optimize()

        # 新しい解盤面が見つかったら
        if model.status == gp.GRB.OPTIMAL:
            solutionCount += 1
            solution = [[0 for _ in range(size)] for _ in range(size)]
            for i in range(size):
                for j in range(size):
                    for k in range(1, size + 1):
                        if isValueInCell[i, j, k].X == 1:
                            solution[i][j] = k

            # 解盤面を保存
            solutions.append(solution)

            # 111~999の連続した配列に情報を格納
            for i in range(size):
                for j in range(size):
                    value = solution[i][j]
                    occurrenceCount[i][j][value - 1] += 1

            # 新しい解を除外する制約を作成
            model.addConstr(gp.quicksum(isValueInCell[i, j, solution[i][j]] for i in range(
                size) for j in range(size)) <= (size * size) - 1)

            print(f"解 {solutionCount}")
            # printBoard(solution)
        else:
            print("全ての解盤面を生成しました。")
            break

    print(f"生成された解の数: {solutionCount}")
    numberOfGeneratedBoards.append(solutionCount)

    while True:  # occurrenceCountに値が1の要素があるか確認
        foundUnique = False
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    if occurrenceCount[i][j][k] == 1:  # 値が1の要素が見つかった
                        foundUnique = True
                        unique_cell = (i, j)
                        unique_value = k + 1  # インデックスが0から始まるので+1
                        break
                if foundUnique:
                    break
            if foundUnique:
                break

        if foundUnique:
            # 値を確定させる
            i, j = unique_cell
            board[i][j] = unique_value
            numberOfHintsAdded += 1

            print(f"マス ({i + 1}, {j + 1}) に値 {unique_value} を追加しました。")

            # 対応する解盤面を取得
            for solution in solutions:
                if solution[i][j] == unique_value:
                    currentSolution = solution
                    break
            else:
                print("エラー: 対応する解盤面が見つかりませんでした。")
                return None, numberOfHintsAdded, numberOfGeneratedBoards

            # その解盤面からヒントを追加していく
            while True:
                # 現在のヒントで唯一解か確認
                isUnique, foundSolution = checkUniqueSolution(
                    board, size, currentSolution)

                if isUnique:
                    print("唯一解が見つかりました。")
                    print(f"追加したヒントの数: {numberOfHintsAdded}")
                    print("最終的な盤面:")
                    printBoard(board)
                    return board, numberOfHintsAdded, numberOfGeneratedBoards
                else:
                    # ヒントを追加する
                    empty_positions = [(x, y) for x in range(size)
                                       for y in range(size) if board[x][y] == 0]
                    if not empty_positions:
                        print("エラー: ヒントを追加できるマスがありません。")
                        return None, numberOfHintsAdded, numberOfGeneratedBoards

                    # ランダムに位置を選択
                    random.shuffle(empty_positions)
                    x, y = empty_positions[0]

                    board[x][y] = currentSolution[x][y]
                    numberOfHintsAdded += 1
                    print(
                        f"マス ({x + 1}, {y + 1}) に値 {currentSolution[x][y]} を追加しました。")

                # 時間制限のチェック
                currentTime = time.time()
                if currentTime - startTime > 1800:  # 30分（1800秒）を超えた場合
                    print("30分を超えたため処理を終了します。")
                    return None, numberOfHintsAdded, numberOfGeneratedBoards  # numberOfGeneratedBoardsも返す
        else:
            # 配列の中で1以上かつ最小の値を確定
            minCount = float('inf')
            minCell = None
            minValue = None
            for i in range(size):
                for j in range(size):
                    if board[i][j] == 0:  # 既にヒントとして確定していないセルのみ
                        for k in range(size):
                            count = occurrenceCount[i][j][k]
                            if 0 < count < minCount:
                                minCount = count
                                minCell = (i, j)
                                minValue = k + 1  # インデックス調整

            if minCell is None:
                print("エラー: 最小出現回数のセルが見つかりませんでした。")
                return None, numberOfHintsAdded, numberOfGeneratedBoards

            # 確定したマスから残りの可能性の盤面のみ抜き出す
            board[minCell[0]][minCell[1]] = minValue
            numberOfHintsAdded += 1
            print(
                f"マス ({minCell[0] + 1}, {minCell[1] + 1}) に値 {minValue} を追加しました。")

    # numberOfGeneratedBoardsも返す
    return board, numberOfHintsAdded, numberOfGeneratedBoards


def checkUniqueSolution(board, size, currentSolution):  # 唯一解になっているかチェック
    # 一時的なモデルを作成
    model = gp.Model("CheckUniqueSolution")

    # 決定変数の作成
    isValueInCell = model.addVars(range(size), range(size), range(
        1, size + 1), vtype=gp.GRB.BINARY, name="IsValueInCell")

    # 制約条件の追加
    for i in range(size):
        for j in range(size):
            model.addConstr(gp.quicksum(
                isValueInCell[i, j, k] for k in range(1, size + 1)) == 1)

    for i in range(size):
        for k in range(1, size + 1):
            model.addConstr(gp.quicksum(
                isValueInCell[i, j, k] for j in range(size)) == 1)

    for j in range(size):
        for k in range(1, size + 1):
            model.addConstr(gp.quicksum(
                isValueInCell[i, j, k] for i in range(size)) == 1)

    blockSize = int(size ** 0.5)
    for bi in range(blockSize):
        for bj in range(blockSize):
            for k in range(1, size + 1):
                model.addConstr(gp.quicksum(isValueInCell[i, j, k]
                                            for i in range(bi * blockSize, (bi + 1) * blockSize)
                                            for j in range(bj * blockSize, (bj + 1) * blockSize)) == 1)

    for i in range(size):
        for j in range(size):
            if board[i][j] != 0:
                model.addConstr(isValueInCell[i, j, board[i][j]] == 1)

    # 解の探索
    model.setObjective(0, gp.GRB.MINIMIZE)  # ダミーの目的関数
    model.optimize()

    if model.status == gp.GRB.OPTIMAL:
        # 解が見つかった場合、さらに解があるか確認
        model.addConstr(gp.quicksum(isValueInCell[i, j, currentSolution[i][j]] for i in range(
            size) for j in range(size)) <= (size * size) - 1)
        model.optimize()
        if model.status == gp.GRB.OPTIMAL:
            return False, model  # 複数の解がある
        else:
            return True, model  # ユニークな解
    else:
        return False, model  # 解が見つからない場合
