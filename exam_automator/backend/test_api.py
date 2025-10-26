"""
API Testing Script for Peer Review Platform
Tests all new endpoints with sample data
"""

import requests
import json
from pathlib import Path
import time

# Base URL
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠️  {message}{RESET}")

def print_header(message):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}{RESET}\n")


class APITester:
    def __init__(self):
        self.submission_id = None
        self.student_id = "test-student-001"
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    def test_health_check(self):
        """Test if server is running"""
        print_header("Testing Server Health")
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print_success("Server is running")
                print_info(f"Response: {response.json()}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Server returned status {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Failed to connect to server: {e}")
            print_warning("Make sure the server is running: python main.py")
            self.results["failed"] += 1
            self.results["errors"].append(str(e))
            return False
    
    def test_system_stats(self):
        """Test system statistics endpoint"""
        print_header("Testing System Statistics")
        try:
            response = requests.get(f"{API_BASE}/peer-review/stats/overview")
            if response.status_code == 200:
                stats = response.json()
                print_success("System stats retrieved")
                print_info(f"Total Submissions: {stats.get('total_submissions', 0)}")
                print_info(f"Plagiarism Reports: {stats.get('plagiarism_reports_generated', 0)}")
                print_info(f"Code Analyses: {stats.get('code_analyses_completed', 0)}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Failed with status {response.status_code}")
                self.results["failed"] += 1
                return False
        except Exception as e:
            print_error(f"Request failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(str(e))
            return False
    
    def test_upload_submission(self):
        """Test submission upload"""
        print_header("Testing Submission Upload")
        
        # Create a test Python file
        test_code = '''
def bubble_sort(arr):
    """
    Sort an array using bubble sort algorithm
    """
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def main():
    numbers = [64, 34, 25, 12, 22, 11, 90]
    print("Original array:", numbers)
    sorted_numbers = bubble_sort(numbers)
    print("Sorted array:", sorted_numbers)

if __name__ == "__main__":
    main()
'''
        
        try:
            # Prepare files
            files = {
                'files': ('bubble_sort.py', test_code, 'text/plain')
            }
            
            # Prepare form data
            data = {
                'student_id': self.student_id,
                'student_name': 'Test Student',
                'student_email': 'test@example.com',
                'submission_type': 'code',
                'title': 'Bubble Sort Implementation',
                'description': 'Implementation of bubble sort algorithm in Python',
                'tags': 'sorting, algorithm, python',
                'programming_languages': 'python'
            }
            
            response = requests.post(
                f"{API_BASE}/peer-review/submissions/upload",
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                result = response.json()
                self.submission_id = result['submission_id']
                print_success(f"Submission uploaded successfully")
                print_info(f"Submission ID: {self.submission_id}")
                print_info(f"Files uploaded: {result['files_uploaded']}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Upload failed with status {response.status_code}")
                print_error(f"Response: {response.text}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print_error(f"Upload failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(str(e))
            return False
    
    def test_get_submission(self):
        """Test getting submission details"""
        print_header("Testing Get Submission")
        
        if not self.submission_id:
            print_warning("Skipping: No submission ID available")
            return False
        
        try:
            response = requests.get(
                f"{API_BASE}/peer-review/submissions/{self.submission_id}"
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success("Submission retrieved successfully")
                print_info(f"Title: {result['submission']['metadata']['title']}")
                print_info(f"Type: {result['submission']['submission_type']}")
                print_info(f"Files: {result['submission']['metadata']['total_files']}")
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Failed with status {response.status_code}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print_error(f"Request failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(str(e))
            return False
    
    def test_code_analysis(self):
        """Test code analysis"""
        print_header("Testing Code Analysis")
        
        if not self.submission_id:
            print_warning("Skipping: No submission ID available")
            return False
        
        try:
            print_info("Running code analysis (this may take a few seconds)...")
            response = requests.post(
                f"{API_BASE}/peer-review/submissions/{self.submission_id}/analyze-code",
                params={'include_ai_feedback': False}  # Disable AI to avoid API key issues
            )
            
            if response.status_code == 200:
                result = response.json()
                report = result['report']
                
                print_success("Code analysis completed")
                print_info(f"Files analyzed: {report['total_files_analyzed']}")
                print_info(f"Average score: {report['average_overall_score']}/100")
                
                if report['file_reports']:
                    first_report = report['file_reports'][0]
                    if 'quality_score' in first_report:
                        print_info(f"Grade: {first_report['quality_score']['grade']}")
                        print_info(f"Complexity: {first_report['metrics']['cyclomatic_complexity']}")
                
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Analysis failed with status {response.status_code}")
                print_error(f"Response: {response.text}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print_error(f"Analysis failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(str(e))
            return False
    
    def test_plagiarism_check(self):
        """Test plagiarism detection"""
        print_header("Testing Plagiarism Detection")
        
        if not self.submission_id:
            print_warning("Skipping: No submission ID available")
            return False
        
        try:
            print_info("Running plagiarism check (this may take a few seconds)...")
            response = requests.post(
                f"{API_BASE}/peer-review/submissions/{self.submission_id}/check-plagiarism",
                params={'check_limit': 10}
            )
            
            if response.status_code == 200:
                result = response.json()
                report = result['report']
                
                print_success("Plagiarism check completed")
                print_info(f"Originality Score: {report['overall_originality_score']}%")
                print_info(f"Risk Level: {report['risk_level']}")
                print_info(f"Matches Found: {report['total_matches_found']}")
                print_info(f"Sources Checked: {report['sources_checked']}")
                
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Check failed with status {response.status_code}")
                print_error(f"Response: {response.text}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print_error(f"Check failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(str(e))
            return False
    
    def test_get_student_submissions(self):
        """Test getting all student submissions"""
        print_header("Testing Get Student Submissions")
        
        try:
            response = requests.get(
                f"{API_BASE}/peer-review/submissions/student/{self.student_id}"
            )
            
            if response.status_code == 200:
                submissions = response.json()
                print_success(f"Retrieved {len(submissions)} submission(s)")
                
                for sub in submissions:
                    print_info(f"  - {sub['metadata']['title']} ({sub['submission_id'][:8]}...)")
                
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Failed with status {response.status_code}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print_error(f"Request failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(str(e))
            return False
    
    def test_student_dashboard(self):
        """Test student dashboard"""
        print_header("Testing Student Dashboard")
        
        try:
            response = requests.get(
                f"{API_BASE}/peer-review/dashboard/student/{self.student_id}"
            )
            
            if response.status_code == 200:
                dashboard = response.json()
                print_success("Dashboard retrieved")
                print_info(f"Total Submissions: {dashboard['total_submissions']}")
                print_info(f"Under Review: {dashboard['submissions_under_review']}")
                print_info(f"Completed: {dashboard['submissions_completed']}")
                
                self.results["passed"] += 1
                return True
            else:
                print_error(f"Failed with status {response.status_code}")
                self.results["failed"] += 1
                return False
                
        except Exception as e:
            print_error(f"Request failed: {e}")
            self.results["failed"] += 1
            self.results["errors"].append(str(e))
            return False
    
    def print_summary(self):
        """Print test summary"""
        print_header("Test Summary")
        
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.results['passed']}{RESET}")
        print(f"{RED}Failed: {self.results['failed']}{RESET}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.results["errors"]:
            print(f"\n{RED}Errors:{RESET}")
            for error in self.results["errors"]:
                print(f"  - {error}")
        
        if pass_rate >= 80:
            print(f"\n{GREEN}🎉 Great! Most tests passed!{RESET}")
        elif pass_rate >= 50:
            print(f"\n{YELLOW}⚠️  Some tests failed. Check the errors above.{RESET}")
        else:
            print(f"\n{RED}❌ Many tests failed. Check server logs and configuration.{RESET}")
    
    def run_all_tests(self):
        """Run all API tests"""
        print(f"{BLUE}")
        print("="*60)
        print("  ProctorIQ Peer Review Platform - API Test Suite")
        print("="*60)
        print(RESET)
        
        # Test in order
        if not self.test_health_check():
            print_error("Server is not running. Stopping tests.")
            return
        
        self.test_system_stats()
        
        if self.test_upload_submission():
            time.sleep(1)  # Wait a bit between tests
            self.test_get_submission()
            time.sleep(1)
            self.test_code_analysis()
            time.sleep(1)
            self.test_plagiarism_check()
        
        time.sleep(1)
        self.test_get_student_submissions()
        time.sleep(1)
        self.test_student_dashboard()
        
        # Print summary
        self.print_summary()


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
