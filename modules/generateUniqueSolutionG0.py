import time
import gurobipy as gp
from gurobipy import GRB
from utility.printBoard import printBoard


def generateUniqueSolutionG0(board, MAX_SOLUTIONS, LIMIT_TIME):
    start_time = time.time()
    numberOfHintsAdded = 0  # 追加したヒントの数をカウントする変数
    numberOfGeneratedBoards = []  # 各内部ループで生成された解の数を保存するリスト
    currentSolution = None  # 唯一解を保存する変数

    print("唯一解生成開始")
    size = len(board)
    max_solutions = MAX_SOLUTIONS  # 生成する解の最大数

    while True:  # 外部ループ: 内部ループ内で解盤面が一つしか見つからなくなったら終了
        solution_count = 0  # 解の数をカウント

        # 111~999の連続した配列 (0-indexedなので実際は[0][0][0]から[8][8][8])
        occurrence_count = [
            [[0 for _ in range(size)] for _ in range(size)] for _ in range(size)]

        # Gurobiモデルの作成
        model = gp.Model("Sudoku")
        model.setParam('OutputFlag', 0)  # ソルバー出力を抑制

        # 決定変数の作成
        isValueInCell = model.addVars(
            size, size, size, vtype=GRB.BINARY, name="IsValueInCell")

        # 制約条件の追加
        # 1. 各マスには1つの数字のみが入る
        for i in range(size):
            for j in range(size):
                model.addConstr(
                    sum(isValueInCell[i, j, k] for k in range(size)) == 1)

        # 2. 各行には1から9の数字が1つずつ入る
        for i in range(size):
            for k in range(size):
                model.addConstr(
                    sum(isValueInCell[i, j, k] for j in range(size)) == 1)

        # 3. 各列には1から9の数字が1つずつ入る
        for j in range(size):
            for k in range(size):
                model.addConstr(
                    sum(isValueInCell[i, j, k] for i in range(size)) == 1)

        # 4. 各ブロックには1から9の数字が1つずつ入る
        block_size = int(size ** 0.5)
        for bi in range(block_size):
            for bj in range(block_size):
                for k in range(size):
                    model.addConstr(sum(isValueInCell[i, j, k]
                                        for i in range(bi * block_size, (bi + 1) * block_size)
                                        for j in range(bj * block_size, (bj + 1) * block_size)) == 1)

        # 5. 初期値（ヒント）の設定
        for i in range(size):
            for j in range(size):
                if board[i][j] != 0:
                    model.addConstr(isValueInCell[i, j, board[i][j] - 1] == 1)

        # 内部ループ
        while solution_count < max_solutions:
            current_time = time.time()
            if current_time - start_time > LIMIT_TIME:  # LIMIT_TIMEを超えた場合
                print("制限時間を超えたため処理を終了します。")
                return None, None, numberOfHintsAdded, numberOfGeneratedBoards  # currentSolutionもNoneで返す

            # モデルの解決
            model.optimize()

            if model.status == GRB.OPTIMAL:
                solution_count += 1
                solution = [[0 for _ in range(size)] for _ in range(size)]
                for i in range(size):
                    for j in range(size):
                        for k in range(size):
                            if isValueInCell[i, j, k].x > 0.5:
                                solution[i][j] = k + 1

                # 111~999の連続した配列に情報を格納
                for i in range(size):
                    for j in range(size):
                        value = solution[i][j]
                        occurrence_count[i][j][value - 1] += 1

                # 新しい解を除外する制約を作成
                new_constraint = sum(
                    isValueInCell[i, j, solution[i][j] - 1] for i in range(size) for j in range(size))
                max_matching_cells = size * size - 1  # 全マス数から1を引いた値
                model.addConstr(new_constraint <= max_matching_cells)

                print(f"解 {solution_count}")
                # printBoard(solution)
            else:
                print("全ての解盤面を生成しました。")
                break

        print(f"生成された解の数: {solution_count}")

        numberOfGeneratedBoards.append(solution_count)

        if solution_count == 1:
            print("唯一解が見つかりました。")
            print(f"追加したヒントの数: {numberOfHintsAdded}")
            currentSolution = solution  # 唯一解を保存
            return board, currentSolution, numberOfHintsAdded, numberOfGeneratedBoards

        # 最小出現回数のマスを見つける
        min_count = float('inf')
        min_pos = None
        min_value = None
        for i in range(size):
            for j in range(size):
                if board[i][j] == 0:  # 空のマスのみを対象とする
                    for k in range(size):
                        if 0 < occurrence_count[i][j][k] < min_count:
                            min_count = occurrence_count[i][j][k]
                            min_pos = (i, j)
                            min_value = k + 1

        if min_pos is None:
            print("エラー: 最小出現回数のマスが見つかりませんでした。")
            return None, None, numberOfHintsAdded, numberOfGeneratedBoards

        # 最小出現回数のマスを盤面に追加
        i, j = min_pos
        board[i][j] = min_value
        numberOfHintsAdded += 1  # ヒントを追加したのでカウントを増やす
        print(f"マス ({i + 1}, {j + 1}) に {min_value} を追加しました。")
        print(f"現在追加したヒントの数: {numberOfHintsAdded}")

        # 盤面の表示
        print("現在の盤面:")
        printBoard(board)

    # While ループが正常に終了した場合（通常はここには到達しない）
    return None, None, numberOfHintsAdded, numberOfGeneratedBoards
