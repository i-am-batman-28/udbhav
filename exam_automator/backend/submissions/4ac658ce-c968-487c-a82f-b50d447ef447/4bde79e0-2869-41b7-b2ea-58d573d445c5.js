/**
 * Binary Search Algorithm
 * Searches for a target value within a sorted array.
 * Returns the index if found, otherwise returns -1.
 * 
 * @param {number[]} array - Sorted array (ascending order)
 * @param {number} target - Element to search for
 * @returns {number}
 */
function binarySearch(array, target) {
    let left = 0;
    let right = array.length - 1;

    while (left <= right) {
        const middle = Math.floor((left + right) / 2);
        const value = array[middle];

        if (value === target) return middle;
        if (value < target) left = middle + 1;
        else right = middle - 1;
    }

    return -1;
}

// Example usage
const arr = [1, 4, 7, 9, 13, 18];
console.log(binarySearch(arr, 9));   // Output: 3
console.log(binarySearch(arr, 10));  // Output: -1
