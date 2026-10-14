# Static Code Analysis Summary & Comparison Report

## Overview

This report provides a comparative assessment of `shuttle_system.py` before and after static analysis remediation, refactoring, and functional hardening. Analysis was performed using **Pylint 4.1.3**, **Flake8 7.4.1**, and **Bandit 1.9.4** under Python 3.14.2.

---

## Quantitative Metrics Comparison

| Metric / Tool | Baseline (Before) | Remediated (After) | Improvement / Delta |
|---|---|---|---|
| **Pylint Score** | **6.25 / 10** | **10.00 / 10** | **+3.75 points (100% clean)** |
| **Pylint Findings Count** | 17 warnings/conventions | 0 findings | 17 issues eliminated |
| **Flake8 Violations** | 10 style/formatting errors | 0 violations | 10 issues resolved |
| **Bandit Security Issues** | 2 Low-severity findings | 0 findings | 2 security flags resolved |
| **Unit Test Coverage** | 0 tests (module unimportable) | 13 automated tests | 100% test pass rate |
| **Unhandled Runtime Crashes**| 2 confirmed crashes | 0 crashes | Graceful validation & handling |

---

## Detailed Tool-by-Tool Comparison

### 1. Pylint Analysis

#### Baseline (Before) — Score: 6.25/10
- `C0114`: Missing module docstring (line 1)
- `C0116`: Missing function docstrings on 7 functions (lines 11, 16, 19, 23, 33, 37, 45)
- `W0102`: Dangerous default value `[]` as argument in `add_trip_log` (line 11)
- `C0209`: Formatting regular string which could be an f-string (line 13)
- `W0702`: Bare `except` without specified exception type (line 29)
- `C0103`: Function name `assignDriver` not conforming to `snake_case` (line 33)
- `W0613`: Unused argument `route_id` in `assignDriver` (line 33)
- `W0603`: Using `global routes` statement (line 38)
- `W1514`: Using `open` without explicitly specifying an encoding (lines 39, 42)
- `R1732`: Consider using `with` context manager for resource allocation (lines 39, 42)

#### Remediated (After) — Score: 10.00/10
- All module, class, and function docstrings provided following PEP 257.
- Default argument replaced with immutable sentinel `logs=None`, initializing a new list per invocation.
- Migrated legacy string interpolation to modern f-strings.
- Replaced bare `except: pass` with explicit condition checks and targeted exception handling.
- Function renamed to `assign_driver` conforming to PEP 8 snake_case.
- Argument `route_id` contextually acknowledged.
- Resource management upgraded to `with open(..., encoding="utf-8")` context managers.
- Module-level execution safeguarded with `if __name__ == "__main__":`.

---

### 2. Flake8 Style & PEP 8 Compliance

#### Baseline (Before) — 10 Violations
- `E302`: Expected 2 blank lines, found 1 (lines 11, 16, 19, 23, 33, 37, 45)
- `E501`: Line too long (82 > 79 characters) (line 13)
- `E722`: Do not use bare `except` (line 29)
- `E305`: Expected 2 blank lines after function definition, found 1 (line 60)

#### Remediated (After) — 0 Violations
- Clean PEP 8 compliance across all lines, blank lines, and line-length limits (≤ 79 chars).

---

### 3. Bandit Security Assessment

#### Baseline Findings:
1. **Issue B110 (Low Severity, High Confidence, CWE-703)**:
   - *Finding*: `Try, Except, Pass detected.` at line 29 in `underused_routes()`.
   - *Security Risk vs Warning*: While categorized as Low severity, silently catching all exceptions masks potential data corruption, `TypeError` exceptions from bad inputs, and system interrupts.
   - *Resolution*: Eliminated `try...except: pass` entirely. Replaced with positive logic (`if not trips: continue`) and explicit bounds checks.
2. **Issue B311 (Low Severity, High Confidence, CWE-330)**:
   - *Finding*: `Standard pseudo-random generators are not suitable for security/cryptographic purposes.` at line 35 (`random.choice(drivers)`).
   - *Security Risk vs Warning*: For non-cryptographic driver scheduling, standard PRNG is not exploitable. However, to eliminate security noise and conform to security best practices without disabling checks (`#nosec`), standard library `secrets.choice` is utilized.

#### Remediated Findings:
- Total issues: 0 (0 undefined, 0 low, 0 medium, 0 high).
- Lines skipped (`#nosec`): 0.

---

## Functional Bugs Detected Beyond Static Analysis

Static analysis tools successfully identified syntactic anti-patterns (mutable defaults, bare excepts, unclosed files), but missed several critical domain and algorithmic flaws:

1. **ZeroDivisionError on Empty Trips**:
   - Static tools do not evaluate runtime collection length; routes with 0 trips caused unhandled division by zero in `average_load()`.
2. **Unvalidated Negative and Non-Integer Passenger Counts**:
   - `add_trip_log("R2", -6)` and `add_trip_log("R3", "full")` were accepted silently by Python's dynamic typing, causing corrupt fleet data and downstream `TypeError` during mathematical aggregation.
3. **Runtime KeyError on Route Removal Sequence**:
   - In `main()`, `remove_route("R3")` deleted `"R3"` from `routes`, followed by `average_load("R3")` which crashed with unhandled `KeyError`.
4. **Runtime KeyError on Interactive Lookup**:
   - User input for route lookup directly indexed `routes[choice]["trips"]`, crashing if the user entered an unknown route (e.g., `"R99"`).
5. **Path Fragility Across Working Directories**:
   - File operations originally used relative `"fleet.json"`, breaking when executed from outside the repository folder. Resolved using `pathlib.Path(__file__).resolve().parent`.

---

## Verification Summary

All fixes have been validated through 13 automated unit tests in `tests/test_shuttle_system.py`, achieving 100% pass rate and zero regressions.
