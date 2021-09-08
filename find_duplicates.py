'''Скрипт выполняет поиск файлов с одинаковым содержимым в заданной директории
Сначала файлы сравниваются по размеру, чтобы выявить потенциальных дубликатов
Затем потенциальные дубликаты сравниваются по md5 хэшу
Формат запуска из консоли: python find_duplicates.py {директория} {файл_вывода.txt}
Формат вывода: в каждой строке выходного файла перечислены через пробел одинаковые между собой файлы'''


import hashlib
import os
import sys

MAX_CHUNK = 4096  #максимаьный размер куска при считывании файла (4кБ)
DEFAULTPATH = os.path.dirname(__file__) #значение директории по умолчанию
DEFAULTOUTPUT = DEFAULTPATH+r'/duplicates.txt'  #имя выходного файла по умолчанию

def get_hash(file):  
    #принимает файл, возвращает его md-5 хэш 
    with open(file, 'rb') as f:
        hashobj = hashlib.md5()
        while True:  
            #считываем кусками, чтобы была возможность читать большие файлы
            chunk = f.read(MAX_CHUNK)
            if not chunk:
                break
            hashobj.update(chunk)
        return hashobj.hexdigest()

path = sys.argv[1] if len(sys.argv)>1 else DEFAULTPATH  #получаем значение директории из аргументов запуска
if not (os.path.isabs(path)):  #на случай, если задан относительный путь
    path = DEFAULTPATH+'\\'+path
output = sys.argv[2] if len(sys.argv)>2 else DEFAULTOUTPUT #получаем имя выходного файла из аргументов запуска
if not (os.path.isabs(output)):
    output = DEFAULTPATH+'\\'+output

try:
    files = os.listdir(path) #список файлов в директории
    sizes_dict = {}  #здесь будет словарь файлов с одинаковым размером
    for name in files:
        #добавляем в словарь по ключу - размеру
        size = os.path.getsize('{}\{}'.format(path,name))
        sizes_dict[size] = sizes_dict.get(size,[])+[name]

    duplicates = {} #здесь будет словарь файлов с одинаковым хэшем
    for same_sizes in sizes_dict.values():
        if len(same_sizes)>1:  #если нет файлов с таким же размером, значит нет дубликатов
            for name in same_sizes:
                #для потенциальных дубликатов считаем хэш и добавляем в словать по ключу-хэшу
                fhash = get_hash('{}\{}'.format(path,name))
                duplicates[fhash] = duplicates.get(fhash, []) + [name]
except OSError:
    #не удалось прочитать файлы (неверно указана директория, нет доступа...)
    sys.exit('Error reading files')
            
try:
    with open(output, 'w') as f:
        #фильтруем файлы, для которых не нашлось дубликатов. Остальные объединяем в строку по одинаковости
        f.writelines(list(map(lambda x: ' '.join(x)+'\n',(filter(lambda x: len(x)>1 ,duplicates.values())))))
except OSError:
    #не удалось записать вывод (неверно указана директория, нет доступа...)
    sys.exit('Error writing output')
            