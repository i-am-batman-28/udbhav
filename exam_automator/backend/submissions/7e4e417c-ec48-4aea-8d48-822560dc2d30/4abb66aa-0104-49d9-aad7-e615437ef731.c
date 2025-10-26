/**
 * Performs binary search on a sorted array to find the target element.
 * Returns the index of the target if found, otherwise returns -1.
 *
 * @param {number[]} sortedArray - Array must be sorted in ascending order
 * @param {number} target - Value to search for
 * @returns {number} Index of target or -1 if not found
 */
function binarySearch(sortedArray, target) {
    let left = 0;
    let right = sortedArray.length - 1;

    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        const midValue = sortedArray[mid];

        if (midValue === target) {
            return mid;
        } else if (midValue < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }

    return -1; // target not found
}

// Example usage:
const data = [1, 3, 5, 7, 9, 11, 13];
const targetValue = 7;
const index = binarySearch(data, targetValue);
console.log(`Target ${targetValue} found at index: ${index}`);
