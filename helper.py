import base64
import hashlib
import yaml

def load_file(file_name):
    file = open(file_name, encoding='utf8')
    result = file.read()
    file.close()
    return result

def load_yaml_file(file_name):
    return yaml.load(load_file(file_name))

def load_strings_file(file_name):
    file = open(file_name, encoding='utf8')
    result = file.readlines()
    file.close()
    return result

def datafile2url(data,directory,url):
    r = None
    try:
        i1 = data.index('data:image/')
        index = data.index('base64,')
        # index = data.index('data:image/jpeg;base64,')
        if i1 >=0 and index >= 0 and ((index - i1) == len('data:image/jpeg;') or (index - i1) == len('data:image/png;')):
            body = data[index + len('base64,'):]
            md5 = hashlib.md5(body.encode('utf-8'))
            filename = '{0}.jpg'.format(md5.hexdigest())
            fh = open(directory + filename, "wb")
            fh.write(base64.b64decode(body))
            fh.close()
            r = url + filename
    except:
        pass
    return r


def dict1base64file2dict(data: dict,directory,url):
    for (d, x) in data.items():
        if isinstance(x, list):
            array1base64file2dict(x,directory,url)
        if isinstance(x, str):
            c = datafile2url(x,directory,url)
            if c is not None:
                data[d] = c
        if isinstance(x, dict):
            dict1base64file2dict(x,directory,url)


def array1base64file2dict(data1: list,directory,url):
    for idx, d in enumerate(data1):
        if isinstance(d, str):
            c = datafile2url(d,directory,url)
            if c is not None:
                data1[idx] = c
        if isinstance(d, dict):
            dict1base64file2dict(d,directory,url)
        if isinstance(d, list):
            array1base64file2dict(d,directory,url)
