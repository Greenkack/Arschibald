#!/usr/bin/env python3
"""
Backend Packaging Test Suite

This script tests the packaged backend executable to ensure it works correctly.

Usage:
    python test_packaging.py [--executable PATH]

Options:
    --executable PATH    Path to the backend executable (default: dist/backend/backend)
"""

import os
import sys
import time
import subprocess
import platform
import argparse
import requests
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(message):
    """Print test message"""
    print(f"\n{Colors.OKBLUE}▶ {message}{Colors.ENDC}")

def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}  ✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}  ✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}  ⚠ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message"""
    print(f"  ℹ {message}")

class BackendTester:
    def __init__(self, executable_path):
        self.executable_path = Path(executable_path)
        self.process = None
        self.base_url = "http://localhost:8000"
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
    
    def test_executable_exists(self):
        """Test 1: Check if executable exists"""
        print_test("Test 1: Checking if executable exists")
        
        if self.executable_path.exists():
            print_success(f"Executable found at {self.executable_path}")
            self.test_results['passed'] += 1
            return True
        else:
            print_error(f"Executable not found at {self.executable_path}")
            self.test_results['failed'] += 1
            return False
    
    def test_executable_permissions(self):
        """Test 2: Check executable permissions"""
        print_test("Test 2: Checking executable permissions")
        
        if platform.system() != 'Windows':
            if os.access(self.executable_path, os.X_OK):
                print_success("Executable has execute permissions")
                self.test_results['passed'] += 1
                return True
            else:
                print_error("Executable does not have execute permissions")
                print_info("Run: chmod +x " + str(self.executable_path))
                self.test_results['failed'] += 1
                return False
        else:
            print_success("Windows executable (no permission check needed)")
            self.test_results['passed'] += 1
            return True
    
    def test_executable_size(self):
        """Test 3: Check executable size"""
        print_test("Test 3: Checking executable size")
        
        size_mb = self.executable_path.stat().st_size / (1024 * 1024)
        print_info(f"Executable size: {size_mb:.2f} MB")
        
        if size_mb < 10:
            print_warning("Executable seems too small, may be incomplete")
            self.test_results['warnings'] += 1
        elif size_mb > 200:
            print_warning("Executable is quite large (>200 MB)")
            self.test_results['warnings'] += 1
        else:
            print_success("Executable size is reasonable")
            self.test_results['passed'] += 1
        
        return True
    
    def test_help_command(self):
        """Test 4: Test --help command"""
        print_test("Test 4: Testing --help command")
        
        try:
            result = subprocess.run(
                [str(self.executable_path), '--help'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 or 'uvicorn' in result.stdout.lower():
                print_success("Help command works")
                print_info(f"Output preview: {result.stdout[:100]}...")
                self.test_results['passed'] += 1
                return True
            else:
                print_warning("Help command returned non-zero exit code")
                print_info(f"Exit code: {result.returncode}")
                self.test_results['warnings'] += 1
                return True
        except subprocess.TimeoutExpired:
            print_warning("Help command timed out")
            self.test_results['warnings'] += 1
            return True
        except Exception as e:
            print_error(f"Failed to run help command: {e}")
            self.test_results['failed'] += 1
            return False
    
    def test_server_startup(self):
        """Test 5: Test server startup"""
        print_test("Test 5: Testing server startup")
        
        try:
            # Start the server
            print_info("Starting backend server...")
            self.process = subprocess.Popen(
                [str(self.executable_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            print_info("Waiting for server to start (10 seconds)...")
            time.sleep(10)
            
            # Check if process is still running
            if self.process.poll() is None:
                print_success("Server started successfully")
                self.test_results['passed'] += 1
                return True
            else:
                print_error("Server process terminated unexpectedly")
                stdout, stderr = self.process.communicate()
                print_info(f"STDOUT: {stdout[:200]}")
                print_info(f"STDERR: {stderr[:200]}")
                self.test_results['failed'] += 1
                return False
        except Exception as e:
            print_error(f"Failed to start server: {e}")
            self.test_results['failed'] += 1
            return False
    
    def test_health_endpoint(self):
        """Test 6: Test health endpoint"""
        print_test("Test 6: Testing health endpoint")
        
        if self.process is None or self.process.poll() is not None:
            print_error("Server is not running")
            self.test_results['failed'] += 1
            return False
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                print_success("Health endpoint responded successfully")
                print_info(f"Response: {response.json()}")
                self.test_results['passed'] += 1
                return True
            else:
                print_error(f"Health endpoint returned status {response.status_code}")
                self.test_results['failed'] += 1
                return False
        except requests.exceptions.ConnectionError:
            print_error("Could not connect to server")
            print_info("Server may not have started properly")
            self.test_results['failed'] += 1
            return False
        except Exception as e:
            print_error(f"Failed to test health endpoint: {e}")
            self.test_results['failed'] += 1
            return False
    
    def test_api_docs(self):
        """Test 7: Test API documentation endpoint"""
        print_test("Test 7: Testing API documentation")
        
        if self.process is None or self.process.poll() is not None:
            print_error("Server is not running")
            self.test_results['failed'] += 1
            return False
        
        try:
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            
            if response.status_code == 200:
                print_success("API documentation is accessible")
                self.test_results['passed'] += 1
                return True
            else:
                print_warning(f"API docs returned status {response.status_code}")
                self.test_results['warnings'] += 1
                return True
        except Exception as e:
            print_warning(f"Could not access API docs: {e}")
            self.test_results['warnings'] += 1
            return True
    
    def test_memory_usage(self):
        """Test 8: Test memory usage"""
        print_test("Test 8: Testing memory usage")
        
        if self.process is None or self.process.poll() is not None:
            print_error("Server is not running")
            self.test_results['failed'] += 1
            return False
        
        try:
            import psutil
            process = psutil.Process(self.process.pid)
            memory_mb = process.memory_info().rss / (1024 * 1024)
            
            print_info(f"Memory usage: {memory_mb:.2f} MB")
            
            if memory_mb > 500:
                print_warning("Memory usage is high (>500 MB)")
                self.test_results['warnings'] += 1
            else:
                print_success("Memory usage is reasonable")
                self.test_results['passed'] += 1
            
            return True
        except ImportError:
            print_warning("psutil not installed, skipping memory test")
            self.test_results['warnings'] += 1
            return True
        except Exception as e:
            print_warning(f"Could not measure memory usage: {e}")
            self.test_results['warnings'] += 1
            return True
    
    def test_response_time(self):
        """Test 9: Test response time"""
        print_test("Test 9: Testing response time")
        
        if self.process is None or self.process.poll() is not None:
            print_error("Server is not running")
            self.test_results['failed'] += 1
            return False
        
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/health", timeout=5)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            print_info(f"Response time: {response_time_ms:.2f} ms")
            
            if response_time_ms > 1000:
                print_warning("Response time is slow (>1000 ms)")
                self.test_results['warnings'] += 1
            else:
                print_success("Response time is good")
                self.test_results['passed'] += 1
            
            return True
        except Exception as e:
            print_warning(f"Could not measure response time: {e}")
            self.test_results['warnings'] += 1
            return True
    
    def test_concurrent_requests(self):
        """Test 10: Test concurrent requests"""
        print_test("Test 10: Testing concurrent requests")
        
        if self.process is None or self.process.poll() is not None:
            print_error("Server is not running")
            self.test_results['failed'] += 1
            return False
        
        try:
            import concurrent.futures
            
            def make_request():
                return requests.get(f"{self.base_url}/health", timeout=5)
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
            success_count = sum(1 for r in results if r.status_code == 200)
            
            if success_count == 10:
                print_success("All concurrent requests succeeded")
                self.test_results['passed'] += 1
            else:
                print_warning(f"Only {success_count}/10 concurrent requests succeeded")
                self.test_results['warnings'] += 1
            
            return True
        except Exception as e:
            print_warning(f"Could not test concurrent requests: {e}")
            self.test_results['warnings'] += 1
            return True
    
    def cleanup(self):
        """Clean up test resources"""
        print_test("Cleaning up")
        
        if self.process and self.process.poll() is None:
            print_info("Stopping backend server...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
                print_success("Server stopped successfully")
            except subprocess.TimeoutExpired:
                print_warning("Server did not stop gracefully, killing...")
                self.process.kill()
                self.process.wait()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'Test Summary'.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")
        
        total = self.test_results['passed'] + self.test_results['failed'] + self.test_results['warnings']
        
        print(f"{Colors.OKGREEN}Passed:   {self.test_results['passed']}/{total}{Colors.ENDC}")
        print(f"{Colors.FAIL}Failed:   {self.test_results['failed']}/{total}{Colors.ENDC}")
        print(f"{Colors.WARNING}Warnings: {self.test_results['warnings']}/{total}{Colors.ENDC}")
        
        if self.test_results['failed'] == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ All critical tests passed!{Colors.ENDC}")
            return 0
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}✗ Some tests failed{Colors.ENDC}")
            return 1
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'Backend Packaging Test Suite'.center(60)}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
        
        print_info(f"Platform: {platform.system()} {platform.machine()}")
        print_info(f"Python: {sys.version.split()[0]}")
        print_info(f"Executable: {self.executable_path}")
        
        try:
            # Run tests
            if not self.test_executable_exists():
                return self.print_summary()
            
            self.test_executable_permissions()
            self.test_executable_size()
            self.test_help_command()
            
            if self.test_server_startup():
                self.test_health_endpoint()
                self.test_api_docs()
                self.test_memory_usage()
                self.test_response_time()
                self.test_concurrent_requests()
        finally:
            self.cleanup()
        
        return self.print_summary()

def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test packaged backend executable')
    parser.add_argument(
        '--executable',
        default=None,
        help='Path to backend executable'
    )
    args = parser.parse_args()
    
    # Determine executable path
    if args.executable:
        executable_path = Path(args.executable)
    else:
        backend_dir = Path(__file__).parent
        if platform.system() == 'Windows':
            executable_path = backend_dir / 'dist' / 'backend' / 'backend.exe'
        else:
            executable_path = backend_dir / 'dist' / 'backend' / 'backend'
    
    # Run tests
    tester = BackendTester(executable_path)
    return tester.run_all_tests()

if __name__ == '__main__':
    sys.exit(main())
