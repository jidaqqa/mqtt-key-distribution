import statistics
import numpy as np

with open('./lora_rssi_1m') as f:
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

mean_variance_low = meanValue - variance*2
mean_variance_high = meanValue + variance*2
print(np.round_(mean_variance_low, 2))
print(np.round_(mean_variance_high, 2))

