import json, re
from urllib.request import urlopen as open_url, Request


def get(url, **headers):
    return open_url(Request(url, headers=headers))


def package_info(name):
    json_mime = 'application/vnd.pypi.simple.v1+json'
    with get(f'https://pypi.org/simple/{name}', accept=json_mime) as data:
        return json.load(data)


def _normalize_tag(tag):
    return re.sub(r'[^\w\d.]+', '_', tag, re.UNICODE)


def tags_to_parts(python, abi, platform, build=None):
    parts = list(map(_normalize_tag, (python, abi, platform)))
    if build is not None:
        parts.insert(0, _normalize_tag(build))
    return parts


def _folder_and_file(name, version, *tags):
    if tags: # wheel
        parts = tags_to_parts(*tags)
        return tags[0], '-'.join([name, version, *parts]) + '.whl'
    else: # sdist
        return 'source', f'{name}-{version}.tar.gz'


def download(name, version, *tags):
    host = 'https://files.pythonhosted.org'
    folder, filename = _folder_and_file(name, version, *tags)
    url = f'{host}/packages/{folder}/{name[0]}/{name}/{filename}'
    with get(url) as data, open(filename, 'wb') as f:
        f.write(data.read())
