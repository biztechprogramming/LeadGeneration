#!/usr/bin/env python3
"""
Iterative AI-Driven Research System - Entry Point

Clean refactored version using modular architecture.
Coordinates intelligent company research using Cerebras AI.

Usage:
    python cerebras_intelligent_research_refactored.py --csv companies.csv --limit 5
    python cerebras_intelligent_research_refactored.py --csv companies.csv --start 10 --limit 20
"""

import argparse
from intelligent_research import IterativeResearchOrchestrator


def main():
    """Main entry point for intelligent research system."""
    parser = argparse.ArgumentParser(
        description='Iterative AI-Driven Research System with Cerebras',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process first 5 companies
  %(prog)s --csv google_maps_leads.csv --limit 5

  # Process companies 10-30
  %(prog)s --csv google_maps_leads.csv --start 10 --limit 20

  # Process all companies with custom output directory
  %(prog)s --csv companies.csv --output my_research

  # Process with more iterations per company
  %(prog)s --csv companies.csv --limit 5 --max-iterations 15
        """
    )

    parser.add_argument(
        '--csv',
        default='google_maps_leads.csv',
        help='Path to CSV file with company data (default: google_maps_leads.csv)'
    )
    parser.add_argument(
        '--output',
        default='intelligent_research_output',
        help='Output directory for research results (default: intelligent_research_output)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Maximum number of companies to process (default: all)'
    )
    parser.add_argument(
        '--start',
        type=int,
        default=0,
        help='Starting index (0-based) (default: 0)'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum research iterations per company (default: 10)'
    )

    args = parser.parse_args()

    try:
        # Create orchestrator
        orchestrator = IterativeResearchOrchestrator(
            csv_path=args.csv,
            output_dir=args.output
        )

        # Run batch research
        orchestrator.run_batch_research(
            limit=args.limit,
            start_index=args.start
        )

    except ValueError as e:
        print(f"\nConfiguration Error: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"\nFile Error: {e}")
        return 1
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
