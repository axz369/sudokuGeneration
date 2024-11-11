import time
import json
import random  # ランダムなヒント追加のために追加

from modules.ConvertToNumber import ConvertToNumber
from modules.Validation import Validation
from modules.AddHintToLineSymmetry import AddHintToLineSymmetry
from modules.UnifiedNumberOfHints import UnifiedNumberOfHints
from modules.generateUniqueSolutionG0 import generateUniqueSolutionG0
from modules.generateUniqueSolutionG1 import generateUniqueSolutionG1
from modules.generateUniqueSolutionG2 import generateUniqueSolutionG2

from utility.generateSolutionBoardG import generateSolutionBoardG
from utility.printBoard import printBoard


if __name__ == "__main__":

    #########################################################
    # プログラム設定
    INPUT_FILE = 'input9.json'
    INPUT_KEY = 'input6'

    ALGORITHM_CHOICE = 0 # 0: 再利用なし 1: 再利用あり(解の補充なし), 2: 再利用あり(解の補充あり)
    AddHintToLineTarget = 0  # 1: 線対称にヒントを追加する, 0: 線対称ヒントを追加しない
    LIMIT_TIME = 60

    if '9' in INPUT_FILE:
        MAX_SOLUTIONS = 100
        TARGET_HINT_COUNT = 20
    elif '16' in INPUT_FILE:
        MAX_SOLUTIONS = 200
        TARGET_HINT_COUNT = 140
    elif '25' in INPUT_FILE:
        MAX_SOLUTIONS = 10
        TARGET_HINT_COUNT = 200
    else:
        MAX_SOLUTIONS = 10
        TARGET_HINT_COUNT = 200
    #########################################################

    # JSONファイルを読み込む
    with open(INPUT_FILE, 'r') as file:
        data = json.load(file)

    # 使用する数独の問題を選択
    sudokuProblem = data["inputs"][INPUT_KEY]
    board = sudokuProblem["board"]
    maxNumber = sudokuProblem["maxNumber"]

    # 入力盤面を表示
    print("入力盤面:")
    printBoard(board)

    # 盤面の文字を数値に変換
    converter = ConvertToNumber(board, maxNumber)
    dataConvertedToNumbers = converter.getConvertedData()

    # Validationクラスを使用して入力ファイルの正当性チェック
    validator = Validation(
        dataConvertedToNumbers['charToNumberMap'], dataConvertedToNumbers['boardConvertedToNumber'], maxNumber)
    if not validator.check():
        print("バリデーション失敗")
        exit(1)
    else:
        print("バリデーション成功")

    # generateSolutionBoard関数を使用して解盤面Aを取得
    boardA = [row[:] for row in dataConvertedToNumbers['boardConvertedToNumber']]

    isSolutionGenerated = generateSolutionBoardG(boardA)

    if not isSolutionGenerated:
        print("解盤面Aの生成に失敗しました。")
        exit(1)
    else:
        print("解盤面Aが生成されました")
        printBoard(converter.convertBack(boardA))

    # AddHintToLineTarget の値に応じて処理を分岐
    if AddHintToLineTarget == 1:
        # 対称性に基づいたヒントを追加するクラスを作成
        symmetryAdder = AddHintToLineSymmetry(
            dataConvertedToNumbers['boardConvertedToNumber'], boardA)

        # 4つの対称盤面を取得
        symmetricBoards = symmetryAdder.getSymmetricBoards()

        # 対称性タイプのリストを定義
        symmetryTypes = ["horizontal", "vertical", "diagonal_up", "diagonal_down"]

        # 対称軸に追加した直後の盤面を表示
        print("******************************************")
        print("対称軸に追加した直後の盤面:")
        print("******************************************")

        for symmetry_type, board in zip(symmetryTypes, symmetricBoards):
            print(f"\n{symmetry_type}Symmetry:")
            printBoard(converter.convertBack(board))

        # ヒント数の統一処理
        hintUnifier = UnifiedNumberOfHints(
            symmetricBoards, boardA, targetHintCount=TARGET_HINT_COUNT)
        unifiedBoards = hintUnifier.unifyHints()

        # ヒント数統一後の盤面を表示
        print("\n******************************************")
        print("ヒント数統一後の盤面:")
        print("******************************************")
        for symmetry_type, board in zip(symmetryTypes, unifiedBoards):
            print(f"\n{symmetry_type}Symmetry:")
            printBoard(converter.convertBack(board))

        # 4盤面から選択
        while True:
            print("\nどの盤面を選びますか?")
            for i, name in enumerate(symmetryTypes):
                print(f"{i + 1}: {name}Symmetry")

            try:
                choice = int(input("選択: ")) - 1
                if 0 <= choice < len(symmetryTypes):
                    selectedBoard = unifiedBoards[choice]
                    selectedBoardName = f"{symmetryTypes[choice]}Symmetry"
                    break
                else:
                    print("無効な選択です。もう一度選んでください。")
            except ValueError:
                print("無効な入力です。数字で選択してください。")

        print(f"選ばれた盤面 : {selectedBoardName}")
        printBoard(selectedBoard)

    else:
        # 対称性に基づいたヒント追加をスキップし、ランダムにヒントを追加
        selectedBoard = [[0 for _ in range(maxNumber)] for _ in range(maxNumber)]  # 空の盤面を作成
        positions = [(i, j) for i in range(maxNumber) for j in range(maxNumber)]
        random.shuffle(positions)

        # 入力盤面のヒントを追加
        hints_added = 0
        for i in range(maxNumber):
            for j in range(maxNumber):
                if dataConvertedToNumbers['boardConvertedToNumber'][i][j] != 0:
                    selectedBoard[i][j] = dataConvertedToNumbers['boardConvertedToNumber'][i][j]
                    hints_added += 1

        # 残りのヒントをランダムに追加
        for pos in positions:
            if hints_added >= TARGET_HINT_COUNT:
                break
            i, j = pos
            if selectedBoard[i][j] == 0:
                selectedBoard[i][j] = boardA[i][j]
                hints_added += 1

        selectedBoardName = "Random Hints"
        print("対称性に基づいたヒント追加をスキップし、解盤面Aからランダムにヒントを追加しました。")
        print(f"選ばれた盤面 : {selectedBoardName}")
        printBoard(selectedBoard)

    # 唯一解の生成
    startTime = time.time()

    if ALGORITHM_CHOICE == 0:
        problemExample, uniqueSolution, numberOfHintsAdded, solutionsPerIteration = generateUniqueSolutionG0(selectedBoard, MAX_SOLUTIONS, LIMIT_TIME)
    elif ALGORITHM_CHOICE == 1:
        problemExample, uniqueSolution, numberOfHintsAdded, solutionsPerIteration = generateUniqueSolutionG1(selectedBoard, MAX_SOLUTIONS, LIMIT_TIME)
    elif ALGORITHM_CHOICE == 2:
        problemExample, uniqueSolution, numberOfHintsAdded, solutionsPerIteration = generateUniqueSolutionG2(selectedBoard, MAX_SOLUTIONS, LIMIT_TIME)

    endTime = time.time()

    if uniqueSolution:
        print("\n******************************************")
        print("唯一解を持つ問題例(数字):")
        print("******************************************")
        printBoard(problemExample)

        print("\n******************************************")
        print("その問題例の解答(数字):")
        print("******************************************")
        printBoard(uniqueSolution)

        # 数値から文字に変換して表示
        print("\n******************************************")
        print("文字に変換された問題例(文字):")
        print("******************************************")
        printBoard(converter.convertBack(problemExample))

        print("\n******************************************")
        print("文字に変換された解答(文字):")
        print("******************************************")
        printBoard(converter.convertBack(uniqueSolution))

    else:
        print("唯一解の生成に失敗しました。")

    generationTime = endTime - startTime
    print(f"生成時間: {generationTime:.2f}秒")

    # 各内部ループで生成された解の数を表示
    print("\n******************************************")
    print("各内部ループで生成された解の数:")
    print("******************************************")
    for iteration, solutions in enumerate(solutionsPerIteration, 1):
        print(f"ループ {iteration}: {solutions} 個の解が生成されました")

    print("\n******************************************")
    print("記録用")
    print("******************************************")
    print(f"{generationTime:.2f}")
    # 解が1つだけの場合は除外する
    solutions_list = [
        solutions for solutions in solutionsPerIteration if solutions > 1]
    print(f"{len(solutions_list)}{solutions_list}")
