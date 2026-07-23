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
