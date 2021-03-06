#-----------------------------------------------------------------------------
# Copyright (c) 2012 - 2017, Anaconda, Inc. All rights reserved.
#
# Powered by the Bokeh Development Team.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Boilerplate
#-----------------------------------------------------------------------------
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest ; pytest

from bokeh.util.api import INTERNAL, PUBLIC ; INTERNAL, PUBLIC
from bokeh.util.testing import verify_api ; verify_api

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from mock import Mock, patch, PropertyMock

# External imports

# Bokeh imports

# Module under test
import bokeh.io.util as biu

#-----------------------------------------------------------------------------
# API Definition
#-----------------------------------------------------------------------------

api = {

    PUBLIC: (

    ), INTERNAL: (

        ( 'default_filename',        (1, 0, 0) ),
        ( 'detect_current_filename', (1, 0, 0) ),
        ( 'temp_filename',           (1, 0, 0) ),

    )

}

Test_api = verify_api(biu, api)

#-----------------------------------------------------------------------------
# Setup
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Public API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Internal API
#-----------------------------------------------------------------------------

def test_detect_current_filename():
    assert biu.detect_current_filename().endswith("py.test")

@patch('bokeh.io.util.NamedTemporaryFile')
def test_temp_filename(mock_tmp):
    fn = Mock()
    type(fn).name = PropertyMock(return_value="Junk.test")
    mock_tmp.return_value = fn

    r = biu.temp_filename("test")
    assert r == "Junk.test"
    assert mock_tmp.called
    assert mock_tmp.call_args[0] == ()
    assert mock_tmp.call_args[1] == {'suffix': '.test'}

def test_default_filename():
    old_detect_current_filename = biu.detect_current_filename
    old__no_access = biu._no_access
    old__shares_exec_prefix = biu._shares_exec_prefix

    biu.detect_current_filename = lambda : "/a/b/foo.py"

    try:
        # .py extension
        with pytest.raises(RuntimeError):
            biu.default_filename("py")

        # a current file, access, and no share exec
        biu._no_access = lambda x: False
        r = biu.default_filename("test")
        assert r == "/a/b/foo.test"

        # a current file, NO access, and no share exec
        biu._no_access = lambda x: True
        r = biu.default_filename("test")
        assert r != "/a/b/foo.test"
        assert r.endswith(".test")

        # a current file, access, but WITH share exec
        biu._no_access = lambda x: False
        biu._shares_exec_prefix = lambda x: True
        r = biu.default_filename("test")
        assert r != "/a/b/foo.test"
        assert r.endswith(".test")

        # no current file
        biu.detect_current_filename = lambda : None
        biu._no_access = lambda x: False
        biu._shares_exec_prefix = lambda x: False
        r = biu.default_filename("test")
        assert r != "/a/b/foo.test"
        assert r.endswith(".test")

    finally:
        biu.detect_current_filename = old_detect_current_filename
        biu._no_access = old__no_access
        biu._shares_exec_prefix = old__shares_exec_prefix

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

@patch('os.access')
def test__no_access(mock_access):
    import os
    biu._no_access("test")
    assert mock_access.called
    assert mock_access.call_args[0] == ("test", os.W_OK | os.X_OK)
    assert mock_access.call_args[1] == {}

def test__shares_exec_prefix():
    import sys
    old_ex = sys.exec_prefix
    try:
        sys.exec_prefix = "/foo/bar"
        assert biu._shares_exec_prefix("/foo/bar") == True
        sys.exec_prefix = "/baz/bar"
        assert biu._shares_exec_prefix("/foo/bar") == False
        sys.exec_prefix = None
        assert biu._shares_exec_prefix("/foo/bar") == False
    finally:
        sys.exec_prefix = old_ex
