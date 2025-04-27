"""Generate a CSV file with random numbers for testing purposes."""

import pandas as pd

# Data matching your INSERT statements
data = [
    {"value": 3.14},
    {"value": 1.618},
    {"value": 2.718},
    {"value": 0.577},
    {"value": 4.669},
]

df = pd.DataFrame(data)
df.to_csv("./data/random_numbers.csv", index=False)
