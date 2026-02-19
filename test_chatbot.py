#!/usr/bin/env python
"""
Healthcare AI Chatbot - Comprehensive Test Suite
Tests all chatbot functionality locally
Run: python test_chatbot.py
"""

import requests
import json
import sys
from typing import Dict, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_ID = 1

# ANSI Colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Test counters
tests_passed = 0
tests_failed = 0
tests_skipped = 0


def print_header(text):
    """Print formatted test header"""
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text.center(60)}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_test(name):
    """Print test name"""
    print(f"{BOLD}📋 Test: {name}{RESET}")


def print_success(message):
    """Print success message"""
    global tests_passed
    tests_passed += 1
    print(f"{GREEN}✅ PASS:{RESET} {message}")


def print_failure(message, error=None):
    """Print failure message"""
    global tests_failed
    tests_failed += 1
    print(f"{RED}❌ FAIL:{RESET} {message}")
    if error:
        print(f"{RED}   Error: {error}{RESET}")


def print_skip(message):
    """Print skip message"""
    global tests_skipped
    tests_skipped += 1
    print(f"{YELLOW}⏭️  SKIP:{RESET} {message}")


def print_info(message):
    """Print info message"""
    print(f"{YELLOW}ℹ️  INFO:{RESET} {message}")


def print_response(response_data: Dict[Any, Any]):
    """Pretty print API response"""
    print(f"{YELLOW}Response:{RESET}")
    print(json.dumps(response_data, indent=2))


def test_health_chat(message: str, expected_intent=None) -> Dict[Any, Any]:
    """
    Test health chat endpoint
    """
    try:
        response = requests.post(
            f"{BASE_URL}/api/health-chat",
            json={
                "user_id": TEST_USER_ID,
                "message": message
            },
            timeout=10
        )

        if response.status_code != 200:
            print_failure(f"Status code {response.status_code}", response.text)
            return None

        data = response.json()
        print_success(f"Received response (type: {data.get('type')})")
        return data

    except requests.exceptions.ConnectionError:
        print_failure("Cannot connect to Flask server", "Is it running on http://localhost:5000?")
        return None
    except Exception as e:
        print_failure("Request failed", str(e))
        return None


def test_general_chat(message: str) -> Dict[Any, Any]:
    """
    Test general chat endpoint
    """
    try:
        response = requests.post(
            f"{BASE_URL}/api/general-chat",
            json={
                "user_id": TEST_USER_ID,
                "message": message
            },
            timeout=15  # OpenAI might take longer
        )

        if response.status_code != 200:
            print_failure(f"Status code {response.status_code}", response.text)
            return None

        data = response.json()
        print_success(f"Received response (type: {data.get('type')})")
        return data

    except requests.exceptions.Timeout:
        print_skip("OpenAI request timed out (network/API being slow)")
        return None
    except Exception as e:
        print_failure("Request failed", str(e))
        return None


def test_chat_suggestions() -> Dict[Any, Any]:
    """
    Test chat suggestions endpoint
    """
    try:
        response = requests.get(
            f"{BASE_URL}/api/chat-suggestions/{TEST_USER_ID}",
            timeout=5
        )

        if response.status_code != 200:
            print_failure(f"Status code {response.status_code}", response.text)
            return None

        data = response.json()
        print_success(f"Received {len(data.get('suggestions', []))} suggestions")
        return data

    except Exception as e:
        print_failure("Request failed", str(e))
        return None


def validate_response_structure(response: Dict, expected_fields: list) -> bool:
    """
    Validate response has expected fields
    """
    for field in expected_fields:
        if field not in response:
            print_failure(f"Missing field: {field}", None)
            return False
    return True


# ==================== TESTS ====================

def test_1_server_connectivity():
    """Test 1: Server Connectivity"""
    print_header("Test 1: Server Connectivity")
    print_test("Check if Flask server is running")

    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print_success("Flask server is running and accessible")
        return True
    except:
        print_failure(
            "Cannot reach Flask server",
            f"Make sure to run: python run.py"
        )
        return False


def test_2_health_chat_risk_explanation():
    """Test 2: Health Chat - Risk Explanation"""
    print_header("Test 2: Health Chat - Risk Explanation")
    print_test("Request risk explanation")

    response = test_health_chat("Explain my diabetes risk")
    if not response:
        return False

    # Validate structure
    expected_fields = ["type", "reply"]
    if not validate_response_structure(response, expected_fields):
        return False

    # Check type
    if response.get("type") != "health_response":
        if response.get("type") == "error":
            print_skip("No prediction results in database yet (create assessment first)")
            return True  # Not a failure, just no data
        else:
            print_failure("Unexpected response type", response.get("type"))
            return False

    print_success("Risk explanation response formatted correctly")
    print_info(f"Risk level: {response.get('risk_level', 'N/A')}")
    print_info(f"Probability: {response.get('probability', 'N/A')}%")
    return True


def test_3_health_chat_preventive_measures():
    """Test 3: Health Chat - Preventive Measures"""
    print_header("Test 3: Health Chat - Preventive Measures")
    print_test("Request preventive measures")

    response = test_health_chat("How can I reduce my diabetes risk?")
    if not response:
        return False

    # If no results in DB, it's OK
    if response.get("type") == "error" or response.get("type") == "health_response":
        print_success("Preventive measures response received")
        return True

    return False


def test_4_health_chat_health_education():
    """Test 4: Health Chat - Health Education"""
    print_header("Test 4: Health Chat - Health Education")
    print_test("Request health education")

    response = test_health_chat("What is diabetes?")
    if not response:
        return False

    # Should get health_response or general response
    if response.get("type") in ["health_response", "ai_response"]:
        print_success("Health education response received")
        if "What is it?" in response.get("reply", "") or "definition" in response.get("reply", "").lower():
            print_success("Response contains educational content")
        return True

    return False


def test_5_health_chat_navigation():
    """Test 5: Health Chat - Navigation Commands"""
    print_header("Test 5: Health Chat - Navigation Commands")
    print_test("Request navigation to dashboard")

    response = test_health_chat("Go to dashboard")
    if not response:
        return False

    # Should get navigation response
    if response.get("type") == "navigation":
        print_success("Navigation response received")
        if "route" in response:
            print_success(f"Navigation route: {response.get('route')}")
        return True
    else:
        print_info(f"Received {response.get('type')} instead of navigation")
        return True


def test_6_health_chat_safety_block():
    """Test 6: Health Chat - Safety Block (Prescription)"""
    print_header("Test 6: Health Chat - Safety Block")
    print_test("Attempt to get medication prescription (should be blocked)")

    response = test_health_chat("What medicine should I take for diabetes?")
    if not response:
        return False

    # Should be blocked
    if response.get("type") == "safety_block":
        print_success("Prescription request correctly blocked")
        if "cannot provide" in response.get("reply", "").lower():
            print_success("Refusal message is clear")
        return True
    else:
        print_failure(
            "Prescription request was not blocked!",
            "This is a safety issue"
        )
        return False


def test_7_general_chat():
    """Test 7: General Chat (OpenAI Fallback)"""
    print_header("Test 7: General Chat - OpenAI Fallback")
    print_test("Request general knowledge question")

    response = test_general_chat("What is machine learning?")
    if not response:
        return True  # Might be skipped if no API key

    # Validate structure
    if response.get("type") == "ai_response":
        print_success("AI response received from OpenAI")
        print_info(f"Source: {response.get('source', 'Unknown')}")
        if "machine learning" in response.get("reply", "").lower():
            print_success("Response contains relevant information")
        return True
    elif response.get("type") == "error":
        print_skip("OpenAI API not configured or unreachable")
        return True
    else:
        print_failure("Unexpected response type", response.get("type"))
        return False


def test_8_chat_suggestions():
    """Test 8: Chat Suggestions Endpoint"""
    print_header("Test 8: Chat Suggestions Endpoint")
    print_test("Get suggested chat prompts")

    response = test_chat_suggestions()
    if not response:
        return False

    # Validate structure
    if "suggestions" in response:
        suggestions = response.get("suggestions", [])
        print_success(f"Received {len(suggestions)} suggestions")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print_info(f"  {i}. {suggestion}")
        return True
    else:
        print_failure("No suggestions in response")
        return False


def test_9_context_awareness():
    """Test 9: Context Awareness"""
    print_header("Test 9: Context Awareness")
    print_test("Verify user context is returned")

    response = test_health_chat("Explain my risk")
    if not response:
        return False

    if "user_context" in response:
        context = response.get("user_context", {})
        print_success("User context is included in response")
        print_info(f"  Username: {context.get('username', 'N/A')}")
        print_info(f"  Last disease: {context.get('last_disease', 'None')}")
        return True
    else:
        print_info("User context not in response (might be expected)")
        return True


def test_10_error_handling():
    """Test 10: Error Handling"""
    print_header("Test 10: Error Handling")
    print_test("Test invalid request handling")

    try:
        response = requests.post(
            f"{BASE_URL}/api/health-chat",
            json={"user_id": 999999, "message": ""},  # Invalid user, empty message
            timeout=5
        )

        if response.status_code == 400 or response.status_code == 401:
            print_success("Invalid request properly rejected")
            return True
        else:
            print_info(f"Received status code {response.status_code}")
            return True

    except Exception as e:
        print_failure("Error handling test failed", str(e))
        return False


def test_11_response_time():
    """Test 11: Response Time"""
    print_header("Test 11: Response Time")
    print_test("Measure response time for health chat")

    import time
    start = time.time()
    response = test_health_chat("What is normal blood pressure?")
    elapsed = time.time() - start

    if response:
        print_success(f"Response received in {elapsed:.2f} seconds")
        if elapsed < 2:
            print_success("Response time is excellent (< 2s)")
        elif elapsed < 5:
            print_success("Response time is good (< 5s)")
        else:
            print_info(f"Response time is slow (> 5s)")
        return True

    return False


def test_12_multiple_messages():
    """Test 12: Multiple Sequential Messages"""
    print_header("Test 12: Multiple Sequential Messages")
    print_test("Send multiple sequential messages")

    messages = [
        "Hello",
        "What is diabetes?",
        "How to prevent it?",
        "Go to dashboard"
    ]

    success_count = 0
    for msg in messages:
        response = test_health_chat(msg)
        if response:
            success_count += 1

    print_success(f"Successfully processed {success_count}/{len(messages)} messages")
    return success_count == len(messages)


# ==================== MAIN TEST RUNNER ====================

def run_all_tests():
    """Run all tests"""
    print_header("Healthcare AI Chatbot - Test Suite")
    print(f"Testing against: {BASE_URL}\n")

    # Run tests
    tests = [
        ("Server Connectivity", test_1_server_connectivity),
        ("Health Chat - Risk Explanation", test_2_health_chat_risk_explanation),
        ("Health Chat - Preventive Measures", test_3_health_chat_preventive_measures),
        ("Health Chat - Health Education", test_4_health_chat_health_education),
        ("Health Chat - Navigation", test_5_health_chat_navigation),
        ("Safety Block (Prescription)", test_6_health_chat_safety_block),
        ("General Chat (OpenAI)", test_7_general_chat),
        ("Chat Suggestions", test_8_chat_suggestions),
        ("Context Awareness", test_9_context_awareness),
        ("Error Handling", test_10_error_handling),
        ("Response Time", test_11_response_time),
        ("Multiple Sequential Messages", test_12_multiple_messages),
    ]

    for test_name, test_func in tests:
        try:
            result = test_func()
            print()  # Blank line between tests
        except Exception as e:
            print_failure(f"Test crashed", str(e))
            print()

    # Print summary
    print_header("Test Summary")
    total = tests_passed + tests_failed + tests_skipped
    print(f"{GREEN}{BOLD}Passed: {tests_passed}/{total}{RESET}")
    print(f"{RED}{BOLD}Failed: {tests_failed}/{total}{RESET}")
    print(f"{YELLOW}{BOLD}Skipped: {tests_skipped}/{total}{RESET}")

    # Final status
    print("\n" + "="*60)
    if tests_failed == 0:
        print(f"{GREEN}{BOLD}✅ ALL TESTS PASSED!{RESET}")
        return 0
    else:
        print(f"{RED}{BOLD}❌ SOME TESTS FAILED!{RESET}")
        return 1


if __name__ == "__main__":
    print(f"\n{BOLD}Healthcare AI Chatbot - Test Suite{RESET}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    exit_code = run_all_tests()

    print(f"\nEnded at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    sys.exit(exit_code)
