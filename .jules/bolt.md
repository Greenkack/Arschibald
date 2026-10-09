## 2024-05-25 - [numpy_financial replacement]
**Learning:** The memory states that `numpy_financial` causes O(N^3) performance bottlenecks for financial calculations and should be removed. It suggests using native Python math operations (e.g., Newton-Raphson method or generator sums) instead.
**Action:** Replace `numpy_financial` with custom implementations for functions like `irr` and `npv` to improve performance.
