"""
generate_stress_tests.py

Lauren Rutledge
March 5, 2026

Purpose
-------
This script generates large stress-test input files for validating the
`max_candy` implementation in `main.py`.

The generated files are written to the `test_case_inputs/` directory and
follow the same input format required by the program:

    Line 1: number of homes
    Line 2: maximum allowed candy
    Lines 3..(2 + homes): candy pieces given by each home

Generated Stress Tests
----------------------
1. stress_10000_all_ones.txt
   - 10,000 homes
   - Each home gives 1 piece of candy
   - Tests performance when the optimal window grows large.

2. stress_10000_alternating.txt
   - 10,000 homes
   - Candy values alternate between 100 and 1
   - Forces frequent sliding-window shrink operations.

These tests are designed to verify both:
    - algorithm correctness
    - performance for the largest allowed input size.

Usage
-----
Run the script once to generate the files:

    python generate_stress_tests.py

The script will create the `test_case_inputs/` directory if it does not
already exist.
"""

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