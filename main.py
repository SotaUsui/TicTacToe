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


def block_clicks():
    global block_input
    while block_input:
        print("wait...")
        #pygame.event.wait()
########################################################
#################  communication #######################
########################################################
def make_move(turn, row, col, conn):
    board[row][col] = turn                          # update board
    try:
        mes = str(row) + str(col)
        conn.sendall(mes.encode())                 # send row and col
        conn.sendall(turn.encode())
    except Exception as e:
        print(f"send error: {e}")

def handle_move(conn):
    try:
        data = recvall(conn,2).decode()
        turn = recvall(conn,1).decode()
        row = int(data[0])
        col = int(data[1])
        board[row][col] = turn
        return True

    except Exception as e:
        print(f"receive error: {e}")
        return False

###################################################################
# Game setup
CREATING_GAME = True
PLAYER = "X"
running = False
current_turn = "X"
block_input = True

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

# Start the block_clicks thread once
block_thread = threading.Thread(target=block_clicks)
block_thread.start()

while running:
    draw_board()
    pygame.display.flip()

    if current_turn == PLAYER:
        block_input = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                row = y // 100              # 0 or 1 or 2
                col = x // 100              # 0 or 1 oe 2
                if board[row][col] == "":
                    block_input = True
                    make_move(current_turn, row, col, connection)
                    current_turn = "O" if current_turn == "X" else "X"


    else:

        success = handle_move(connection)
        if not success:
            print("Opponent disconnected or move failed.")
            running = False
        current_turn = "O" if current_turn == "X" else "X"

pygame.quit()
sys.exit()
