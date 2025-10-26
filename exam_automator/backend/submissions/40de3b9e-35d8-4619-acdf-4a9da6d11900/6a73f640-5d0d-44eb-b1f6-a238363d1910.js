/**
 * Binary Search Algorithm Implementation
 * 
 * This function performs a binary search on a sorted array to find the index
 * of a target value. If the target is not found, it returns -1.
 * 
 * @param {Array<number>} sortedArray - The sorted array to search through
 * @param {number} targetValue - The value to search for
 * @returns {number} The index of the target value, or -1 if not found
 */
function performBinarySearch(sortedArray, targetValue) {
    // Initialize the left and right pointers
    let leftPointer = 0;
    let rightPointer = sortedArray.length - 1;
    
    // Continue searching while the left pointer is less than or equal to the right pointer
    while (leftPointer <= rightPointer) {
        // Calculate the middle index
        const middleIndex = Math.floor((leftPointer + rightPointer) / 2);
        
        // Check if the middle element is the target
        if (sortedArray[middleIndex] === targetValue) {
            return middleIndex;
        }
        
        // If the target is greater than the middle element, search the right half
        if (sortedArray[middleIndex] < targetValue) {
            leftPointer = middleIndex + 1;
        } else {
            // If the target is less than the middle element, search the left half
            rightPointer = middleIndex - 1;
        }
    }
    
    // Return -1 if the target was not found
    return -1;
}

// Example usage demonstrating the binary search functionality
const numericalData = [2, 5, 8, 12, 16, 23, 38, 42, 55, 68];
const searchResult1 = performBinarySearch(numericalData, 12);
const searchResult2 = performBinarySearch(numericalData, 7);

console.log(`Searching for 12: Index ${searchResult1}`); // Expected output: Index 3
console.log(`Searching for 7: Index ${searchResult2}`);  // Expected output: Index -1
