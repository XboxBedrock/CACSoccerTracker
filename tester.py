with open('test-sessions/1.txt', 'r') as f:
    line_num = 0
    for line in f:
        line_num += 1
        if line_num == 55:
            print(line)
