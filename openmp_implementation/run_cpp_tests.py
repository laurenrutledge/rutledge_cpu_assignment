"""
run_cpp_tests.py

Lauren Rutledge
March 5, 2026

Purpose
-------
This script serves as an automated test harness specifically for the
C++ OpenMP implementation: `halloween_omp` binary.

It runs a collection of predefined input files stored in the
`test_case_inputs/` directory and verifies that the binary's output
matches the expected results exactly.

How it works
------------
1. Each test case is defined by:
       - an input file in `test_case_inputs/`
       - an expected output string stored in the `EXPECTED` dictionary.

2. For each test:
       - The path to the test file is passed as a command-line argument to the binary.
       - The compiled `halloween_omp` binary is invoked as a subprocess.
       - Its stdout is captured and compared against the expected output.

3. Each test prints either:
       [PASS] filename
       [FAIL] filename

4. A final summary reports whether all tests passed.

Important Notes
---------------
- Output comparison is **character-for-character**, meaning spacing,
  punctuation, and wording must match the expected string exactly.

- The C++ binary must be compiled before running:
      g++-15 -fopenmp halloween_omp.cpp -o halloween_omp

Usage
-----
    python openmp_implementation/run_cpp_tests.py

The script exits with:
    0 --> all tests passed
    1 --> one or more tests failed
"""

import os
import sys
import subprocess

# Determine the absolute path to the directory containing this script 
# Always resolve paths relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory where all test input files live (in this repository, that's one level up from this script)
TEST_DIR   = os.path.join(SCRIPT_DIR, "..", "test_case_inputs")

# Path to the compiled C++ OpenMP binary located in THIS script's directory
CPP_BINARY = os.path.join(SCRIPT_DIR, "halloween_omp")


# Map: filename -> expected exact output (must match character-for-character)
EXPECTED = {
    "given_sample_input.txt":                   "Start at home 2 and go to home 5 getting 10 pieces of candy",
    "single_home_under_max.txt":                "Start at home 1 and go to home 1 getting 7 pieces of candy",
    "single_home_equal_max.txt":                "Start at home 1 and go to home 1 getting 7 pieces of candy",
    "single_home_over_max.txt":                 "Don't go here",
    "max_zero_all_positive.txt":                "Don't go here",
    "zeros_allowed_max_zero.txt":               "Start at home 1 and go to home 1 getting 0 pieces of candy",
    "shrink_window_multiple_times.txt":          "Start at home 3 and go to home 6 getting 7 pieces of candy",
    "best_window_middle.txt":                   "Start at home 1 and go to home 2 getting 9 pieces of candy",
    "tie_breaker_case.txt":                     "Start at home 1 and go to home 2 getting 4 pieces of candy",
    "dont_go_here_all_exceed_max.txt":          "Don't go here",
    "all_homes_exceed_max.txt":                 "Don't go here",
    "all_homes_fit.txt":                        "Start at home 1 and go to home 4 getting 35 pieces of candy",
    "tie_same_best_sum_different_lengths.txt":  "Start at home 1 and go to home 2 getting 5 pieces of candy",
    "leading_zeros_before_best.txt":            "Start at home 1 and go to home 3 getting 3 pieces of candy",
    "best_window_at_end.txt":                   "Start at home 5 and go to home 6 getting 8 pieces of candy",
    "first_home_over_max_others_not.txt":       "Start at home 2 and go to home 3 getting 2 pieces of candy",
    "all_zeros_max_positive.txt":               "Start at home 1 and go to home 1 getting 0 pieces of candy",
    "zero_then_max_then_zeros.txt":             "Start at home 1 and go to home 2 getting 5 pieces of candy",
    "zeros_bridge_two_possible_windows.txt":    "Start at home 2 and go to home 7 getting 5 pieces of candy",
    "max_1000_single_home_exactly_1000.txt":    "Start at home 1 and go to home 1000 getting 1000 pieces of candy",
    "another_tie_breaker_case.txt":             "Start at home 1 and go to home 5 getting 2 pieces of candy",
    # ---- STRESS TESTS ----
    "stress_10000_all_ones.txt":                "Start at home 1 and go to home 1000 getting 1000 pieces of candy",
    "stress_10000_alternating.txt":             "Start at home 2 and go to home 2 getting 1 pieces of candy",
}


def run_one_test(input_path: str) -> str:
    """
    Runs the halloween_omp binary and passes the input_path 
    directly as a command line argument.
    """

    try:
        # We MUST pass input_path in the list so C++ can see it in argv[1]
        result = subprocess.run(
            [CPP_BINARY, input_path],
            capture_output=True,
            text=True,
            timeout=10,      # If test gets stuck, this counts as a fail
        )

        # If the program printed an error to stderr, it's helpful to know
        if result.stderr:
            print(f"  Debug Stderr: {result.stderr.strip()}")

        return result.stdout.strip()
    
    except subprocess.TimeoutExpired:
        return "Error: Test timed out after 10 seconds."
    
    except Exception as e:
        return f"Error running binary: {str(e)}"
    

def run_all_tests() -> int:
    """
    Runs all tests in EXPECTED. Prints a PASS/FAIL report.
    Returns 0 if all pass, 1 otherwise.
    """
    
    # Check that the binary exists before running any tests
    if not os.path.exists(CPP_BINARY):
        print(f"[ERROR] Binary not found: {CPP_BINARY}")
        print(f"        Compile first with:")
        print(f"        g++-15 -fopenmp halloween_omp.cpp -o halloween_omp")
        return 1

    failures = 0

    for filename in sorted(EXPECTED.keys()):
        input_path = os.path.join(TEST_DIR, filename)

        # Skip the test if the actual text file is missing from the input directory
        if not os.path.exists(input_path):
            print(f"[SKIP] {filename} (file not found)")
            continue

        expected = EXPECTED[filename].strip()
        actual   = run_one_test(input_path).strip()

        if actual == expected:
            print(f"[PASS] {filename}")
        else:
            failures += 1
            print(f"[FAIL] {filename}")
            print(f"  expected: {expected!r}")
            print(f"  actual:   {actual!r}")

    print("\n" + "=" * 50)
    if failures == 0:
        print("ALL TESTS PASSED")
    else:
        print(f"{failures} TEST(S) FAILED")
    print("=" * 50)

    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())