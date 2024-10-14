import gurobipy as gp
from gurobipy import GRB

def generateSolutionBoardG(board):
    max_number = len(board)  # ボードの長さから max_number を自動で取得

    # 問題の定義
    prob = gp.Model("Sudoku")
    prob.Params.LogToConsole = 0  # ソルバーの出力を抑制

    # 決定変数の作成
    choices = prob.addVars(
        range(max_number),   # 行インデックス
        range(max_number),   # 列インデックス
        range(1, max_number+1),  # 数字（1から max_number）
        vtype=GRB.BINARY,
        name="Choice"
    )

    # 目的関数（この場合は特に必要ないので、定数ゼロを設定）
    prob.setObjective(0)

    # 制約条件の追加
    # 1. 各セルには1つの数字のみが入る
    for r in range(max_number):
        for c in range(max_number):
            prob.addConstr(gp.quicksum(choices[r, c, n] for n in range(1, max_number+1)) == 1)

    # 2. 各行には1からmax_numberの数字が1つずつ入る
    for r in range(max_number):
        for n in range(1, max_number+1):
            prob.addConstr(gp.quicksum(choices[r, c, n] for c in range(max_number)) == 1)

    # 3. 各列には1からmax_numberの数字が1つずつ入る
    for c in range(max_number):
        for n in range(1, max_number+1):
            prob.addConstr(gp.quicksum(choices[r, c, n] for r in range(max_number)) == 1)

    # 4. 各ブロックには1からmax_numberの数字が1つずつ入る
    block_size = int(max_number ** 0.5)
    for br in range(block_size):
        for bc in range(block_size):
            for n in range(1, max_number+1):
                prob.addConstr(
                    gp.quicksum(
                        choices[r, c, n]
                        for r in range(br * block_size, (br + 1) * block_size)
                        for c in range(bc * block_size, (bc + 1) * block_size)
                    ) == 1
                )

    # 5. 既に数字が入っているセルの制約
    for r in range(max_number):
        for c in range(max_number):
            if board[r][c] != 0:
                prob.addConstr(choices[r, c, board[r][c]] == 1)

    # 問題を解く
    prob.optimize()

    # 解が見つかった場合、盤面を更新
    if prob.Status == GRB.OPTIMAL:
        for r in range(max_number):
            for c in range(max_number):
                for n in range(1, max_number+1):
                    if choices[r, c, n].X > 0.5:
                        board[r][c] = n
        return True
    else:
        return False

# mainから呼び出される関数
def generateSolutionBoardWrapper(board):
    board_copy = [row[:] for row in board]
    if generateSolutionBoardG(board_copy):
        for i in range(len(board)):
            for j in range(len(board)):
                board[i][j] = board_copy[i][j]
        return True
    return False
