import numpy as np
import pandas as pd
import pytest

from scripts.evaluate_model import build_features


def test_build_features_creates_expected_columns_and_values():
    source = pd.DataFrame({
        "current_usage": [120, 0],
        "avg_usage": [100, 0],
    })

    features = build_features(source)

    assert list(features.columns) == [
        "current_usage", "avg_usage", "usage_ratio", "variability"
    ]
    assert features["usage_ratio"].tolist() == [1.2, 1.0]
    assert features["variability"].tolist() == [20.0, 0.0]


@pytest.mark.parametrize(
    ("current", "average"),
    [
        (["bad"], [100]),
        ([np.nan], [100]),
        ([np.inf], [100]),
        ([-1], [100]),
        ([100], [-1]),
    ],
)
def test_build_features_rejects_invalid_usage(current, average):
    frame = pd.DataFrame({"current_usage": current, "avg_usage": average})

    with pytest.raises(ValueError):
        build_features(frame)
