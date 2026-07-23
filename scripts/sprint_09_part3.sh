#!/usr/bin/env bash

set -e

PROJECT="/home/souhaib/ACF"

echo "========================================"
echo " ACF Sprint 09 - Partie 3"
echo " Dataset Analyzer"
echo "========================================"

mkdir -p "$PROJECT/src/acf/ai/analyzers"

touch "$PROJECT/src/acf/ai/analyzers/__init__.py"

####################################################
# DATASET ANALYZER
####################################################

cat > "$PROJECT/src/acf/ai/analyzers/dataset_analyzer.py" << 'EOF'
"""
Dataset Analyzer
"""

import numpy as np


class DatasetAnalyzer:
    """
    Analyse un ensemble de variables météorologiques.
    """

    def analyze(self, dataset):

        report = {}

        for name, values in dataset.items():

            array = np.asarray(values)

            report[name] = {
                "shape": array.shape,
                "dtype": str(array.dtype),
                "min": float(np.nanmin(array)),
                "max": float(np.nanmax(array)),
                "mean": float(np.nanmean(array)),
            }

        return report

    ##################################################

    def variables(self, dataset):

        return sorted(dataset.keys())

    ##################################################

    def summary(self, dataset):

        return {
            "variables": self.variables(dataset),
            "count": len(dataset),
        }
EOF

####################################################
# TESTS
####################################################

cat > "$PROJECT/tests/test_dataset_analyzer.py" << 'EOF'
import numpy as np

from acf.ai.analyzers.dataset_analyzer import DatasetAnalyzer


def test_summary():

    analyzer = DatasetAnalyzer()

    dataset = {
        "temperature": np.array([[20,21],[22,23]]),
        "pressure": np.array([[1010,1012],[1011,1013]])
    }

    result = analyzer.summary(dataset)

    assert result["count"] == 2

    assert "temperature" in result["variables"]


def test_statistics():

    analyzer = DatasetAnalyzer()

    dataset = {
        "temperature": np.array([10,20,30])
    }

    report = analyzer.analyze(dataset)

    assert report["temperature"]["min"] == 10.0
    assert report["temperature"]["max"] == 30.0
    assert report["temperature"]["mean"] == 20.0
EOF

####################################################
# EXEMPLE
####################################################

mkdir -p "$PROJECT/examples"

cat > "$PROJECT/examples/demo_dataset_analyzer.py" << 'EOF'
import numpy as np

from acf.ai.analyzers.dataset_analyzer import DatasetAnalyzer

dataset = {
    "temperature": np.random.uniform(-15,35,(100,100)),
    "pressure": np.random.uniform(980,1035,(100,100)),
    "humidity": np.random.uniform(0,100,(100,100))
}

analyzer = DatasetAnalyzer()

print("Summary")
print(analyzer.summary(dataset))

print()

print("Statistics")
print(analyzer.analyze(dataset))
EOF

echo
echo "Dataset Analyzer installed successfully."

