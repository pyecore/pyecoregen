"""Command line interface for generation of static Python classes from Ecore model."""
import argparse
import collections
import logging
import sys
import re

import pyecore.resources
from pyecoregen.ecore import EcoreGenerator

URL_PATTERN = re.compile('^http(s)?://.*')


def main():
    generate_from_cli(sys.argv[1:])  # nocover


def generate_from_cli(args):
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate Python classes from an Ecore model.")
    parser.add_argument(
        '--ecore-model',
        '-e',
        help="Path to Ecore XMI file.",
        required=True
    )
    parser.add_argument(
        '--out-folder',
        '-o',
        help="Path to directory, where output files are generated.",
        required=True
    )
    parser.add_argument(
        '--auto-register-package',
        help="Generate package auto-registration for the PyEcore 'global_registry'.",
        action='store_true'
    )
    parser.add_argument(
        '--user-module',
        help="Dotted name of module with user-provided mixins to import from generated classes.",
    )
    parser.add_argument(
        '--with-dependencies',
        help="Generates code for every metamodel the input metamodel depends on.",
        action='store_true'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        help="Increase logging verbosity.",
        action='count'
    )

    parsed_args = parser.parse_args(args)

    configure_logging(parsed_args)
    model = load_model(parsed_args.ecore_model)
    EcoreGenerator(
        auto_register_package=parsed_args.auto_register_package,
        user_module=parsed_args.user_module,
        with_dependencies=parsed_args.with_dependencies
    ).generate(model, parsed_args.out_folder)


def configure_logging(parsed_args):
    loglevel_map = collections.defaultdict(lambda: logging.WARNING)
    loglevel_map.update({
        1: logging.INFO,
        2: logging.DEBUG
    })
    logging.basicConfig(
        format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
        level=loglevel_map[parsed_args.verbose]
    )


def select_uri_implementation(ecore_model_path):
    """Select the right URI implementation regarding the Ecore model path schema."""
    if URL_PATTERN.match(ecore_model_path):
        return pyecore.resources.resource.HttpURI
    return pyecore.resources.URI


def load_model(ecore_model_path):
    """Load a single Ecore model and return the root package."""
    rset = pyecore.resources.ResourceSet()
    uri_implementation = select_uri_implementation(ecore_model_path)
    resource = rset.get_resource(uri_implementation(ecore_model_path))
    return resource.contents[0]


if __name__ == '__main__':  # nocover
    main()
