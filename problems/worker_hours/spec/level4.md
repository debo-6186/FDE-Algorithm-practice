## Level 4

Introduce an operation for marking time periods as double-paid.

*   `set_double_paid(self, start_timestamp: int, end_timestamp: int) -> None` — should mark the period between `start_timestamp` and `end_timestamp` as **double-paid** for every worker. Time worked inside a double-paid period earns twice the compensation.
    *   Double-paid periods can be set at any time and apply to past and future sessions.
    *   Periods may overlap. Overlapping periods do **not** stack: pay is at most doubled.

*   `calc_salary` must now take double-paid periods into account.

### Examples

The example below shows how these operations should work (the section is scrollable to the right):

| Queries | Explanations |
| --- | --- |
| `add_worker("Ann", "Engineer", 100)` | returns True |
| `set_double_paid(5, 10)` | returns None |
| `register("Ann", 1)` | returns "registered" |
| `register("Ann", 15)` | returns "registered"; session 1..15 |
| `calc_salary("Ann", 0, 20)` | returns 1900; 4 * 100 + 5 * 200 + 5 * 100 |
| `set_double_paid(8, 12)` | returns None; overlaps: double-paid time is now 5..12 |
| `calc_salary("Ann", 0, 20)` | returns 2100; 4 * 100 + 7 * 200 + 3 * 100 |
| `calc_salary("Ann", 9, 11)` | returns 400; 2 * 200 |
| `set_double_paid(100, 200)` | returns None |
| `register("Ann", 150)` | returns "registered" |
| `register("Ann", 250)` | returns "registered"; 50 double-paid units + 50 normal units |
| `calc_salary("Ann", 0, 1000)` | returns 17100; 2100 + 50 * 200 + 50 * 100 |

### Input/Output

*   **[execution time limit]** 3 seconds
*   **[memory limit]** 1 GB
