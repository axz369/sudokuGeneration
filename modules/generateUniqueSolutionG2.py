import time
import gurobipy as gp
from gurobipy import GRB
import random

from utility.printBoard import printBoard  # 必要に応じて


def generateUniqueSolutionG2(board, maxSolutions):
    startTime = time.time()
    numberOfHintsAdded = 0  # 追加したヒントの数をカウントする変数
    numberOfGeneratedBoards = []  # 各ステップで生成された解の数を保存するリスト

    print("唯一解生成開始")
    size = len(board)

    while True:
        currentTime = time.time()
        if currentTime - startTime > 1800:  # 30 分を超えた場合
            print("30 分を超えたため処理を終了します。")
            return None, None, numberOfHintsAdded, numberOfGeneratedBoards

        # ステップ① 解盤面を最大 maxSolutions 個生成
        # 問題を再定義
        model, isValueInCell = defineSudokuProblem(board, size)

        solutions = []  # 生成された解を保存するリスト

        while len(solutions) < maxSolutions:
            # 問題を解く
            model.optimize()
            if model.Status == GRB.OPTIMAL:
                # ステップ② 解盤面の情報を配列に保存
                solution = extractSolution(isValueInCell, size)
                solutions.append(solution)

                # ステップ③ 解盤面の除外の制約を追加
                exclude_constraint = gp.quicksum(
                    isValueInCell[i, j, solution[i][j]] for i in range(size) for j in range(size)
                ) <= (size * size) - 1
                model.addConstr(exclude_constraint)

                # 進捗の表示
                print(f"解 {len(solutions)}")
            else:
                print("全ての解盤面を生成しました。")
                break  # 解が見つからなくなったらループを終了

        numberOfGeneratedBoards.append(len(solutions))
        print(f"生成された解の数: {len(solutions)}")

        # ステップ⑤ 生成できたのが 1 盤面だけ？
        if len(solutions) == 1:
            print("唯一解が見つかりました。")
            unique_solution = solutions[0]  # 解盤面を保存

            # 問題盤面（ヒント付きの盤面）をコピーして返す
            problem_board = [row[:] for row in board]

            return problem_board, unique_solution, numberOfHintsAdded, numberOfGeneratedBoards
        elif len(solutions) == 0:
            print("エラー: 解が存在しません。追加したヒントを元に戻します。")
            # 最後に追加したヒントを取り消す
            if numberOfHintsAdded == 0:
                print("これ以上ヒントを取り消せません。唯一解の生成に失敗しました。")
                return None, None, numberOfHintsAdded, numberOfGeneratedBoards
            i, j = lastHintPosition
            board[i][j] = 0
            numberOfHintsAdded -= 1
            # ヒントを戻した後、再度解を探索
            continue
        else:  # 生成できた盤面が2以上(次回ループで再利用する盤面がある)
            # ステップ⑥ 投票配列に格納
            occurrenceCount = calculateOccurrenceCount(solutions, size)

            # ステップ⑦ 投票配列の最小の位置にヒント追加
            minCount, minCell, minValue = findMinOccurrence(
                occurrenceCount, board, size)
            if minCell is None:
                print("エラー: 最小出現回数のセルが見つかりませんでした。")
                return None, None, numberOfHintsAdded, numberOfGeneratedBoards

            i, j = minCell
            board[i][j] = minValue
            lastHintPosition = (i, j)  # 最後に追加したヒントの位置を記録
            numberOfHintsAdded += 1
            print(f"マス ({i + 1}, {j + 1}) に値 {minValue} を追加しました。")

            # ステップ⑧ 投票配列と今までの制約をリセット
            occurrenceCount = None  # 投票配列をリセット
            model = None  # 問題をリセット

            # ステップ⑨ 最小の値が 2 以上か確認
            if minCount >= 2:
                # ステップ⑩ フィルタリング処理を行う
                solutions = filterSolutionsByHint(solutions, i, j, minValue)
                print(f"ヒントを追加した後の残りの解の数: {len(solutions)}")

                if len(solutions) == 0:
                    print("エラー: フィルタリング後に解が存在しません。")
                    # ヒントを取り消す
                    board[i][j] = 0
                    numberOfHintsAdded -= 1
                    continue  # 再度ループの最初から

                # フィルタリング後の解盤面を表示
                print("フィルタリング後の解盤面:")
                for idx, solution in enumerate(solutions):
                    print(f"解 {idx + 1}:")
                    printBoard(solution)

                # 問題を再定義し、フィルタリング後の解を除外する制約を追加
                model, isValueInCell = defineSudokuProblem(board, size)
                constraint_counter = 1  # 制約式の番号カウンター
                for solution in solutions:
                    exclude_constraint = gp.quicksum(
                        isValueInCell[i, j, solution[i][j]] for i in range(size) for j in range(size)
                    ) <= (size * size) - 1
                    model.addConstr(exclude_constraint)

                    # 制約式の表示
                    print(f"{constraint_counter}つ目の制約式:")
                    print(exclude_constraint)
                    constraint_counter += 1

                continue  # ステップ①へ戻る
            else:
                print("最小の値が 1")
                # ステップ①へ戻る（再度解を生成）
                continue

    # 万が一ここに到達した場合
    return None, None, numberOfHintsAdded, numberOfGeneratedBoards


def defineSudokuProblem(board, size):
    model = gp.Model("Sudoku")
    model.Params.LogToConsole = 0  # ソルバーの出力を抑制

    # 決定変数の作成
    isValueInCell = model.addVars(
        range(size), range(size), range(1, size + 1),
        vtype=GRB.BINARY, name="IsValueInCell"
    )

    # 制約条件の追加
    # 1. 各マスには 1 つの数字のみが入る
    for i in range(size):
        for j in range(size):
            model.addConstr(
                gp.quicksum(isValueInCell[i, j, k] for k in range(1, size + 1)) == 1
            )

    # 2. 各行には 1 からサイズの数字が 1 つずつ入る
    for i in range(size):
        for k in range(1, size + 1):
            model.addConstr(
                gp.quicksum(isValueInCell[i, j, k] for j in range(size)) == 1
            )

    # 3. 各列には 1 からサイズの数字が 1 つずつ入る
    for j in range(size):
        for k in range(1, size + 1):
            model.addConstr(
                gp.quicksum(isValueInCell[i, j, k] for i in range(size)) == 1
            )

    # 4. 各ブロックには 1 からサイズの数字が 1 つずつ入る
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

    return model, isValueInCell


# ステップ② 解盤面の情報を配列に保存
def extractSolution(isValueInCell, size):
    solution = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(1, size + 1):
                if isValueInCell[i, j, k].X > 0.5:
                    solution[i][j] = k
                    break
    return solution


def calculateOccurrenceCount(solutions, size):
    occurrenceCount = [
        [[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]
    for solution in solutions:
        for i in range(size):
            for j in range(size):
                value = solution[i][j]
                occurrenceCount[i][j][value - 1] += 1
    return occurrenceCount


# 投票配列の最小位置と最小値を特定
def findMinOccurrence(occurrenceCount, board, size):
    minCount = float('inf')
    minCells = []
    for i in range(size):
        for j in range(size):
            if board[i][j] == 0:  # 空のセルのみ
                for k in range(size):
                    count = occurrenceCount[i][j][k]
                    if 0 < count < minCount:
                        minCount = count
                        minCells = [(i, j, k + 1)]
                    elif count == minCount:
                        minCells.append((i, j, k + 1))
    if minCells:
        # ランダムに一つ選択
        i, j, minValue = random.choice(minCells)
        return minCount, (i, j), minValue
    else:
        return None, None, None


# 解盤面から現在のヒントと矛盾しない解盤面だけを残すフィルタリング
def filterSolutionsByHint(solutions, i, j, minValue):
    filteredSolutions = []
    for solution in solutions:
        if solution[i][j] == minValue:
            filteredSolutions.append(solution)
    return filteredSolutions
