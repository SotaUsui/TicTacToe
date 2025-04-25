import threading
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
    if PLAYER == "X":
        screen.fill(WHITE)
    else:
        screen.fill((255,255,0))

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


def recvall(conn, length):
    """Receive exactly 'length' bytes from the connection."""
    data = b""
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet:
            return None  # Connection closed
        data += packet
    return data


def is_terminate(board, row, col):
    # "0"= not terminate, "1"= "x" win, "2"= "o" win, "3"= tie

    # check row
    if board[row][0] == board[row][1] == board[row][2] and board[row][0] != "":
        if board[row][0] == "X":
            return "1"
        else:
            return "2"

    # check col
    elif board[0][col] == board[1][col] == board[2][col] and board[0][col] != "":
        if board[0][col] == "X":
            return "1"
        else:
            return "2"

    # check if there is a diagonal
    if row == col and board[0][0] == board[1][1] == board[2][2] and board[0][0] != "":
        if board[0][0] == "X":
            return "1"
        elif board[0][0] == "O":
            return "2"

    # anti-diagonal
    if row + col == 2 and board[0][2] == board[1][1] == board[2][0] and board[0][2] != "":
        return "1" if board[0][2] == "X" else "2"

    # check if board is full (tie)
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                return "0"  # not terminate yet

    return "3"      # tie

########################################################
#################  communication #######################
########################################################
def make_move(turn, row, col, conn):
    board[row][col] = turn                          # update board
    status = is_terminate(board, row, col)                    # 0=not terminate, 1=x win, 2=o win, 3= tie
    try:
        mes = str(row) + str(col)
        conn.sendall(mes.encode())                 # send row and col
        conn.sendall(turn.encode())
        conn.sendall(status.encode())
        return status
    except Exception as e:
        print(f"send error: {e}")

def handle_move(conn):
    try:
        data = recvall(conn,2).decode()
        turn = recvall(conn,1).decode()
        status = recvall(conn,1).decode()
        row = int(data[0])
        col = int(data[1])
        board[row][col] = turn
        return True, status

    except Exception as e:
        print(f"receive error: {e}")
        return False

###################################################################
# Game setup
CREATING_GAME = True
PLAYER = "X"
running = False
current_turn = "X"
status = "0"

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

    if status != "0":
        # display the result
        font = pygame.font.SysFont(None, 48)

        if status == "3":
            result_text = "It's a Tie"
            fcolor = (0,0,0)
        elif (status == "1" and PLAYER == "X") or (status == "2" and PLAYER == "O"):
            result_text = "Winner!!"
            fcolor = (200, 0, 0)
        else:
            result_text = "Loser"
            fcolor = (0,0,200)

        # Render text
        text_surface = font.render(result_text, True, fcolor)
        text_rect = text_surface.get_rect(center=(150, 150))  # Center of 300x300 screen

        # Create translucent background
        bg_surface = pygame.Surface((text_rect.width + 20, text_rect.height + 10), pygame.SRCALPHA)
        bg_surface.fill((255, 255, 255, 180))  # White with some transparency

        # Draw background then text
        screen.blit(bg_surface, (text_rect.x - 10, text_rect.y - 5))
        screen.blit(text_surface, text_rect)

        pygame.display.flip()
        pygame.time.wait(20000)
        running = False
        break

    if current_turn == PLAYER:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                row = y // 100              # 0 or 1 or 2
                col = x // 100              # 0 or 1 oe 2
                if board[row][col] == "":
                    status = make_move(current_turn, row, col, connection)
                    current_turn = "O" if current_turn == "X" else "X"


    else:
        try:

            success, status = handle_move(connection)
            if not success:
                print("Opponent disconnected or move failed.")
                running = False
            current_turn = "O" if current_turn == "X" else "X"
            pygame.event.clear()
        except:
            print("in except")

pygame.quit()
sys.exit()
