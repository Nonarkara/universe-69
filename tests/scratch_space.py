"""Portable fixture storage, preferring the workbench's external volume."""
import os


def scratch_root():
    root = os.environ.get('UNIVERSE69_TEST_SCRATCH')
    if not root and os.path.isdir('/Volumes/Data'):
        root = '/Volumes/Data/agent-scratch/universe69-tests'
    if root:
        os.makedirs(root, exist_ok=True)
    return root  # None lets tempfile honor TMPDIR and other-machine defaults.
