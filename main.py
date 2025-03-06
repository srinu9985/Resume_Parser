def isValidParenthesis(s):
    stack = []
    bracket_map = {')': '(', '}': '{', ']': '['}  # Closing to opening map
    
    for char in s:
        if char in "({[":  # Opening bracket
            stack.append(char)
        elif char in ")}]":  # Closing bracket
            if not stack or stack.pop() != bracket_map[char]:
                print(stack.pop() != bracket_map[char])
                return False
    
    return len(stack) == 0  # Stack should be empty if valid

# Test Cases
# print(isValidParenthesis("()"))        # ✅ True
# print(isValidParenthesis("({[]})"))    # ✅ True
# print(isValidParenthesis("([{]})"))    # ❌ False
# print(isValidParenthesis("{[()]}"))    # ✅ True
print(isValidParenthesis("{[(])}"))    # ❌ False
