import os
import ustruct

for f in os.listdir():
    if f.endswith('.bin'):
        with open(f, 'rb') as logfile:
            data = b''.join(logfile.readlines())
            print(ustruct.unpack('f'*(len(data)//32), data))
