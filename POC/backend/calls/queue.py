"""A waiting line of finished calls.

A list is enough. The oldest job is at the front. In this demo the HTTP
request puts one job on the line and a worker takes it immediately, so the
screen can show the steps. The line is still a separate object, which is
the same shape as a real queue.
"""


class JobQueue:
    """Jobs waiting, and jobs that have finished."""

    def __init__(self):
        # Oldest job is index 0.
        self.jobs = []
        self.done = []

    def clear(self):
        """Empty both lists. Used by Reset."""
        self.jobs = []
        self.done = []

    def enqueue(self, job):
        """Add a job at the back. Status starts as queued."""
        stored = {**job, "status": "queued"}
        self.jobs.append(stored)
        return stored

    def dequeue(self):
        """Take the oldest job and mark it running. None if the line is empty."""
        if not self.jobs:
            return None
        job = self.jobs.pop(0)
        job["status"] = "running"
        return job

    def finish(self, job):
        """Move a finished job onto the done list."""
        job["status"] = "done"
        self.done.append(job)

    def snapshot(self):
        """A copy the screen can show without changing the line."""
        return {"waiting": list(self.jobs), "done": list(self.done)}
