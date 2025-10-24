"""
Function registry for tracking and executing research actions.

This module manages the registration and execution of research functions,
logging missing functions for future implementation.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, Callable, Optional


class FunctionRegistry:
    """
    Tracks available functions and logs missing ones.
    Provides centralized function registration and execution.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize function registry.

        Args:
            output_dir: Directory for logging missing functions
        """
        self.functions: Dict[str, Callable] = {}
        self.missing_log_path = Path(output_dir) / "missing_functions.json"
        self.missing_functions: Dict[str, int] = {}
        self._load_missing_log()

    def _load_missing_log(self) -> None:
        """Load existing missing functions log from disk."""
        if self.missing_log_path.exists():
            try:
                with open(self.missing_log_path, 'r') as f:
                    self.missing_functions = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load missing functions log: {e}")
                self.missing_functions = {}

    def register(self, name: str, function: Callable) -> None:
        """
        Register a function for execution.

        Args:
            name: Function name identifier
            function: Callable function to register
        """
        self.functions[name] = function

    def has_function(self, name: str) -> bool:
        """
        Check if function exists in registry.

        Args:
            name: Function name to check

        Returns:
            True if function is registered
        """
        return name in self.functions

    def execute(self, name: str, params: Dict[str, Any]) -> Tuple[bool, Any]:
        """
        Execute a registered function with parameters.

        Args:
            name: Function name to execute
            params: Dictionary of function parameters

        Returns:
            Tuple of (success: bool, result: Any)
            - success: True if function executed successfully
            - result: Function return value or error message
        """
        if name not in self.functions:
            self._log_missing(name)
            return False, f"Function '{name}' not implemented"

        try:
            result = self.functions[name](**params)
            return True, result
        except TypeError as e:
            return False, f"Function '{name}' parameter error: {str(e)}"
        except Exception as e:
            return False, f"Function '{name}' failed: {str(e)}"

    def _log_missing(self, name: str) -> None:
        """
        Log a missing function call.

        Increments counter for the function and persists to disk.

        Args:
            name: Function name that was called but not found
        """
        self.missing_functions[name] = self.missing_functions.get(name, 0) + 1

        try:
            # Ensure parent directory exists
            self.missing_log_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.missing_log_path, 'w') as f:
                json.dump(self.missing_functions, f, indent=2)

            print(f"    ⚠ Missing function: {name} (logged)")
        except IOError as e:
            print(f"    ⚠ Missing function: {name} (could not log: {e})")

    def get_missing_functions(self) -> Dict[str, int]:
        """
        Get dictionary of missing functions and their call counts.

        Returns:
            Dictionary mapping function names to call counts
        """
        return self.missing_functions.copy()

    def get_registered_functions(self) -> list:
        """
        Get list of registered function names.

        Returns:
            List of function names currently registered
        """
        return list(self.functions.keys())

    def clear_missing_log(self) -> None:
        """Clear the missing functions log."""
        self.missing_functions = {}
        if self.missing_log_path.exists():
            self.missing_log_path.unlink()
