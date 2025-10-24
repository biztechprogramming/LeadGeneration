#!/usr/bin/env python3
"""
Test Script for Intelligent Research System

This script demonstrates the AI-driven iterative research approach by:
1. Testing with the first company from CSV
2. Showing the AI decision-making process in real-time
3. Demonstrating function registry and logging
4. Testing image detection (if available)
5. Showing data accumulation across iterations
6. Verifying missing function logging
7. Using actual Cerebras API with verbose output
8. Proper error handling and reporting

Usage:
    python test_intelligent_research.py
    python test_intelligent_research.py --verbose
    python test_intelligent_research.py --max-iterations 5
"""

import sys
import json
import os
from pathlib import Path
from datetime import datetime
from cerebras_intelligent_research import (
    IterativeResearchOrchestrator,
    GeminiCerebrasClient,
    AIDecisionEngine,
    FunctionRegistry,
    DataAccumulator,
    ImageCollector,
    load_env_file
)


class VerboseTestRunner:
    """
    Wrapper that adds verbose output to the research process.
    """

    def __init__(self, orchestrator: IterativeResearchOrchestrator, verbose: bool = True):
        """
        Initialize test runner.

        Args:
            orchestrator: The research orchestrator
            verbose: Enable verbose output
        """
        self.orchestrator = orchestrator
        self.verbose = verbose
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "tests_passed": [],
            "tests_failed": [],
            "ai_decisions": [],
            "functions_executed": [],
            "functions_missing": [],
            "images_detected": [],
            "data_progression": []
        }

    def log(self, category: str, message: str, data: any = None):
        """
        Log test information.

        Args:
            category: Log category
            message: Log message
            data: Optional data to store
        """
        if self.verbose:
            print(f"[{category.upper()}] {message}")
            if data and self.verbose:
                print(f"  Data: {json.dumps(data, indent=2)[:500]}")

        # Store for final report
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "message": message,
            "data": data
        }

        if category == "ai_decision":
            self.test_results["ai_decisions"].append(log_entry)
        elif category == "function_executed":
            self.test_results["functions_executed"].append(log_entry)
        elif category == "function_missing":
            self.test_results["functions_missing"].append(log_entry)
        elif category == "image_detected":
            self.test_results["images_detected"].append(log_entry)
        elif category == "data_progression":
            self.test_results["data_progression"].append(log_entry)

    def test_api_connection(self) -> bool:
        """
        Test 1: Verify Cerebras API connection.

        Returns:
            True if connection successful
        """
        print("\n" + "="*60)
        print("TEST 1: Cerebras API Connection")
        print("="*60)

        try:
            client = self.orchestrator.client

            # Send simple test prompt
            response = client.send_prompt(
                "Say 'API connection successful' and nothing else.",
                system_prompt="You are a test assistant.",
                max_tokens=50
            )

            if response and "successful" in response.lower():
                self.log("test", "API connection test PASSED")
                self.test_results["tests_passed"].append("api_connection")
                print("✓ Cerebras API is responding correctly")
                return True
            else:
                self.log("test", "API connection test FAILED", {"response": response})
                self.test_results["tests_failed"].append({
                    "test": "api_connection",
                    "reason": "Unexpected response"
                })
                print("✗ API responded but with unexpected output")
                return False

        except Exception as e:
            self.log("test", "API connection test FAILED", {"error": str(e)})
            self.test_results["tests_failed"].append({
                "test": "api_connection",
                "reason": str(e)
            })
            print(f"✗ API connection failed: {e}")
            return False

    def test_function_registry(self) -> bool:
        """
        Test 2: Verify function registry and missing function logging.

        Returns:
            True if registry working correctly
        """
        print("\n" + "="*60)
        print("TEST 2: Function Registry & Missing Function Logging")
        print("="*60)

        try:
            registry = self.orchestrator.registry

            # Test registered function
            print("\n→ Testing registered function (save_contact)...")
            success, result = registry.execute("save_contact", {
                "name": "Test User",
                "title": "Test Title",
                "email": "test@example.com"
            })

            if success:
                self.log("function_executed", "Registered function executed", {
                    "function": "save_contact",
                    "success": True
                })
                print("  ✓ Registered function executed successfully")
            else:
                print(f"  ✗ Registered function failed: {result}")
                return False

            # Test missing function
            print("\n→ Testing missing function (nonexistent_function)...")
            success, result = registry.execute("nonexistent_function", {
                "param": "value"
            })

            if not success and "not implemented" in result:
                self.log("function_missing", "Missing function logged", {
                    "function": "nonexistent_function"
                })
                print("  ✓ Missing function correctly logged")
            else:
                print("  ✗ Missing function handling failed")
                return False

            # Check missing functions log
            print("\n→ Verifying missing functions log file...")
            if registry.missing_log_path.exists():
                with open(registry.missing_log_path, 'r') as f:
                    missing_log = json.load(f)
                    print(f"  ✓ Missing functions log exists")
                    print(f"  → Contains {len(missing_log)} entries")
                    if self.verbose:
                        print(f"  → Log: {json.dumps(missing_log, indent=2)}")

            self.test_results["tests_passed"].append("function_registry")
            print("\n✓ Function registry test PASSED")
            return True

        except Exception as e:
            self.log("test", "Function registry test FAILED", {"error": str(e)})
            self.test_results["tests_failed"].append({
                "test": "function_registry",
                "reason": str(e)
            })
            print(f"✗ Function registry test failed: {e}")
            return False

    def test_data_accumulator(self) -> bool:
        """
        Test 3: Verify data accumulation across iterations.

        Returns:
            True if accumulator working correctly
        """
        print("\n" + "="*60)
        print("TEST 3: Data Accumulator & Progression")
        print("="*60)

        try:
            # Create test accumulator
            test_company = {"Title": "Test Company", "WebsiteURL": "test.com"}
            accumulator = DataAccumulator(test_company)

            print("\n→ Testing data accumulation...")

            # Add various data types
            accumulator.add_contact("John Doe", "CEO", "john@test.com")
            accumulator.add_pain_point("Budget constraints", "Hiring freeze mentioned", "About page")
            accumulator.add_technology("Python", "Backend", "Job posting")
            accumulator.add_news("Funding Round", "Raised $5M", "http://news.com", "2025-01-15")
            accumulator.add_source("http://test.com", "homepage")
            accumulator.increment_iteration()

            # Get context and verify
            context = accumulator.get_context()

            checks = {
                "contacts": len(context['contacts']) == 1,
                "pain_points": len(context['pain_points']) == 1,
                "tech_stack": len(context['tech_stack']) == 1,
                "news": len(context['news']) == 1,
                "sources": len(context['sources_explored']) == 1,
                "iterations": context['metadata']['iterations'] == 1
            }

            for check_name, passed in checks.items():
                status = "✓" if passed else "✗"
                print(f"  {status} {check_name}: {passed}")

            if all(checks.values()):
                self.log("data_progression", "Data accumulation working", context)
                self.test_results["tests_passed"].append("data_accumulator")
                print("\n✓ Data accumulator test PASSED")
                return True
            else:
                self.test_results["tests_failed"].append({
                    "test": "data_accumulator",
                    "reason": "Some checks failed"
                })
                print("\n✗ Data accumulator test FAILED")
                return False

        except Exception as e:
            self.log("test", "Data accumulator test FAILED", {"error": str(e)})
            self.test_results["tests_failed"].append({
                "test": "data_accumulator",
                "reason": str(e)
            })
            print(f"✗ Data accumulator test failed: {e}")
            return False

    def test_ai_decision_engine(self) -> bool:
        """
        Test 4: Verify AI decision engine with real API call.

        Returns:
            True if AI decision engine working correctly
        """
        print("\n" + "="*60)
        print("TEST 4: AI Decision Engine")
        print("="*60)

        try:
            engine = self.orchestrator.ai_engine

            # Create test data
            test_company = {
                "Title": "Triangle Manufacturing Co., Inc.",
                "WebsiteURL": "trianglemfg.com",
                "Address": "25 Park Way, Upper Saddle River, NJ 07458"
            }

            test_data = {
                "company": test_company,
                "contacts": [],
                "pain_points": [],
                "sources_explored": [
                    {"source": "trianglemfg.com", "type": "homepage"}
                ],
                "metadata": {"iterations": 1}
            }

            print("\n→ Sending data to AI for analysis...")
            print(f"  Company: {test_company['Title']}")
            print(f"  Current sources: {len(test_data['sources_explored'])}")

            decision = engine.analyze_data(test_data, test_company)

            print("\n→ AI Decision received:")
            print(f"  Status: {decision.get('status', 'unknown')}")
            print(f"  Actions: {len(decision.get('actions', []))}")
            print(f"  Next steps: {len(decision.get('next_steps', []))}")
            print(f"  Relevant data: {len(decision.get('relevant_data', []))}")

            if self.verbose:
                print("\n  Full decision:")
                print(json.dumps(decision, indent=2))

            # Log decision
            self.log("ai_decision", "AI analysis completed", decision)

            # Verify decision structure
            required_keys = ['status', 'actions', 'next_steps', 'relevant_data']
            has_all_keys = all(key in decision for key in required_keys)

            if has_all_keys:
                self.test_results["tests_passed"].append("ai_decision_engine")
                print("\n✓ AI decision engine test PASSED")
                return True
            else:
                missing = [key for key in required_keys if key not in decision]
                self.test_results["tests_failed"].append({
                    "test": "ai_decision_engine",
                    "reason": f"Missing keys: {missing}"
                })
                print(f"\n✗ AI decision missing keys: {missing}")
                return False

        except Exception as e:
            self.log("test", "AI decision engine test FAILED", {"error": str(e)})
            self.test_results["tests_failed"].append({
                "test": "ai_decision_engine",
                "reason": str(e)
            })
            print(f"✗ AI decision engine test failed: {e}")
            return False

    def test_image_collector(self) -> bool:
        """
        Test 5: Verify image detection logic.

        Returns:
            True if image collector working correctly
        """
        print("\n" + "="*60)
        print("TEST 5: Image Detection & Collection")
        print("="*60)

        try:
            collector = self.orchestrator.image_collector

            # Test HTML with various image types
            test_html = """
            <html>
                <body>
                    <img src="team/john-doe.jpg" alt="John Doe - CEO" />
                    <img src="logo.png" alt="Company Logo" />
                    <img src="staff/jane-smith.jpg" alt="Jane Smith, CTO" />
                    <img src="product-shot.jpg" alt="Our Product" />
                </body>
            </html>
            """

            print("\n→ Testing image detection heuristics...")

            # Test is_likely_person_image
            test_cases = [
                ("team/john.jpg", "Team member", True),
                ("logo.png", "Company Logo", False),
                ("headshot-ceo.jpg", "CEO Portrait", True),
                ("product.jpg", "Product Image", False),
                ("staff-photo.jpg", "Staff member", True)
            ]

            passed = 0
            for src, alt, expected in test_cases:
                result = collector._is_likely_person_image(src, alt)
                status = "✓" if result == expected else "✗"
                print(f"  {status} '{src}' + '{alt}': {result} (expected {expected})")
                if result == expected:
                    passed += 1

            print(f"\n  → Passed {passed}/{len(test_cases)} detection tests")

            if passed >= len(test_cases) * 0.8:  # 80% pass rate
                self.log("image_detected", "Image detection working", {
                    "passed": passed,
                    "total": len(test_cases)
                })
                self.test_results["tests_passed"].append("image_collector")
                print("\n✓ Image collector test PASSED")
                return True
            else:
                self.test_results["tests_failed"].append({
                    "test": "image_collector",
                    "reason": f"Only {passed}/{len(test_cases)} tests passed"
                })
                print("\n✗ Image collector test FAILED")
                return False

        except Exception as e:
            self.log("test", "Image collector test FAILED", {"error": str(e)})
            self.test_results["tests_failed"].append({
                "test": "image_collector",
                "reason": str(e)
            })
            print(f"✗ Image collector test failed: {e}")
            return False

    def run_live_company_test(self, max_iterations: int = 3) -> bool:
        """
        Test 6: Run actual research on first company from CSV.

        Args:
            max_iterations: Maximum iterations for research

        Returns:
            True if research completed successfully
        """
        print("\n" + "="*60)
        print("TEST 6: Live Company Research (First Company from CSV)")
        print("="*60)

        try:
            # Load first company
            companies = self.orchestrator.load_companies()
            if not companies:
                print("✗ No companies found in CSV")
                return False

            company = companies[0]
            print(f"\n→ Company: {company.get('Title', 'Unknown')}")
            print(f"→ Website: {company.get('WebsiteURL', 'N/A')}")
            print(f"→ Max iterations: {max_iterations}")

            # Run research with monitoring
            print("\n→ Starting iterative research...\n")

            accumulated_data = self.orchestrator.research_company(
                company,
                max_iterations=max_iterations
            )

            # Analyze results
            print("\n→ Research completed! Analyzing results...")

            analysis = {
                "iterations_completed": accumulated_data['metadata']['iterations'],
                "contacts_found": len(accumulated_data['contacts']),
                "pain_points_found": len(accumulated_data['pain_points']),
                "technologies_found": len(accumulated_data['tech_stack']),
                "news_found": len(accumulated_data['news']),
                "images_collected": len(accumulated_data['images']),
                "sources_explored": len(accumulated_data['sources_explored'])
            }

            print("\n→ Results Summary:")
            for key, value in analysis.items():
                print(f"  • {key.replace('_', ' ').title()}: {value}")

            # Generate report
            company_name = company.get('Title', 'Unknown')
            self.orchestrator.generate_final_report(company_name, accumulated_data)

            self.log("data_progression", "Live research completed", analysis)
            self.test_results["tests_passed"].append("live_company_research")
            print("\n✓ Live company research test PASSED")
            return True

        except Exception as e:
            self.log("test", "Live company research FAILED", {"error": str(e)})
            self.test_results["tests_failed"].append({
                "test": "live_company_research",
                "reason": str(e)
            })
            print(f"✗ Live company research failed: {e}")
            return False

    def save_test_report(self):
        """Save comprehensive test report."""
        self.test_results["end_time"] = datetime.now().isoformat()
        self.test_results["summary"] = {
            "total_tests": len(self.test_results["tests_passed"]) + len(self.test_results["tests_failed"]),
            "passed": len(self.test_results["tests_passed"]),
            "failed": len(self.test_results["tests_failed"])
        }

        report_path = self.orchestrator.output_dir / "test_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.test_results, f, indent=2)

        print(f"\n📄 Full test report saved: {report_path}")

    def print_final_summary(self):
        """Print final test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = len(self.test_results["tests_passed"])
        failed = len(self.test_results["tests_failed"])
        total = passed + failed

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {passed} ✓")
        print(f"Failed: {failed} ✗")

        if self.test_results["tests_passed"]:
            print("\n✓ Passed Tests:")
            for test in self.test_results["tests_passed"]:
                print(f"  • {test}")

        if self.test_results["tests_failed"]:
            print("\n✗ Failed Tests:")
            for test in self.test_results["tests_failed"]:
                print(f"  • {test['test']}: {test['reason']}")

        print("\n" + "="*60)

        # Additional stats
        print(f"\nAI Decisions Made: {len(self.test_results['ai_decisions'])}")
        print(f"Functions Executed: {len(self.test_results['functions_executed'])}")
        print(f"Missing Functions Logged: {len(self.test_results['functions_missing'])}")
        print(f"Images Detected: {len(self.test_results['images_detected'])}")

        print("\n" + "="*60)


def main():
    """Main test execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Test Intelligent Research System'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=3,
        help='Maximum iterations for live test (default: 3)'
    )
    parser.add_argument(
        '--csv',
        default='google_maps_leads.csv',
        help='Path to CSV file'
    )
    parser.add_argument(
        '--output',
        default='test_output',
        help='Output directory for test results'
    )

    args = parser.parse_args()

    # Banner
    print("\n" + "="*60)
    print("INTELLIGENT RESEARCH SYSTEM - TEST SUITE")
    print("="*60)
    print(f"CSV: {args.csv}")
    print(f"Output: {args.output}")
    print(f"Verbose: {args.verbose}")
    print(f"Max Iterations: {args.max_iterations}")
    print("="*60)

    # Check environment
    load_env_file()
    if not os.environ.get('CEREBRAS_API_KEY'):
        print("\n✗ ERROR: CEREBRAS_API_KEY not found!")
        print("\nSetup instructions:")
        print("1. Create .env file: cp .env.example .env")
        print("2. Add your key: CEREBRAS_API_KEY=your-key-here")
        print("3. Get key from: https://cloud.cerebras.ai/")
        sys.exit(1)

    print("\n✓ Environment configured")

    try:
        # Create orchestrator
        print("\n→ Initializing orchestrator...")
        orchestrator = IterativeResearchOrchestrator(
            csv_path=args.csv,
            output_dir=args.output
        )
        print("✓ Orchestrator initialized")

        # Create test runner
        runner = VerboseTestRunner(orchestrator, verbose=args.verbose)

        # Run tests
        tests = [
            ("API Connection", runner.test_api_connection),
            ("Function Registry", runner.test_function_registry),
            ("Data Accumulator", runner.test_data_accumulator),
            ("AI Decision Engine", runner.test_ai_decision_engine),
            ("Image Collector", runner.test_image_collector),
            ("Live Company Research", lambda: runner.run_live_company_test(args.max_iterations))
        ]

        print("\n→ Running test suite...\n")

        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                print(f"\n✗ FATAL ERROR in {test_name}: {e}")
                runner.test_results["tests_failed"].append({
                    "test": test_name,
                    "reason": f"Fatal error: {str(e)}"
                })

        # Save and print results
        runner.save_test_report()
        runner.print_final_summary()

        # Exit code
        failed = len(runner.test_results["tests_failed"])
        sys.exit(0 if failed == 0 else 1)

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
