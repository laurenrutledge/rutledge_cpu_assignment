# The Halloween Candy Optimizer

## Introduction

Halloween is approaching and parents want to give children an upper bound on the amount of candy they can receive, while
children want to maximize the candy they collect! 


### Overview
This repository contains a solution to determine the best consecutive sequence of homes a child can visit in a
neighborhood on Halloween while collecting candy without exceeding the parents' pre-defined  maximum allowed amount. 

The goal is to maximize the children's total amount of candy collected on Halloween while respecting the maximum limit 
set by the parents. 

If multiple valid sequences (subsections of consecutive houses in one neighborhood) achieve the same maximum sum of
of candy, the sequence with the **smallest starting home index** is chosen. 

If no valid sequence of houses in the neighborhood exist, the program prints: 

Don't go here


### Problem Statement
Given a neighborhood of homes each handing out a fixed number of candy pieces, find the contiguous sequence of homes a 
child should visit such that:
•	The total candy collected does not exceed the parent-set maximum.
•	The total candy collected by the children is as large as possible.
•	If multiple sequences tie on total candy, the one starting at the lowest-numbered (index) home wins.

The children must also visit every home in their chosen range in order — they cannot skip homes or "discard candy".

---

## Algorithm 

### Sliding Window (Two Pointers)

The solution uses a **sliding window (two-pointer) technique**.

**Because all candy values are non-negative** (>= 0), a sliding window gives an optimal linear-time solution. This is 
because by using two pointers, the valid window of consecutive houses can be expanded to the right and /or shrunken from 
the left pointer whenever the sum exceeds the maximum allowed.

Specifically, the algorithm works as follows: 
There exist two pointers, left and right, that define the current window of homes:
•	The right pointer advances each iteration, adding the next home's candy to the running sum.
•	When the sum exceeds max, the left advances to the left to shrink the window from the front, until the sum is back 
    within budget.
•	After each adjustment, if the current window's sum is a new best, it is recorded.

Since the left pointer only ever moves forward, the first window found with a given sum is always the earliest-starting 
one — so a simple > comparison on the sum is sufficient to enforce the tie-breaking rule without any extra logic.

Note: If the problem statement were to expand to incorporate "dropped candy" along the way (negative candy values are 
allowed), this approach would break. This is because the sliding window technique relies on the fact that all candy 
values are non-negative to ensure that expanding the window would only increase the total sum, and shrinking the window 
would only decrease the total sum. In other words, if negative candy values were allowed, a window that temporarily 
exceeds the maximum could later become valid again after adding a negative value. In that case, this current 
implementation of the sliding window algorithm would discard such windows immediately, and therefore, it would miss 
valid optimal solutions. 

If negative candy values were allowed, a different algorithm such as prefix sums over a balanced search tree would be 
required instead, which would give a runtime of: O(n log n).


