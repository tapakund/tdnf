#
# Copyright (C) 2019 - 2020 VMware, Inc. All Rights Reserved.
#
# Licensed under the GNU General Public License v2 (the "License");
# you may not use this file except in compliance with the License. The terms
# of the License are located in the COPYING file of this distribution.
#
#   Author: Siddharth Chandrasekaran <csiddharth@vmware.com>

import os
import tempfile
import pytest

@pytest.fixture(scope='module', autouse=True)
def setup_test(utils):
    yield
    teardown_test(utils)

def teardown_test(utils):
    for pkg in ("mulversion_pkgname", "requiring_package", "required_package") :
        pkgname = utils.config[pkg]
        utils.run(['tdnf', 'erase', '-y', pkgname])

# specifying the version should not override the exclude (negative test)
def test_install_package_with_version_suffix(utils):
    pkgname = utils.config["mulversion_pkgname"]
    pkgversion = utils.config["mulversion_lower"]
    utils.erase_package(pkgname)

    utils.run([ 'tdnf', 'install', '--exclude=', pkgname, '-y', '--nogpgcheck', pkgname + '-' + pkgversion ])
    assert(utils.check_package(pkgname) == False)

# basic test (negative test)
def test_install_package_without_version_suffix(utils):
    pkgname = utils.config["mulversion_pkgname"]
    utils.erase_package(pkgname)

    utils.run([ 'tdnf', 'install', '--exclude=', pkgname, '-y', '--nogpgcheck', pkgname ])
    assert(utils.check_package(pkgname) == False)

# excluded dependency (negative test)
def test_install_package_with_excluded_dependency(utils):
    pkgname = utils.config["requiring_package"]
    pkgname_required = utils.config["required_package"]
    utils.erase_package(pkgname)
    utils.erase_package(pkgname_required)

    utils.run([ 'tdnf', 'install', '--exclude=', pkgname_required, '-y', '--nogpgcheck', pkgname ])
    assert(utils.check_package(pkgname) == False)

# an update should skip an excluded package (negative test)
def test_update_package(utils):
    pkgname = utils.config["mulversion_pkgname"]
    pkgversion1 = utils.config["mulversion_lower"]
    pkgversion2 = utils.config["mulversion_higher"]

    if '-' in pkgversion1:
        pkgversion1 = pkgversion1.split('-')[0]
    if '-' in pkgversion2:
        pkgversion2 = pkgversion2.split('-')[0]

    utils.erase_package(pkgname)

    utils.run([ 'tdnf', 'install', '-y', '--nogpgcheck', pkgname + '-' + pkgversion1 ])
    assert(utils.check_package(pkgname, pkgversion1) == True)

    utils.run([ 'tdnf', 'update', '--exclude=', pkgname, '-y', '--nogpgcheck', pkgname + '-' + pkgversion2 ])
    assert(utils.check_package(pkgname, pkgversion2) == False)
    assert(utils.check_package(pkgname, pkgversion1) == True)

# removing an excluded package should fail (dnf behavior) (negative test)
def test_remove_package(utils):
    pkgname = utils.config["mulversion_pkgname"]

    utils.run([ 'tdnf', 'install', '-y', '--nogpgcheck', pkgname ])

    utils.run([ 'tdnf', 'remove', '--exclude=', pkgname, '-y', '--nogpgcheck', pkgname ])
    # package should still be there
    assert(utils.check_package(pkgname) == True)

