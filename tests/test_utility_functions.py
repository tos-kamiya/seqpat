import pytest
from seqpat import R, T, gsub, split_by


def test_gsub():
    pattern = T("int", repl=["INTEGER"])
    seq = ["int", "a", "int", "b", "double"]

    result = gsub(pattern, seq)
    assert result == ["INTEGER", "a", "INTEGER", "b", "double"]

    pattern = R(r"int\s+(\w+);", repl=["INTEGER"])
    seq = ["int a;", "int b;", "double c;"]

    result = gsub(pattern, seq)
    assert result == ["INTEGER", "INTEGER", "double c;"]


def test_gsub_with_repeat():
    pattern = T("int", repl=["INTEGER"]) * 2
    seq = ["int", "int", "double"]

    result = gsub(pattern, seq)
    assert result == ["INTEGER", "INTEGER", "double"]


def test_split_by():
    pattern = T(";")
    seq = ["int", "a", ";", "double", "b", ";", "float", "c"]

    result = split_by(pattern, seq)
    assert result == [["int", "a"], ["double", "b"], ["float", "c"]]

    result = split_by(pattern, seq, keep_delimiters=True)
    assert result == [["int", "a"], [";"], ["double", "b"], [";"], ["float", "c"]]


def test_split_by_no_delimiter():
    pattern = T(";")
    seq = ["int", "a", "double", "b", "float", "c"]

    result = split_by(pattern, seq)
    assert result == [["int", "a", "double", "b", "float", "c"]]


def test_split_by_all_delimiters():
    pattern = T(";")
    seq = [";", ";", ";"]

    result = split_by(pattern, seq)
    assert result == [[], [], [], []], f"Expected [[], [], [], []] but got {result}"


def test_split_by_with_regex():
    pattern = R(r";")
    seq = ["int", "a", ";", "double", "b", ";", "float", "c"]

    result = split_by(pattern, seq)
    assert result == [["int", "a"], ["double", "b"], ["float", "c"]]

    result = split_by(pattern, seq, keep_delimiters=True)
    assert result == [["int", "a"], [";"], ["double", "b"], [";"], ["float", "c"]]


def test_split_by_delimiter_at_start():
    pattern = T(";")
    seq = [";", "int", "a", "double", "b", "float", "c"]

    result = split_by(pattern, seq)
    assert result == [[], ["int", "a", "double", "b", "float", "c"]]

    result = split_by(pattern, seq, keep_delimiters=True)
    assert result == [[], [";"], ["int", "a", "double", "b", "float", "c"]]


def test_split_by_delimiter_at_end():
    pattern = T(";")
    seq = ["int", "a", "double", "b", "float", "c", ";"]

    result = split_by(pattern, seq)
    assert result == [["int", "a", "double", "b", "float", "c"], []]

    result = split_by(pattern, seq, keep_delimiters=True)
    assert result == [["int", "a", "double", "b", "float", "c"], [";"], []]


def test_split_by_delimiter_at_start_and_end():
    pattern = T(";")
    seq = [";", "int", "a", "double", "b", "float", "c", ";"]

    result = split_by(pattern, seq)
    assert result == [[], ["int", "a", "double", "b", "float", "c"], []]

    result = split_by(pattern, seq, keep_delimiters=True)
    assert result == [[], [";"], ["int", "a", "double", "b", "float", "c"], [";"], []]


def test_split_by_consecutive_delimiters():
    pattern = T(";")
    seq = ["int", "a", ";", ";", "double", "b"]

    result = split_by(pattern, seq)
    assert result == [["int", "a"], [], ["double", "b"]]

    result = split_by(pattern, seq, keep_delimiters=True)
    assert result == [["int", "a"], [";"], [], [";"], ["double", "b"]]
