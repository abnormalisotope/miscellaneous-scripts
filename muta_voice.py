import os, sys

def readFile(path):
    bytes = []
    with open(path, 'rb') as f:
        while (byte := f.read(1)):
            bytes.append(byte)
    return bytes

def writeFile(path, bytes):
    with open(path, 'wb') as f:
        for i in range(len(bytes)):
            f.write(bytes[i])
    
def intToByte(num):
    return num.to_bytes(1, 'big')

def transform(bytes):
    for i in range(len(bytes)):
        num = int.from_bytes(bytes[i])
        if (num >= 40):
            if (num == 44 or num == 100):
                bytes[i] = intToByte(num)
            elif (num < 40 or num >= 64):
                if (num < 64 or num >= 80):
                    if (num < 80 or num >= 96):
                        if (num < 96 or num >= 120):
                            bytes[i] = intToByte(num)
                        else:
                            bytes[i] = intToByte(num - 56)
                    else:
                        bytes[i] = intToByte(num - 16)
                else:
                    bytes[i] = intToByte(num + 16)
            else:
                bytes[i] = intToByte(num + 56)
        else:
            bytes[i] = intToByte(num)

if __name__ == "__main__":
    if (sys.argv[1]):
        path = sys.argv[1]
        file, ext = os.path.splitext(path)
        if (ext != '.voice' and ext != '.htsvoice'):
            raise ValueError('Unsupported file extension')
        print(f'reading file: {path}')
        bytes = readFile(path)
        print('decrypting...')
        transform(bytes)
        print('done!')
        if (ext == '.voice'):
            path = file + '.new.htsvoice'
            print(f'saving file: {path}')
            writeFile(path, bytes)
            print('saved!')
        elif (ext == '.htsvoice'):
            path = file + '.new.voice'
            print(f'saving file: {path}')
            writeFile(path, bytes)
            print('saved!')
        input()
    else:
        print('usage: muta_voice.py [.voice/.htsvoice]')