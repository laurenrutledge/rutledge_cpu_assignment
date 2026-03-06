"""
File: main.py

Lauren Rutledge
March 5, 2026


This file contains an implementation that solves the "Halloween candy neighborhood problem" described in the README by
finding the consecutive sequence of one or more homes that yields the largest possible amount of candy without exceeding
the child’s maximum allowed candy limit.

Approach:
    This implementation uses a sliding window / two-pointer technique to find the best valid contiguous range of homes
    in O(n) time, where n is the number of homes in a neighborhood. This approach works because all candy values are
    assumed to be non-negative (as described further in the Implementation Assumptions Section below)

Input format assumptions:
    - The file represents exactly one neighborhood.
    - Line 1 contains the number of homes, `homes`.
    - Line 2 contains the maximum allowed candy, `max_candy_allowed`.
    - Each remaining line contains exactly one integer representing the number
      of candy pieces available at one home.
    - Leading and trailing whitespace are allowed, but blank lines are not.
    - Each line must contain exactly one integer value.

Data constraints from the prompt:
    - 0 < homes <= 10000
    - 0 <= max_candy_allowed <= 1000
    - 0 <= pieces <= 1000 for each home

Important assumptions:
** SEE THE FULL LIST OF DETAILED INSTRUCTIONS IN THE README FILE **
    - Candy counts are non-negative. This is required for the sliding window
      technique to be correct.
    - Homes must be visited in their given order.
    - The child must visit a consecutive block of one or more homes.
    - The child must take all candy from each visited home.
    - If multiple valid ranges produce the same best candy total, the range
      with the smallest starting home index is chosen.
    - If no valid non-empty range exists, the output is:
      "Don't go here"

If negative candy values were allowed, this O(n) sliding window approach would
no longer be valid.
"""

# ------------------------------------------------------------
# Project configuration: change this ONE line to swap default inputs.
# ------------------------------------------------------------
INPUT_FILENAME = "test_case_inputs/input.txt"


def read_input(filename:str):
    """
    This function reads in the input file (default input is input.txt)
    and stores / returns the values seen in the input text so they can
    be used in the max_candy function. These values are:

    - num_homes:
        integer representing the maximum number of homes on a block.
        Constraint from given prompt: 0 < num_homes <= 10,000
     - max:
        integer representing the maximum number of pieces of candy the child may collect.
        Constraint from given prompt: 0 <= max_candy_allowed <= 1000
    - pieces:
        a list of length num_homes where each entry is an integer representing the
        number of pieces given at that home.
        Constraint from given prompt: 0 <= pieces <= 1000 for each home

    Returns:
        tuple[int, int, list[int]]:
            A tuple containing:
            - num_homes: total number of homes in the neighborhood
            - max_candy_allowed: maximum candy the child may collect
            - pieces_per_home: list of candy counts for each home

    Raises:
        ValueError:
            If the file format is invalid, a line does not contain exactly one
            integer, or any prompt constraint is violated.
    """

    # Read all  lines from the file and enforce:
    # - no blank lines
    # - exactly one integer per line
    lines = []
    with open(filename, "r") as f:
        for line_number, raw_line in enumerate(f, start=1):
            stripped = raw_line.strip()

            # Reject blank lines
            if stripped == "":
                raise ValueError(f"Line {line_number} is empty. Blank lines are not allowed.")

            # Ensure there is exactly one value per line in the input text
            tokens = stripped.split()
            if len(tokens) != 1:
                raise ValueError(  f"Line {line_number} must contain exactly ONE integer. "
                                   f"Got: '{stripped}'")

            lines.append(tokens[0])

    # Basic structure check: the file must contain at least the two header lines for num_homes and max_candy_allowed.
    if len(lines) < 2:
        raise ValueError("Input file must contain at least two lines: homes and max.")


    # Parse num_homes (first line) and validate constraints:
    try:
        num_homes = int(lines[0])
    except ValueError:
        raise ValueError("First line (homes) must be an integer.")

    if (num_homes <= 0) or (num_homes > 10000):
        raise ValueError(f"homes must satisfy 0 < homes <= 10000. Got: {num_homes}")


    # Parse max_candy_allowed (second line) and validate constraints:
    try:
        max_candy_allowed = int(lines[1])
    except ValueError:
        raise ValueError("Second line (max_candy_allowed) must be an integer.")

    if (max_candy_allowed < 0) or (max_candy_allowed > 1000):
        raise ValueError(f"max candy allowed must satisfy 0 <= max <= 1000. Got: {max_candy_allowed}")


    # Check that the num of homes' lines matches up with num_homes given on first line:
    expected_total_lines = 2 + num_homes
    if len(lines) != expected_total_lines:
        raise ValueError(f"Expected {num_homes} lines of candy counts after num_homes given in input"
                         f"text, but found {len(lines) - 2} homes with candy.")


    # Parse each pieces of candy per home amount and validate pieces constraints:
    pieces_per_home = []
    for i in range(num_homes):
        raw_pieces_data = lines[2 + i]

        try:
            pieces = int(raw_pieces_data)
        except ValueError:
            raise ValueError(f"Home {i + 1} pieces must be an integer. Got: {raw_pieces_data}")

        if (pieces < 0) or (pieces > 1000):
            raise ValueError(f"Home {i + 1} pieces must satisfy 0 <= pieces <= 1000. "
                             f"Got: {pieces}")

        pieces_per_home.append(pieces)

    # Return validated values for num_homes, max_candy_allowed, pieces_per_home
    return num_homes, max_candy_allowed, pieces_per_home




def max_candy(filename: str = INPUT_FILENAME):
    """
    This function implements the following three tasks:
        1. Reads in the "already-validated" input values from input.txt
            - Results are validated in the read_input function
        2. Computes the best consecutive sequence of homes such that:
            - The total candy collected per kid is <= max_candy_allowed
            - The total candy collected is as LARGE as possible (best_sum)
            - If there is a tie in best_sum, choose the sequence with the SMALLEST
              starting home index (tie-breaking rule from the prompt)
        3. Prints the expected output message
            - If no valid range exists, print: "Don't go here"
    """

    # 1. Read the validated inputs for num_homes, max_candy_allowed, pieces_per_home:
    num_homes, max_candy_allowed, pieces_per_home = read_input(filename)

    # 2. Initialize the "two pointer" sliding window into variables to hold the start/end of
    # window. The current_sum holds the total candy pieces for the current window [left..right].
    current_candy_sum = 0

    # Define left: do so as a 0 based starting string that we will change back to 1-based after main algo
    left = 0

    # Define variables to help track the best solution / window found so far:
    best_candy_sum = -1
    best_left_index = float("inf")  # Set to large number so tie-break case works more naturally
    best_right_index = -1

    # 3. Expand window one home at a time from left to right, calculate values associated within "window"
    for right in range(0, num_homes):

        # Add the candy from the new rightmost home into the current window sum.
        pieces = pieces_per_home[right]  # Use 0-based index, convert 1-based home index later
        current_candy_sum += pieces

        # If the sum of the current window exceeds the max candy allowed by parents, shrink window
        # from left until sum is within constraints again:
        while (current_candy_sum > max_candy_allowed) and (left <= right):
            current_candy_sum -= pieces_per_home[left]
            left += 1  # Shrink the window from the left by excluding one home.

        # If we have a non-empty valid window, compare it to current best. Note that a non-empty
        # window means left <= right.
        if (left <= right):
            # Update the best window if:
            #   - the sum is larger than best_sum, OR
            #   - the sum ties best_sum but has a smaller starting home index (tie-break rule)
            if ((current_candy_sum > best_candy_sum) or
                    (current_candy_sum == best_candy_sum and left < best_left_index)):
                best_candy_sum = current_candy_sum
                best_left_index = left
                best_right_index = right


    # 4. Print the result in the required format:
    if best_candy_sum == -1:
        print("Don't go here")
    else:
        # When printing, make sure to convert back to 1-based indexing, as the problem asks
        print(
            f"Start at home {best_left_index + 1} and go to home {best_right_index + 1} getting "
            f"{best_candy_sum} pieces of candy"
        )





if __name__ == "__main__":
    max_candy(INPUT_FILENAME)
