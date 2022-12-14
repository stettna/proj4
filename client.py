#Nathan Stettler, Austin Black
#CMSC-280: Project 4
#12/07/22

import sys
import socket
import time
from termios import TCIFLUSH, tcflush
import display


def client():

    try:
        host_name = sys.argv[1]

    except:
        print("You must enter a host name")
        return

    host = host_name
    port = 5001

    client_socket = socket.socket()
    client_socket.connect((host, port))

    player_no = client_socket.recv(1).decode()   #player number determined by join order

    print( "WELCOME TO TIC TAC TOE\n" )
    print( "You are Player: " + str( player_no ) )
    print('''The goal of the game is to try and get three in a row.

--To make a move--
-When it is your turn, enter the number shown in the positon you wish to place your piece.

The program runs until there is a winner.
If a cat (tie) occurs, a new round begins.''')
    time.sleep(3)

    #Start of game logic
    while True:
        board = display.Display()
        status = ['GIP']      

        if player_no == "1":
            char = 'X'
            print("Waiting for opponent to join ... ")

            receive_data(client_socket, board, status)  
            make_move(char, client_socket, board) 
            receive_data(client_socket, board, status)

        else:
            char = 'O'
            receive_data(client_socket, board, status)

        while True:
            try:
                print("Waiting for opponent to move ...")

                receive_data(client_socket, board, status)
                if not status[0] == 'GIP':
                    break

                make_move(char, client_socket, board)

                receive_data(client_socket, board, status)
                if not status[0] == 'GIP':
                    break

            except ValueError:
                sys.exit( "client disconnected" )
            except KeyboardInterrupt:
                sys.exit( "You quit!" )


        if status[0] == 'CAT':
            print( "CAT! Restarting game..." )
            time.sleep(3)
            continue

        elif str(player_no) == status[0][1]:
            print("YOU WON!")
        else:
            print("You Lost :( ")
        break	


def receive_data(client_socket, board, status):
    "This function handles the receiving and processing of the current game state"

    data = client_socket.recv(12).decode()   #receive game data from server
    if not data:
        sys.exit("error: client disconnected")

    board.piece_list = list(data[:9])        #only the piece list
    board.draw_board()
    status[0] = data[9:12]                   #game status
   

def make_move(char, client_socket, board):
    "This function handles input of players next move and sends new board state back to the server"

    tcflush(sys.stdin, TCIFLUSH)             #flush all input while waiting
    move = input("Make your next move: ")    #get input

    while not is_valid_play(move, board):    #only numbers 1 - 9 are valid input
        tcflush(sys.stdin, TCIFLUSH)
        move = input("Invalid move! Try again: ") #redo input if not valid

    board.piece_list[int(move)-1] = char     #make X or O in players input

    client_socket.send(''.join(board.piece_list).encode()) #pack up and send


def is_valid_play(move, board):
    "This function checks to see if the players input is a valid move"

    if (move.isdigit() and int(move) > 0 and int(move) <= 9):
        if board.piece_list[int(move)-1].isdigit():
            return True

    return False



if __name__ == '__main__':
    client()
