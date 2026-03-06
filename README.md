# The Halloween Candy Optimizer

## Introduction

Halloween is approaching and parents want to place an upper bound on the amount of candy their children can collect, while
the children want to maximize the amount of candy they receive! 


### Overview
This repository contains two implementations that both determine the **best consecutive sequence of homes** a child can visit in a
neighborhood on Halloween while collecting candy **without exceeding the parents' pre-defined  maximum allowed amount**. 

| Implementation | Language | Approach | Location |
|---------------|----------|----------|----------|
| **Primary** | Python | Sliding window — O(n) | `main.py` |
| **Subsidiary** | C++ + OpenMP | Prefix sum + binary search — O(n log n), parallelized | `openmp_implementation/` |


The goal is to maximize the children's total candy collected on Halloween while respecting the maximum allowed amount 
set by the parents. 

If multiple valid sequences (subsections of consecutive houses in one neighborhood) achieve the same maximum sum of
candy, the sequence with the **smallest starting home index** is chosen. 

If no valid sequence of houses in the neighborhood exists

```text
Don't go here
```


### Problem Statement
Given a neighborhood of homes where each home hands out a fixed number of candy pieces, determine the **contiguous 
sequence of homes** a child should visit such that:
- The total candy collected does not exceed the parent-set maximum.
- The total candy collected is as large as possible.
- If multiple sequences tie on total candy, the one starting at the lowest-numbered home is chosen.

Additional Constraints: 
- Children must visit every home in the chosen range.
- Homes must be visited in order.
- Children cannot skip homes or "discard candy".

---

## Algorithms 

### Primary: Sliding Window (Two Pointers) -- Python

The solution uses a **sliding window (two-pointer) technique**.

**Because all candy values are non-negative** (>= 0), a sliding window provides an optimal linear-time solution.

Using two pointers allows the algorithm to maintain a valid window of consecutive homes and adjust it dynamically.

#### Algorithm Steps: 
Two pointers define the current window:
- Left pointer (left) — start of the current window
- Right pointer (right) — end of the current window

The algorithm then proceeds as follows: 

1. The right pointer expands the window one home at a time, adding the candy value at that house to a running sum.
2. If the sum exceeds the maximum allowed, the left pointer moves forward to shrink the window until the candy sum is 
within the allowed limit.
3. After each adjustment (one adjustment is finding a window that gives a current sum within the allowed amount), the 
algorithm checks whether the current window produces a better valid sum than the "best sum" recorded prior, and sets the 
"best sum" to the current window's sum if so.

Because the left pointer only moves forward, earlier-starting valid windows are encountered before later-starting ones. 
In addition, the implementation explicitly enforces the tie-breaking rule by preferring the window with the smallest 
starting home index whenever two windows achieve the same best sum.

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

The algorithm uses only a constant amount of additional memory, storing a small fixed number of variables such as the 
window pointers, running sum, and best window information.


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

### Subsidiary: Prefix Sum + Binary Search — C++ + OpenMP

The subsidiary solution, provided in response to the OpenMP parallelization question, uses a **prefix sum array
combined with binary search**.

Unlike the sliding window, which carries state across iterations, this approach evaluates each starting home
**completely independently** — making it naturally suited for parallelization with OpenMP.

#### Algorithm Steps:

**Serial setup (before the parallel region):**
1. Build a prefix sum array where `prefix[i]` = total candy from homes `0` through `i-1`.
   This allows any window sum to be computed in O(1): `sum(start..end) = prefix[end] - prefix[start]`.

**Parallel region (`#pragma omp parallel`):**

Each thread independently processes a subset of starting homes:

1. For a given starting home, compute the maximum allowed prefix value:
   `upper_limit = prefix[start] + max_candy`
2. Use binary search (`upper_bound`) to find the farthest valid ending home — the last home reachable without
   exceeding the candy limit.
3. Walk back over any trailing zeros to find the shortest window with that sum (satisfying the tie-breaking rule).
4. Compute the candy total for that window and update the thread's local best if it is an improvement.

**Merge step (`#pragma omp critical`):**

After all iterations complete, each thread merges its local best into the global best one at a time,
using a critical section to prevent race conditions.

#### Why not parallelize the sliding window directly?
The sliding window carries state (left pointer, running sum) across iterations. Parallelizing it directly would
produce incorrect results because threads would overwrite each other's state. The prefix sum approach avoids this
entirely since every starting home is evaluated independently.

#### Time Complexity:
```text
O(n log n)
```

Each of the n starting homes performs a binary search over the prefix array — O(log n) per iteration.

#### Space Complexity:
```text
O(n)
```

The prefix sum array requires O(n) additional memory.

#### Note on Negative Candy Values
This implementation also relies on the assumption that all candy values are non-negative. Since all candy 
values are non-negative, we know that the prefix sums are monotonically non-decreasing. This is what makes binary 
search on the prefix sums valid.

---
## How to Run

### Requirements

**Python (Primary Implementation):**
    - Python 3.9+
    - No external dependencies — standard library only

**C++ OpenMP (Subsidiary Implementation):**
    - g++ with OpenMP support (e.g. `g++-15`)
    - OpenMP library (`-fopenmp` flag)

### File Structure

```text
rutledge_cpu_assignment/
│
├── main.py                     # Primary implementation — sliding window algorithm
├── run_tests.py                # Automated test runner for the Python implementation
├── generate_stress_tests.py    # Script to generate large stress test inputs
├── README.md                   # Project documentation
├── ComputeAssignment.pdf       # Original assignment prompt
│
├── test_case_inputs/           # Directory containing all test input files
│
└── openmp_implementation/      # Subsidiary C++ + OpenMP implementation
    ├── halloween_omp.cpp        # C++ OpenMP implementation
    └── run_cpp_tests.py         # Automated test runner for the C++ implementation
```

### Running the Primary Python Implementation

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


### Running the Subsidiary C++ OpenMP Implementation

**Step 1: Compile**

From the root directory:
```bash
g++-15 -fopenmp openmp_implementation/halloween_omp.cpp -o openmp_implementation/halloween_omp
```

Or from inside the `openmp_implementation/` folder:
```bash
cd openmp_implementation
g++-15 -fopenmp halloween_omp.cpp -o halloween_omp
```

**Step 2: Run**

The binary reads from `input.txt` in the same directory as the binary. Place your input file there and run:
```bash
./openmp_implementation/halloween_omp
```

### Running the Subsidiary C++ OpenMP Test Suite

Make sure the binary is compiled first (see above), then:

```bash
python openmp_implementation/run_cpp_tests.py
```

This can be run from the root directory — paths are resolved relative to the script's own location automatically.


--- 

## Implementation Assumptions

### Input File Structure Format

The program reads data from a text file (by default: `input.txt`).  

The file must contain the following values:
```text
<number_of_homes>
<maximum_candy_allowed>
<candy_at_home_1>
<candy_at_home_2>
...
<candy_at_home_n>
```

Where:
- `number_of_homes` — the total number of homes in the neighborhood  
- `maximum_candy_allowed` — the maximum number of candy pieces a child may collect  
- Each subsequent line represents the number of candy pieces given at that home


**If these input conditions are violated, the program raises a ValueError.**


An example input text file may contain the contents: 
```text
5
10
2
4
3
2
1
```
... which would represent a neighborhood with: 
- 5 homes in the neighborhood
- A maximum allowed candy total of 10
- Candy distribution per home (starting at home 1) `[2, 4, 3, 2, 1]`

#### Invalid Input Handling

This implementation performs **strict input validation** before running the sliding window algorithm.

If the input file violates the expected format or value constraints (constraints are noted in the next section), the 
program raises a `ValueError` with a descriptive message.

Specifically, the input file must satisfy all of the following conditions:

| Validation Rule | Behavior |
|-----------------|----------|
| Exactly one neighborhood per file | The file must describe exactly one neighborhood instance. |
| Minimum required structure | The file must contain at least two lines: one for `number_of_homes` and one for `maximum_candy_allowed`. |
| Exact line count | If the first line specifies `n` homes, then the file must contain exactly `2 + n` total lines. |
| One integer per line | Each line must contain exactly one integer value. Multiple integers on the same line are not allowed. |
| No blank lines | Blank or empty lines are rejected. |
| Leading/trailing whitespace allowed | Whitespace is allowed only if the line still contains exactly one integer after stripping. |
| First line constraint | `number_of_homes` must be an integer satisfying `0 < homes ≤ 10,000`. |
| Second line constraint | `maximum_candy_allowed` must be an integer satisfying `0 ≤ max ≤ 1,000`. |
| Home candy constraints | Each home candy value must be an integer satisfying `0 ≤ pieces ≤ 1,000`. |

Examples of invalid input include:

- blank lines
- non-integer values
- multiple integers on one line
- too few or too many house lines
- values outside the allowed ranges

--- 

### Output Format Structure

The program prints exactly **one line of output**.

The output depends on whether a valid sequence of homes exists.

#### On Success

If a valid sequence of homes exists, the program prints:
```text
Start at home <first> and go to home <last> getting <sum> pieces of candy
```

For example, given the sample input above (a success case), the expected output would be: 
```text
Start at home 2 and go to home 5 getting 10 pieces of candy
```

#### On Failure

If **no valid sequence of one or more homes** satisfies the candy limit, the program prints:
```text
Don't go here
```

---

### Data Types 
The program operates entirely on **integer values** parsed from the input file.

#### Input Data Types

| Variable | Type | Description |
|--------|------|-------------|
| `number_of_homes` | integer | Total number of homes in the neighborhood |
| `maximum_candy_allowed` | integer | Maximum number of candy pieces the child is allowed to collect |
| `candy_at_home_i` | integer | Number of candy pieces given at the *i-th* home |

All values in the input file must be valid integers.


#### Internal Data Types

Within the implementation, the following Python data types are used:

| Variable | Type | Purpose |
|--------|------|--------|
| `num_homes` | `int` | Stores the number of homes |
| `max_candy_allowed` | `int` | Stores the maximum candy constraint |
| `pieces_per_home` | `list[int]` | Stores the candy values for each home |
| `current_candy_sum` | `int` | Tracks the candy sum within the current sliding window |
| `left` | `int` | Left pointer of the sliding window |
| `right` | `int` | Right pointer of the sliding window |
| `best_candy_sum` | `int` | Best valid candy total found so far |
| `best_left_index` | `int` | Starting home index of the best window |
| `best_right_index` | `int` | Ending home index of the best window |


#### Constraints on Values

From the problem specification:

| Variable | Constraint |
|--------|------------| 
| `number_of_homes` | `0 < homes ≤ 10,000` |
| `maximum_candy_allowed` | `0 ≤ max ≤ 1,000` |
| `candy_at_home_i` | `0 ≤ pieces ≤ 1,000` |

All candy values are **non-negative integers**, which is an important requirement that enables the **sliding window 
algorithm** used in this solution.

--- 
### Ordering of Homes

Homes are assumed to appear in fixed sequential order within the input file.

| Rule                   | Description                                            |
| ---------------------- | ------------------------------------------------------ |
| Fixed ordering         | Homes are implicitly ordered as `1, 2, 3, ..., n`.     |
| No reordering allowed  | The algorithm cannot rearrange homes.                  |
| Consecutive visitation | Valid solutions must visit **consecutive homes only**. |

Examples of Valid & Invalid Sequences: 

#### Valid Sequence: 
```text
homes 3 → 7
```

#### Invalid Sequence: 
```text
homes 1 → 4 → 6
```

--- 
### Child Behavior Rules
Based on the problem constraints, the child must follow these rules:

| Rule                 | Explanation                                                                  |
| -------------------- | ---------------------------------------------------------------------------- |
| Visit homes in order | The child walks through the neighborhood sequentially.                       |
| No skipping          | If a window includes homes `i..j`, every home in that range must be visited. |
| Take all candy       | The child must take **all pieces of candy offered** at each home.            |
| No discarding        | Candy cannot be discarded to stay within the limit.                          |

This means that the candy total for a window will always be: 
```text
sum(candy[i..j])
```

---

### Window Size Constraint

The assignment requires selecting one or more homes.

| Constraint          | Meaning                                            |
| ------------------- | -------------------------------------------------- |
| Minimum window size | A valid window must include **at least one home**. |
| Empty window        | An empty selection is not allowed.                 |

If no single home satisfies the candy constraint, the program outputs:
```text
Don't go here
```

--- 
### Tie Breaking Rules

The problem statement specifies the following primary tie-breaking rule:

- If multiple valid sequences achieve the same best candy sum, choose the sequence with the **smallest starting home 
index**. Or more specifically: 

| Rule               | Behavior                                                                                                                       |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| Primary tie-break  | Choose the window with the **smallest starting home index**.                                                                   |
| Secondary behavior | If two windows have the same start and sum, the algorithm keeps the **first encountered window** while scanning left-to-right. |


For example, if houses give out [candy]:
```text
[2, 3, 2, 3]
max = 5
```

then the following windows are all valid and achieve the same best sum:
```text
1-2
2-3
3-4
```

As such, the expected output of the algorithm in this tie-breaking case would be: 
```text
Start at home 1 and go to home 2 getting 5 pieces of candy
```
because it is the first optimal window discovered.


***However***, it is also possible for multiple windows to have:

- the same best sum, and
- the same starting home index

This can happen when trailing (or leading) homes contribute `0` pieces of candy.

In these cases, this implementation keeps the **first such window encountered while scanning left-to-right**, which 
corresponds to the **smallest ending home index** among windows tied on both starting index and sum. This design choice 
was chosen because Halloween is equally as much about showing off your costume as it is collecting candy! That said, it 
is assumed that if the child has yet to collect any candy, and there exists a few houses at the end of the road that will
still give out candy within the allowed_maximum, then the child will want to stop at the houses that don't give out candy
to show off their costume before getting to the houses IN THE SAME NEIGHBORHOOD that will give out at least one piece. 

At the same time, if no houses in the neighborhood give out candy and it is pre-known to the children, then it is assumed
that the children will only want to show off their costume to one house before heading home to eat the candy at their own 
house! 

Below are two examples that fall within this "unique tie-breaking case" category: 

#### Example 1: Trailing Zeros 

If the neighborhood candy values are:

```text
[5, 0, 0, 0]
max = 5
```
then all of the following windows are valid and achieve the same best sum:
```text
1-1
1-2
1-3
1-4
```

In this case, it is expected that the algorithm will select: 
```text
Start at home 1 and go to home 1 getting 5 pieces of candy
```
because it is the **first optimal window** discovered. In other words, it is the valid window of the options with the 
lowest starting / left index, and the lowest ending / right index. 


#### Example 2: Leading Zeros

If the neighborhood candy values are:

```text
[0, 0, 5, 0, 0]
max = 5
```

then again, multiple windows achieve the best sum: 

```text
1-3
1-4
1-5
2-3
2-4
2-5
3-3
3-4
3-5
```

According to the assignment's tie-breaking rule and the assumptions noted above, the correct output is:
```text
Start at home 1 and go to home 3 getting 5 pieces of candy
```

This is because the `1-3` window has the smallest starting home index among all optimal windows. Among the windows that 
also start at `1`, it is encountered first and therefore kept by the implementation.

---

## Test Cases

The following test cases were designed to validate both correctness and edge-case handling, including boundary 
conditions, tie-breaking rules, zero values, and algorithmic behavior of the sliding window implementation.

All test input files are located in the `test_case_inputs/` directory and executed via `run_tests.py`. Both test 
suites (`run_tests.py` and `openmp_implementation/run_cpp_tests.py`) use the same test cases and expected outputs.

| Filename | Expected Output | Purpose / Edge Case Covered                                                                                 |
|---------|----------------|-------------------------------------------------------------------------------------------------------------|
| `given_sample_input.txt` | `Start at home 2 and go to home 5 getting 10 pieces of candy` | Basic example from the assignment prompt to confirm baseline correctness.                                   |
| `single_home_under_max.txt` | `Start at home 1 and go to home 1 getting 7 pieces of candy` | Tests behavior when only one home exists and the candy amount is under the limit.                           |
| `single_home_equal_max.txt` | `Start at home 1 and go to home 1 getting 7 pieces of candy` | Verifies that `sum == max` is treated as a valid solution when one home exists.                             |
| `single_home_over_max.txt` | `Don't go here` | Ensures the algorithm correctly rejects a neighborhood where the only home exceeds the allowed candy limit. |
| `max_zero_all_positive.txt` | `Don't go here` | Tests the case where `max = 0` but all homes give positive candy.                                           |
| `zeros_allowed_max_zero.txt` | `Start at home 1 and go to home 1 getting 0 pieces of candy` | Confirms the algorithm handles zero candy values correctly when `max = 0`.                                  |
| `shrink_window_multiple_times.txt` | `Start at home 3 and go to home 6 getting 7 pieces of candy` | Verifies that the sliding window correctly shrinks repeatedly when the sum exceeds the maximum.             |
| `best_window_middle.txt` | `Start at home 1 and go to home 2 getting 9 pieces of candy` | Tests that the optimal window may occur in the middle of the neighborhood.                                  |
| `tie_breaker_case.txt` | `Start at home 1 and go to home 2 getting 4 pieces of candy` | Confirms that when two windows have the same sum, the window with the smallest starting index is chosen.    |
| `dont_go_here_all_exceed_max.txt` | `Don't go here` | Tests failure when every home individually exceeds the allowed maximum, multiple homes included.            |
| `all_homes_exceed_max.txt` | `Don't go here` | Additional validation that the algorithm correctly detects when no valid window exists.                     |
| `all_homes_fit.txt` | `Start at home 1 and go to home 4 getting 35 pieces of candy` | Ensures the algorithm correctly identifies when the entire neighborhood is the optimal window.              |
| `tie_same_best_sum_different_lengths.txt` | `Start at home 1 and go to home 2 getting 5 pieces of candy` | Tests tie-breaking behavior when two windows produce the same best sum but have different lengths.          |
| `leading_zeros_before_best.txt` | `Start at home 1 and go to home 3 getting 3 pieces of candy` | Verifies that leading zeros do not prevent earlier valid windows from being selected.                       |
| `best_window_at_end.txt` | `Start at home 5 and go to home 6 getting 8 pieces of candy` | Ensures the algorithm correctly identifies a best window that occurs at the end of the neighborhood.        |
| `first_home_over_max_others_not.txt` | `Start at home 2 and go to home 3 getting 2 pieces of candy` | Tests that the algorithm skips an invalid first home and correctly identifies a later valid window.         |
| `all_zeros_max_positive.txt` | `Start at home 1 and go to home 1 getting 0 pieces of candy` | Confirms correct handling when all homes give zero candy but `max > 0`.                                     |
| `zero_then_max_then_zeros.txt` | `Start at home 1 and go to home 2 getting 5 pieces of candy` | Tests behavior when zeros appear before and after the optimal candy value.                                  |
| `zeros_bridge_two_possible_windows.txt` | `Start at home 2 and go to home 7 getting 5 pieces of candy` | Ensures the tie-breaking rule selects the earliest valid start among multiple windows with the same sum.    |
| `max_1000_single_home_exactly_1000.txt` | `Start at home 1 and go to home 1000 getting 1000 pieces of candy` | Validates correct behavior at the upper bound of allowed candy values.                                      |

### Stress Tests

| Filename | Expected Output | Purpose |
|---------|----------------|---------|
| `stress_10000_all_ones.txt` | `Start at home 1 and go to home 1000 getting 1000 pieces of candy` | Tests performance with the maximum allowed number of homes (10,000) and verifies linear-time scaling. |
| `stress_10000_alternating.txt` | `Start at home 2 and go to home 2 getting 1 pieces of candy` | Stress test with alternating values to ensure the sliding window repeatedly expands and shrinks efficiently. |


---

## Author

Lauren Rutledge  
March 2026

Repository created for the Compute Assignment evaluation.