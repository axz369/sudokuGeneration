import time
import pulp
import random


from utility.printBoard import printBoard  # 必要に応じて


def generateUniqueSolution2(board, maxSolutions):
    startTime = time.time()
    numberOfHintsAdded = 0  # 追加したヒントの数をカウントする変数
    numberOfGeneratedBoards = []  # 各ステップで生成された解の数を保存するリスト

    print("唯一解生成開始")
    size = len(board)

    # 解盤面を保存するリスト
    solutions = []

    # 数独の制約問題を関数を使って定義
    problem, isValueInCell = defineSudokuProblem(board, size)

    # 除外した解の制約を保持するリスト
    excluded_solutions_constraints = []

    while True:
        # ステップ① 解盤面を最大 maxSolutions 個生成
        currentTime = time.time()
        if currentTime - startTime > 1800:  # 30分を超えた場合
            print("30分を超えたため処理を終了します。")
            return None, None, numberOfHintsAdded, numberOfGeneratedBoards

        solutions = []  # 生成された解を保存するリストをリセット
        problem, isValueInCell = defineSudokuProblem(board, size)  # 問題を再定義
        excluded_solutions_constraints = []  # 除外制約もリセット

        while len(solutions) < maxSolutions:
            # 問題を解く
            status = problem.solve(pulp.PULP_CBC_CMD(msg=False))

            if pulp.LpStatus[status] == 'Optimal':
                # ステップ② 解盤面の情報を配列に保存
                solution = extractSolution(isValueInCell, size)
                solutions.append(solution)

                # ステップ③ 解盤面の除外の制約を追加
                exclude_constraint = pulp.lpSum([isValueInCell[i][j][solution[i][j]] for i in range(size)
                                                 for j in range(size)]) <= (size * size) - 1
                problem += exclude_constraint
                excluded_solutions_constraints.append(exclude_constraint)

                # 進捗の表示
                print(f"現在の解の数: {len(solutions)}")

                continue  # 解の上限に達するまで繰り返す
            else:
                print("全ての解盤面を生成しました。")
                break  # 解が見つからなくなったらループを終了

        numberOfGeneratedBoards.append(len(solutions))
        print(f"生成された解の数: {len(solutions)}")

        # ステップ⑤ 生成できたのが1盤面だけ？
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
        else:
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

            # 投票配列と制約をリセット
            occurrenceCount = [
                [[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]
            # problem, isValueInCell = defineSudokuProblem(board, size)
            # 除外制約もリセット（新たに解を生成するため）

            # ステップ⑨ 最小の値が2以上か確認
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

                # フィルタリング後の解盤面を表示（ここが追加されたコードです）
                print("フィルタリング後の解盤面:")
                for idx, solution in enumerate(solutions):
                    print(f"解 {idx + 1}:")
                    printBoard(solution)

                # 投票配列へ格納して制約を追加
                occurrenceCount = calculateOccurrenceCount(solutions, size)
                problem += isValueInCell[i][j][minValue] == 1
                # 除外した解の制約を再度追加
                for solution in solutions:
                    exclude_constraint = pulp.lpSum([isValueInCell[i][j][solution[i][j]] for i in range(size)
                                                     for j in range(size)]) <= (size * size) - 1
                    problem += exclude_constraint
                    excluded_solutions_constraints.append(exclude_constraint)
            else:
                print("最小の値が1")
                # ステップ①へ戻る（解盤面と制約をリセットして再度解を生成）
                continue

            # 時間制限のチェック
            currentTime = time.time()
            if currentTime - startTime > 1800:  # 30分を超えた場合
                print("30分を超えたため処理を終了します。")
                return None, None, numberOfHintsAdded, numberOfGeneratedBoards

            # 再度解を生成するためにループの最初に戻る
            continue

    # 万が一ここに到達した場合
    return None, None, numberOfHintsAdded, numberOfGeneratedBoards


def defineSudokuProblem(board, size):
    problem = pulp.LpProblem("Sudoku", pulp.LpMinimize)

    # 決定変数の作成
    isValueInCell = pulp.LpVariable.dicts("IsValueInCell",
                                          (range(size), range(size),
                                           range(1, size + 1)),
                                          cat='Binary')

    # 制約条件の追加
    # 1. 各マスには1つの数字のみが入る
    for i in range(size):
        for j in range(size):
            problem += pulp.lpSum([isValueInCell[i][j][k]
                                   for k in range(1, size + 1)]) == 1

    # 2. 各行には1からサイズの数字が1つずつ入る
    for i in range(size):
        for k in range(1, size + 1):
            problem += pulp.lpSum([isValueInCell[i][j][k]
                                   for j in range(size)]) == 1

    # 3. 各列には1からサイズの数字が1つずつ入る
    for j in range(size):
        for k in range(1, size + 1):
            problem += pulp.lpSum([isValueInCell[i][j][k]
                                   for i in range(size)]) == 1

    # 4. 各ブロックには1からサイズの数字が1つずつ入る
    blockSize = int(size ** 0.5)
    for bi in range(blockSize):
        for bj in range(blockSize):
            for k in range(1, size + 1):
                problem += pulp.lpSum([isValueInCell[i][j][k]
                                       for i in range(bi * blockSize, (bi + 1) * blockSize)
                                       for j in range(bj * blockSize, (bj + 1) * blockSize)]) == 1

    # 5. 初期値（ヒント）の設定
    for i in range(size):
        for j in range(size):
            if board[i][j] != 0:
                problem += isValueInCell[i][j][board[i][j]] == 1

    return problem, isValueInCell


# ステップ② 解盤面の情報を配列に保存
def extractSolution(isValueInCell, size):
    solution = [[0 for _ in range(size)] for _ in range(size)]
    for i in range(size):
        for j in range(size):
            for k in range(1, size + 1):
                if pulp.value(isValueInCell[i][j][k]) == 1:
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
