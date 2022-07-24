import statistics
import numpy as np

# file_path = "./lora_rssi_1m"
file_path = "./bl_rssi_1m"

with open(file_path) as f:
    lines = f.readlines()

rssi_values = []

count = 0
for line in lines:
    rssi_values.insert(count, int(line))
    count += 1

meanValue = statistics.mean(rssi_values)
print(np.round_(meanValue, 2))

variance = statistics.variance(rssi_values, meanValue)
print(np.round_(variance, 2))

# mean_variance_low = meanValue - variance*2
# mean_variance_high = meanValue + variance*2
mean_variance_low = meanValue - variance
mean_variance_high = meanValue + variance
print(np.round_(mean_variance_low, 2))
print(np.round_(mean_variance_high, 2))

stdev = statistics.pstdev(rssi_values)
print(stdev)
