SCREEN_HEIGHT=770
SCREEN_WIDTH=900
SCREEN_TITLE="Chess AI"

BOARD_SIZE=650

# reference: https://github.com/healeycodes/andoma
# Elo: ~1500 Depth 4
# build: pyinstaller.exe --add-binary ".\stockfish\stockfish-windows-x86-64-avx2.exe;." --onefile .\main.py

# Lỗi không đi khi is_stalemate
# 8/8/2Q3Q1/8/8/8/k4K2/8 w - - 5 80

# Lỗi không đi khi -inf
# 8/8/4k3/1b6/8/8/3q4/1K6 w - - 0 1