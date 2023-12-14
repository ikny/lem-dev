import threading


more = True


def my_input() -> None:
    global more
    f = input()
    more = False
    print(f)


def print_numbers() -> None:
    global more
    i = 0
    while more == True:
        i += 1
    print(i)


if __name__ == "__main__":
    thread1 = threading.Thread(target=my_input)
    thread2 = threading.Thread(target=print_numbers)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
