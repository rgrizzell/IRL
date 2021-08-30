#!/usr/bin/env python
import circup
import shutil
import os
import pathlib


def copy_code(source=None, destination=None):
    """
    Copies files to the CircuitPython device.

    :param source:
    :param destination:
    :return boolean:
    """
    if not source:
        source = os.path.dirname(os.path.realpath(__file__)) + '/../circuitpython/code.py'
    if not destination:
        destination = circup.find_device()
        print(f"Found device: {destination}")

    try:
        shutil.copyfile(str(source), str(destination) + '/code.py')
    except Exception as e:
        print(e)
        return False

    return True


def update_libraries(destination=None):
    """
    Trigger circup and update the device.
    TODO: Get this to work: `ModuleNotFoundError: No module named 'board'`

    :param destination:
    :return:
    """
    if not destination:
        destination = circup.find_device()

    requirement = 'requirements.txt'

    available_modules = circup.get_bundle_versions(circup.get_bundles_list())
    mod_names = {}
    for module, metadata in available_modules.items():
        mod_names[module.replace(".py", "").lower()] = metadata

    cwd = os.path.abspath(os.getcwd())
    requirements_txt = open(cwd + "/" + requirement, "r").read()
    requested_installs = sorted(set(circup.libraries_from_requirements(requirements_txt)))

    to_install = circup.get_dependencies(requested_installs, mod_names=mod_names)
    device_modules = circup.get_device_versions(destination)
    if to_install is not None:
        to_install = sorted(to_install)

        for library in to_install:
            circup.install_module(
                destination, device_modules, library, False, mod_names
            )


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Installs the latest CircuitPython code onto the device'
    )

    parser.add_argument(
        '-d', '--destination',
        help='Destination to deploy the CircuitPython code to.',
        type=pathlib.Path
    )

    parser.add_argument(
        '-s', '--source',
        help='Source of the CircuitPython code.',
        type=pathlib.Path
    )

    parser.add_argument(
        '-y', '--yes',
        action='store_true',
        help='Deployment mode, skips confirmation prompt.',
        default=False
    )

    args = parser.parse_args()
    print(args)
    if copy_code(args.source, args.destination):
        print("Code copied to device!")
        exit(0)
