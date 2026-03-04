"""
# Assumptions:
- Regarding the structure of the file:
    - The file represents exactly one neighborhood: where the number of lines
    containing an integer from the third line onwards (the number of "homes" lines)
    is exactly the number of homes in the neighborhood
        - So the expected total lines are: 2 + homes
        - If there are only two lines given in the input (no homes lines), then a
        Value Error will be raised
    - Each value appears on its own line: one integer on one line represents the
    number of pieces of candy handed out at THAT ONE house. If there is more than
    one integer on a line in the input.txt, a Value Error will be raised.
    - Lines may contain leading or trailing whitespace, but must contain exactly
    one integer.

- Regarding the Data Types:
    - We assume every value can be parsed as an integer in its numerical format

- Regarding Value Ranges for the Stored Data Values:
    - From the prompt:
        Variable | Constraint
           homes |	0 < homes ≤ 10000
            max	 |  0 ≤ max ≤ 1000
         pieces	 |  0 ≤ pieces ≤ 1000
    This also confirms that **All candy values are non-negative** (which is why the
    sliding window technique works
    - IF negative numbers were allowed, the algorithm used here would break

- Regarding Ordering of the Homes:
    - Homes in the home lines are ordered as: 1, 2, 3, ... , n
        - The homes cannot be re-ordered and as such, the sequence of the homes remain
        consecutive.
        - This means that a valid window would be: homes 3 through 7.
        - An INVALID window would be: homes 1, 4, 6, etc.

- Regarding "Child Behavior Rules":
    - From our prompted given constraints, each child must:
        1. Visit homes in order in their neighborhood
        2. Visit every home in their chosen, outputted range
        3. Take all pieces of candy offered at each house they go to
        4. The child cannot discard candy in any form if it is true that they visited
        a house that gave candy.

        - This confirms that the sum of each child's candy gathered (at the end of visiting
        all houses) is: sum(pieces[i..j])

- Regarding Output Uniqueness:
    - The given prompt specifies the "tie breaking rule":
        - If multiple sequences have the same best sum, choose the one with the smallest
        starting home / home index

- Regarding the minimum window size:
    - The prompt gives us that the output must be "one or more consecutive homes"
        - The window size must be >= 1, OR, a printed message: "Don’t go here” will
        be outputted
        - We CANNOT return an empty window

- Regarding the Failure Case:
    - The failure case exists when the input does NOT show a sequence of >= 1 homes where
    the sum <= max.
        - If there are 3 homes in the sequence, the max is 2, and all three of the homes' give
        out 3+ pieces of candy, then the children cannot visit ANY home.
        - If a failure case is inputted, the output will be: "Don’t go here”

- Implicit Algorithm Assumptions:
    - Since we are assuming that pieces will always be >= 0, we are able to use the "sliding
    window technique" that achieves O(n).
    - If "negative pieces of candy" were allowed to be handed out at each house, the sliding
    technique could no longer be used. Instead, we would need to conduct a prefix sum on a
    built balanced tree, which would take O(nlogn)
"""

# ------------------------------------------------------------
# Project configuration: change this ONE line to swap inputs.
# ------------------------------------------------------------
INPUT_FILENAME = "test_case_inputs/input.txt"

from collections import deque

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
        Constraint from given prompt: 0 <= max_allowed <= 1000
    - pieces:
        a list of length num_homes where each entry is an integer representing the
        number of pieces given at that home.
        Constraint from given prompt: 0 <= pieces <= 1000 for each home

        If any constraint is violated, this function raises a ValueError with a clear message.
    """

    # Read all  lines from the file and enforce:
    # - no blank lines
    # - - exactly one integer
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

    # Basic structure check: confirm we have at least 2 lines at top for (num_homes and max_allowed)
    # plus num_homes piece lines:
    if len(lines) < 2:
        raise ValueError("Input file must contain at least two lines: homes and max.")


    # Parse num_homes (first line) and validate constraints:
    try:
        num_homes = int(lines[0])
    except ValueError:
        raise ValueError("First line (homes) must be an integer.")

    if (num_homes <= 0) or (num_homes > 10000):
        raise ValueError(f"homes must satisfy 0 < homes <= 10000. Got: {num_homes}")


    # Parse max_allowed (second line) and validate constraints:
    try:
        max_candy_allowed = int(lines[1])
    except ValueError:
        raise ValueError("Second line (max_candy_allowed) must be an integer.")

    if (max_candy_allowed < 0) or (max_candy_allowed > 1000):
        raise ValueError(f"max must satisfy 0 <= max <= 1000. Got: {max_candy_allowed}")


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

    #print("num_homes: ", num_homes)
    #print("Max_candy_allowed: ", max_candy_allowed)
    #print("pieces_per_home: ", pieces_per_home)

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
    """

    # 1. Read the validated inputs for num_homes, max_allowed, pieces_per_home:
    num_homes, max_candy_allowed, pieces_per_home = read_input(filename)

    # 2. Initialize the "two pointer" sliding window into variables to hold the start/end of
    # window. The current_sum holds the total candy pieces for the current window [left..right].
    current_candy_sum = 0

    # Define left: the 1-based starting index for first home in defined window:
    left = 1

    # Define variables to help track the best solution / window found so far:
    best_candy_sum = -1
    best_left_index = -1
    best_right_index = -1

    # 3. Expand window one home at a time from left to right, calculate values associated within "window"
    for right in range(1, num_homes + 1):

        # Add the candy from the new rightmost home into the current window sum.
        pieces = pieces_per_home[right - 1]  # convert 1-based to zero-based index to complete algo
        current_candy_sum += pieces

        # If the sum of the current window exceeds the max allowed by parents, shrink window
        # from left until sum is within constraints again:
        while (current_candy_sum > max_candy_allowed) and (left <= right):
            current_candy_sum -= pieces_per_home[left -1]
            left += 1  # move the left index one to right to exclude one house

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
        print(
            f"Start at home {best_left_index} and go to home {best_right_index} getting "
            f"{best_candy_sum} pieces of candy"
        )






if __name__ == "__main__":
    max_candy(INPUT_FILENAME)