import json, re
from urllib.request import urlopen as open_url, Request


def get(url, **headers):
    return open_url(Request(url, headers=headers))


def package_info(name):
    json_mime = 'application/vnd.pypi.simple.v1+json'
    with get('https://pypi.org/simple/' + name, accept=json_mime) as data:
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
        return 'source', '{}-{}.tar.gz'.format(name, version)


def download(into, name, version, *tags):
    prefix = 'https://files.pythonhosted.org/packages'
    folder, filename = _folder_and_file(name, version, *tags)
    url = '{}/{}/{}/{}/{}'.format(prefix, folder, name[0], name, filename)
    destination = into / filename
    destination.parent.mkdir(parents=True, exist_ok=True)
    with get(url) as data:
        destination.write_bytes(data.read())
