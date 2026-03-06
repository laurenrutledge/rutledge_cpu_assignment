// g++-15 -fopenmp halloween_omp.cpp -o halloween_omp

// Subsidiary implementation using OpenMP for multi-core execution.
// Main implementation is written in Python.

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
*/
static int is_better(int candidate_sum, int candidate_start, int current_sum, int current_start) {
    
    // Candidate has more candy than the current sum, so candidate window / sum is "automatically better"
    // If candidate window is preferred --> RETURN FALSE 
    if (candidate_sum > current_sum) {
        return 1; 
    }
    // Candidate has same candy as current sum, but candidate starting index is smaller than the current starting index,
    //  so candidate window is preferred. If candidate window is preferred --> RETURN FALSE 
    if (candidate_sum == current_sum && candidate_start < current_start) {
        return 1; 
    }

    // If neither of the above are true, then the current window is better than THIS candidate's window of houses. 
    // If current window is preferred --> RETURN TRUE 
    return 0; 
}



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
        Set up distribution of the loop iterations across various threads. 
            - Each thread wlll process a subset of windows starting form the same starting homes.
        */
        #pragma omp for
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
            Now that we have the upper candy limit for THIS starting home, we can use binary search to find the first prefix value that is 
            greater than the limit (we are searching for the upper_bound). 
                - This allows us to determine the farthest valid ending home.
            */
           auto it = upper_bound(prefix.begin() + start + 1, prefix.end(), upper_candy_limit);

           /*
            Now that we found the upper bound house index, we should convert the iterator position back into the window that is wtihin the limit (inclusive)
                - Subtract 1 because upper_bound returns the first element > limit.
            */
           int end_inclusive = (it - prefix.begin()) - 1;

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
                end_exclusive already corresponds to the correct 1-based home, so add name for easier readability
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
        "Catch to Parallelisim" for this implmentation: 
        Only one thread at a time updates the global best result. Not that this can prevent race conditions when multiple threads finish.
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

    } // end "pragma unroll" block 

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


    return 0;

}