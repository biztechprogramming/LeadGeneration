"""
Intelligent Research System - Modular Architecture

A refactored AI-driven research system that uses iterative exploration
to build comprehensive company intelligence.

Main Components:
- GeminiCerebrasClient: API communication with Cerebras
- AIDecisionEngine: AI-powered decision making and analysis
- FunctionRegistry: Manages available research functions
- DataAccumulator: Stores collected research data
- ImageCollector: Handles people image detection and download
- WebsiteExplorer: Web page exploration (stub implementation)
- IterativeResearchOrchestrator: Main coordination logic

Usage:
    from intelligent_research import IterativeResearchOrchestrator

    orchestrator = IterativeResearchOrchestrator(
        csv_path='companies.csv',
        output_dir='research_output'
    )
    orchestrator.run_batch_research(limit=5)
"""

__version__ = "2.0.0"

from .utils import load_env_file, sanitize_filename, validate_url
from .cerebras_client import GeminiCerebrasClient
from .ai_decision_engine import AIDecisionEngine
from .function_registry import FunctionRegistry
from .data_accumulator import DataAccumulator
from .image_collector import ImageCollector
from .website_explorer import WebsiteExplorer
from .research_orchestrator import IterativeResearchOrchestrator

__all__ = [
    # Utility functions
    'load_env_file',
    'sanitize_filename',
    'validate_url',

    # Core components
    'GeminiCerebrasClient',
    'AIDecisionEngine',
    'FunctionRegistry',
    'DataAccumulator',
    'ImageCollector',
    'WebsiteExplorer',

    # Main orchestrator
    'IterativeResearchOrchestrator',
]
