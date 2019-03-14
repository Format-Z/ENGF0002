import time

lst = []
for length in range(1000, 1000001, 10000):
    while len(lst) < length:
        lst.append(42)
    count = 0
    starttime = time.time()
    while count < 200:
        lst.pop(length//2)
        count += 1
    now = time.time()
    print(length, now - starttime)

