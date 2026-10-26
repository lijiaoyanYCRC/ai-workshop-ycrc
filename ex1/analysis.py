# A simple Python data analysis script that uses NumPy
import numpy as np

# Example research measurements
measurements = [12.5, 15.2, 14.8, 16.1, 13.9]

# Convert measurements to a NumPy array
data = np.array(measurements)

# Calculate summary statistics
print("Mean:", np.mean(data))
print("Standard deviation:", np.std(data))
print("Maximum:", np.max(data))
