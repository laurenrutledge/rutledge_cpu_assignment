import os

os.makedirs("test_case_inputs", exist_ok=True)

# Test 1: all ones
with open("test_case_inputs/stress_10000_all_ones.txt", "w") as f:
    f.write("10000\n")
    f.write("1000\n")
    for _ in range(10000):
        f.write("1\n")

# Test 2: alternating big/small
with open("test_case_inputs/stress_10000_alternating.txt", "w") as f:
    f.write("10000\n")
    f.write("50\n")
    for i in range(10000):
        f.write("100\n" if i % 2 == 0 else "1\n")

print("Stress tests generated.")