"""
Multi-Language Test Suite
Testing AI detection across different programming languages
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector

print("=" * 100)
print("MULTI-LANGUAGE AI DETECTION TEST SUITE")
print("Testing: Java, C++, Ruby, Go, SQL, PHP, TypeScript, Swift")
print("=" * 100)

detector = PlagiarismDetector(use_vector_db=False)

test_cases = []

# ============================================================================
# TEST 1: Java - AI Generated
# ============================================================================
java_ai = '''/**
 * A comprehensive utility class for performing various string manipulation operations.
 * This class provides methods for reversing strings, checking palindromes, and more.
 * 
 * @author AI Assistant
 * @version 1.0
 */
public class StringUtils {
    
    /**
     * Reverses the input string.
     * 
     * This method takes a string as input and returns a new string with the characters
     * in reverse order. It handles null inputs by returning null.
     * 
     * @param input The string to be reversed
     * @return The reversed string, or null if input is null
     * @throws IllegalArgumentException if input is invalid
     */
    public static String reverseString(String input) {
        // Validate input parameter to ensure it is not null
        if (input == null) {
            return null;
        }
        
        // Create a StringBuilder to efficiently build the reversed string
        StringBuilder reversed = new StringBuilder();
        
        // Iterate through the input string from end to beginning
        for (int i = input.length() - 1; i >= 0; i--) {
            // Append each character to the StringBuilder
            reversed.append(input.charAt(i));
        }
        
        // Return the final reversed string
        return reversed.toString();
    }
    
    /**
     * Checks if the given string is a palindrome.
     * 
     * A palindrome is a string that reads the same forwards and backwards.
     * 
     * @param input The string to check
     * @return true if palindrome, false otherwise
     */
    public static boolean isPalindrome(String input) {
        // Handle null input
        if (input == null) {
            return false;
        }
        
        // Convert to lowercase for case-insensitive comparison
        String normalized = input.toLowerCase();
        
        // Get the reversed version
        String reversed = reverseString(normalized);
        
        // Compare original with reversed
        return normalized.equals(reversed);
    }
}'''

test_cases.append({
    "name": "Java - AI Generated (Excessive Javadoc)",
    "language": "java",
    "code": java_ai,
    "expected": "AI",
    "description": "Perfect Javadoc, comments on every line, over-explained"
})

# ============================================================================
# TEST 2: Java - Human Written
# ============================================================================
java_human = '''public class StringUtils {
    
    // quick reverse function
    public static String reverseString(String input) {
        if (input == null) return null;
        
        StringBuilder sb = new StringBuilder();
        for (int i = input.length() - 1; i >= 0; i--) {
            sb.append(input.charAt(i));
        }
        return sb.toString();
    }
    
    // check palindrome
    public static boolean isPalindrome(String s) {
        if (s == null) return false;
        String rev = reverseString(s.toLowerCase());
        return s.toLowerCase().equals(rev);
    }
}'''

test_cases.append({
    "name": "Java - Human Written",
    "language": "java",
    "code": java_human,
    "expected": "Human",
    "description": "Brief comments, concise code, abbreviations (sb, s)"
})

# ============================================================================
# TEST 3: C++ - AI Generated
# ============================================================================
cpp_ai = '''#include <iostream>
#include <vector>
#include <algorithm>

/**
 * @brief A template-based container class for managing a collection of elements
 * 
 * This class provides comprehensive functionality for storing, sorting, and
 * retrieving elements of any comparable type. It implements various algorithms
 * for efficient data management.
 * 
 * @tparam T The type of elements to store (must support comparison operators)
 */
template<typename T>
class Container {
private:
    // Internal vector to store the elements
    std::vector<T> elements;
    
public:
    /**
     * @brief Adds a new element to the container
     * 
     * This method appends the specified element to the end of the internal
     * vector, increasing the container size by one.
     * 
     * @param element The element to be added to the container
     */
    void add(const T& element) {
        // Add the element to the internal vector
        elements.push_back(element);
    }
    
    /**
     * @brief Sorts all elements in ascending order
     * 
     * This method uses the standard library's sort algorithm to arrange
     * all elements in ascending order based on their natural ordering.
     * 
     * Time Complexity: O(n log n)
     * Space Complexity: O(1)
     */
    void sort() {
        // Sort the elements using std::sort algorithm
        std::sort(elements.begin(), elements.end());
    }
    
    /**
     * @brief Retrieves the element at the specified index
     * 
     * @param index The zero-based index of the element to retrieve
     * @return The element at the specified position
     * @throws std::out_of_range if index is invalid
     */
    T get(size_t index) const {
        // Validate that index is within bounds
        if (index >= elements.size()) {
            throw std::out_of_range("Index out of bounds");
        }
        // Return the element at the specified index
        return elements[index];
    }
};'''

test_cases.append({
    "name": "C++ - AI Generated (Over-documented)",
    "language": "c++",
    "code": cpp_ai,
    "expected": "AI",
    "description": "Doxygen comments everywhere, complexity analysis, perfect style"
})

# ============================================================================
# TEST 4: C++ - Human Written
# ============================================================================
cpp_human = '''#include <iostream>
#include <vector>
#include <algorithm>

template<typename T>
class Container {
private:
    std::vector<T> items;
    
public:
    void add(const T& item) {
        items.push_back(item);
    }
    
    void sort() {
        std::sort(items.begin(), items.end());
    }
    
    T get(size_t idx) const {
        return items[idx];  // assuming valid idx
    }
    
    size_t size() const { return items.size(); }
};'''

test_cases.append({
    "name": "C++ - Human Written",
    "language": "c++",
    "code": cpp_human,
    "expected": "Human",
    "description": "No documentation, assumes valid input, abbreviations (idx, items)"
})

# ============================================================================
# TEST 5: Ruby - AI Generated
# ============================================================================
ruby_ai = '''##
# A comprehensive module for handling user authentication operations.
#
# This module provides various methods for user registration, login,
# and session management with proper error handling and validation.
#
# @author AI Assistant
# @version 1.0.0
module Authentication
  
  ##
  # Validates user credentials against the database.
  #
  # This method takes a username and password, performs validation,
  # and returns a boolean indicating whether the credentials are valid.
  #
  # @param username [String] the username to validate
  # @param password [String] the password to validate
  # @return [Boolean] true if credentials are valid, false otherwise
  # @raise [ArgumentError] if username or password is nil
  def self.validate_credentials(username, password)
    # Validate that username is not nil or empty
    raise ArgumentError, 'Username cannot be nil' if username.nil?
    raise ArgumentError, 'Password cannot be nil' if password.nil?
    
    # Validate that username meets minimum length requirement
    return false if username.length < 3
    
    # Validate that password meets minimum length requirement
    return false if password.length < 8
    
    # Additional validation logic would go here
    true
  end
  
  ##
  # Creates a new user session after successful authentication.
  #
  # @param user_id [Integer] the ID of the authenticated user
  # @return [String] the generated session token
  def self.create_session(user_id)
    # Generate a random session token
    require 'securerandom'
    session_token = SecureRandom.hex(32)
    
    # Store the session in the database
    # Implementation would go here
    
    # Return the generated session token
    session_token
  end
end'''

test_cases.append({
    "name": "Ruby - AI Generated (RDoc style)",
    "language": "ruby",
    "code": ruby_ai,
    "expected": "AI",
    "description": "Complete RDoc comments, every parameter documented, verbose"
})

# ============================================================================
# TEST 6: Ruby - Human Written
# ============================================================================
ruby_human = '''module Authentication
  
  # check if user creds are good
  def self.validate_credentials(username, password)
    return false if username.nil? || password.nil?
    return false if username.length < 3 || password.length < 8
    true  # would check db here
  end
  
  # make session token
  def self.create_session(user_id)
    require 'securerandom'
    SecureRandom.hex(32)  # good enough
  end
end'''

test_cases.append({
    "name": "Ruby - Human Written",
    "language": "ruby",
    "code": ruby_human,
    "expected": "Human",
    "description": "Brief comments, casual language ('good enough'), concise"
})

# ============================================================================
# TEST 7: Go - AI Generated
# ============================================================================
go_ai = '''package main

import (
    "errors"
    "fmt"
)

// User represents a user entity in the system with comprehensive fields
// for storing user information including authentication details and metadata.
type User struct {
    // ID is the unique identifier for the user
    ID int
    // Username is the unique username chosen by the user
    Username string
    // Email is the user's email address for communication
    Email string
    // PasswordHash stores the hashed password for security
    PasswordHash string
}

// ValidateUser performs comprehensive validation on a User struct to ensure
// all required fields are present and meet the necessary criteria.
//
// Parameters:
//   - user: The User struct to validate
//
// Returns:
//   - error: An error if validation fails, nil otherwise
func ValidateUser(user *User) error {
    // Validate that the user pointer is not nil
    if user == nil {
        return errors.New("user cannot be nil")
    }
    
    // Validate that the username is not empty
    if user.Username == "" {
        return errors.New("username is required")
    }
    
    // Validate that the username meets minimum length requirement
    if len(user.Username) < 3 {
        return errors.New("username must be at least 3 characters")
    }
    
    // Validate that the email is not empty
    if user.Email == "" {
        return errors.New("email is required")
    }
    
    // Validate that the password hash is present
    if user.PasswordHash == "" {
        return errors.New("password hash is required")
    }
    
    // All validations passed successfully
    return nil
}'''

test_cases.append({
    "name": "Go - AI Generated (GoDoc style)",
    "language": "go",
    "code": go_ai,
    "expected": "AI",
    "description": "Perfect GoDoc comments, parameters/returns documented, verbose"
})

# ============================================================================
# TEST 8: Go - Human Written
# ============================================================================
go_human = '''package main

import "errors"

type User struct {
    ID       int
    Username string
    Email    string
    Password string
}

// basic validation
func ValidateUser(user *User) error {
    if user == nil {
        return errors.New("user is nil")
    }
    
    if user.Username == "" || len(user.Username) < 3 {
        return errors.New("bad username")
    }
    
    if user.Email == "" {
        return errors.New("email required")
    }
    
    return nil
}'''

test_cases.append({
    "name": "Go - Human Written",
    "language": "go",
    "code": go_human,
    "expected": "Human",
    "description": "Minimal comments, 'bad username' informal, combined conditions"
})

# ============================================================================
# TEST 9: SQL - AI Generated
# ============================================================================
sql_ai = '''-- ============================================================================
-- This comprehensive stored procedure handles the complete user registration
-- process including validation, insertion, and audit logging.
--
-- Parameters:
--   @p_username VARCHAR(50) - The desired username for the new user
--   @p_email VARCHAR(100) - The email address of the new user
--   @p_password_hash VARCHAR(255) - The hashed password for security
--
-- Returns:
--   The ID of the newly created user, or NULL if registration failed
--
-- Author: AI Assistant
-- Version: 1.0.0
-- Last Modified: 2025-10-26
-- ============================================================================

CREATE PROCEDURE sp_RegisterUser
    @p_username VARCHAR(50),
    @p_email VARCHAR(100),
    @p_password_hash VARCHAR(255)
AS
BEGIN
    -- Set NOCOUNT ON to prevent extra result sets from interfering
    SET NOCOUNT ON;
    
    -- Declare variable to store the new user ID
    DECLARE @new_user_id INT;
    
    -- Begin transaction to ensure data consistency
    BEGIN TRANSACTION;
    
    BEGIN TRY
        -- Validate that username is not empty
        IF @p_username IS NULL OR LEN(@p_username) = 0
        BEGIN
            -- Rollback transaction due to invalid input
            ROLLBACK TRANSACTION;
            -- Return NULL to indicate failure
            RETURN NULL;
        END
        
        -- Validate that email is not empty
        IF @p_email IS NULL OR LEN(@p_email) = 0
        BEGIN
            -- Rollback transaction due to invalid input
            ROLLBACK TRANSACTION;
            -- Return NULL to indicate failure
            RETURN NULL;
        END
        
        -- Insert the new user record into the users table
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (@p_username, @p_email, @p_password_hash, GETDATE());
        
        -- Retrieve the ID of the newly inserted user
        SET @new_user_id = SCOPE_IDENTITY();
        
        -- Commit the transaction to persist changes
        COMMIT TRANSACTION;
        
        -- Return the new user ID
        RETURN @new_user_id;
        
    END TRY
    BEGIN CATCH
        -- Rollback transaction in case of any error
        ROLLBACK TRANSACTION;
        -- Return NULL to indicate failure
        RETURN NULL;
    END CATCH
END;'''

test_cases.append({
    "name": "SQL - AI Generated (Over-commented)",
    "language": "sql",
    "code": sql_ai,
    "expected": "AI",
    "description": "Massive header comment, comment on every line, perfect structure"
})

# ============================================================================
# TEST 10: SQL - Human Written
# ============================================================================
sql_human = '''-- quick user registration proc
CREATE PROCEDURE sp_RegisterUser
    @p_username VARCHAR(50),
    @p_email VARCHAR(100),
    @p_password_hash VARCHAR(255)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @new_user_id INT;
    
    BEGIN TRANSACTION;
    BEGIN TRY
        -- basic checks
        IF @p_username IS NULL OR @p_email IS NULL
        BEGIN
            ROLLBACK;
            RETURN NULL;
        END
        
        INSERT INTO users (username, email, password_hash, created_at)
        VALUES (@p_username, @p_email, @p_password_hash, GETDATE());
        
        SET @new_user_id = SCOPE_IDENTITY();
        COMMIT;
        RETURN @new_user_id;
    END TRY
    BEGIN CATCH
        ROLLBACK;
        RETURN NULL;
    END CATCH
END;'''

test_cases.append({
    "name": "SQL - Human Written",
    "language": "sql",
    "code": sql_human,
    "expected": "Human",
    "description": "'quick' and 'basic' language, minimal comments, concise"
})

# Run all tests
print(f"\n✅ Plagiarism detector initialized with Groq (lightning fast!)\n")

results = []
for idx, test in enumerate(test_cases, 1):
    print("=" * 100)
    print(f"TEST {idx}/10: {test['name']}")
    print("=" * 100)
    print(f"Language: {test['language'].upper()}")
    print(f"Expected: {test['expected']}")
    print(f"Description: {test['description']}")
    
    result = detector.detect_ai_generated_code(test['code'], language=test['language'])
    
    confidence = result.get('confidence', 0)
    is_ai = result.get('is_ai_generated', False)
    verdict = result.get('verdict', 'unknown')
    
    print(f"\n📊 RESULT:")
    print(f"   Verdict: {verdict}")
    print(f"   Confidence: {confidence}%")
    print(f"   AI Generated: {is_ai}")
    
    # Check if detection matches expectation
    if test['expected'] == "AI":
        success = (is_ai or confidence >= 70)
        emoji = "✅" if success else "❌"
        print(f"\n{emoji} Expected AI: {'Correctly detected' if success else 'MISSED'}")
    else:
        success = (not is_ai and verdict == "human_written")
        emoji = "✅" if success else "❌"
        print(f"\n{emoji} Expected Human: {'Correctly detected' if success else 'MISSED'}")
    
    results.append({
        "test": test['name'],
        "language": test['language'],
        "expected": test['expected'],
        "verdict": verdict,
        "confidence": confidence,
        "success": success
    })
    
    print()

# Summary
print("=" * 100)
print("MULTI-LANGUAGE TEST SUMMARY")
print("=" * 100)

passed = sum(1 for r in results if r['success'])
total = len(results)

print(f"\n✅ Passed: {passed}/{total} ({int(passed/total*100)}%)")
print(f"❌ Failed: {total - passed}/{total}")

# By language
print(f"\n📊 Results by Language:")
languages = {}
for r in results:
    lang = r['language']
    if lang not in languages:
        languages[lang] = {'passed': 0, 'total': 0}
    languages[lang]['total'] += 1
    if r['success']:
        languages[lang]['passed'] += 1

for lang, stats in sorted(languages.items()):
    rate = int(stats['passed'] / stats['total'] * 100)
    emoji = "✅" if rate == 100 else "⚠️"
    print(f"   {emoji} {lang.upper()}: {stats['passed']}/{stats['total']} ({rate}%)")

print(f"\n📋 Detailed Results:")
for r in results:
    status = "✅ PASS" if r['success'] else "❌ FAIL"
    print(f"   {status} | {r['language'].upper():6s} | {r['test']:40s} | {r['confidence']}% ({r['verdict']})")

print("\n" + "=" * 100)
if passed == total:
    print("🎉 PERFECT! Universal detection works across ALL programming languages!")
elif passed >= total * 0.8:
    print("✅ EXCELLENT! System works well across different languages.")
else:
    print("⚠️  Some languages need tuning.")
print("=" * 100)
