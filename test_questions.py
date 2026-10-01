"""
Test question definitions for the agent API regression test runner.

Add, remove, or edit entries here to change the test suite.
Each entry is a dict with:
  - name      (str, required)  : short label shown in the report
  - question  (str, required)  : the user message sent to the agent
  - agent     (str, optional)  : overrides DEFAULT_AGENT in run_tests.py
  - db_id     (str, optional)  : overrides DEFAULT_DB_ID in run_tests.py
"""

TESTS = [
    {
        "name": "List accelerators defined on Db2",
        "question": "List the accelerators that are defined on my Db2",
    },
    {
        "name": "Port and IP for accelerator ACCEL194",
        "question": "List the port number of the accelerator ACCEL194 and its IP address",
    },
    {
        "name": "IP address of accelerator SIM043",
        "question": "What is the IP address of the accelerator SIM043",
    },
    {
        "name": "Who created accelerator ACCEL194",
        "question": "Who created the accelerator ACCEL194",
    },
    {
        "name": "Who created accelerator with IP 10.101.14.43",
        "question": "Who created the accelerator with the IP address 10.101.14.43",
    },
    {
        "name": "All rows of SYSACCELERATORS",
        "question": "Give me all rows of the IDAA catalog table SYSACCELERATORS",
    },
    {
        "name": "All rows of SYSACCELERATEDTABLES",
        "question": "Give me all rows of the IDAA catalog table sysacceleratedtables",
    },
    {
        "name": "Accelerated tables altered in last month",
        "question": "Has any IDAA accelerated tables been altered in the last month? Give me the alter timestamp, sort by the newest",
    },
    {
        "name": "Last refresh timestamp of accelerated tables",
        "question": "Give me the last refresh timestamp of the accelerated tables",
    },
    {
        "name": "Accelerated tables with refresh older than 24 hours",
        "question": "Give me the last refresh timestamp of the accelerated tables that are older than 24 hours",
    },
    {
        "name": "All accelerators with connection details",
        "question": "Show me all accelerators and their connection details",
    },
    {
        "name": "Tables accelerated by SIM043",
        "question": "List all tables that are accelerated by SIM043",
    },
    {
        "name": "Find currently active accelerators",
        "question": "Find accelerators that are currently active",
    },
    {
        "name": "Authorization mappings for accelerator ACCEL194",
        "question": "Show me the authorization mappings for accelerator ACCEL194",
    },
    {
        "name": "All remote locations defined for IDAA",
        "question": "List all remote locations defined for IDAA",
    },
    {
        "name": "All TCP/IP connections for accelerators",
        "question": "Show me all TCP/IP connections for accelerators",
    },
    {
        "name": "Accelerated tables not refreshed in last week",
        "question": "Find accelerated tables that haven't been refreshed in the last week",
    },
    {
        "name": "Count of accelerated tables per accelerator",
        "question": "Get the count of accelerated tables per accelerator",
    },
    {
        "name": "Accelerators with IP addresses sorted by IP",
        "question": "Show me accelerators with their IP addresses sorted by IP",
    },
    {
        "name": "Accelerated tables altered today",
        "question": "List accelerated tables that were altered today",
    },
]
