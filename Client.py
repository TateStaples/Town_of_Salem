import socket, threading

game_over = False
byte_type = "utf-8"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def receive_input():
    global game_over
    while not game_over:
        msg = s.recv(64)
        msg = msg.decode(byte_type)
        if msg != "":
            print(msg, end="")
            if msg == "Server: game over!":
                game_over = True
    quit()


def output():
    global game_over
    while not game_over:
        thing = input("")
        if len(thing) > 0:
            s.send(bytes(thing, byte_type))


def main():
    name = input("What do you want to be your username?  ")
    s.connect(('192.168.0.23', 1234))  # host and code
    msg = s.recv(128)  # this is data amount received
    print(msg.decode(byte_type))

    msg = s.recv(128)
    print(msg.decode(byte_type))

    s.send(bytes(name[:10], byte_type))  # confines username to shorter than 10

    t1 = threading.Thread(target=receive_input)
    t2 = threading.Thread(target=output)
    t1.start()
    t2.start()


if __name__ == "__main__":
    main()
