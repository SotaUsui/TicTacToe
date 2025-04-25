import pygame
import sys
from socket import *

pygame.init()
screen = pygame.display.set_mode((300, 300))
pygame.display.set_caption("Tic Tac Toe")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

board = [["" for _ in range(3)] for _ in range(3)]

def draw_board():
    screen.fill(WHITE)
    for x in range(1, 3):
        pygame.draw.line(screen, BLACK, (0, 100 * x), (300, 100 * x), 2)
        pygame.draw.line(screen, BLACK, (100 * x, 0), (100 * x, 300), 2)

    font = pygame.font.SysFont(None, 72)
    for i in range(3):
        for j in range(3):
            if board[i][j]:
                mark = font.render(board[i][j], True, BLACK)
                screen.blit(mark, (j * 100 + 30, i * 100 + 10))

def getLocalIPAddress():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]




# Game setup
CREATING_GAME = True
PLAYER = "X"
running = False
current_turn = "X"

if len(sys.argv) == 3:
    ip = sys.argv[1]
    port = int(sys.argv[2])
    CREATING_GAME = False
    PLAYER = "O"

    # join to the game
    try:
        clientSock = socket(AF_INET, SOCK_STREAM)
        clientSock.connect((ip, port))
        connection = clientSock
        running = True
    except Exception as e:
        print(f"{e}")
        sys.exit(1)

elif len(sys.argv) == 1:
    # Waiting for opponent
    # open listening socket
    try:
        listener = socket(AF_INET, SOCK_STREAM)
        listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        listener.bind(('', 0))
        listener.listen(1)  # listening only one person
        listenPort = listener.getsockname()[1]
        ipaddress = getLocalIPAddress()
        print("IPAddress - " + str(ipaddress))
        print("Port - " + str(listenPort))

        connection, addr = listener.accept()
        listener.close()
        running = True

    except Exception as e:
        print(f"{e}")
        sys.exit(1)

else:
    print("Invalid Usage.")
    sys.exit(1)



##########################################################
#################### game running ########################
##########################################################


while running:
    draw_board()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row = y // 100              # 0 or 1 or 2
            col = x // 100              # 0 or 1 oe 2
            if board[row][col] == "":
                board[row][col] = current
                current = "O" if current == "X" else "X"

pygame.quit()
sys.exit()
