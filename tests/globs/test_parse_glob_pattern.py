from lore.globs.parse_glob_pattern import parse_glob_pattern


def test_parse_literal_path():
    result = parse_glob_pattern("src/utils/file.ts")
    assert result["raw"] == "src/utils/file.ts"
    assert result["is_dir"] is False
    assert len(result["segments"]) == 3
    assert all(s["type"] == "literal" for s in result["segments"])
    assert [s["value"] for s in result["segments"]] == ["src", "utils", "file.ts"]


def test_parse_directory_pattern():
    result = parse_glob_pattern("src/utils/")
    assert result["is_dir"] is True
    assert len(result["segments"]) == 2


def test_parse_wildcard():
    result = parse_glob_pattern("src/*.ts")
    assert result["segments"][0]["type"] == "literal"
    assert result["segments"][1]["type"] == "wildcard"
    assert result["segments"][1]["prefix"] == ""
    assert result["segments"][1]["suffix"] == ".ts"


def test_parse_wildcard_with_prefix():
    result = parse_glob_pattern("src/test_*.ts")
    seg = result["segments"][1]
    assert seg["type"] == "wildcard"
    assert seg["prefix"] == "test_"
    assert seg["suffix"] == ".ts"


def test_parse_globstar():
    result = parse_glob_pattern("src/**/test.ts")
    assert result["segments"][0]["type"] == "literal"
    assert result["segments"][1]["type"] == "globstar"
    assert result["segments"][2]["type"] == "literal"


def test_parse_globstar_only():
    result = parse_glob_pattern("**")
    assert len(result["segments"]) == 1
    assert result["segments"][0]["type"] == "globstar"


def test_parse_complex():
    result = parse_glob_pattern("app/**/src/*.js")
    assert result["segments"][0] == {"type": "literal", "value": "app"}
    assert result["segments"][1] == {"type": "globstar", "value": "**"}
    assert result["segments"][2] == {"type": "literal", "value": "src"}
    assert result["segments"][3] == {
        "type": "wildcard",
        "value": "*.js",
        "prefix": "",
        "suffix": ".js",
    }
