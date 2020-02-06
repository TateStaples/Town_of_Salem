import threading
import time

game_over = False


def user_input():
    global game_over
    while not game_over:
        thing = input("say thing\n")

        print(thing)


def say_hi():
    global game_over
    while not game_over:
        time.sleep(2)
        print("hi")


t1 = threading.Thread(target=user_input)
t2 = threading.Thread(target=say_hi)
t1.start()
t2.start()
time.sleep(10)
game_over = True
