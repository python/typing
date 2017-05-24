import glob
import os
import re
from subprocess import Popen, PIPE
from typing import Text, List, Iterable, Tuple, Any

import pytest
import yaml


DEFAULT_PATH = 'main.py'
ENCODING = 'utf-8'


def load_test_cases(root: Text) -> Iterable[Tuple[Text, Text, List[dict]]]:
    paths = glob.glob(os.path.join(root, '*.yml'))
    assert paths, 'No test data found in %s' % os.path.abspath(root)

    for path in paths:
        with open(path, 'rb') as fd:
            raw_data = yaml.load(fd)
        for case in raw_data:
            _, filename = os.path.split(path)
            name = case.get('case')
            assert name, 'Unnamed case: %r' % case
            files = case.get('files', [])
            unique = {file.get('path', DEFAULT_PATH) for file in files}
            assert len(files) == len(unique), 'Duplicate files in %s' % name
            yield filename, name, files


def inline_errors(errors: List[Text], files: List[dict]) -> List[dict]:
    contents = {
        file.get('path', DEFAULT_PATH): strip_errors(file.get('content', ''))
        for file in files}

    for error in errors:
        index, message, path = parse_error_line(error)
        content = contents.get(path)
        assert content, 'Cannot find contents of %s' % path
        lines = content.splitlines(keepends=True)
        assert 0 <= index < len(lines)
        line = lines[index]
        updated = '%s# E: %s\n' % (line.rstrip('\n'), message)
        lines[index] = updated
        contents[path] = ''.join(lines)

    results = [file.copy() for file in files]
    for result in results:
        result['content'] = contents.get(result.get('path', DEFAULT_PATH), '')
    return results


def strip_errors(s: Text) -> Text:
    return re.sub(r'#\s*E:.*', r'', s)


def parse_error_line(line: Text) -> Tuple[int, Text, Text]:
    m = re.match(r'(.+):([0-9]+): (error): (.+)', line)
    assert m, 'Cannot parse output line: %s' % line
    path = m.group(1)
    index = int(m.group(2)) - 1
    message = m.group(4)
    return index, message, path


@pytest.mark.parametrize('filename,case,files', load_test_cases('test-data'))
def test_yaml_case(filename: Text, case: Text, files: List[dict],
                   tmpdir: Any) -> None:
    assert filename
    assert case

    for file in files:
        path = file.get('path', DEFAULT_PATH)
        dirname, filename = os.path.split(path)
        filedir = tmpdir.mkdir(dirname) if dirname else tmpdir
        with filedir.join(filename).open('w', encoding=ENCODING) as fd:
            fd.write(file.get('content', ''))

    tmpdir.chdir()

    with Popen(['mypy', '.'], stdout=PIPE, stderr=PIPE) as proc:
        stdout, stderr = proc.communicate()

    output = stdout + b'\n' + stderr
    output_lines = output.decode(ENCODING).strip().splitlines()
    actual_files = inline_errors(output_lines, files)
    for expected, actual in zip(files, actual_files):
        assert expected.get('content', '') == actual.get('content', '')
