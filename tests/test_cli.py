from unittest import mock

import pyecore
import pytest
from pyecoregen.cli import generate_from_cli, select_uri_implementation


@mock.patch('pyecoregen.cli.EcoreGenerator')
def test__generate_from_cli(generator_mock, cwd_module_dir):
    mock_generator = generator_mock()
    mock_generator.generate = mock.MagicMock()

    generate_from_cli(['-e', 'input/library.ecore', '-o', 'some/folder'])

    # look at arguments of generate call:
    mock_generate = generator_mock().generate
    model = mock_generator.generate.call_args[0][0]
    path = mock_generator.generate.call_args[0][1]
    global_vars = mock_generator.generate.call_args[1]['global_vars']

    assert isinstance(model, pyecore.ecore.EPackage)
    assert model.name == 'library'
    assert path == 'some/folder'
    assert not global_vars['auto_register_package']
    assert global_vars['out_folder'] == 'some/folder'
    assert global_vars['ecore_model'] == 'input/library.ecore'


@mock.patch('pyecoregen.cli.EcoreGenerator')
def test__generate_from_cli_autoregistration(generator_mock, cwd_module_dir):
    mock_generator = generator_mock()
    mock_generator.generate = mock.MagicMock()

    generate_from_cli(['-e', 'input/library.ecore', '-o', 'some/folder', '-a'])

    # look at arguments of generate call:
    mock_generate = generator_mock().generate
    model = mock_generator.generate.call_args[0][0]
    path = mock_generator.generate.call_args[0][1]
    global_vars = mock_generator.generate.call_args[1]['global_vars']

    assert isinstance(model, pyecore.ecore.EPackage)
    assert model.name == 'library'
    assert path == 'some/folder'
    assert global_vars['auto_register_package']
    assert global_vars['out_folder'] == 'some/folder'
    assert global_vars['ecore_model'] == 'input/library.ecore'


@mock.patch('pyecoregen.cli.EcoreGenerator')
def test__generate_from_cli(generator_mock, cwd_module_dir):
    mock_generator = generator_mock()
    mock_generator.generate = mock.MagicMock()

    generate_from_cli(['-e', 'input/library.ecore', '-o', 'some/folder'])

    # look at arguments of generate call:
    mock_generate = generator_mock().generate
    model = mock_generator.generate.call_args[0][0]
    path = mock_generator.generate.call_args[0][1]

    assert isinstance(model, pyecore.ecore.EPackage)
    assert model.name == 'library'
    assert path == 'some/folder'


testdata = [
    ('/tmp/test.ecore', pyecore.resources.URI),
    ('C:\\test.ecore', pyecore.resources.URI),
    ('./test.ecore', pyecore.resources.URI),
    ('test.ecore', pyecore.resources.URI),
    ('http://test.com/myuri.ecore', pyecore.resources.resource.HttpURI),
    ('http://test.com/myuri', pyecore.resources.resource.HttpURI),
    ('https://test.com/myuri.ecore', pyecore.resources.resource.HttpURI),
    ('https://test.com/mypath?path=uri.ecore', pyecore.resources.resource.HttpURI),
]


@pytest.mark.parametrize("path, implementation", testdata)
def test__selected_uri(path, implementation):
    uri = select_uri_implementation(path)
    assert uri is implementation
