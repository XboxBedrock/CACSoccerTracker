import matplotlib.pyplot as plt

ts = []
xs = []
ys = []
zs = []

with open('data.txt', 'r') as f:
    t = 0
    for line in f.readlines():
        nums = list(map(float, line[1:-2].split(', ')))
        ts.append(t)
        xs.append(nums[0])
        ys.append(nums[1])
        zs.append(nums[2])
        t += 1

plt.plot(ts, xs, '-r', label='x')
plt.plot(ts, ys, '-g', label='y')
plt.plot(ts, zs, '-b', label='z')
plt.legend(loc="lower left")
plt.show()

# ts = []
# vs = []
# vs_filtered = []

# with open('data.txt', 'r') as f:
#     t = 0
#     for line in f.readlines():
#         # print(line[:-1], end = ' ')
#         nums = tuple(map(float, line.split()))
#         # print(nums)
#         ts.append(t)
#         vs_filtered.append(nums[0])
#         vs.append(nums[1])
#         t += 1

# plt.plot(ts, vs, '-g', label='Raw data')
# plt.plot(ts, vs_filtered, '-r', label='Filtered data')
# plt.legend(loc="lower left")
# plt.show()