"""
Additional Programming Languages Test
Testing: PHP, TypeScript, Swift, Rust, Kotlin
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "exam_automator" / "backend"))

from services.plagiarism_detector import PlagiarismDetector

print("=" * 100)
print("ADDITIONAL LANGUAGES TEST: PHP, TypeScript, Swift, Rust, Kotlin")
print("=" * 100)

detector = PlagiarismDetector(use_vector_db=False)

test_cases = []

# ============================================================================
# TEST 1: PHP - AI Generated
# ============================================================================
php_ai = '''<?php
/**
 * UserValidator class - Provides comprehensive user data validation functionality
 * 
 * This class implements various validation methods for user input including
 * email validation, password strength checking, and username format verification.
 * All methods follow PSR-12 coding standards and include proper error handling.
 * 
 * @package App\Validators
 * @author AI Assistant
 * @version 1.0.0
 */
class UserValidator {
    
    /**
     * Validates an email address format using comprehensive regex pattern
     * 
     * This method checks if the provided email string matches the standard
     * email format including local part, @ symbol, and domain requirements.
     * 
     * @param string $email The email address to validate
     * @return bool True if email is valid, false otherwise
     * @throws InvalidArgumentException if email parameter is not a string
     */
    public static function validateEmail($email) {
        // Validate that the input parameter is a string
        if (!is_string($email)) {
            throw new InvalidArgumentException('Email must be a string');
        }
        
        // Use filter_var with FILTER_VALIDATE_EMAIL for comprehensive validation
        return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
    }
    
    /**
     * Validates password strength against security requirements
     * 
     * This method ensures passwords meet minimum security standards including
     * length requirements and character complexity rules.
     * 
     * @param string $password The password to validate
     * @return bool True if password meets requirements, false otherwise
     */
    public static function validatePassword($password) {
        // Check minimum length requirement (8 characters)
        if (strlen($password) < 8) {
            return false;
        }
        
        // Check for at least one uppercase letter
        if (!preg_match('/[A-Z]/', $password)) {
            return false;
        }
        
        // Check for at least one lowercase letter
        if (!preg_match('/[a-z]/', $password)) {
            return false;
        }
        
        // Check for at least one digit
        if (!preg_match('/[0-9]/', $password)) {
            return false;
        }
        
        // All validation checks passed
        return true;
    }
}
?>'''

test_cases.append({
    "name": "PHP - AI Generated",
    "language": "php",
    "code": php_ai,
    "expected": "AI",
    "description": "PHPDoc everywhere, comments on every check, overly verbose"
})

# ============================================================================
# TEST 2: PHP - Human Written
# ============================================================================
php_human = '''<?php
class UserValidator {
    
    // check email format
    public static function validateEmail($email) {
        return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
    }
    
    // password needs 8+ chars, upper, lower, number
    public static function validatePassword($pass) {
        if (strlen($pass) < 8) return false;
        
        // check requirements
        $hasUpper = preg_match('/[A-Z]/', $pass);
        $hasLower = preg_match('/[a-z]/', $pass);
        $hasNumber = preg_match('/[0-9]/', $pass);
        
        return $hasUpper && $hasLower && $hasNumber;
    }
}
?>'''

test_cases.append({
    "name": "PHP - Human Written",
    "language": "php",
    "code": php_human,
    "expected": "Human",
    "description": "Brief comments, abbreviation (pass), combined checks"
})

# ============================================================================
# TEST 3: TypeScript - AI Generated
# ============================================================================
typescript_ai = '''/**
 * Interface representing a comprehensive user entity with all necessary fields
 * for authentication and profile management in the application.
 * 
 * @interface User
 */
interface User {
    /** The unique identifier for the user */
    id: number;
    /** The username chosen by the user (must be unique) */
    username: string;
    /** The user's email address for communication */
    email: string;
    /** Indicates whether the user has verified their email */
    emailVerified: boolean;
    /** Timestamp of when the user account was created */
    createdAt: Date;
}

/**
 * A service class providing comprehensive user management functionality
 * including registration, authentication, and profile updates.
 * 
 * @class UserService
 */
class UserService {
    /**
     * Creates a new user in the system with proper validation
     * 
     * This method validates all user input, checks for existing users,
     * and creates a new user record in the database with appropriate
     * default values and timestamps.
     * 
     * @param username - The desired username (minimum 3 characters)
     * @param email - The user's email address (must be valid format)
     * @param password - The password (minimum 8 characters)
     * @returns Promise<User> The newly created user object
     * @throws Error if validation fails or user already exists
     */
    async createUser(username: string, email: string, password: string): Promise<User> {
        // Validate that username meets minimum length requirement
        if (username.length < 3) {
            throw new Error('Username must be at least 3 characters long');
        }
        
        // Validate that email is not empty
        if (!email || email.length === 0) {
            throw new Error('Email is required');
        }
        
        // Validate that password meets security requirements
        if (password.length < 8) {
            throw new Error('Password must be at least 8 characters long');
        }
        
        // Create the user object with all required fields
        const newUser: User = {
            id: Date.now(), // Generate temporary ID
            username: username,
            email: email,
            emailVerified: false,
            createdAt: new Date()
        };
        
        // Return the newly created user
        return newUser;
    }
}'''

test_cases.append({
    "name": "TypeScript - AI Generated",
    "language": "typescript",
    "code": typescript_ai,
    "expected": "AI",
    "description": "TSDoc everywhere, every parameter documented, verbose comments"
})

# ============================================================================
# TEST 4: TypeScript - Human Written
# ============================================================================
typescript_human = '''interface User {
    id: number;
    username: string;
    email: string;
    emailVerified: boolean;
    createdAt: Date;
}

class UserService {
    // quick user creation
    async createUser(username: string, email: string, password: string): Promise<User> {
        // basic validation
        if (username.length < 3) throw new Error('Username too short');
        if (!email) throw new Error('Email required');
        if (password.length < 8) throw new Error('Password too short');
        
        return {
            id: Date.now(),
            username,
            email,
            emailVerified: false,
            createdAt: new Date()
        };
    }
}'''

test_cases.append({
    "name": "TypeScript - Human Written",
    "language": "typescript",
    "code": typescript_human,
    "expected": "Human",
    "description": "'quick' language, shorthand properties, brief comments"
})

# ============================================================================
# TEST 5: Swift - AI Generated
# ============================================================================
swift_ai = '''import Foundation

/**
 A comprehensive structure representing a user entity with full documentation
 
 This struct encapsulates all necessary user information including authentication
 credentials and profile data. It conforms to Codable for JSON serialization.
 
 - Author: AI Assistant
 - Version: 1.0.0
 */
struct User: Codable {
    /// The unique identifier for the user
    let id: Int
    /// The username chosen by the user
    let username: String
    /// The user's email address
    let email: String
    /// Indicates whether the email has been verified
    var emailVerified: Bool
    
    /**
     Validates the user's data to ensure all fields meet requirements
     
     This method performs comprehensive validation on all user fields including
     username length, email format, and other business rules.
     
     - Returns: A Boolean value indicating whether the user data is valid
     - Throws: ValidationError if any field fails validation
     */
    func validate() -> Bool {
        // Validate that username meets minimum length requirement
        guard username.count >= 3 else {
            return false
        }
        
        // Validate that email is not empty
        guard !email.isEmpty else {
            return false
        }
        
        // Validate email format using regex pattern
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,64}"
        let emailPredicate = NSPredicate(format:"SELF MATCHES %@", emailRegex)
        guard emailPredicate.evaluate(with: email) else {
            return false
        }
        
        // All validation checks passed successfully
        return true
    }
}'''

test_cases.append({
    "name": "Swift - AI Generated",
    "language": "swift",
    "code": swift_ai,
    "expected": "AI",
    "description": "Complete documentation, /// comments, verbose validation"
})

# ============================================================================
# TEST 6: Swift - Human Written
# ============================================================================
swift_human = '''import Foundation

struct User: Codable {
    let id: Int
    let username: String
    let email: String
    var emailVerified: Bool
    
    // basic validation
    func validate() -> Bool {
        guard username.count >= 3 && !email.isEmpty else {
            return false
        }
        
        // check email format
        let regex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,64}"
        let pred = NSPredicate(format:"SELF MATCHES %@", regex)
        return pred.evaluate(with: email)
    }
}'''

test_cases.append({
    "name": "Swift - Human Written",
    "language": "swift",
    "code": swift_human,
    "expected": "Human",
    "description": "Brief comments, abbreviations (pred, regex), combined guards"
})

# ============================================================================
# TEST 7: Rust - AI Generated
# ============================================================================
rust_ai = '''/// A comprehensive structure representing a user entity with complete documentation
///
/// This struct contains all necessary fields for user management including
/// authentication credentials and metadata. All fields are properly typed
/// and validated according to business requirements.
///
/// # Examples
///
/// ```
/// let user = User::new(1, "johndoe".to_string(), "john@example.com".to_string());
/// ```
#[derive(Debug, Clone)]
pub struct User {
    /// The unique identifier for this user
    pub id: u32,
    /// The username chosen by the user (must be unique)
    pub username: String,
    /// The user's email address for communication
    pub email: String,
}

impl User {
    /// Creates a new User instance with comprehensive validation
    ///
    /// This function validates all input parameters to ensure they meet
    /// the business requirements before creating the User instance.
    ///
    /// # Arguments
    ///
    /// * `id` - The unique identifier for the user
    /// * `username` - The desired username (minimum 3 characters)
    /// * `email` - The email address (must be valid format)
    ///
    /// # Returns
    ///
    /// Returns `Some(User)` if validation passes, `None` otherwise
    ///
    /// # Examples
    ///
    /// ```
    /// let user = User::new(1, "alice".to_string(), "alice@example.com".to_string());
    /// ```
    pub fn new(id: u32, username: String, email: String) -> Option<User> {
        // Validate that username meets minimum length requirement
        if username.len() < 3 {
            return None;
        }
        
        // Validate that email is not empty
        if email.is_empty() {
            return None;
        }
        
        // Create and return the new User instance
        Some(User {
            id,
            username,
            email,
        })
    }
}'''

test_cases.append({
    "name": "Rust - AI Generated",
    "language": "rust",
    "code": rust_ai,
    "expected": "AI",
    "description": "Complete rustdoc, examples, all parameters documented"
})

# ============================================================================
# TEST 8: Rust - Human Written
# ============================================================================
rust_human = '''#[derive(Debug, Clone)]
pub struct User {
    pub id: u32,
    pub username: String,
    pub email: String,
}

impl User {
    // quick constructor with basic checks
    pub fn new(id: u32, username: String, email: String) -> Option<User> {
        if username.len() < 3 || email.is_empty() {
            return None;
        }
        
        Some(User { id, username, email })
    }
}'''

test_cases.append({
    "name": "Rust - Human Written",
    "language": "rust",
    "code": rust_human,
    "expected": "Human",
    "description": "'quick' language, combined checks, minimal docs"
})

# ============================================================================
# TEST 9: Kotlin - AI Generated
# ============================================================================
kotlin_ai = '''/**
 * A comprehensive data class representing a user entity with complete documentation
 *
 * This data class encapsulates all necessary user information including identification,
 * authentication, and metadata fields. It provides automatic implementations of
 * equals, hashCode, toString, and copy methods.
 *
 * @property id The unique identifier for the user
 * @property username The username chosen by the user (must be unique in the system)
 * @property email The user's email address for communication and authentication
 * @property emailVerified Indicates whether the user has verified their email address
 * @constructor Creates a new User instance with the specified properties
 * @author AI Assistant
 * @version 1.0.0
 */
data class User(
    val id: Int,
    val username: String,
    val email: String,
    var emailVerified: Boolean = false
) {
    /**
     * Validates all user data to ensure it meets business requirements
     *
     * This method performs comprehensive validation on all user fields including
     * username length validation, email format verification, and other business rules.
     *
     * @return true if all validations pass, false otherwise
     */
    fun validate(): Boolean {
        // Validate that username meets minimum length requirement of 3 characters
        if (username.length < 3) {
            return false
        }
        
        // Validate that email is not empty or blank
        if (email.isBlank()) {
            return false
        }
        
        // Validate email format using regular expression pattern
        val emailPattern = "[a-zA-Z0-9._-]+@[a-z]+\\\\.+[a-z]+"
        if (!email.matches(emailPattern.toRegex())) {
            return false
        }
        
        // All validation checks passed successfully
        return true
    }
}'''

test_cases.append({
    "name": "Kotlin - AI Generated",
    "language": "kotlin",
    "code": kotlin_ai,
    "expected": "AI",
    "description": "KDoc everywhere, @property tags, verbose comments"
})

# ============================================================================
# TEST 10: Kotlin - Human Written
# ============================================================================
kotlin_human = '''data class User(
    val id: Int,
    val username: String,
    val email: String,
    var emailVerified: Boolean = false
) {
    // quick validation
    fun validate(): Boolean {
        if (username.length < 3 || email.isBlank()) {
            return false
        }
        
        val pattern = "[a-zA-Z0-9._-]+@[a-z]+\\\\.+[a-z]+"
        return email.matches(pattern.toRegex())
    }
}'''

test_cases.append({
    "name": "Kotlin - Human Written",
    "language": "kotlin",
    "code": kotlin_human,
    "expected": "Human",
    "description": "'quick' language, combined checks, minimal comments"
})

# Run all tests
print(f"\n✅ Plagiarism detector initialized!\n")

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
print("ADDITIONAL LANGUAGES TEST SUMMARY")
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
    print(f"   {status} | {r['language'].upper():10s} | {r['test']:35s} | {r['confidence']}% ({r['verdict']})")

print("\n" + "=" * 100)
if passed == total:
    print("🎉 PERFECT! Universal detection works across ALL these languages!")
elif passed >= total * 0.8:
    print("✅ EXCELLENT! System works well across these languages.")
else:
    print("⚠️  Some languages need tuning.")
print("=" * 100)
