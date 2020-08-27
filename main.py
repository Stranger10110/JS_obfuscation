import shutil
from random import choice, uniform, randrange
from time import time

from PIL import Image, ImageEnhance
from bs4 import BeautifulSoup

from convert import *


def reduce_opacity(im, opacity):
    """Returns an image with reduced opacity."""
    assert  0 <= opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im


def watermark(im, mark, position, opacity=1):
    """Adds a watermark to an image."""
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    if position == 'tile':
        for y in range(0, im.size[1], mark.size[1]):
            for x in range(0, im.size[0], mark.size[0]):
                layer.paste(mark, (x, y))
    elif position == 'scale':
        # scale, but preserve the aspect ratio
        ratio = min(float(im.size[0]) / mark.size[0], float(im.size[1]) / mark.size[1])
        w = int(mark.size[0] * ratio)
        h = int(mark.size[1] * ratio)
        mark = mark.resize((w, h))
        layer.paste(mark, (int((im.size[0] - w) / 2), int((im.size[1] - h) / 2)))
    else:
        layer.paste(mark, position)
    # composite the watermark with the layer
    return Image.composite(layer, im, layer)


def apply_watermark(image_file):
    img = Image.open(image_file)

    mark1 = Image.open('mark.png')
    mark2 = Image.open('mark2.png') # r'C:\Temp\Python\JS_obfus\mark2.png'

    img = watermark(img, mark1, (img.size[0] - mark1.size[0] - 5, img.size[1] - mark1.size[1] - 5),
                    round(uniform(0.06, 0.085), 5))
    img = watermark(img, mark2, 'scale', round(uniform(0.06, 0.085), 5))
    file = image_file.replace('.jpeg', '')
    file = file.replace('.jpg', '')
    file = file.replace('.png', '')
    file = "{}.png".format(file)
    img.save(file)


def md5sum(filename, block_size=2**20):
    """
    Returns MD% checksum for given file.
    """
    import hashlib

    md5 = hashlib.md5()
    try:
        file = open(filename, 'rb')
        while True:
            data = file.read(block_size)
            if not data:
                break
            md5.update(data)
    except IOError:
        print('File \'' + filename + '\' not found!')
        return None
    except:
        return None
    return md5.hexdigest()


'''def change_md5_of_image(image_filename):
    import pyexiv2
    image = pyexiv2.ImageMetadata(image_filename)
    image.read()
    image['Exif.Image.ImageDescription'] = '%030x' % randrange(256**15)
    image.write()'''


def change_md5_of_image(image_filename):
    import piexif

    filename = os.path.splitext(image_filename)[0]
    extension = os.path.splitext(image_filename)[1][1:]
    if extension == 'jpg':
        extension = 'jpeg'

    img = Image.open(image_filename)
    exif_dict = {'Image': {'ImageDescription': '%030x' % randrange(256**15)}} # img['Exif.Image.ImageDescription'] = '%030x' % randrange(256**15)
    exif_bytes = piexif.dump(exif_dict)
    img.save(image_filename, exif=exif_bytes)


'''def change_md5_of_image(image_filename):
    s = 's' * randint(256, 512)
    os.system('echo -n {} >> {}'.format(s, image_filename))'''


def make_new_directory_for(file):
    if not os.path.exists(os.path.dirname(file)):
        os.makedirs(os.path.dirname(file))


def get_files_with_extension(extension, mini_game_path):
    files = []
    for dirpath, dirnames, filenames in os.walk(mini_game_path):
        for filename in [f for f in filenames if f.endswith(extension)]:
            if '__temp__' not in filename and '__temp2__' not in filename:
                path = re.sub(r'\\', r'/', os.path.join(dirpath, filename))
                files.insert(0, path)
    return files


def get_all_files(mini_game_path):
    files = []
    for dirpath, dirnames, filenames in os.walk(mini_game_path):
        for filename in filenames:
            if '__temp__' not in filename and '__temp2__' not in filename:
                path = re.sub(r'\\', r'/', os.path.join(dirpath, filename))
                files.insert(0, path)
    return files


def come_up_with_new_directories(used_names):
    result = []

    for i in range(randint(2, 3)):
        random_name, used_names = get_random_name(used_names)
        random_name_2, used_names = get_random_name(used_names)
        t = '/'.join((random_name, choice([random_name_2, ''])))
        if '/' not in t[-1]:
            t += '/'
        result.append(t)

    return result, used_names


def parse_html(file):
    old_relative_paths = []
    with open(file, encoding='utf8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    javascript = soup.find_all('script')
    images = soup.find_all('img')
    css_s = soup.find_all('link')
    for js in javascript:
        if js.has_attr('src'):
            old_relative_paths.append([js.attrs['src']])
    for img in images:
        if img.has_attr('src'):
            old_relative_paths.append([img.attrs['src']])
    for css in css_s:
        if css.has_attr('href'):
            old_relative_paths.append([css.attrs['href']])
    return old_relative_paths


def change_file_paths_in_files(mini_game_path, new_paths):
    files = get_all_files(mini_game_path)
    extensions = ('.gif', '.ico', '.jpeg', '.jpg', '.png', '.aif', '.cda', '.mid', '.mp3', '.mpa', '.ogg',
                  '.wav', '.wma', '.wpl', '.3g2', '.3gp', '.avi', '.flv', '.h264', '.m4v', '.mkv', '.mpeg',
                  '.mp4', '.mpg')
    count_img = 0
    for file in files:
        write = False
        if sum(set(map(lambda x: int(file.endswith(x)), ('.jpeg', '.jpg', '.png')))):
            md5_1 = md5sum(file)
            apply_watermark(file)
            change_md5_of_image(file)
            md5_2 = md5sum(file)
            if md5_1 == md5_2:
                count_img += 1

        if file.endswith('.js') or file.endswith('.html'):
            with open(file, encoding='utf8') as hkl:
                original = hkl.read()
                write = True
            if file.endswith('.html'):
                imports = []
                other_files = []
                from_html = parse_html(file)
            else:
                from_html = []
                imports = list(get_imported_files(file))
                other_files = get_paths_to_other_files(file)

            for old_relative_path in imports + other_files + from_html:
                html = False
                pre = False
                if old_relative_path[0:2] == './':
                    pre = True
                if isinstance(old_relative_path, type(list())):
                    old_relative_path = old_relative_path[0]
                    if old_relative_path[0:2] != './':
                        html = True
                        pre = False
                c = True
                for ex in extensions:
                    if ex in old_relative_path: c = False
                if c:
                    wd = '/'.join(file.split('/')[:-1])
                    if wd[0:2] == './':
                        old_path = os.path.normpath(os.path.join(wd, os.path.normpath(old_relative_path)))
                        if old_path[0:2] != './':
                            old_path = './' + old_path
                    else:
                        old_path = os.path.normpath(os.path.join(wd, os.path.normpath(old_relative_path)))
                    old_path = re.sub(r'\\', r'/', old_path)
                else:
                    old_path = mini_game_path + '/' + os.path.normpath(old_relative_path)
                    old_path = re.sub(r'\\', r'/', old_path)
                if old_path[-2:] == 'js':
                    old_path = old_path[:-2].rstrip('.')
                '''print(file)
                print(old_relative_path)
                print(old_path)'''
                try:
                    abc = ((os.path.exists(old_path) or os.path.exists(old_path + '.js')
                           or os.path.exists(old_path + '.css')) and not os.path.isdir(old_path))
                except:
                    abc = False
                if abc:
                    try:
                        new_path = new_paths[old_path]
                    except:
                        try:
                            new_path = new_paths[old_path + '.js']
                        except:
                            new_path = new_paths[old_path + '.css']
                    new_relative_path = re.sub(r'\\', r'/', os.path.relpath(new_path, os.path.dirname(new_paths[file])))
                    if './' not in new_relative_path[0:2] and '../' not in new_relative_path[0:3]:
                        new_relative_path = './' + new_relative_path
                    for ex in extensions:
                        if (ex in new_relative_path or html) and not pre:
                            new_relative_path = new_relative_path.lstrip('../').lstrip('./')
                    if old_relative_path[-3:] != '.js':
                        if new_relative_path[-3:] == '.js':
                            new_relative_path = new_relative_path[:-3]
                    '''
                    print(file)
                    print(old_relative_path)
                    #print(old_path)
                    print(new_relative_path, '\n')
                    #print(new_path)
                    
                    with open(file, encoding='utf8') as koko:
                        program_text = koko.read()
                        #program_text = program_text.replace(old_relative_path, new_relative_path)
                        #to_replace = r'\b' + old_relative_path.lstrip('../').lstrip('./') + r'\b'
                        #program_text = re.sub(to_replace, new_relative_path, program_text)
                        program_text = re.sub(re.escape(old_relative_path) + r'\b', new_relative_path, program_text)
                    if len(from_html) == 0:
                        program_text = replace_str_by_token_method(old_relative_path, new_relative_path, file)
                    else:
                        with open(file, encoding='utf8') as koko:
                            program_text = koko.read()
                        program_text = re.sub(re.escape(old_relative_path) + r'\b', new_relative_path, program_text)'''
                    with open(file, encoding='utf8') as koko:
                        program_text = koko.read()
                    program_text = re.sub(re.escape(old_relative_path) + r"\b", new_relative_path,
                                          program_text)
                    program_text = re.sub(re.escape(old_relative_path) + r'\b', new_relative_path,
                                          program_text)
                    # program_text = replace_str_by_token_method(old_relative_path, new_relative_path, file)
                    with open(file, 'w', encoding='utf8') as efj:
                        efj.write(program_text)
        shutil.copy2(file, new_paths[file])
        if write:
            with open(file, 'w', encoding='utf8') as fil:
                fil.write(original)
    if count_img:
        print('\n~ WARNING ~ Number of images with not changed md5:', count_img, '\n\n')


def shuffle_and_copy_files(src, dst):
    """
    Randomly copy every file from src to dst
    :param src: path to directory
    :param dst: path to another directory
    :return: old_paths - array, new_paths - object
    """
    excluded = {'raw-assets', 'index.js', 'cocos2d', 'index.js', 'main.js', 'libs'} # 'cocos2d','index.js', 'main.js', 'libs'
    make_new_directory_for(dst + '1.txt')
    files = get_all_files(src)
    new_paths = {}
    new_directories = []
    used_names = []
    for fil in [src + '/' + x for x in os.listdir(src + '/') if x != 'New_']:
        if os.path.isdir(fil):
            directories, used_names = come_up_with_new_directories([])
            new_directories.append(directories)
    for file in files:
        old_path = file
        statement = bool(min(set(map(lambda x: int(x not in file), excluded))))
        if os.path.dirname(file) != src and not file.endswith('.json') and statement:
            t = os.path.dirname(file)
            new_dirs = t.replace(src + '/', '').split('/')[0] + '/'
            ns = new_directories[randint(0, len(new_directories) - 1)]
            new_dirs += ns[randint(0, len(ns) - 1)]
            extension = '.' + str(file.split('.')[-1])
            if file not in ('main.js', 'game.js'):
                file, used_names = get_random_name(used_names)
                file += extension
        else:
            new_dirs = ''
            if not file.endswith('.json') and statement:
                file = file.split('/')[-1]
            else:
                file = file.replace(src, '').lstrip('/')
        new_path = dst + new_dirs + file
        make_new_directory_for(new_path)

        new_paths[old_path] = new_path

    return new_paths, used_names


def main():
    start_of_the_script = time()
    MINI_GAME_PATH = argv[1].rstrip('/')  # 'D:/Temp/Flappy_bird'
    output_path = argv[2].rstrip('/')
    n_times = int(argv[3])

    for i in range(n_times):
        print('\n~ Iteration #{} ~'.format(i + 1) + '\n')
        # Preparation
        start_time = time()
        if os.path.exists(os.path.dirname(output_path + '/New_{}/'.format(i + 1) + '1.txt')):
            shutil.rmtree(output_path + '/New_{}'.format(i + 1), ignore_errors=True)

        try:
            temp_folder = shutil.copytree(MINI_GAME_PATH, MINI_GAME_PATH + '/TEMP_FOLDer')
        except:
            shutil.rmtree(MINI_GAME_PATH + '/TEMP_FOLDer', ignore_errors=True)
            temp_folder = shutil.copytree(MINI_GAME_PATH, MINI_GAME_PATH + '/TEMP_FOLDer')
        # convert(temp_folder)

        new_game_path = temp_folder + '/New_{}/'.format(i + 1)
        if os.path.exists(os.path.dirname(new_game_path + '1.txt')):
            shutil.rmtree(new_game_path, ignore_errors=True)
        if os.path.exists('./temp_random_words.txt'):
            os.remove('./temp_random_words.txt')
        with open('./random_words.txt', encoding='utf8') as f:
            content = f.read()
            with open('./temp_random_words.txt', 'w', encoding='utf8') as fi:
                fi.write(content)
        print("--- Preparation: %s seconds ---\n" % (round(time() - start_time, 3)))

        # Shuffle, rename all directories, files and copy them to a new directory
        start_time = time()
        new_paths, used_names = shuffle_and_copy_files(temp_folder, new_game_path)
        print("--- Shuffle files: %s seconds ---\n" % (round(time() - start_time, 3)))
        change_file_paths_in_files(temp_folder, new_paths)
        print("--- Rename files: %s seconds ---\n" % (round(time() - start_time, 3)))

        # Convert the code
        start_time = time()
        convert(new_game_path)
        print("--- Conversion: %s seconds ---\n" % (round(time() - start_time, 3)))

        # Remove temp files
        shutil.copytree(new_game_path, output_path + '/New_{}'.format(i + 1))
        shutil.rmtree(temp_folder, ignore_errors=True)
        os.remove('./temp_random_words.txt')

    time_1 = round((time() - start_of_the_script) / 60, 3)
    time_2 = round(time() - start_of_the_script, 3)
    print("\n--- Script took: {} min ({} sec) ---".format(time_1, time_2))


if __name__ == '__main__':
    main()