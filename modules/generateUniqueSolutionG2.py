import time
import gurobipy as gp
from gurobipy import GRB
import random  # ランダムな選択のために追加

from utility.printBoard import printBoard


def generateUniqueSolutionG2(board, maxSolutions, LIMIT_TIME):
    startTime = time.time()
    numberOfHintsAdded = 0  # 追加したヒントの数をカウントする変数
    numberOfGeneratedBoards = []  # 生成された解の数を保存するリスト

    print("唯一解生成開始")
    size = len(board)
    maxSolutions = maxSolutions  # 生成する解の最大数

    # 解盤面を保存するリスト
    solutions = []

    # occurrenceCount 配列の初期化
    occurrenceCount = [
        [[0 for _ in range(size)] for _ in range(size)] for _ in range(size)
    ]

    # Gurobiモデルの作成
    model = gp.Model("Sudoku")
    model.Params.LogToConsole = 0  # ソルバーの出力を抑制

    # 決定変数の作成
    isValueInCell = model.addVars(
        range(size), range(size), range(1, size + 1),
        vtype=GRB.BINARY, name="IsValueInCell"
    )

    # 制約条件の追加
    # 1. 各マスには1つの数字のみが入る
    for i in range(size):
        for j in range(size):
            model.addConstr(
                gp.quicksum(isValueInCell[i, j, k] for k in range(1, size + 1)) == 1
            )

    # 2. 各行には1から9の数字が1つずつ入る
    for i in range(size):
        for k in range(1, size + 1):
            model.addConstr(
                gp.quicksum(isValueInCell[i, j, k] for j in range(size)) == 1
            )

    # 3. 各列には1から9の数字が1つずつ入る
    for j in range(size):
        for k in range(1, size + 1):
            model.addConstr(
                gp.quicksum(isValueInCell[i, j, k] for i in range(size)) == 1
            )

    # 4. 各3x3ブロックには1から9の数字が1つずつ入る
    blockSize = int(size ** 0.5)
    for bi in range(blockSize):
        for bj in range(blockSize):
            for k in range(1, size + 1):
                model.addConstr(
                    gp.quicksum(
                        isValueInCell[i, j, k]
                        for i in range(bi * blockSize, (bi + 1) * blockSize)
                        for j in range(bj * blockSize, (bj + 1) * blockSize)
                    ) == 1
                )

    # 5. 初期値（ヒント）の設定
    for i in range(size):
        for j in range(size):
            if board[i][j] != 0:
                model.addConstr(isValueInCell[i, j, board[i][j]] == 1)

    # 解の生成フェーズ
    solutionCount = 0
    while solutionCount < maxSolutions:
        currentTime = time.time()
        if currentTime - startTime > LIMIT_TIME:
            print("30分を超えたため処理を終了します。")
            return None, numberOfHintsAdded, numberOfGeneratedBoards, solutionCount

        # 問題を解く
        model.optimize()

        # 新しい解盤面が見つかったら
        if model.Status == GRB.OPTIMAL:
            solutionCount += 1
            solution = [[0 for _ in range(size)] for _ in range(size)]
            for i in range(size):
                for j in range(size):
                    for k in range(1, size + 1):
                        if isValueInCell[i, j, k].X > 0.5:
                            solution[i][j] = k

            # 解盤面を保存
            solutions.append(solution)

            # occurrenceCountに情報を格納
            for i in range(size):
                for j in range(size):
                    value = solution[i][j]
                    occurrenceCount[i][j][value - 1] += 1

            # 新しい解を除外する制約を作成
            model.addConstr(
                gp.quicksum(
                    isValueInCell[i, j, solution[i][j]] for i in range(size) for j in range(size)
                ) <= (size * size) - 1
            )

            print(f"解 {solutionCount}")
            # printBoard(solution)
        else:
            print("全ての解盤面を生成しました。")
            break

    print(f"生成された解の数: {solutionCount}")
    numberOfGeneratedBoards.append(solutionCount)

    # 唯一解を求めるループ
    while True:
        foundUnique = False
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    if occurrenceCount[i][j][k] == 1:
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
                return None, numberOfHintsAdded, numberOfGeneratedBoards, solutionCount

            # その解盤面からヒントを追加していく
            while True:
                # 現在のヒントで唯一解か確認
                isUnique, foundSolution = checkUniqueSolution(board, size, currentSolution)
                if isUnique:
                    print("唯一解が見つかりました。")
                    print(f"追加したヒントの数: {numberOfHintsAdded}")
                    print("最終的な盤面:")
                    printBoard(board)
                    return board, currentSolution, numberOfHintsAdded, numberOfGeneratedBoards
                else:
                    # ヒントを追加する
                    empty_positions = [(x, y) for x in range(size) for y in range(size) if board[x][y] == 0]
                    if not empty_positions:
                        print("エラー: ヒントを追加できるマスがありません。")
                        return None, numberOfHintsAdded, numberOfGeneratedBoards, solutionCount

                    # ランダムに位置を選択
                    random.shuffle(empty_positions)
                    x, y = empty_positions[0]

                    board[x][y] = currentSolution[x][y]
                    numberOfHintsAdded += 1
                    print(f"マス ({x + 1}, {y + 1}) に値 {currentSolution[x][y]} を追加しました。")

                # 時間制限のチェック
                currentTime = time.time()
                if currentTime - startTime > LIMIT_TIME: 
                    print("30分を超えたため処理を終了します。")
                    return None, numberOfHintsAdded, numberOfGeneratedBoards, solutionCount
        else:
            # occurrenceCountの中で最小の正の値を見つける
            minCount = float('inf')
            minCell = None
            minValue = None
            for i in range(size):
                for j in range(size):
                    if board[i][j] == 0:
                        for k in range(size):
                            count = occurrenceCount[i][j][k]
                            if 0 < count < minCount:
                                minCount = count
                                minCell = (i, j)
                                minValue = k + 1

            if minCell is None:
                print("エラー: 最小出現回数のセルが見つかりませんでした。")
                return None, numberOfHintsAdded, numberOfGeneratedBoards, solutionCount

            # 値を確定させる
            i, j = minCell
            board[i][j] = minValue
            numberOfHintsAdded += 1

            print(f"マス ({i + 1}, {j + 1}) に値 {minValue} を追加しました。")
            print(f"現在のヒント数: {numberOfHintsAdded}")

            # 追加したヒントに一致する解盤面のみを残す
            remainingSolutions = []
            for solution in solutions:
                if solution[i][j] == minValue:
                    remainingSolutions.append(solution)

            if not remainingSolutions:
                print("エラー: 残った解盤面がありません。")
                return None, numberOfHintsAdded, numberOfGeneratedBoards, solutionCount

            # occurrenceCountを再計算
            occurrenceCount = [
                [[0 for _ in range(size)] for _ in range(size)] for _ in range(size)
            ]
            for solution in remainingSolutions:
                for i in range(size):
                    for j in range(size):
                        value = solution[i][j]
                        occurrenceCount[i][j][value - 1] += 1

            # solutionsリストを更新
            solutions = remainingSolutions

            # 生成された解の数を更新
            solutionCount = len(solutions)
            numberOfGeneratedBoards.append(solutionCount)

            print(f"残りの解の数: {solutionCount}")

        # 時間制限のチェック
        currentTime = time.time()
        if currentTime - startTime > LIMIT_TIME:
            print("30分を超えたため処理を終了します。")
            return None, numberOfHintsAdded, numberOfGeneratedBoards, solutionCount


def checkUniqueSolution(board, size, currentSolution):
    # Gurobiモデルの作成
    model = gp.Model("SudokuCheck")
    model.Params.LogToConsole = 0  # ソルバーの出力を抑制

    # 決定変数の作成
    isValueInCell = model.addVars(
        range(size), range(size), range(1, size + 1),
        vtype=GRB.BINARY, name="IsValueInCell"
    )

    # 制約条件の追加
    # 1. 各マスには1つの数字のみが入る
    for i in range(size):
        for j in range(size):
            model.addConstr(
                gp.quicksum(isValueInCell[i, j, k] for k in range(1, size + 1)) == 1
            )

    # 2. 各行には1から9の数字が1つずつ入る
    for i in range(size):
        for k in range(1, size + 1):
            model.addConstr(
                gp.quicksum(isValueInCell[i, j, k] for j in range(size)) == 1
            )

    # 3. 各列には1から9の数字が1つずつ入る
    for j in range(size):
        for k in range(1, size + 1):
            model.addConstr(
                gp.quicksum(isValueInCell[i, j, k] for i in range(size)) == 1
            )

    # 4. 各ブロックには1から9の数字が1つずつ入る
    blockSize = int(size ** 0.5)
    for bi in range(blockSize):
        for bj in range(blockSize):
            for k in range(1, size + 1):
                model.addConstr(
                    gp.quicksum(
                        isValueInCell[i, j, k]
                        for i in range(bi * blockSize, (bi + 1) * blockSize)
                        for j in range(bj * blockSize, (bj + 1) * blockSize)
                    ) == 1
                )

    # 現在のヒントの設定
    for i in range(size):
        for j in range(size):
            if board[i][j] != 0:
                model.addConstr(isValueInCell[i, j, board[i][j]] == 1)

    # 解の探索（最大2つまで）
    solutions_found = 0
    foundSolution = None
    while solutions_found < 2:
        model.optimize()

        if model.Status == GRB.OPTIMAL:
            solutions_found += 1
            solution = [[0 for _ in range(size)] for _ in range(size)]
            for i in range(size):
                for j in range(size):
                    for k in range(1, size + 1):
                        if isValueInCell[i, j, k].X > 0.5:
                            solution[i][j] = k

            if foundSolution is None:
                foundSolution = solution
            else:
                if solution != foundSolution:
                    return False, None  # 複数の異なる解が見つかった

            # 見つかった解を除外する制約を追加
            model.addConstr(
                gp.quicksum(
                    isValueInCell[i, j, solution[i][j]] for i in range(size) for j in range(size)
                ) <= (size * size) - 1
            )
        else:
            break

    if solutions_found == 1 and foundSolution == currentSolution:
        return True, foundSolution
    else:
        return False, None
