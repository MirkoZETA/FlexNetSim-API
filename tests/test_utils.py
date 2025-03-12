import os
from contextlib import contextmanager

@contextmanager
def temporarily_rename_file(source_path, temp_path):
    """
    Context manager to safely rename a file temporarily and restore it afterward,
    even if an exception occurs.
    
    Args:
        source_path: Path to the file to rename
        temp_path: Temporary path to use
    """
    original_exists = os.path.exists(source_path)
    temp_exists = os.path.exists(temp_path)
    
    # Only proceed if the source file exists
    if original_exists:
        try:
            # If a temp file already exists, delete it
            if temp_exists:
                os.remove(temp_path)
            
            # Rename the source file to the temp path
            os.rename(source_path, temp_path)
            yield
        finally:
            # Always attempt to restore the original file
            if os.path.exists(temp_path):
                os.rename(temp_path, source_path)
            
            # Restore any backed up temp file
            if temp_exists and os.path.exists(f"{temp_path}.backup"):
                os.rename(f"{temp_path}.backup", temp_path)
    else:
        yield
