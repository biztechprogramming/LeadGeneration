#!/usr/bin/env python3
"""
Test script for Cerebras Sales Intelligence Research System

This script runs the analysis on a small sample of companies
to verify the system works before processing all 122 companies.
"""

from sales_intelligence_cerebras import CerebrasSalesIntelligenceResearcher


def main():
    """Run test analysis on first 3 companies."""

    print("\n" + "="*70)
    print("CEREBRAS SALES INTELLIGENCE RESEARCH SYSTEM - TEST MODE")
    print("="*70)
    print("\nThis will process the FIRST 3 COMPANIES as a test.")
    print("Review the output before running full batch processing.")
    print("="*70 + "\n")

    # Confirm with user
    response = input("Continue with test? (y/n): ").strip().lower()
    if response != 'y':
        print("Test cancelled.")
        return

    # Create researcher instance
    researcher = CerebrasSalesIntelligenceResearcher(
        csv_path='google_maps_leads.csv',
        output_dir='test_reports_cerebras'  # Use separate directory for tests
    )

    # Process first 3 companies
    researcher.run_batch_analysis(limit=3, start_index=0)

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nReview the generated files in: test_reports_cerebras/")
    print("\nIf everything looks good, run the full batch:")
    print("  python sales_intelligence_cerebras.py")
    print("\nOr continue processing in batches:")
    print("  python sales_intelligence_cerebras.py --limit 10 --start 0")
    print("  python sales_intelligence_cerebras.py --limit 10 --start 10")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
