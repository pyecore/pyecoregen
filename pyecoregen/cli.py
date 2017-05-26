"""Command line interface for generation of static Python classes from Ecore model."""
import argparse

import sys

import pyecore.resources
from pyecoregen.ecore import EcoreGenerator


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

    parsed_args = parser.parse_args(args)
    model = load_model(parsed_args.ecore_model)
    EcoreGenerator().generate(model, parsed_args.out_folder)


def load_model(ecore_model_path):
    """Load a single Ecore model and return the root package."""
    rset = pyecore.resources.ResourceSet()
    resource = rset.get_resource(pyecore.resources.URI(ecore_model_path))
    model = resource.contents[0]
    rset.metamodel_registry[model.nsURI] = model
    return model


if __name__ == '__main__':  # nocover
    main()
