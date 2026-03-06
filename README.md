# The Halloween Candy Optimizer

## Introduction

Halloween is approaching and parents want to place an upper bound on the amount of candy their children can collect, while
the children want to maximize the amount of candy they receive! 


### Overview
This repository contains a solution that determines the **best consecutive sequence of homes** a child can visit in a
neighborhood on Halloween while collecting candy **without exceeding the parents' pre-defined  maximum allowed amount**. 

The goal is to maximize the children's total candy collected on Halloween while respecting the maximum allowed amount.
set by the parents. 

If multiple valid sequences (subsections of consecutive houses in one neighborhood) achieve the same maximum sum of
of candy, the sequence with the **smallest starting home index** is chosen. 

If no valid sequence of houses in the neighborhood exist, the program prints: 

```text
Don't go here
```


### Problem Statement
Given a neighborhood of homes where each home hands out a fixed number of candy pieces, determine the **contiguous 
sequence of homes** a child should visit such that:
•	The total candy collected does not exceed the parent-set maximum.
•	The total candy collected by the children is as large as possible.
•	If multiple sequences tie on total candy, the one starting at the lowest-numbered (index) home is chosen.

Additional Constraints: 
•   Children must visit every home in the chosen range.
•   Homes must be visited in order.
•   Children cannot skip homes or "discard candy".

---

## Algorithm 

### Sliding Window (Two Pointers)

The solution uses a **sliding window (two-pointer) technique**.

**Because all candy values are non-negative** (>= 0), a sliding window provides an optimal linear-time solution.

Using two pointers allows the algorithm to maintain a valid window of consecutive homes and adjust it dynamically.

#### Algorithm Steps: 
Two pointers define the current window:
- Left pointer (left) — start of the current window
- Right pointer (right) — end of the current window
The algorithm proceeds as follows: 
1. The right pointer expands the window one home at a time, adding the candy value at that house to a running sum.
2. If the sum exceeds the maximum allowed, the left pointer moves forward to shrink the window until the candy sum is 
within the allowed limit.
3. After each adjustment (one adjustment is finding a window that gives a current sum within the allowed amount), the 
algorithm checks whether the current window produces a better valid sum than the "best sum" recorded prior, and sets the 
"best sum" to the current window's sum if so.

Because the left pointer only moves forward, the first window encountered with a given sum will always have the smallest 
starting index. This naturally enforces the tie-breaking rule without additional logic.

#### Time Complexity: 
```text
O(n)
```

Each house is processed at most twice:
- once when expanding the window
- once when shrinking it

#### Space Complexity:
```text
O(1)
```

The algorithm uses only a constant amount of additional memory (we only store pointers for the first and last indicies of the current window). .

#### Negative Candy Values
This algorithm relies on the assumption that all candy values are non-negative.

Sliding window works because:
- Expanding the window can only increase the sum
- Shrinking the window can only decrease the sum

If the problem statement were to expand to incorporate "dropped candy" along the way (negative candy values are 
allowed), this approach would break. 

This is because if negative values were incorporated, the sliding window technique wouldn't work for the cases where a 
window might temporarily exceed the allowed maximum, but later become valid again after adding a negative value. Since 
the sliding window algorithm immediately discards windows that exceed the maximum, it would fail to consider such cases.

If negative candy values were allowed, a different approach would be required, such as prefix sums over a balanced
search tree, which would give a time complexity of: 
```text
O(n log n).
```


---
## How to Run

### Requirements
    •	Python 3.9+
    •   No external dependencies - standard library only

### File Structure

```text
rutledge_cpu_assignment/
│
├── main.py                   # Implementation of the sliding window algorithm
├── run_tests.py              # Automated test runner
├── generate_stress_tests.py  # Script to generate large stress test inputs (to be run in run_tests.py)
├── README.md                 # Project documentation containing instructions for running this solution and assumptions
├── ComputeAssignment.pdf     # Original assignment prompt and documentation
│
└── test_case_inputs/         # Directory containing input test files
```

### Running the Program

Run the algorithm with:

```text
python main.py
```

### Running the Test Suite
To run all automated tests:

```text
python run_tests.py
```

This executes every test case in test_case_inputs/ and compares the program output against the expected results.


#### Incorporating Stress Tests
Large stress tests (including the maximum constraint of 10,000 homes) can be generated with:

```text
python generate_stress_tests.py
```

#### Important
Run this script before running the test suite for the first time because the run_tests.py file includes expected outputs
for the generated stress test files, so those input files must exist beforehand.

After generating the stress tests, run:

```text
python run_tests.py
```

to execute the full test suite.




