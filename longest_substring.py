'''Given a string s having lowercase characters, find the length of the longest substring without repeating characters. 

Examples:

Input: s = "geeksforgeeks"
Output: 7 
Explanation: The longest substrings without repeating characters are "eksforg” and "ksforge", with lengths of 7.

Input: s = "aaa"
Output: 1
Explanation: The longest substring without repeating characters is "a"

Input: s = "abcdefabcbb"
Output: 6
Explanation: The longest substring without repeating characters is "abcdef".'''

def longest_substring_with_hash(s):
    seen = set()
    left = 0
    max_len = 0
    for right in range(len(s)):
        print("seen before", "--->", seen)
        while s[right] in seen:
            seen.remove(s[left])
            left += 1
        print("seen after", "--->", seen)
        seen.add(s[right])
        max_len = max(max_len, right - left + 1)
        
    return max_len
    
def longest_substring(s):
    left = 0
    max_len = 0
    seen = [-1] * 26
    for right in range(len(s)):
        print("seen before", "--->", seen)
        while s[right] in seen:
            seen.remove(s[left])
            left += 1
        print("seen after", "--->", seen)
        seen.add(s[right])
        max_len = max(max_len, right - left + 1)
        
    return max_len
    
s = "abcdefabcbb"
print(longest_substring(s))