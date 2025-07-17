import sys
import types

# -------------------------------------------------------------------
# Stub external modules (openai, requests, pandas, sklearn) that are
# imported by eval.evaluate_models but are not required for unit-testing
# the matching helpers.  This prevents ImportError during test collection.
# -------------------------------------------------------------------

def _create_dummy_module(name):
    module = types.ModuleType(name)
    sys.modules[name] = module
    return module

# Basic stubs
for missing_mod in ["openai", "requests", "pandas"]:
    if missing_mod not in sys.modules:
        _create_dummy_module(missing_mod)

# Stub sklearn and sklearn.metrics with minimal API
if "sklearn" not in sys.modules:
    sklearn_mod = _create_dummy_module("sklearn")
else:
    sklearn_mod = sys.modules["sklearn"]

metrics_mod = types.ModuleType("sklearn.metrics")
for func_name in ["precision_score", "recall_score", "f1_score", "accuracy_score"]:
    setattr(metrics_mod, func_name, lambda *args, **kwargs: 0.0)

sklearn_mod.metrics = metrics_mod
sys.modules["sklearn.metrics"] = metrics_mod

import pytest

from eval.evaluate_models import normalize_answer, extract_choice_text, answers_match

# ------------------------------------------------------------
# Fixtures
# ------------------------------------------------------------
@pytest.fixture
def sample_question():
    return {
        "Question": "Sample question?",
        "Option A": "geo-information science",
        "Option B": "geology science",
        "Option C": "geographic information system",
        "Option D": "life science",
        "Answer": "geographic information system",
    }

# ------------------------------------------------------------
# normalize_answer tests
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "raw, expected",
    [
        ("  Geographic INFORMATION  System.", "geographic information system"),
        ("GeoGRAPHIC information system!!", "geographic information system"),
        ("  geographic    information    system  ", "geographic information system"),
    ],
)
def test_normalize_answer(raw, expected):
    assert normalize_answer(raw) == expected

# ------------------------------------------------------------
# extract_choice_text tests
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "response, expected_letter",
    [
        ("A", "Option A"),
        ("a", "Option A"),
        ("A.", "Option A"),
        ("(A) geo-information science", "Option A"),
        ("C) geographic information system", "Option C"),
        ("geographic information system", "Option C"),
        ("I think the answer is geographic information system because ...", "Option C"),
    ],
)
def test_extract_choice_text(sample_question, response, expected_letter):
    extracted = extract_choice_text(sample_question, response)
    assert extracted == sample_question[expected_letter]

# ------------------------------------------------------------
# answers_match tests
# ------------------------------------------------------------
@pytest.mark.parametrize(
    "predicted, ground_truth, should_match",
    [
        ("C", "geographic information system", True),
        ("c", "geographic information system", True),
        ("geographic information system", "geographic information system", True),
        ("Geographic Information System", "geographic information system", True),
        ("geo-information science", "geographic information system", False),
        ("B", "geographic information system", False),
    ],
)
def test_answers_match(sample_question, predicted, ground_truth, should_match):
    assert answers_match(predicted, ground_truth, sample_question) is should_match