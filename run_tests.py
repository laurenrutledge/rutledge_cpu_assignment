"""
run_tests.py

Lauren Rutledge
March 5, 2026

Purpose
-------
This script serves as an automated test harness for the `max_candy` function
implemented in `main.py`.

It runs a collection of predefined input files stored in the
`test_case_inputs/` directory and verifies that the program output matches
the expected results exactly.

How it works
------------
1. Each test case is defined by:
       - an input file in `test_case_inputs/`
       - an expected output string stored in the `EXPECTED` dictionary.

2. The function `max_candy()` is executed for each input file.

3. Standard output from the function is captured using
   `contextlib.redirect_stdout` and compared against the expected output.

4. Each test prints either:
       [PASS] filename
       [FAIL] filename

5. A final summary reports whether all tests passed.

Important Notes
---------------
- Output comparison is **character-for-character**, meaning spacing,
  punctuation, and wording must match the expected string exactly.

- Stress tests are included to verify correctness and performance for
  larger inputs (e.g., 10,000 homes).

Usage
-----
Run the test suite from the command line:

    python test_runner.py

The script exits with:
    0 → all tests passed
    1 → one or more tests failed
"""

import os
import sys
from contextlib import redirect_stdout
from io import StringIO

# Import the function to be tested
from main import max_candy

# File name that all test cases are stored in
TEST_DIR = "test_case_inputs"

# Map: filename -> expected exact output (must match character-for-character)
EXPECTED = {
    "given_sample_input.txt": "Start at home 2 and go to home 5 getting 10 pieces of candy",
    "single_home_under_max.txt": "Start at home 1 and go to home 1 getting 7 pieces of candy",
    "single_home_equal_max.txt": "Start at home 1 and go to home 1 getting 7 pieces of candy",
    "single_home_over_max.txt": "Don't go here",
    "max_zero_all_positive.txt": "Don't go here",
    "zeros_allowed_max_zero.txt": "Start at home 1 and go to home 1 getting 0 pieces of candy",
    "shrink_window_multiple_times.txt": "Start at home 3 and go to home 6 getting 7 pieces of candy",
    "best_window_middle.txt": "Start at home 1 and go to home 2 getting 9 pieces of candy",
    "tie_breaker_case.txt": "Start at home 1 and go to home 2 getting 4 pieces of candy",
    "dont_go_here_all_exceed_max.txt": "Don't go here",
    "all_homes_exceed_max.txt": "Don't go here",
    "all_homes_fit.txt": "Start at home 1 and go to home 4 getting 35 pieces of candy",
    "tie_same_best_sum_different_lengths.txt": "Start at home 1 and go to home 2 getting 5 pieces of candy",
    "leading_zeros_before_best.txt": "Start at home 1 and go to home 3 getting 3 pieces of candy",
    "best_window_at_end.txt": "Start at home 5 and go to home 6 getting 8 pieces of candy",
    "first_home_over_max_others_not.txt": "Start at home 2 and go to home 3 getting 2 pieces of candy",
    "all_zeros_max_positive.txt": "Start at home 1 and go to home 1 getting 0 pieces of candy",
    "zero_then_max_then_zeros.txt": "Start at home 1 and go to home 2 getting 5 pieces of candy",
    "zeros_bridge_two_possible_windows.txt": "Start at home 2 and go to home 7 getting 5 pieces of candy",
    "max_1000_single_home_exactly_1000.txt": "Start at home 1 and go to home 1000 getting 1000 pieces of candy",
    "another_tie_breaker_case.txt": "Start at home 1 and go to home 5 getting 2 pieces of candy",
    # ---- STRESS TESTS ----
    "stress_10000_all_ones.txt": "Start at home 1 and go to home 1000 getting 1000 pieces of candy",
    "stress_10000_alternating.txt": "Start at home 2 and go to home 2 getting 1 pieces of candy",
}

def run_one_test(input_path: str) -> str:
    """
    Runs max_candy(input_path) for one test case and captures what it prints.
    """
    buffer = StringIO()

    with redirect_stdout(buffer):
        max_candy(input_path)

    return buffer.getvalue().strip()

def run_all_tests() -> int:
    """
        Runs all tests in EXPECTED. Prints a PASS/FAIL report.
        Returns an exit code: 0 if all pass, 1 otherwise.
        """

    failures = 0

    for filename in sorted(EXPECTED.keys()):
        input_path = os.path.join(TEST_DIR, filename)

        if not os.path.exists(input_path):
            print(f"[SKIP] {filename} (file not found at {input_path})")
            continue

        expected = EXPECTED[filename].strip()
        actual = run_one_test(input_path).strip()

        if actual == expected:
            print(f"[PASS] {filename}")
        else:
            failures += 1
            print(f"[FAIL] {filename}")
            print(f"  expected: {expected!r}")
            print(f"  actual:   {actual!r}")


    print("\n====================")
    if failures == 0:
        print("ALL TESTS PASSED")
        return 0
    else:
        print(f"{failures} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)