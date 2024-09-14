import pytest
from seqpat import Pattern, Sequence, Choice, Repeat, R, T


def test_T_match():
    pattern = T("hello")
    seq = ["hello", "world"]

    result = pattern.parse(seq, 0)
    assert result == (["hello"], 1)

    result = pattern.parse(seq, 1)
    assert result is None


def test_R_match():
    pattern = R(r"^int\s+(\w+);$")
    seq = ["int a;", "int b;", "double c;"]

    result = pattern.parse(seq, 0)
    assert result == (["int a;"], 1)

    result = pattern.parse(seq, 1)
    assert result == (["int b;"], 2)

    result = pattern.parse(seq, 2)
    assert result is None


def test_Sequence():
    pattern = Sequence(T("int"), T("a"), T(";"))
    seq = ["int", "a", ";", "b"]

    result = pattern.parse(seq, 0)
    assert result == (["int", "a", ";"], 3)

    result = pattern.parse(seq, 3)
    assert result is None


def test_Choice():
    pattern = Choice(T("int"), T("double"))
    seq = ["int", "double", "float"]

    result = pattern.parse(seq, 0)
    assert result == (["int"], 1)

    result = pattern.parse(seq, 1)
    assert result == (["double"], 2)

    result = pattern.parse(seq, 2)
    assert result is None


def test_Repeat():
    pattern = Repeat(T("int"), count=3)
    seq = ["int", "int", "int", "double"]

    result = pattern.parse(seq, 0)
    assert result == (["int", "int", "int"], 3)

    result = pattern.parse(seq, 3)
    assert result is None


def test_Repeat_with_separator():
    pattern = Repeat(T("int"), count=(1, 3), sep=";")
    seq = ["int", "int", "int", "double"]

    result = pattern.parse(seq, 0)
    assert result == (["int", ";", "int", ";", "int"], 3)

    result = pattern.parse(seq, 3)
    assert result is None

    pattern = Repeat(T("int"), count=2, sep=";")
    result = pattern.parse(seq, 0)
    assert result == (["int", ";", "int"], 2)
