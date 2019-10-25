import random
def random_with_probability():
    prefix = []
    sum = 0

    for i in [27, 1, 1, 1]:
        sum += i
        prefix.append(sum)

    rand = random.randint(0, sum)

    for i in prefix:
        if rand < i:
            rand = i
            break

    print(prefix)
    print(rand)

if __name__ == '__main__':
    random_with_probability()
