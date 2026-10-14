# Day00: Fibonacci template

Day00 is a practice problem that makes the repository runnable before adding
official Advent of Code puzzles. It mirrors the Scala repository's Day00.

The Fibonacci sequence starts with `fib(0) = 0` and `fib(1) = 1`. Each subsequent
number is the sum of the preceding two: `fib(n) = fib(n - 1) + fib(n - 2)`.

## Input

Read one nonnegative integer per line from `inputs/Day00.txt`. The sample in
`inputs/Day00Test.txt` is identical:

```text
10
1000
```

## Part 1

Compute the Fibonacci number at the index on the first line. The example answer
is `fib(10) = 55`.

## Part 2

Compute the Fibonacci number at the index on the last line. The example answer
is `fib(1000)`, a 209-digit integer:

```text
43466557686937456435688527675040625802564660517371780402481729089536555417949051890403879840079255169295922593080322634775209689623239873322471161642996440906533187938298969649928516003704476137795166849228875
```

The input must contain at least one integer. A single-line input uses the same
index for both parts. Python's arbitrary-precision integers keep the full answer;
an iterative solution avoids recursion limits.
