path = str(input('path:'))
rebase = bool(input('上書き(True, False):'))
delimiter = str(input('区切り文字:'))

lines = []
a = 0

with open(path, mode='r') as f:
    lines = f.readlines()
    for index, line in enumerate(lines):
        texts = line.split(delimiter, 1)
        print(texts)
        if len(texts) > 1:
            lines[index] = texts[1]
    

with open(path, mode='w') as f:
    if rebase:
        f.writelines(lines)