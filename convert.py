import os
import re
from sys import argv
import esprima
from random import randint
from pprint import pprint


def get_random_name(used_names):
    with open('./temp_random_words.txt', encoding='utf8') as fi:
        lines = fi.readlines()
    with open('./temp_random_words.txt', encoding='utf8') as f:
        content = f.read()
    while True:
        random_name = lines[randint(0, len(lines) - 1)]
        random_name = random_name.replace('\n', '')
        if random_name not in used_names:
            used_names.append(random_name)
            content = re.sub(r"\b%s\b\n" % random_name, '', content)
            with open('./temp_random_words.txt', 'w', encoding='utf8') as fil:
                fil.write(content)
            return random_name, used_names


def tokenize_program(file):
    with open(file, encoding="utf8") as f:
        program = f.read()
        tokens = esprima.tokenize(program)
        return tokens


def replace_str_by_token_method(old_string, new_string, file):
    tokens = tokenize_program(file)

    def compare(token):
        if token.type == 'String' and token.value.strip("'").strip('"') == old_string:
            return '"' + new_string + '"'
        return token

    nt = list(map(compare, tokens)) # + [[], []]
    new_tokens = []
    '''
    def t(x):
        try:
            if x.type != 'Punctuator':
                result = ' ' + x.value + ' '
            elif x.value == ';':
                result = '' + x.value + '\n'
            else:
                result = x.value
        except:
            result = x
        return result
    new_tokens = list(map(t, nt))'''

    for i in range(len(nt) - 2):
        left = ' '
        right = ' '

        if nt[i] != '.':
            if nt[i + 1] != '.':
                if nt[i - 1] != '.':
                    pass
                else:
                    left = ''
            elif nt[i - 1] != '.':
                right = ''
            else:
                right = ''
                left = ''
        else:
            left = ''
            right = ''

        if nt[i] in (';', '{', '}'):
            left = ''
            right = '\n'
        if nt[i + 1] == ';':
            right = ''

        if nt[i] in ('[', ']', '(', ')'):
            left = ''
            right = ''

        if nt[i - 1] in ('[', '('):
            left = ''

        if nt[i + 1] in ('[', ']', '(', ')'):
            right = ''

        if nt[i] == ',':
            left = ''
        if nt[i + 1] == ',':
            right = ''

        if nt[i] == '!':
            right = ''
        if nt[i - 1] == '!':
            left = ''

        new_tokens.append(left + nt[i] + right)

    return ''.join(new_tokens)


def get_imported_files(file):
    tokens = tokenize_program(file)
    files = set()
    for i in range(len(tokens)):
        if tokens[i].value in ('import', 'require'):
            try:
                for j in range(1, len(tokens[i:])):
                    if tokens[i + j].type == 'String':
                        t = tokens[i + j].value.strip('"').strip("'")
                        files.add(t)
                    if tokens[i + j].value == ';' or tokens[i + j + 1].value == 'import':
                        break
            except:
                pass
    return files


def get_paths_to_other_files(file):
    file_extensions = ['.aif', '.cda', '.mid', '.mp3', '.mpa', '.ogg', '.wav', '.wma', '.wpl', '.7z', '.arj', '.deb',
                       '.pkg', '.rar', '.rpm', '.tar.gz', '.z', '.zip', '.bin', '.dmg', '.iso', '.toast', '.vcd', '.ps',
                       '.midi', '.csv', '.dbf', '.dat', '.db', '.log', '.mdb', '.sav', '.sql', '.tar', '.xml', '.bin',
                       '.cgi', '.apk', '.pl', '.com', '.exe', '.gadget', '.jar', '.py', '.wsf', '.json', '.ai', '.bmp',
                       '.tiff', '.bat', '.gif', '.ico', '.jpeg', '.jpg', '.png', '.psd', '.svg', '.tif', '.fnt', '.fon',
                       '.otf', '.ttf', '.xhtml', '.asp', '.aspx', '.cer', '.cfm', '.cgi', '.css', '.htm', '.php',
                       '.rss', '.part', '.jsp', '.html', '.key', '.odp', '.pps', '.ppt', '.pptx', '.ods', '.xlr', '.rm',
                       '.xls', '.xlsx', '.bak', '.cab', '.cfg', '.cpl', '.cur', '.dll', '.dmp', '.drv', '.icns', '.ico',
                       '.ini', '.lnk', '.msi', '.sys', '.tmp', '.3g2', '.3gp', '.avi', '.flv', '.h264', '.m4v', '.mkv',
                       '.mp4', '.mpg', '.mpeg', '.swf', '.vob', '.wmv', '.doc', '.docx', '.odt', '.pdf', '.rtf', '.wpd',
                       '.tex', '.txt', '.wks', '.wps', '.js']
    tokens = tokenize_program(file)
    files = []
    for token in tokens:
        if token.type == 'String':
            for ex in file_extensions:
                if ex in token.value:
                    files.append(token.value.strip('"').strip("'"))
    return files


def get_files_with_exten(extension, mini_game_path):
    files = []
    for dirpath, dirnames, filenames in os.walk(mini_game_path):
        for filename in [f for f in filenames if f.endswith(extension)]:
            if '__temp__' not in filename and '__temp2__' not in filename:
                path = re.sub(r'\\', r'/', os.path.join(dirpath, filename))
                files.insert(0, path)
    return files


def convert(mini_game_path):
    js_files = get_files_with_exten('.js', mini_game_path)
    for js_file in js_files:
        if 'min' in js_file.split('/')[-1]:
            continue
        file_size = os.path.getsize(js_file)
        if file_size <= 2048:
            rotate = 0
        else:
            rotate = 1
        options = ' {}'.format(rotate)

        os.system('./convert_linux_x64 ' + js_file + options)
        #os.system('convert_win.exe ' + js_file + options)
        try:
            with open('./obfuscated_program.txt', encoding='utf8') as file:
                obfuscated_program = file.read()
            with open(js_file, 'w', encoding='utf8') as f:
                f.write(obfuscated_program)
            os.remove('./obfuscated_program.txt')
        except:
            pass


if __name__ == '__main__':
    new = replace_str_by_token_method('qwidjifweif', 'GG', argv[1] + '/main.4846b.js')
    with open(argv[1] + '/main.4846b.js', 'w') as f:
        f.write(new)
    input()
    convert(argv[1])
    #print(get_imported_files(r"C:\Users\Nikita\Desktop\wechatgame\libs\weapp-adapter\EventIniter\index.js"))
    # tokenize_program(r'C:\Temp\starwar\game_2.js')
    #convert()
