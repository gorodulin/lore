from lore.store.validate_fact_structure import validate_fact_structure
from lore import error_codes


class TestValidateFactStructure:
    def test_valid_minimal_fact(self):
        fact = {"fact": "Test fact", "incl": ["p:**/*.js"]}
        errors = validate_fact_structure("f1", fact)
        assert errors == []

    def test_valid_fact_with_skip(self):
        fact = {
            "fact": "Test fact",
            "incl": ["p:**/*.js"],
            "skip": ["p:vendor/**"],  # exclude from root
        }
        errors = validate_fact_structure("f1", fact)
        assert errors == []

    def test_valid_fact_multiple_matchers(self):
        fact = {
            "fact": "Test fact",
            "incl": ["p:**/*.js", "p:**/*.ts"],
            "skip": ["p:vendor/**", "p:node_modules/**"],  # exclude from root
        }
        errors = validate_fact_structure("f1", fact)
        assert errors == []

    def test_fact_not_dict_error(self):
        errors = validate_fact_structure("f1", "not a dict")
        assert len(errors) == 1
        assert errors[0]["code"] == error_codes.INVALID_FACT_STRUCTURE

    def test_missing_fact_field_error(self):
        fact = {"incl": ["p:**/*.js"]}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.MISSING_FACT_FIELD for e in errors)

    def test_fact_field_not_string_error(self):
        fact = {"fact": 123, "incl": ["p:**/*.js"]}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_FACT_STRUCTURE for e in errors)

    def test_missing_incl_field_error(self):
        fact = {"fact": "Test"}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.MISSING_INCL_FIELD for e in errors)

    def test_incl_not_list_error(self):
        fact = {"fact": "Test", "incl": "p:**/*.js"}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_FACT_STRUCTURE for e in errors)

    def test_incl_empty_list_error(self):
        fact = {"fact": "Test", "incl": []}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.EMPTY_INCL_LIST for e in errors)

    def test_skip_not_list_error(self):
        fact = {"fact": "Test", "incl": ["p:**/*.js"], "skip": "p:**/vendor/**"}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_FACT_STRUCTURE for e in errors)

    def test_invalid_matcher_prefix_error(self):
        fact = {"fact": "Test", "incl": ["x:**/*.js"]}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_MATCHER_PREFIX for e in errors)

    def test_invalid_matcher_no_prefix_error(self):
        fact = {"fact": "Test", "incl": ["**/*.js"]}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_MATCHER_PREFIX for e in errors)

    def test_invalid_glob_pattern_error(self):
        fact = {"fact": "Test", "incl": ["p:**/**/*.js"]}  # multiple **
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_MULTIPLE_GLOBSTARS for e in errors)

    def test_matcher_not_string_error(self):
        fact = {"fact": "Test", "incl": [123]}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_MATCHER_FORMAT for e in errors)

    def test_multiple_errors_collected(self):
        fact = {"incl": []}  # missing fact, empty incl
        errors = validate_fact_structure("f1", fact)
        assert len(errors) >= 2

    def test_error_includes_fact_id(self):
        fact = {"fact": "Test", "incl": []}
        errors = validate_fact_structure("my-fact-id", fact)
        assert any("my-fact-id" in e["message"] for e in errors)

    def test_valid_tags(self):
        fact = {"fact": "Test", "incl": ["p:**/*.py"], "tags": ["hook:read", "kind:convention"]}
        errors = validate_fact_structure("f1", fact)
        assert errors == []

    def test_tags_not_list_error(self):
        fact = {"fact": "Test", "incl": ["p:**/*.py"], "tags": "hook:read"}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_TAGS_FIELD for e in errors)

    def test_tag_element_not_string_error(self):
        fact = {"fact": "Test", "incl": ["p:**/*.py"], "tags": [123]}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_TAGS_FIELD for e in errors)

    def test_empty_tags_list_valid(self):
        fact = {"fact": "Test", "incl": ["p:**/*.py"], "tags": []}
        errors = validate_fact_structure("f1", fact)
        assert errors == []

    def test_valid_regex_matcher(self):
        fact = {"fact": "Test", "incl": ["c:raise\\s+"]}
        errors = validate_fact_structure("f1", fact)
        assert errors == []

    def test_invalid_regex_syntax_error(self):
        fact = {"fact": "Test", "incl": ["c:[invalid"]}
        errors = validate_fact_structure("f1", fact)
        assert any(e["code"] == error_codes.INVALID_REGEX_PATTERN for e in errors)

    def test_regex_value_starting_with_r_colon_valid(self):
        fact = {"fact": "Test", "incl": ["c:r:\\d+"]}
        errors = validate_fact_structure("f1", fact)
        assert errors == []
