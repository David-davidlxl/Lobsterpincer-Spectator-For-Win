"""This module is responsible for processing the digital board.

The three functions in this module are invoked in the main program ("lobsterpincer_spectator.py").

(This module is not intended to be used separately; you'll run into `ModuleNotFoundError` if you run this file directly.)
"""


import chess
import chess.pgn
import cv2

from lpspectator.visualize_fen import (
    generate_fen_image,
    add_evaluation_bar_to_plot,
    add_boom_lobsterpincer_mate_to_plot,
    add_boom_checkmate_to_plot,
    add_god_stalemate_to_plot,
    add_last_move_critical_moment_and_whose_turn_to_plot,
    # add_engine_output_to_plot,
)
from lpspectator.play_audio import (
    play_sound_effect_for_detected_move,
    play_lobsterpincer_audio,
    play_checkmate_audio,
    play_stalemate_audio,
    play_harry_audio,
    play_critical_moment_audio,
)
from lpspectator.evaluate_position import (
    detect_lobsterpincer,
    generate_engine_output,
    num_of_lights_to_turn_on,
    detect_harry,
    is_critical_moment,
)


def print_legal_moves(board: chess.Board):
    """Print the legal moves in the current position.

    :param board: Current board position.
    """
    legal_move_array = [board.san(move) for move in board.legal_moves]
    if len(legal_move_array) > 2:
        legal_moves = (
            f"{', '.join(map(str, legal_move_array[:-1]))}, and {legal_move_array[-1]}"
        )
        print(f"\tThe legal moves are {legal_moves}\n")
    elif len(legal_move_array) == 2:
        print(
            f"\tThe only legal moves in this position are {legal_move_array[0]} and {legal_move_array[1]}\n"
        )
    else:  # There is only one legal move
        print(f"\tThe only legal move in this position is {legal_move_array[0]}\n")


def process_updated_board(
    board: chess.Board,
    detected_move: chess.Move,
    engine: chess.engine.SimpleEngine,
    print_best_moves_in_terminal: bool,
) -> bool:
    """Process the updated board.

    This function prints out the updated FEN, visualizes the updated FEN, plays the sound effect for the detected move,
    evaluates the position, determines whether the position is critical, turns on the LED lights, displays the detected
    move on the LCD screen, and more (e.g., detects Harry, detects checkmate, and detects stalemate).

    :param board: Current (updated) board position.

    :param detected_move: Last move that was detected to be played.

    :param print_best_moves_in_terminal: Whether to print the best moves in the position in the terminal.

    :return: Whether it is the end of the game (checkmate/stalemate).
    """
    game_over = False
    fen = board.fen().split(" ")[0]
    print(f"\tPredicted FEN: {fen}")
    print(f"\tFull FEN: {board.fen()}")
    fen_image = generate_fen_image(fen)

    cv2.imshow("Current position", cv2.cvtColor(fen_image, cv2.COLOR_RGB2BGR))
    cv2.waitKey(1)

    play_sound_effect_for_detected_move(board, detected_move)

    if board.is_checkmate():
        if board.result() == "1-0":
            fen_image = add_evaluation_bar_to_plot(8, fen_image)
        else:
            fen_image = add_evaluation_bar_to_plot(0, fen_image)

        if detect_lobsterpincer(board):
            fen_image = add_boom_lobsterpincer_mate_to_plot(fen_image)
            cv2.imshow("Current position", cv2.cvtColor(fen_image, cv2.COLOR_RGB2BGR))
            cv2.waitKey(200)

            print("\tBoooooom! Lobster Pincer mate!!! Press 'q' to exit the program\n")
            play_lobsterpincer_audio()
        else:
            fen_image = add_boom_checkmate_to_plot(fen_image)
            cv2.imshow("Current position", cv2.cvtColor(fen_image, cv2.COLOR_RGB2BGR))
            cv2.waitKey(200)

            print("\tBoooooom! Checkmate!!! Press 'q' to exit the program\n")
            play_checkmate_audio()
        game_over = True
    elif board.is_stalemate():
        fen_image = add_evaluation_bar_to_plot(4, fen_image)
        fen_image = add_god_stalemate_to_plot(fen_image)
        cv2.imshow("Current position", cv2.cvtColor(fen_image, cv2.COLOR_RGB2BGR))
        cv2.waitKey(200)

        print("\tGod! Stalemate?!!! Press 'q' to exit the program")
        play_stalemate_audio()
        game_over = True
    elif len(list(board.legal_moves)) == 1:
        engine_output = generate_engine_output(
            engine, board, print_best_moves_in_terminal
        )
        # fen_image = add_engine_output_to_plot(engine_output, fen_image)
        # cv2.imshow("Current position", cv2.cvtColor(fen_image, cv2.COLOR_RGB2BGR))
        # cv2.waitKey(200)

        num_of_lights = num_of_lights_to_turn_on(engine_output)
        fen_image = add_evaluation_bar_to_plot(num_of_lights, fen_image)

        board.pop()
        detected_move_san = board.san(detected_move)
        board.push(detected_move)
        turn = board.turn
        fen_image = add_last_move_critical_moment_and_whose_turn_to_plot(
            detected_move_san, False, turn, fen_image
        )
        cv2.imshow("Current position", cv2.cvtColor(fen_image, cv2.COLOR_RGB2BGR))
        cv2.waitKey(200)

        if detect_harry(detected_move, engine_output, board):
            play_harry_audio()
        print(f"\t(critical_moment, num_of_lights) = ({False}, {num_of_lights})\n")
    else:  # There's more than one legal move
        engine_output = generate_engine_output(
            engine, board, print_best_moves_in_terminal
        )
        # fen_image = add_engine_output_to_plot(engine_output, fen_image)
        # cv2.imshow("Current position", cv2.cvtColor(fen_image, cv2.COLOR_RGB2BGR))
        # cv2.waitKey(200)

        num_of_lights = num_of_lights_to_turn_on(engine_output)
        fen_image = add_evaluation_bar_to_plot(num_of_lights, fen_image)

        board.pop()
        detected_move_san = board.san(detected_move)
        board.push(detected_move)
        critical_moment = is_critical_moment(engine_output)
        turn = board.turn
        fen_image = add_last_move_critical_moment_and_whose_turn_to_plot(
            detected_move_san, critical_moment, turn, fen_image
        )
        cv2.imshow("Current position", cv2.cvtColor(fen_image, cv2.COLOR_RGB2BGR))
        cv2.waitKey(200)

        if critical_moment:
            play_critical_moment_audio()
        elif detect_harry(detected_move, engine_output, board):
            play_harry_audio()
        print(
            f"\t(critical_moment, num_of_lights) = ({critical_moment}, {num_of_lights})\n"
        )

    return game_over


def save_current_pgn(game: chess.pgn.Game, full_fen_of_starting_position: str) -> str:
    """Save the moves played so far into a PGN-file ("saved_game.pgn").

    :param game: Current game variable storing all the moves played so far.

    :param full_fen_of_starting_position: Full FEN of the starting position.

    :return: Current PGN string.
    """
    exporter = chess.pgn.StringExporter(headers=False, columns=None)
    game_str = game.accept(exporter)[:-2]

    pgn_str = ""
    if not full_fen_of_starting_position == chess.STARTING_FEN:
        pgn_str = pgn_str + '[Variant "From Position"]\n'
        pgn_str = pgn_str + f'[FEN "{full_fen_of_starting_position}"]\n\n'

    pgn_str = pgn_str + f"{game_str}"
    with open("saved_game.pgn", "w") as pgn_file:
        pgn_file.write(pgn_str)
    return pgn_str
