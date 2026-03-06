/*
 * File: halloween_omp.cpp
 * Lauren Rutledge
 * March 5, 2026
 *
 * This file contains a subsidiary implementation of the "Halloween candy neighborhood problem"
 * described in the README. The primary implementation is written in Python (main.py). This
 * implementation parallelizes the solution using OpenMP for multi-core execution, as described
 * in the subsidiary question of the assignment.
 *
 * Approach:
 *     This implementation uses a prefix sum array combined with binary search (upper_bound)
 *     to find the best valid contiguous range of homes in O(n log n) time. Unlike the serial
 *     sliding-window solution used in the Python implementation, this approach allows each
 *     starting home to be evaluated independently, making it well-suited for parallelization
 *     with OpenMP. Each thread processes a subset of starting homes, maintains a local best
 *     result, and merges it into the global best using a critical section.
 *
 * Input format assumptions:
 *     - The file represents exactly one neighborhood.
 *     - Line 1 contains the number of homes, `num_homes`.
 *     - Line 2 contains the maximum allowed candy, `max_candy`.
 *     - Each remaining line contains exactly one integer representing the number
 *       of candy pieces available at one home.
 *
 * Data constraints from the prompt:
 *     - 0 < homes <= 10000
 *     - 0 <= max_candy <= 1000
 *     - 0 <= pieces <= 1000 for each home
 *
 * Important assumptions:
 *     - Candy counts are non-negative, which ensures prefix sums are monotonically
 *       non-decreasing and binary search is valid.
 *     - Homes must be visited in their given order.
 *     - The child must visit a consecutive block of one or more homes.
 *     - The child must take all candy from each visited home.
 *     - If multiple valid ranges produce the same best candy total, the range
 *       with the smallest starting home index is chosen.
 *     - If no valid non-empty range exists, the output is:
 *       "Don't go here"
 *
 * Compile: g++-15 -fopenmp halloween_omp.cpp -o halloween_omp
 */

#include <iostream>         // for cout, cerr
#include <fstream>          // for file input
#include <vector>           // for dynamic arrays 
#include <algorithm>        // for upper_bound
#include <omp.h>            // for OpenMP Parallelization

using namespace std;



/*
* Helper Function: is_better
* This function determines whether a candidate window is better than the current best window.
* 
* A window is considered better than the alternative (candidiate vs. current) if:
*   1. It contains more total candy, OR
*   2. It contains the same amount of candy but starts at an earlier home (this follows the tie-breaking rule from the problem statement).
* 
* The function returns: 
*   - 1: If the candidate window is better than the current window (1 = True)
*   - 0: If the candidate window is NOT better than the current window (0 = False)
*/

static int is_better(int candidate_sum, int candidate_start, int current_sum, int current_start) {
    
    // Candidate has more candy than the current sum, so candidate window / sum is "automatically better"
    // If candidate window is preferred --> RETURN TRUE
    if (candidate_sum > current_sum) {
        return 1; 
    }
    // Candidate has same candy as current sum, but candidate starting index is smaller than the current starting index,
    //  so candidate window is preferred. If candidate window is preferred --> RETURN TRUE 
    if (candidate_sum == current_sum && candidate_start < current_start) {
        return 1; 
    }

    // If neither of the above are true, then the current window is better than THIS candidate's window of houses. 
    // If current window is preferred --> RETURN FALSE
    return 0; 
}



/*
* Main Function
*
* This function:
*   1. Reads the input file (num_homes, max_candy, and candy values per home)
*   2. Builds a prefix sum array for O(1) range sum queries
*   3. Runs a parallelized search across all starting homes using OpenMP
*   4. Merges each thread's local best into the global best via a critical section
*   5. Prints the best valid candy window, or "Don't go here" if none exists
*/

int main() {

    // Open the input file
    ifstream fin("input.txt");

    // Check that the file opened successfully
    if (!fin) {
        cerr << "Could not open input file: input.txt" << endl;
        return 1;
    }

    // Read the total number of homes in the neighborhood (the number of lines we should expect in file - 2) 
    int num_homes;
    fin >> num_homes;

    // Read in the parent's upper limit / the maximum candy the children are allowed
    int max_candy;
    fin >> max_candy;


    /*
    Read the candy amounts each home gives out
    pieces[i] = number of pieces of candy given at home i. Store them as 0-based index
    */
    vector<int> pieces(num_homes); 
    for (int i = 0; i < num_homes; i++) {
        fin >> pieces[i]; 
    }


    /*
    Build the Prefix Sum Array: 
    - Define: prefix[i] = total candy from homes 0 through i-1.
        To do so, add the previous home's candy to the running total, input the current total into the next bucket of the array
        - Example: 
          pieces = [2,4,3,2,1]
          prefix = [0,2,6,9,11,12]

        - Why? This allows us to compute the candy between any two homes quickly (O(1)):
          Candy(start..end) = prefix[end+1] - prefix[start]

        This is O(1) time instead of summing every time.
    */
    vector<int> prefix(num_homes + 1, 0);
    for (int i = 0; i < num_homes; i++) {
        prefix[i+1] = prefix[i] + pieces[i]; 
    }

    /*
    Define variables to store the Global Best Window (shared across all threads)
        - These variables store the best sequence of homes found overall.
        - Ensure these values remain 1-based to match the output required in the problem statement.
    */
    int best_left_index = -1;  // Ensure this remains 1-based 
    int best_right_index = -1;  // Ensure this remains 1-based 
    int best_candy_sum = -1; 

    /*
    OPENMP PARALLEL REGION: 
    - Each thread will independently evaluate possible starting homes.
    - Threads maintain their own local best result to avoid race conditions.
    */
    #pragma omp parallel 
    {
        /*
        Store Variables to represent the local best window(per thread)
            - Each thread keeps track of its best candidate window.
            - Afterwards, the results across all threads will be compared with the global best 
        */

        int local_best_left_index = -1; 
        int local_best_right_index = -1; 
        int local_best_candy_sum = -1; 

        /*
        Pragma Omp is what parallelizes this loop: 
         - the line tells OpenMP to divide the loop iterations among the available threads so that different starting homes are 
         processed in parallel
        */
        #pragma omp for

        /*
                OpenMP Parrallel Loop: 

        Each iteration of this loop evaluates ALL windows / candidates per a different possible starting home 
        for the trick-or-treat route. 

        For a given starting home, start, ONE thread: 
            1. Computes the maximum allowed prefix sum: 
                - prefix[start] + max_candy) 
            2. Uses binary search (upper_bound) to find the last valid ending home that can be visited without exceeding 
             the candy limit -- last valid home meaning the last home in the sequence we can visit wtihout candy exceeding the total limit
            3. Computes the candy total for the window with the last valid ending home that can be reached without exceeding the limit
            4. The thread updates its thread-local BEST WINDOW if this window is better than the previously stored best window 

        Because each starting home is evaluated independently, different starting homes can be processed by different threads without 
         interfering with one another. 
        */

        for (int start = 0; start < num_homes; start++) {

            /*
            For THIS starting home, determine the maximum allowed prefix value.
                - More specifically, we want:
                    prefix[end] - prefix[start] <= max_candy
                which is equivalent to: 
                prefix[end] <= prefix[start] + max_candy
            */
            int upper_candy_limit = prefix[start] + max_candy; 

            /*
            Now that we have the upper candy limit for THIS starting home, use binary search to find the first prefix value that is 
            greater than the max_candy limit (we are searching for the upper_bound). 
                - This allows us to determine the farthest valid ending home.
            */
           auto it = upper_bound(prefix.begin() + start + 1, prefix.end(), upper_candy_limit);

           /*
            Now that we found the upper bound house index, we should convert the iterator position back into the window that is wtihin the limit (inclusive)
                - Subtract 1 because upper_bound returns the first element > limit.
            */
           int end_inclusive = (it - prefix.begin()) - 1;

            /*
            Walk back over trailing zeros so we return the shortest valid window to satisfy the unique tie-breaking case: 
            Same Sum, prefer the smallest start. 
            If same sum and same start, prefer the smallest end index 
            
            */

            while (end_inclusive > start + 1 && pieces[end_inclusive - 1] == 0) {
                end_inclusive--;
            }   // end while loop 
            
           /*
            Finally, ensure we found a valid window with at least one home: 
            */
           if (end_inclusive >= start + 1) {
                /*
                Compute total candy in this window.
                Recall that prefix difference already gives candy from start to end inclusive.
                */
                int current_candy_sum = prefix[end_inclusive] - prefix[start]; 

                /*
                Convert the start index to a 1-based home index for the output.
                */
               int current_left_index = start + 1;

               /*
                end_inclusive already corresponds to the correct 1-based home, so add name for easier readability
                */
                int current_right_index = end_inclusive;

                /*
                Use Helper function to check if THIS window is better than the thread's current best.
                */
                if (is_better(current_candy_sum, current_left_index,
                              local_best_candy_sum, local_best_left_index)) {

                    local_best_candy_sum = current_candy_sum;
                    local_best_left_index = current_left_index;
                    local_best_right_index = current_right_index;
                } 
           
            }   // end: if (end_inclusive >= start + 1) 

        }   // end: for loop that loops through all subsets of "home windows" that ONE thread processes 
        
        /*
        * Critical section:
        * Only one thread at a time may update the global best result.
        * This prevents race conditions during the merge step.
        */
       #pragma omp critical
        {
            if (is_better(local_best_candy_sum, local_best_left_index,
                          best_candy_sum, best_left_index)) {

                best_candy_sum = local_best_candy_sum;
                best_left_index = local_best_left_index;
                best_right_index = local_best_right_index;
            }
        }

    }   // end pragma omp parallel

    /*
    OUTPUT RESULTS: 
    - Note: if no valid window was found, print the required message: "Don't go here"
    - Otherwise print the best sequence of homes and total candy.
    */
    if (best_candy_sum == -1) {
        cout << "Don't go here" << endl;
    } else {
        cout << "Start at home " << best_left_index
             << " and go to home " << best_right_index
             << " getting " << best_candy_sum
             << " pieces of candy" << endl;
    }

    fin.close(); 

    return 0;

}