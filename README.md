# Lobsterpincer Spectator: Real-Time Chessboard Processor

- [Lobsterpincer Spectator: Real-Time Chessboard Processor](#lobsterpincer-spectator-real-time-chessboard-processor)
  - [Overview](#overview)
  - [Software Installation](#software-installation)
  - [Data Collection and Model Training](#data-collection-and-model-training)
  - [Usage of Main Program](#usage-of-main-program)
  - [Technical Details](#technical-details)
  - [Acknowledgements](#acknowledgements)
  - [Contact](#contact)

## Overview

Lobsterpincer Spectator (named after the "Lobster Pincer mate") is a chessboard processor that gives players feedback in real time. There are three versions of the Lobsterpincer Spectator: Windows standalone version, [Raspberry Pi's standalone version](https://github.com/David-davidlxl/Lobsterpincer-Spectator-For-RPi), and [Windows and Raspberry Pi's combination version](https://github.com/David-davidlxl/Lobsterpincer-Spectator-For-Win-RPi-Combo). This repository contains the Windows standalone version of the Lobsterpincer Spectator. This version is the most compact of the three in terms of hardware (no hardware configuration is required), and it has the following features:

- register each move in less than 6 seconds with manual chessboard detection (with Intel Core i5-8250U)
  - register each move in less than 8 seconds with automatic chessboard detection (with Intel Core i5-8250U)
- alert the players (via speaker) at critical moments of the game
- inform the players (via OpenCV window) of the evaluation of the current position
- show the players (via OpenCV window) the move played in the previous position

![](README%20attachments/High-level%20diagram%20for%20overview.png)

[![](https://markdown-videos.deta.dev/youtube/YRgol4snGFI)](https://youtu.be/YRgol4snGFI)

## Software Installation

The only dependencies of "ChessPieceModelTraining" are [`numpy`](https://pypi.org/project/numpy/) and [`Pillow`](https://pypi.org/project/Pillow/), which are automatically installed during the installation procedure for "LobsterpincerSpectatorForWin" presented below.

The installation procedure (for "LobsterpincerSpectatorForWin") below has been tested to be fully functional for Windows 11.

First, install Python 3.10 from Microsoft Store. It is important NOT to install Python 3.11 instead as it is currently incompatible with [`onnxruntime`](https://pypi.org/project/onnxruntime/).

Then make sure your `pip` is up to date by running the following command in Windows PowerShell:

```
pip install --upgrade pip
```

If you see any warning about some directory not on PATH, follow [this](https://stackoverflow.com/a/51165784) and restart the computer to resolve it.

In order to successfully install `tensorflow`, you need to first [enable long paths](https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=powershell#enable-long-paths-in-windows-10-version-1607-and-later). To do so, open another PowerShell as administrator and run the following command:

```
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

Now you can install all the relevant packages by running the following commands in Windows PowerShell:

```
pip install numpy
pip install opencv-python
pip install chess
pip install scipy
pip install pygame
pip install Pillow
pip install tensorflow
pip install onnxruntime
pip install matplotlib
pip install pyclipper
pip install scikit-learn
```

(The "requirements.txt" file shows a complete list of the installed Python packages (with their version numbers included) up to this point.)

Finally, in order to successfully import `tensorflow`, you also need to install a Microsoft Visual C++ Redistributable package from [here](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170). Since [Windows 11 only has the 64-bit version](https://www.intowindows.com/where-can-i-download-windows-11-32-bit-iso/), you can simply download and install [this](https://aka.ms/vs/17/release/vc_redist.x64.exe).

## Data Collection and Model Training

The "SqueezeNet1p1_all_last.onnx" chess-piece model (in "LobsterpincerSpectatorForWin/livechess2fen/selected_models") provided in this repository was obtained by transfer learning based on 508 images of [this specific chessboard](https://www.amazon.com/dp/B07YG7R27P?psc=1&ref=ppx_yo2ov_dt_b_product_details) under various lighting conditions. If you have a different chessboard, you should follow the procedure below to collect your own data and obtain your own model.

First, collect labeled image data using "capture_and_label_img.py" (in "LobsterpincerSpectatorForWin/lpspectator"):

1. You will need an app on your phone that turns your phone into an IP camera. For Android, you can use [IP Webcam](https://play.google.com/store/apps/details?id=com.pas.webcam&pli=1). Make sure your phone and the computer (that will run "capture_and_label_img.py") are in the same Wi-Fi network, open the app, and edit the `IMAGE_SOURCE` variable in "capture_and_label_img.py" accordingly. You will also need some kind of physical structure (such as a [phone holder](https://www.amazon.com/dp/B0B9N41MCS?ref=ppx_yo2ov_dt_b_product_details&th=1)) that you can use to hold the phone.

2. Paste the PGN of the game to be played (during data collection) into "game_to_be_played.pgn" (in "LobsterpincerSpectatorForWin").

3. Run "capture_and_label_img.py" from the "LobsterpincerSpectatorForWin" directory (NOT from the "LobsterpincerSpectatorForWin/lpspectator" directory) to collect image data.

4. Cut everything in the "Captured Images" folder (in "LobsterpincerSpectatorForWin") and paste it into a subfolder in "ChessPieceModelTraining/BoardSlicer/images/chessboards" (NOT directly in "ChessPieceModelTraining/BoardSlicer/images/chessboards").

5. Repeat steps 2-4 until you have a sufficient number (e.g., hundreds) of labeled images under various lighting conditions.

Next, process the data and obtain the trained model as follows:

1. Run "board_slicer.py" and copy (or cut) all the output in the "ChessPieceModelTraining/BoardSlicer/images/tiles" folder into the "ChessPieceModelTraining/DataSplitter/data/full" folder.

2. Run "data_splitter.py" to randomize and split the data. The next two steps are optional (but somewhat recommended):

   1. Delete the "ChessPieceModelTraining/DataSplitter/data/full" folder (to reduce the size of the "ChessPieceModelTraining/DataSplitter/data" folder and thus reduce the time it takes to upload the data to Google Colab later).
   
   2. Discard a significant amount of the empty-square data in "ChessPieceModelTraining/DataSplitter/data/train/\_" and "ChessPieceModelTraining/DataSplitter/data/validation/\_" (such that, for example, the amount of the remaining empty-square data is comparable to that of the white-pawn data or black-pawn data).

3. Compress the "ChessPieceModelTraining/DataSplitter/data" folder into a "data.zip" ZIP-file (in the "ChessPieceModelTraining/DataSplitter" folder).

4. Open "SqueezeNet1p1_model_training.ipynb" (in "ChessPieceModelTraining/ModelTrainer") with Google Colab, enable GPU on Google Colab, and upload the "data.zip" (in "ChessPieceModelTraining/DataSplitter") and "models.zip" (in "ChessPieceModelTraining/ModelTrainer") files to Google Colab.

5. Run the entire "SqueezeNet1p1_model_training.ipynb" notebook to perform transfer learning (which should take at least a couple of hours, but exactly how long it takes depends on how much image data you collected in the first place).

6. Download the "SqueezeNet1p1_all_last.onnx" (and, optionally, "SqueezeNet1p1_all_last.h5") from Google Colab (in the "models" folder) to the "LobsterpincerSpectatorForWin/livechess2fen/selected_models" folder.

The following video walks through the entire data-collection-and-model-training procedure. Only 5 images under the same lighting condition are collected in this demo in order to keep the video brief; you want to collect hundreds of images under various lighting conditions in practice. Also, even though ["LobsterpincerSpectatorForRPi"](https://github.com/David-davidlxl/Lobsterpincer-Spectator-For-RPi/tree/main/LobsterpincerSpectatorForRPi) and Raspberry Pi are used for data collection in this demo, the procedure is very much the same for "LobsterpincerSpectatorForWin" and a Windows computer.

[![](https://markdown-videos.deta.dev/youtube/Yl_WZxMeNjk)](https://youtu.be/Yl_WZxMeNjk)

## Usage of Main Program

To use the main program, "lobsterpincer_spectator.py" (in "LobsterpincerSpectatorForWin"):

1. Make sure your phone and Windows computer are in the same Wi-Fi network.

2. Open the app on your phone (that turns your phone into an IP camera), mount the phone on some kind of physical structure, and edit the `IMAGE_SOURCE` variable in "capture_and_label_img.py" (see step 1 of the data-collection procedure above).

3. Edit the `FULL_FEN_OF_STARTING_POSITION`, `A1_POS`, and `BOARD_CORNERS` variables in "lobsterpincer_spectator.py" (feel free to edit other variables as well, but these three are generally the most relevant to the user).

4. Run "lobsterpincer_spectator.py" from the "LobsterpincerSpectatorForWin" directory and tune the slider values.

5. Play the game against your opponent (the game you play has nothing to do with the "LobsterpincerSpectatorForWin/game_to_be_played.pgn" file, by the way, which is only relevant to data collection). At any point during the game, feel free to press 'p' to pause the program, press 'r' to resume the program, or press 'q' to quit the program.

6. After the game, feel free to use "saved_game.pgn" (in "LobsterpincerSpectatorForWin") for postgame analysis.

The video in the [Overview](#overview) section demos the case where `BOARD_CORNERS` is set to `[[0, 0], [1199, 0], [1199, 1199], [0, 1199]]`. In this case, manual (predetermined) chessboard detection is used, which accelerates the move-registration process (each move takes at most 6 seconds to register with Intel Core i5-8250U). If `BOARD_CORNERS` is set to `None`, automatic (neural-network-based) chessboard detection is used, and each moves takes at most 8 seconds to register with Intel Core i5-8250U.

## Technical Details

The figure below shows a high-level diagram for the signal-processing workflow:

![](README%20attachments/High-level%20diagram%20for%20technical%20details.png)

There are a few things to note:

1. The Windows computer is responsible for all the heavy computation.

2. The chess-piece model discussed in the [Data Collection and Model Training](#data-collection-and-model-training) section above is responsible for move detection.

3. After each move is registered (i.e., validated), a sound effect is played. There are sound effects for making "regular" moves, capturing, castling, promoting, checking, and checkmating. These are the same sound effects that you would hear in an online game on [chess.com](http://www.chess.com).

4. Engine evaluation is accomplished with [Stockfish](https://stockfishchess.org/) 15.1 at depth 17, [which corresponds to an ELO rating of about 2695](https://chess.stackexchange.com/questions/8123/stockfish-elo-vs-search-depth/8125#8125).

5. A critical moment is defined as one when one of the two conditions is satisfied:

   1. The best move forces a checkmate (against the opponent) whereas the second-best move does not.
   
   2. Neither the best move nor the second-best move forces checkmate, but the best move is significantly better than the second-best move (a floating-point evaluation difference of 2 or more), and the position would not be completely winning (a position is considered completedly winning if its floating-point evaluation is at least 2) for the player if they played the second-best move.

    The precise definition can be found in the `is_critical_moment()` function in "evaluate_position.py" (in "LobsterpincerSpectatorForWin/lpspectator").

6. Besides the ability to detect critical moments, the program also detects Harry the h-pawn and the Lobster Pincer mate. When a player pushes Harry the h-pawn into (or further into) the opponent's territory (but Harry has not promoted into a queen yet) and the player pushing the h-pawn is not losing (a position is considered losing if its floating-point evaluation is at most -2), the "Look at Harry! Come on, Harry!" audio is played. When the Lobster Pincer mate happens, a special piece of audio is played as well.

## Acknowledgements

I give special thanks to David Mallasén Quintana. This project was made possible by Quintana's work: [LiveChess2FEN](https://github.com/davidmallasen/LiveChess2FEN). LiveChess2FEN provided me with the foundation for chess-piece identification. The "models.zip" file (in "ChessPieceModelTraining/ModelTrainer") came directly from the LiveChess2FEN repository, and the "SqueezeNet1p1_model_training.ipynb" notebook (in "ChessPieceModelTraining/ModelTrainer") was written largely based on the work in "cpmodels" folder in the repository as well.

I also thank Linmiao Xu for his [chessboard-recognizer project](https://github.com/linrock/chessboard-recognizer), which helped me develop the "ChessPieceModelTraining/BoardSlicer" program.

Finally, I thank [Simon Williams](https://www.youtube.com/@GingerGM) and [Daniel Naroditsky](https://www.youtube.com/@DanielNaroditskyGM) for creating the entertaining YouTube videos that I used to create the audio files. They also inspired and helped me to become a much stronger chess player than I would be without them.

## Contact

If you find this repository to be useful (but please use my work responsibly; use it in friendly practice games instead of tournament games!), or if you have any feedback, please do not hesitate to reach out to me at davidlxl@umich.edu.