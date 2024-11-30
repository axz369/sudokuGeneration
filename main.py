import time
import json
import random  # ランダムなヒント追加のために追加

from modules.ConvertToNumber import ConvertToNumber
from modules.Validation import Validation
from modules.AddHintToLineSymmetry import AddHintToLineSymmetry
from modules.UnifiedNumberOfHints import UnifiedNumberOfHints

from modules.generateUniqueSolutionOriginal import generateUniqueSolutionOriginal
from modules.generateUniqueSolutionG1 import generateUniqueSolutionG1
from modules.generateUniqueSolutionG2 import generateUniqueSolutionG2
from modules.generateUniqueSolutionG3 import generateUniqueSolutionG3

from utility.generateSolutionBoardG import generateSolutionBoardG
from utility.printBoard import printBoard


if __name__ == "__main__":

    #########################################################
    # プログラム設定
    INPUT_FILE = 'input9.json'
    INPUT_KEY = 'input1'

    # 0: 再利用なし(オリジナル盤面保存あり)
    # 1: 再利用なし(盤面保存なし)
    # 2: 再利用あり(解の補充なし)
    # 3: 再利用あり(解の補充あり)
    ALGORITHM_CHOICE = 1
    AddHintToLineTarget = 0  # 1: 線対称にヒントを追加する, 0: 線対称ヒントを追加しない
    # 0: 毎回MAX_SOLUTIONS個生成．1: generationLimitsに格納された上限数をヒント追加ごとに設定
    changeGenerationLimit = 0

    # 全体の時間制限を30分に設定
    TOTAL_LIMIT_TIME = 30 * 60  # 30分を秒に換算

    #########################################################

    # JSONファイルを読み込む
    with open(INPUT_FILE, 'r') as file:
        data = json.load(file)

    # 使用する数独の問題を選択
    sudokuProblem = data["inputs"][INPUT_KEY]
    board = sudokuProblem["board"]
    maxNumber = sudokuProblem["maxNumber"]

    # maxNumberに応じて設定
    if maxNumber == 9:
        TARGET_HINT_COUNT = 16
        TARGET_ADDED_HINTS = 5  # 追加ヒント数が5の盤面を目指す
    elif maxNumber == 16:
        TARGET_HINT_COUNT = 51
        TARGET_ADDED_HINTS = None  # 特に設定しない
    elif maxNumber == 25:
        TARGET_HINT_COUNT = 281  # 全マスの45%
        TARGET_ADDED_HINTS = None  # 特に設定しない
    else:
        TARGET_HINT_COUNT = 16  # デフォルト値
        TARGET_ADDED_HINTS = None

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
    boardA = [row[:]
              for row in dataConvertedToNumbers['boardConvertedToNumber']]

    isSolutionGenerated = generateSolutionBoardG(boardA)

    if not isSolutionGenerated:
        print("解盤面Aの生成に失敗しました。")
        exit(1)
    else:
        print("解盤面Aが生成されました")
        printBoard(converter.convertBack(boardA))

    # ここから修正箇所
    ###############################################
    # 追加ヒント数の最小値を設定
    min_added_hints = None
    best_problem_example = None
    best_unique_solution = None
    best_solutions_per_iteration = None
    best_time_per_hint = None

    # チャレンジ回数
    challenge_count = 0

    # 各チャレンジの情報を保存するリスト
    challenge_times = []
    challenge_problem_examples = []
    challenge_unique_solutions = []
    challenge_added_hints = []
    challenge_solutions_per_iteration = []
    challenge_time_per_hint = []

    # 全体の開始時間
    total_start_time = time.time()

    while True:
        # 30分を超えたら終了
        current_time = time.time()
        if current_time - total_start_time > TOTAL_LIMIT_TIME:
            print("30分を超えたため処理を終了します。")
            break

        # チャレンジ回数を増やす
        challenge_count += 1
        print(f"\n=== チャレンジ {challenge_count} ===")

        # 唯一解の生成の開始時間
        startTime = time.time()

        # ランダムにヒントを追加する
        if AddHintToLineTarget == 1:
            # 対称性に基づいたヒント追加の処理（必要に応じて実装）
            pass
        else:
            # ランダムにヒントを追加
            selectedBoard = [[0 for _ in range(maxNumber)]
                             for _ in range(maxNumber)]  # 空の盤面を作成
            positions = [(i, j) for i in range(maxNumber)
                         for j in range(maxNumber)]
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
            print(
                "対称性に基づいたヒント追加をスキップし、解盤面Aからランダムにヒントを追加しました。")
            print(f"選ばれた盤面 : {selectedBoardName}")
            printBoard(selectedBoard)

        # maxNumberに応じた設定
        if maxNumber == 9:
            MAX_SOLUTIONS = 100
            # TARGET_ADDED_HINTS は既に設定済み
        elif maxNumber == 16:
            MAX_SOLUTIONS = None  # 上限盤面数を特に設定しない
            # TARGET_ADDED_HINTS は None
        elif maxNumber == 25:
            MAX_SOLUTIONS = None  # 上限盤面数を特に設定しない
            # TARGET_ADDED_HINTS は None
        else:
            MAX_SOLUTIONS = 100
            # TARGET_ADDED_HINTS は None

        if ALGORITHM_CHOICE == 1:
            if changeGenerationLimit == 0:
                generationLimits = None
            else:
                # generationLimitsを設定する必要がある場合はここで設定
                generationLimits = None  # 必要に応じて設定

            # selectedBoard のコピーを作成
            currentBoard = [row[:] for row in selectedBoard]

            problemExample, uniqueSolution, numberOfHintsAdded, solutionsPerIteration, timePerHint = generateUniqueSolutionG1(
                currentBoard, MAX_SOLUTIONS, TOTAL_LIMIT_TIME - (current_time - total_start_time), changeGenerationLimit, generationLimits)
            endTime = time.time()

            # チャレンジの情報を保存
            challenge_times.append(endTime - startTime)
            challenge_problem_examples.append(problemExample)
            challenge_unique_solutions.append(uniqueSolution)
            challenge_added_hints.append(numberOfHintsAdded)
            challenge_solutions_per_iteration.append(solutionsPerIteration)
            challenge_time_per_hint.append(timePerHint)

            # 最良の盤面を更新
            if min_added_hints is None or numberOfHintsAdded < min_added_hints:
                min_added_hints = numberOfHintsAdded
                best_problem_example = problemExample
                best_unique_solution = uniqueSolution
                best_solutions_per_iteration = solutionsPerIteration
                best_time_per_hint = timePerHint

            # 追加ヒント数が TARGET_ADDED_HINTS 以下なら終了
            if TARGET_ADDED_HINTS is not None and numberOfHintsAdded <= TARGET_ADDED_HINTS:
                print(
                    f"追加ヒント数が {TARGET_ADDED_HINTS} 以下の盤面が見つかったため、処理を終了します。")
                break
        else:
            print("ALGORITHM_CHOICE が 1 以外は未対応です。")
            break

    # 最終的な結果を出力
    print("\n=== 最終結果 ===")
    print(f"チャレンジ回数: {challenge_count}")
    print(f"最小の追加ヒント数: {min_added_hints}")

    if best_unique_solution:
        print("\n******************************************")
        print("唯一解を持つ問題例(数字):")
        print("******************************************")
        printBoard(best_problem_example)

        print("\n******************************************")
        print("その問題例の解答(数字):")
        print("******************************************")
        printBoard(best_unique_solution)

        # 数値から文字に変換して表示
        print("\n******************************************")
        print("文字に変換された問題例(文字):")
        print("******************************************")
        printBoard(converter.convertBack(best_problem_example))

        print("\n******************************************")
        print("文字に変換された解答(文字):")
        print("******************************************")
        printBoard(converter.convertBack(best_unique_solution))

    else:
        print("唯一解の生成に失敗しました。")

    total_generation_time = sum(challenge_times)
    print(f"\n総生成時間: {total_generation_time:.2f}秒")

    # 各チャレンジの結果を表示
    for idx in range(challenge_count):
        print(f"\n--- チャレンジ {idx + 1} ---")
        print(f"処理時間: {challenge_times[idx]:.2f}秒")

        # 生成盤面数のリストのコピー
        solutions_list = challenge_solutions_per_iteration[idx].copy()

        # 最後の要素が1の場合、それを削除
        if solutions_list and solutions_list[-1] == 1:
            solutions_list.pop()

        # ヒント追加回数と生成盤面数のリストを表示
        hints_added = challenge_added_hints[idx]
        print(f"{hints_added}[{', '.join(map(str, solutions_list))}]")

        # ヒント追加ごとの生成時間も表示（必要に応じて）
        print("ヒント追加ごとの生成時間（秒）:")
        # 時間のリストをコピーし、solutions_list の長さに合わせる
        time_list = challenge_time_per_hint[idx].copy()
        if len(time_list) > len(solutions_list):
            time_list = time_list[:len(solutions_list)]
        print([round(t, 3) for t in time_list])

    # 最良の盤面に対して、要求された形式で表示
    print("\n******************************************")
    print("最良の盤面の詳細")
    print("******************************************")

    # 最良の盤面のヒント追加回数
    hints_added = min_added_hints

    # 最良の盤面の生成盤面数のリストをコピー
    solutions_list = best_solutions_per_iteration.copy()

    # 最後の要素が1の場合、それを削除
    if solutions_list and solutions_list[-1] == 1:
        solutions_list.pop()

    # ヒント追加回数と生成盤面数のリストを表示
    print(f"{hints_added}[{', '.join(map(str, solutions_list))}]")

    # 全体の処理時間を小数点第2位までで四捨五入して表示
    total_generation_time_rounded = round(total_generation_time, 2)
    print(f"総生成時間: {total_generation_time_rounded}秒")

    # ヒント追加ごとの生成時間も表示
    print("ヒント追加ごとの生成時間（秒）:")
    # 時間のリストをコピーし、solutions_list の長さに合わせる
    time_list = best_time_per_hint.copy()
    if len(time_list) > len(solutions_list):
        time_list = time_list[:len(solutions_list)]
    print([round(t, 3) for t in time_list])
    ###############################################
