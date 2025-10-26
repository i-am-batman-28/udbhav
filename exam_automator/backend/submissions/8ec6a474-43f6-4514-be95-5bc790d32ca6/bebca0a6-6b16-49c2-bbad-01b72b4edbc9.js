// quick binary search I wrote
function binSearch(arr, x) {
  let l = 0, r = arr.length - 1;
  while (l <= r) {
    let m = Math.floor((l + r) / 2);
    if (arr[m] === x) return m;
    if (arr[m] < x) l = m + 1;
    else r = m - 1;
  }
  return -1; // not found
}

// quick check
const nums = [2, 5, 8, 12, 16, 23, 38];
console.log(binSearch(nums, 12)); // expect 3
console.log(binSearch(nums, 7));  // expect -1
