# Lab 5: Static Code Analysis — Campus Shuttle Timetable & Fleet Tracker


**Your file:** `shuttle_system.py`

Follow the lab handout for the full instructions.

## About the program

A tracker for campus shuttle routes. It logs passenger counts per trip, works out average loads, flags under-used routes and syncs the fleet data to `fleet.json`.

The code works, but only just. It has quality, style and security problems of the kind Pylint, Flake8 and Bandit are built to find.

## What to do

1. **Run it first** and read the output carefully:
   ```bash
   python shuttle_system.py
   ```
   It asks one question. Press Enter to use the default, then try a few inputs of your own. Not every problem in this file is something a tool will flag, so pay attention to output that looks wrong.

2. **Install the tools:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the analysis** and save the reports:
   ```bash
   pylint shuttle_system.py > reports/before/pylint_report.txt
   flake8 shuttle_system.py > reports/before/flake8_report.txt
   bandit -r shuttle_system.py > reports/before/bandit_report.txt
   ```

4. **Document the issues** in `issues.md` using this table (at least 4 rows, high and medium severity first):

   | Issue | Type | Line(s) | Description | Fix Approach |
   |-------|------|---------|-------------|--------------|
   | ... | ... | ... | ... | ... |

5. **Fix the code.** Fix at least 4 of the issues you documented, then rerun all three tools to confirm they are gone. Repeat until you are satisfied. The program should still do its job when you are done.

6. **Reflect.** Answer the four reflection questions from the handout in `reflection.md`.

---

## Summary of Fixes

The codebase has undergone comprehensive static analysis remediation, functional bug fixing, and defensive hardening:

1. **Eliminated Runtime Crashes**:
   - `average_load()` validates route existence and handles empty trip lists (`len == 0`) by returning `0.0` instead of raising `ZeroDivisionError`.
   - Calling `average_load("R3")` after `remove_route("R3")` safely returns `None` without crashing with `KeyError`.
   - User input for route lookup checks for route existence before dictionary access, gracefully handling unknown routes (e.g., `"R99"`).
2. **Strict Input Validation**:
   - `add_trip_log()` rejects negative counts and non-integer inputs (such as `-6` or `"full"`), raising descriptive `ValueError` exceptions before appending data.
3. **Removed Mutable Default Arguments**:
   - Replaced `logs=[]` in `add_trip_log` with `logs=None`, dynamically initializing a new list per call to prevent state leakage across unrelated calls.
4. **Eliminated Bare Except & Exception Swallowing**:
   - Removed `try...except: pass` in `underused_routes()`. Replaced with explicit positive condition checks.
5. **Secure File Handling & Path Independence**:
   - Refactored `sync_fleet_data()` to use `with open(..., encoding="utf-8")` context managers.
   - Resolved file paths using `pathlib.Path(__file__).resolve().parent / "fleet.json"`, ensuring correct execution from any shell working directory.
   - Separated atomic persistence into `save_fleet_data()` and `load_fleet_data()`.
6. **Code Quality, Security & Style Compliance**:
   - Renamed `assignDriver` to PEP 8 compliant `assign_driver`.
   - Used standard library `secrets.choice()` for secure randomness (resolving Bandit B311).
   - Added complete PEP 257 docstrings to all functions and module level.
   - Converted legacy `%` string formatting to f-strings.
   - Added `if __name__ == "__main__":` entry point guard.
   - Achieved a perfect **10.00 / 10** Pylint score, **0 Flake8 violations**, and **0 Bandit findings**.

---

## Running the Program and Tests

### Run the Interactive Program
```bash
python shuttle_system.py
```

### Run the Automated Test Suite
```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

### Run Static Analysis Verification
```bash
python -m pylint shuttle_system.py
python -m flake8 shuttle_system.py
python -m bandit -r shuttle_system.py
```

---

## Deliverables & Report Locations

- **Cleaned Code**: `shuttle_system.py`
- **Issue Documentation**: `issues.md`
- **Handout Reflection**: `reflection.md`
- **Automated Tests**: `tests/test_shuttle_system.py`
- **Starter Fleet File**: `fleet.json`
- **Official Submission PDF**: `Lab5_Static_Analysis_Results.pdf` (contains labeled terminal screenshots of Pylint, Flake8, Bandit, and Tests)
- **Baseline Reports**: `reports/before/`
  - `reports/before/pylint_report.txt`
  - `reports/before/flake8_report.txt`
  - `reports/before/bandit_report.txt`
- **Final Reports**: `reports/after/`
  - `reports/after/pylint_report.txt`
  - `reports/after/flake8_report.txt`
  - `reports/after/bandit_report.txt`
- **Comparative Analysis**: `reports/summary.md`
- **Submission Information**: `SUBMISSION_INFO.txt`
