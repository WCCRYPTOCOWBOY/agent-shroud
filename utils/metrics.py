"""
Metrics utility for Shroud.
Currently a placeholder — in the future we can track:
- number of jobs attempted
- success vs failure rate
- runtime stats
"""

def observe_attempt(success: bool):
    """
    Record the result of a job attempt.
    For now, just prints to console.
    """
    status = "success" if success else "failure"
    print(f"[Metrics] Attempt recorded: {status}")
