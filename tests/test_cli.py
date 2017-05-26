from unittest import mock

import pyecore.ecore
from pyecoregen.cli import generate_from_cli


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
