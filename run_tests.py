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