"""Touch operation detection and handling for Memory filesystem."""
import os
import psutil
import logging
from typing import Optional
from contextlib import contextmanager

@contextmanager
def find_touch_processes():
    """Find all touch processes currently running.
    
    Yields:
        List of (touch_proc, parent_proc) tuples
    """
    touch_procs = []
    try:
        for proc in psutil.process_iter(['name', 'pid', 'ppid']):
            if proc.info['name'] == 'touch':
                try:
                    parent = psutil.Process(proc.info['ppid'])
                    touch_procs.append((proc, parent))
                except psutil.NoSuchProcess:
                    continue
        yield touch_procs
    finally:
        # Process objects don't need explicit cleanup
        pass

def is_being_touched(path: str, mount_point: str, logger: Optional[logging.Logger] = None) -> bool:
    """Check if path is being accessed by a touch process.
    
    Args:
        path: FUSE path to check
        mount_point: FUSE mount point
        logger: Optional logger instance
        
    Returns:
        bool: True if a touch process is accessing this path
    """
    try:
        # Normalize all paths to absolute
        abs_mount = os.path.abspath(mount_point)
        rel_path = path.lstrip('/')  # Remove leading slash
        sys_path = os.path.join(abs_mount, rel_path)
        sys_path = os.path.abspath(sys_path)
        
        if logger:
            logger.debug(f"Checking touch status for {path} (sys_path: {sys_path})")
        
        # Use context manager to safely handle process resources
        with find_touch_processes() as touch_procs:
            # Look for our path in touch process open files
            for touch_proc, parent_proc in touch_procs:
                try:
                    # Check if touch command targets our file
                    cmdline = touch_proc.cmdline()
                    if logger:
                        logger.debug(f"Found touch process {touch_proc.pid} with cmdline: {cmdline}")
                    
                    # Look for our path in command line args
                    try:
                        # Get the touch process's current working directory
                        touch_cwd = touch_proc.cwd()
                        if logger:
                            logger.debug(f"Touch process {touch_proc.pid} cwd: {touch_cwd}")
                        
                        # Handle paths relative to the mount point
                        for arg in cmdline[1:]:
                            # Get absolute path of touch target
                            abs_target = os.path.abspath(os.path.join(touch_cwd, arg))
                            
                            # Check if either:
                            # 1. The touch command is targeting our exact file
                            # 2. The touch command is run from inside mount point and targets match
                            if sys_path == abs_target:
                                if logger:
                                    logger.debug(f"Touch command targets our file: {sys_path}")
                                return True
                                
                            # Convert both paths to be relative to mount point for comparison
                            if touch_cwd.startswith(abs_mount):
                                try:
                                    # Get target path relative to touch's cwd first
                                    target_in_cwd = os.path.abspath(os.path.join(touch_cwd, arg))
                                    # Then make it relative to mount point
                                    target_rel = os.path.relpath(target_in_cwd, touch_cwd)
                                    if logger:
                                        logger.debug(f"Comparing relative paths: /{rel_path} vs /{target_rel}")
                                    if rel_path == target_rel:
                                        if logger:
                                            logger.debug(f"Touch command targets our file via relative path")
                                        return True
                                except ValueError:
                                    # Handle case where target is outside mount point
                                    continue
                    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                        if logger:
                            logger.debug(f"Error getting touch process cwd: {e}")
                    
                    # Also check open files as backup
                    open_files = touch_proc.open_files() + parent_proc.open_files()
                    if logger:
                        logger.debug(f"Open files for touch process {touch_proc.pid}: {[f.path for f in open_files]}")
                    
                    for f in open_files:
                        abs_path = os.path.abspath(f.path)
                        if abs_path == sys_path:
                            if logger:
                                logger.debug(f"Found our file in open files: {abs_path}")
                            return True
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    if logger:
                        logger.debug(f"Error accessing process {touch_proc.pid}: {e}")
                    continue
                    
    except Exception as e:
        if logger:
            logger.error(f"Error checking touch status: {e}")
        else:
            logging.error(f"Error checking touch status: {e}")
    
    if logger:
        logger.debug(f"No touch operation detected for {path}")
    return False