lines = []
path = str(input('path:'))

with open(path, mode='r') as f:
    lines = f.readlines()
    delimiter = str(input('delimiter:'))
    for index, line in enumerate(lines):
        texts = line.split(delimiter, 1)
        if len(texts) > 1:
            lines[index] = texts[1]

with open(path, mode='w') as f:
    rebase = bool(input('rebase(True, False):'))
    if rebase:
        f.writelines(lines)
