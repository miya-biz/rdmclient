"""Test `osf ls` command"""

from dateutil import tz
from mock import call
from mock import patch

from osfclient import OSF
from osfclient.cli import list_
from osfclient.models import OSFCore

from osfclient.tests import fake_responses
from osfclient.tests.mocks import MockProject
from osfclient.tests.mocks import MockArgs
from osfclient.tests.mocks import FakeResponse


@patch('osfclient.cli.OSF')
def test_anonymous_doesnt_use_password(MockOSF):
    args = MockArgs(project='1234')

    def simple_getenv(key):
        return None

    with patch('osfclient.cli.os.getenv',
               side_effect=simple_getenv) as mock_getenv:
        list_(args)

    # if there is no username we should not try to obtain a password either
    assert call('OSF_USERNAME') in mock_getenv.mock_calls
    assert call('OSF_PASSWORD') not in mock_getenv.mock_calls
    MockOSF.assert_called_once_with(username=None, password=None, token=None,
                                    base_url=None)


@patch('osfclient.cli.OSF')
def test_username_password(MockOSF):
    args = MockArgs(username='joe@example.com', project='1234')

    def simple_getenv(key):
        if key == 'OSF_PASSWORD':
            return 'secret'

    with patch('osfclient.cli.os.getenv',
               side_effect=simple_getenv) as mock_getenv:
        list_(args)

    MockOSF.assert_called_once_with(username='joe@example.com',
                                    password='secret', token=None,
                                    base_url=None)
    mock_getenv.assert_called_with('OSF_PASSWORD')


@patch('osfclient.cli.OSF')
def test_token(MockOSF):
    args = MockArgs(project='1234')

    def simple_getenv(key):
        if key == 'OSF_TOKEN':
            return 'secret'

    with patch('osfclient.cli.os.getenv',
               side_effect=simple_getenv) as mock_getenv:
        list_(args)

    MockOSF.assert_called_once_with(username=None,
                                    password=None, token='secret',
                                    base_url=None)
    mock_getenv.assert_called_with('OSF_TOKEN')


@patch('osfclient.cli.OSF')
def test_base_url(MockOSF):
    args = MockArgs(base_url='https://api.test.osf.io/v2/', project='1234')

    def simple_getenv(key):
        if key == 'OSF_TOKEN':
            return 'secret'

    with patch('osfclient.cli.os.getenv',
               side_effect=simple_getenv) as mock_getenv:
        list_(args)

    MockOSF.assert_called_once_with(username=None,
                                    password=None, token='secret',
                                    base_url='https://api.test.osf.io/v2/')
    mock_getenv.assert_called_with('OSF_TOKEN')


def test_list(capsys):
    args = MockArgs(project='f3szh')

    njson = fake_responses._build_node('nodes')
    rjson = fake_responses.files_node('f3szh', 'osfstorage',
                                      file_names=['hello.txt', 'bye.txt'],
                                      folder_names=['folder1', 'folder2'])
    fjson1 = fake_responses.files_node('f3szh', 'osfstorage',
                                       file_names=['folder1/folder1content.txt'])
    fjson2 = fake_responses.files_node('f3szh', 'osfstorage',
                                       file_names=['folder2/folder2content.txt'])
    sjson = fake_responses.storage_node('f3szh', ['osfstorage'])

    def simple_OSFCore_get(url):
        if url == 'https://api.osf.io/v2//nodes/f3szh/':
            return FakeResponse(200, njson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/':
            return FakeResponse(200, sjson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/osfstorage/':
            return FakeResponse(200, rjson)
        elif url == 'https://api.osf.io/v2/nodes/9zpcy/files/osfstorage/folder1123/':
            return FakeResponse(200, fjson1)
        elif url == 'https://api.osf.io/v2/nodes/9zpcy/files/osfstorage/folder2123/':
            return FakeResponse(200, fjson2)
        elif url == 'https://api.osf.io/v2//guids/f3szh/':
            return FakeResponse(200, {'data': {'type': 'nodes'}})
        else:
            print(url)
            raise ValueError()

    with patch.object(OSFCore, '_get',
                      side_effect=simple_OSFCore_get) as mock_osf_get:
        list_(args)
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out.split('\n') == ['osfstorage/bye.txt',
                                        'osfstorage/hello.txt',
                                        'osfstorage/folder2/folder2content.txt',
                                        'osfstorage/folder1/folder1content.txt',
                                        '']


def test_sublist_exists(capsys):
    args = MockArgs(project='f3szh', base_path='osfstorage/folder2/')

    njson = fake_responses._build_node('nodes')
    rjson = fake_responses.files_node('f3szh', 'osfstorage',
                                      file_names=['hello.txt', 'bye.txt'],
                                      folder_names=['folder1', 'folder2'])
    fjson1 = fake_responses.files_node('f3szh', 'osfstorage',
                                       file_names=['folder1/folder1content.txt'])
    fjson2 = fake_responses.files_node('f3szh', 'osfstorage',
                                       file_names=['folder2/folder2content.txt'])
    sjson = fake_responses.storage_node('f3szh', ['osfstorage'])

    def simple_OSFCore_get(url):
        if url == 'https://api.osf.io/v2//nodes/f3szh/':
            return FakeResponse(200, njson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/':
            return FakeResponse(200, sjson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/osfstorage/':
            return FakeResponse(200, rjson)
        elif url == 'https://api.osf.io/v2/nodes/9zpcy/files/osfstorage/folder2123/':
            return FakeResponse(200, fjson2)
        elif url == 'https://api.osf.io/v2//guids/f3szh/':
            return FakeResponse(200, {'data': {'type': 'nodes'}})
        else:
            print(url)
            raise ValueError()

    with patch.object(OSFCore, '_get',
                      side_effect=simple_OSFCore_get) as mock_osf_get:
        list_(args)
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out.split('\n') == ['osfstorage/folder2/folder2content.txt', '']


def test_sublist_empty(capsys):
    args = MockArgs(project='f3szh', base_path='googledrive/')

    njson = fake_responses._build_node('nodes')
    sjson = fake_responses.storage_node('f3szh', ['osfstorage'])

    def simple_OSFCore_get(url):
        if url == 'https://api.osf.io/v2//nodes/f3szh/':
            return FakeResponse(200, njson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/':
            return FakeResponse(200, sjson)
        elif url == 'https://api.osf.io/v2//guids/f3szh/':
            return FakeResponse(200, {'data': {'type': 'nodes'}})
        else:
            print(url)
            raise ValueError()

    with patch.object(OSFCore, '_get',
                      side_effect=simple_OSFCore_get) as mock_osf_get:
        list_(args)
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out.split('\n') == ['']


def test_sublist_exists(capsys):
    args = MockArgs(project='f3szh', base_path='/osfstorage/folder2')

    njson = fake_responses._build_node('nodes')
    rjson = fake_responses.files_node('f3szh', 'osfstorage',
                                      file_names=['hello.txt', 'bye.txt'],
                                      folder_names=['folder1', 'folder2'])
    fjson1 = fake_responses.files_node('f3szh', 'osfstorage',
                                       file_names=['folder1/folder1content.txt'])
    fjson2 = fake_responses.files_node('f3szh', 'osfstorage',
                                       file_names=['folder2/folder2content.txt'])
    sjson = fake_responses.storage_node('f3szh', ['osfstorage'])

    def simple_OSFCore_get(url):
        if url == 'https://api.osf.io/v2//nodes/f3szh/':
            return FakeResponse(200, njson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/':
            return FakeResponse(200, sjson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/osfstorage/':
            return FakeResponse(200, rjson)
        elif url == 'https://api.osf.io/v2/nodes/9zpcy/files/osfstorage/folder2123/':
            return FakeResponse(200, fjson2)
        elif url == 'https://api.osf.io/v2//guids/f3szh/':
            return FakeResponse(200, {'data': {'type': 'nodes'}})
        else:
            print(url)
            raise ValueError()

    with patch.object(OSFCore, '_get',
                      side_effect=simple_OSFCore_get) as mock_osf_get:
        list_(args)
    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out.split('\n') == ['osfstorage/folder2/folder2content.txt', '']


def test_long_format_list(capsys):
    args = MockArgs(project='f3szh', long_format=True)

    dates = ['"2019-02-20T14:02:00.000000Z"', '"2019-02-19T17:01:00.000000Z"']
    njson = fake_responses._build_node('nodes')
    fjson = fake_responses.files_node('f3szh', 'osfstorage',
                                      file_names=['hello.txt', 'bye.txt'],
                                      file_sizes=['5', '3'],
                                      file_dates_modified=dates)
    sjson = fake_responses.storage_node('f3szh', ['osfstorage'])

    def simple_OSFCore_get(url):
        if url == 'https://api.osf.io/v2//nodes/f3szh/':
            return FakeResponse(200, njson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/':
            return FakeResponse(200, sjson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/osfstorage/':
            return FakeResponse(200, fjson)
        elif url == 'https://api.osf.io/v2//guids/f3szh/':
            return FakeResponse(200, {'data': {'type': 'nodes'}})
        else:
            print(url)
            raise ValueError()

    with patch('osfclient.cli.get_localzone',
               return_value=tz.tzutc()) as mock_get_localzone:
        with patch.object(OSFCore, '_get',
                          side_effect=simple_OSFCore_get) as mock_osf_get:
            list_(args)
    captured = capsys.readouterr()
    assert captured.err == ''
    expected = ['2019-02-19 17:01:00 3 osfstorage/bye.txt',
                '2019-02-20 14:02:00 5 osfstorage/hello.txt', '']
    assert captured.out.split('\n') == expected


def test_long_format_list_with_null(capsys):
    args = MockArgs(project='f3szh', long_format=True)

    dates = ['null', 'null']
    njson = fake_responses._build_node('nodes')
    fjson = fake_responses.files_node('f3szh', 'osfstorage',
                                      file_names=['hello.txt', 'bye.txt'],
                                      file_sizes=['null', 'null'],
                                      file_dates_modified=dates)
    sjson = fake_responses.storage_node('f3szh', ['osfstorage'])

    def simple_OSFCore_get(url):
        if url == 'https://api.osf.io/v2//nodes/f3szh/':
            return FakeResponse(200, njson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/':
            return FakeResponse(200, sjson)
        elif url == 'https://api.osf.io/v2/nodes/f3szh/files/osfstorage/':
            return FakeResponse(200, fjson)
        elif url == 'https://api.osf.io/v2//guids/f3szh/':
            return FakeResponse(200, {'data': {'type': 'nodes'}})
        else:
            print(url)
            raise ValueError()

    with patch('osfclient.cli.get_localzone',
               return_value=tz.tzutc()) as mock_get_localzone:
        with patch.object(OSFCore, '_get',
                          side_effect=simple_OSFCore_get) as mock_osf_get:
            list_(args)
    captured = capsys.readouterr()
    assert captured.err == ''
    expected = ['- - - osfstorage/bye.txt',
                '- - - osfstorage/hello.txt', '']
    assert captured.out.split('\n') == expected


@patch.object(OSF, 'project', return_value=MockProject('1234'))
def test_get_project(OSF_project):
    args = MockArgs(project='1234')

    list_(args)

    OSF_project.assert_called_once_with('1234')
    # check that the project and the files have been printed
    for store in OSF_project.return_value.storages:
        assert store._name_mock.called
        for f in store.files:
            assert f._path_mock.called
