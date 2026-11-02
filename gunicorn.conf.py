"""Gunicorn configuration for CloudOps AI."""

from prometheus_client import multiprocess


def child_exit(server, worker):
    """Notify Prometheus when a Gunicorn worker exits."""
    multiprocess.mark_process_dead(worker.pid)
