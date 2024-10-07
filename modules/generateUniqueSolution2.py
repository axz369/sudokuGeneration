import time
import pulp
import random  # ランダムな選択のために追加

from utility.printBoard import printBoard  # 必要に応じて


def generateUniqueSolution2(board, maxSolutions):
    startTime = time.time()
    numberOfHintsAdded = 0  # 追加したヒントの数をカウントする変数
    numberOfGeneratedBoards = []  # 各ステップで生成された解の数を保存するリスト

    print("唯一解生成開始")
    size = len(board)
    maxSolutions = maxSolutions  # 生成する解の最大数

    # 解盤面を保存するリスト
    solutions = []

    # 投票配列の初期化
    occurrenceCount = [
        [[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]

    # 数独の制約問題を定義
    problem, isValueInCell = defineSudokuProblem(board, size)

    # 除外した解の制約を保持するリスト
    excluded_solutions_constraints = []

    while True:
        # ステップ① 解盤面を一つ生成
        currentTime = time.time()
        if currentTime - startTime > 1800:  # 30分を超えた場合
            print("30分を超えたため処理を終了します。")
            return None, numberOfHintsAdded, numberOfGeneratedBoards

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

            print(f"\n解が見つかりました。現在の解の数: {len(solutions)}")

            # ステップ④ 上限まで生成した or すべて出し切った
            if len(solutions) >= maxSolutions:
                numberOfGeneratedBoards.append(len(solutions))
                print(f"生成された解の数: {len(solutions)}")
                break  # ループを終了
            else:
                continue  # ステップ①へ戻る
        else:
            print("全ての解盤面を生成しました。")
            numberOfGeneratedBoards.append(len(solutions))
            print(f"生成された解の数: {len(solutions)}")
            break  # ループを終了

    while True:
        # ステップ⑤ 生成できたのが1盤面だけ？
        if len(solutions) == 1:
            print("唯一解が見つかりました。")
            board = solutions[0]
            print(f"追加したヒントの数: {numberOfHintsAdded}")
            print("最終的な盤面:")
            printBoard(board)
            return board, numberOfHintsAdded, numberOfGeneratedBoards
        elif len(solutions) == 0:
            print("エラー: 解が存在しません。")
            return None, numberOfHintsAdded, numberOfGeneratedBoards
        else:
            # ステップ⑥ 投票配列に格納
            occurrenceCount = calculateOccurrenceCount(solutions, size)

            # ステップ⑦ 投票配列の最小の位置にヒント追加
            minCount, minCell, minValue = findMinOccurrence(
                occurrenceCount, board, size)
            if minCell is None:
                print("エラー: 最小出現回数のセルが見つかりませんでした。")
                return None, numberOfHintsAdded, numberOfGeneratedBoards

            i, j = minCell
            board[i][j] = minValue
            numberOfHintsAdded += 1
            print(f"マス ({i + 1}, {j + 1}) に値 {minValue} を追加しました。")

            # ステップ⑧ 投票配列と今までの制約をリセット
            occurrenceCount = [
                [[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]
            problem, isValueInCell = defineSudokuProblem(board, size)

            # 除外した解の制約を再度追加
            for constraint in excluded_solutions_constraints:
                problem += constraint

            # ステップ⑨ 最小の値が2以上か確認
            if minCount >= 2:
                # ステップ⑩ 最小のヒント位置に当てはまる盤面を探して、その盤面のみの解盤面配列を作成
                solutions = filterSolutionsByHint(solutions, i, j, minValue)
                print(f"ヒントを追加した後の残りの解の数: {len(solutions)}")

                if len(solutions) == 0:
                    print("エラー: 残った解盤面がありません。")
                    return None, numberOfHintsAdded, numberOfGeneratedBoards

                # ステップ⑪ 投票配列へ格納して制約を追加。その後①の処理へ
                occurrenceCount = calculateOccurrenceCount(solutions, size)
                problem += isValueInCell[i][j][minValue] == 1
            else:
                # 最小の値が1の場合は、そのまま
                pass

            # 時間制限のチェック
            currentTime = time.time()
            if currentTime - startTime > 1800:  # 30分を超えた場合
                print("30分を超えたため処理を終了します。")
                return None, numberOfHintsAdded, numberOfGeneratedBoards

            # 再度解を生成するためにループの最初に戻る
            # 解盤面リストをクリア
            solutions = []
            continue

    # 万が一ここに到達した場合
    return None, numberOfHintsAdded, numberOfGeneratedBoards


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

    # 2. 各行には1から9の数字が1つずつ入る
    for i in range(size):
        for k in range(1, size + 1):
            problem += pulp.lpSum([isValueInCell[i][j][k]
                                   for j in range(size)]) == 1

    # 3. 各列には1から9の数字が1つずつ入る
    for j in range(size):
        for k in range(1, size + 1):
            problem += pulp.lpSum([isValueInCell[i][j][k]
                                   for i in range(size)]) == 1

    # 4. 各ブロックには1から9の数字が1つずつ入る
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


def findMinOccurrence(occurrenceCount, board, size):
    minCount = float('inf')
    minCell = None
    minValue = None
    for i in range(size):
        for j in range(size):
            if board[i][j] == 0:  # 空のセルのみ
                for k in range(size):
                    count = occurrenceCount[i][j][k]
                    if 0 < count < minCount:
                        minCount = count
                        minCell = (i, j)
                        minValue = k + 1  # インデックス調整
    return minCount, minCell, minValue


def filterSolutionsByHint(solutions, i, j, minValue):
    filteredSolutions = []
    for solution in solutions:
        if solution[i][j] == minValue:
            filteredSolutions.append(solution)
    return filteredSolutions
