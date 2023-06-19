import pytest

import f3dasm_simulate


def test_add_one():
    assert f3dasm_simulate.add_one(1) == 2