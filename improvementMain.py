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
    TOTAL_LIMIT_TIME = 1800  # 30分を秒に換算

    # 早期終了を有効にするかどうか (0: 無効, 1: 有効)
    EARLY_TERMINATION_ENABLED = 0  # 0または1で設定

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
    best_problem_examples = []
    best_unique_solutions = []
    best_solutions_per_iterations = []
    best_time_per_hints = []
    addedHintInformations = []

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
        print(f"\n=== {challenge_count}回目 ===")

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
            MAX_SOLUTIONS = 1000
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

            problemExample, uniqueSolution, numberOfHintsAdded, solutionsPerIteration, timePerHint, newAddedHintInformation= generateUniqueSolutionG1(
                currentBoard, MAX_SOLUTIONS, TOTAL_LIMIT_TIME - (current_time - total_start_time), changeGenerationLimit, generationLimits)
            addedHintInformations.append(newAddedHintInformation)
            endTime = time.time()

            # チャレンジの情報を保存
            challenge_times.append(endTime - startTime)
            challenge_problem_examples.append(problemExample)
            challenge_unique_solutions.append(uniqueSolution)
            challenge_added_hints.append(numberOfHintsAdded)
            challenge_solutions_per_iteration.append(solutionsPerIteration)
            challenge_time_per_hint.append(timePerHint)

            # 'problemExample' と 'uniqueSolution' が有効かどうかをチェック
            if problemExample is not None and uniqueSolution is not None:
                # 最良の盤面を更新
                if min_added_hints is None or numberOfHintsAdded < min_added_hints:
                    min_added_hints = numberOfHintsAdded
                    best_problem_examples = [problemExample]
                    best_unique_solutions = [uniqueSolution]
                    best_solutions_per_iterations = [solutionsPerIteration]
                    best_time_per_hints = [timePerHint]
                elif numberOfHintsAdded == min_added_hints:
                    best_problem_examples.append(problemExample)
                    best_unique_solutions.append(uniqueSolution)
                    best_solutions_per_iterations.append(solutionsPerIteration)
                    best_time_per_hints.append(timePerHint)
            else:
                print("唯一解の生成に失敗しました。")

            # EARLY_TERMINATION_ENABLED が 1 で、TARGET_ADDED_HINTS が設定されている場合の早期終了条件
            if EARLY_TERMINATION_ENABLED == 1 and TARGET_ADDED_HINTS is not None:
                if numberOfHintsAdded <= TARGET_ADDED_HINTS:
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

    # 各チャレンジの結果を表示
    for idx in range(challenge_count):
        print(f"\n{idx + 1}回目")
        print(f"処理時間: {challenge_times[idx]:.2f}秒")

        # 生成盤面数のリストのコピー
        solutions_list = challenge_solutions_per_iteration[idx]
        if solutions_list is not None:
            solutions_list = solutions_list.copy()
            # 最後の要素が1の場合、それを削除
            if solutions_list and solutions_list[-1] == 1:
                solutions_list.pop()
        else:
            solutions_list = []

        # ヒント追加回数と生成盤面数のリストを表示
        hints_added = challenge_added_hints[idx]
        if solutions_list:
            print(f"{hints_added}[{', '.join(map(str, solutions_list))}]")
        else:
            print(f"{hints_added}[]")

        # ヒント追加ごとの生成時間も表示
        time_list = challenge_time_per_hint[idx]
        if time_list is not None and solutions_list:
            # 時間のリストをコピーし、solutions_list の長さに合わせる
            time_list = time_list.copy()
            if len(time_list) > len(solutions_list):
                time_list = time_list[:len(solutions_list)]
            print("ヒント追加ごとの生成時間（秒）:")
            print([round(t, 3) for t in time_list])
        else:
            print("ヒント追加ごとの生成時間（秒）:")
            print("[]")

    # 最良の盤面を最後に表示
    if best_unique_solutions:
        print("\n******************************************")
        print("最良の盤面の詳細")
        print("******************************************")
        total_generation_time = sum(challenge_times)
        total_generation_time_rounded = round(total_generation_time, 2)
        print(f"総生成時間: {total_generation_time_rounded}秒")

        for idx, (problem, solution, solutions_list, time_list) in enumerate(zip(best_problem_examples, best_unique_solutions, best_solutions_per_iterations, best_time_per_hints)):
            print(f"\n--- 最良の盤面 {idx + 1} ---")
            print("唯一解を持つ問題例(数字):")
            printBoard(problem)

            print("その問題例の解答(数字):")
            printBoard(solution)

            # 数値から文字に変換して表示
            print("文字に変換された問題例(文字):")
            printBoard(converter.convertBack(problem))

            print("文字に変換された解答(文字):")
            printBoard(converter.convertBack(solution))

            # 生成盤面数のリストのコピー
            solutions_list_copy = solutions_list.copy() if solutions_list else []

            # 最後の要素が1の場合、それを削除
            if solutions_list_copy and solutions_list_copy[-1] == 1:
                solutions_list_copy.pop()

            # ヒント追加回数と生成盤面数のリストを表示
            if solutions_list_copy:
                print(f"{min_added_hints}[{', '.join(map(str, solutions_list_copy))}]")
            else:
                print(f"{min_added_hints}[]")

            # ヒント追加ごとの生成時間も表示
            time_list_copy = time_list.copy() if time_list else []
            if time_list_copy and solutions_list_copy:
                if len(time_list_copy) > len(solutions_list_copy):
                    time_list_copy = time_list_copy[:len(solutions_list_copy)]
                print("ヒント追加ごとの生成時間（秒）:")
                print([round(t, 3) for t in time_list_copy])
            else:
                print("ヒント追加ごとの生成時間（秒）:")
                print("[]")
            
            # 追加ヒント情報の表示
            print("ヒントの追加位置:")
            if idx < len(addedHintInformations):
                added_hint_information = addedHintInformations[idx]
                number_to_char = {v: k for k, v in dataConvertedToNumbers['charToNumberMap'].items()}
                # (row, col, num) 形式で表示
                print(",".join(f"({row}, {col}, {number_to_char[num]})" for row, col, num in added_hint_information))
            else:
                print("追加ヒント情報なし")

    else:
        print("最良の盤面が見つかりませんでした。")

    ###############################################
