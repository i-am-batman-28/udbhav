"""
Data Processor - Student Submission

Quick utility for processing student grades
"""

import json

def load_data(file):
    with open(file) as f:
        return json.load(f)

def calc_avg(nums):
    return sum(nums) / len(nums) if nums else 0

def process_grades(data):
    results = {}
    for student, grades in data.items():
        avg = calc_avg(grades)
        results[student] = {
            'average': round(avg, 2),
            'total': sum(grades),
            'count': len(grades),
            'passing': avg >= 60
        }
    return results

def save_results(results, outfile):
    with open(outfile, 'w') as f:
        json.dump(results, f, indent=2)

# Quick test
if __name__ == '__main__':
    test_data = {
        'Alice': [85, 90, 78],
        'Bob': [65, 70, 75],
        'Charlie': [55, 58, 52]
    }
    res = process_grades(test_data)
    print(res)
