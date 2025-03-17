from collections import Counter
import string

def filter_line(line, reintroduce=False):
    letters_to_remove = "alonge" if reintroduce else "aslonge"
    return "".join(c for c in line if c.lower() not in letters_to_remove)

def replace_f_with_r(line):
    return line.replace('f', 'r').replace('F', 'R')

def remove_punctuation(line):
    return line.translate(str.maketrans('', '', string.punctuation))

def most_frequent_character(counter, excluded_chars, text):
    # Remove excluded characters from counter
    filtered_counter = {char: count for char, count in counter.items() if char not in excluded_chars and char != ' '}
    
    if not filtered_counter:
        return None, []

    # Find the maximum frequency
    max_count = max(filtered_counter.values())

    # Find all characters with the maximum frequency
    candidates = [char for char in filtered_counter if filtered_counter[char] == max_count]

    # Find the character closest to the end of the text
    closest_char = None
    for char in reversed(text):
        if char in candidates:
            closest_char = char
            break

    return closest_char, candidates

def process_lines(lines):
    result = []
    excluded_chars_part1 = set()
    excluded_chars_part2 = set()
    text = "".join(lines).replace(" ", "").lower()
    cumulative_counter = Counter()
    c_selected_part1 = False  # To track if 'c' has been selected in the first part
    c_selected_part2 = False  # To track if 'c' has been selected in the second part

    num_lines = len(lines)
    reset_line_index = num_lines - 3  # 3rd line from the bottom

    for i, line in enumerate(reversed(lines)):
        line = remove_punctuation(line)
        line = replace_f_with_r(line)
        reintroduce = i >= reset_line_index  # Reintroduce only on the 3rd line from the bottom and after

        if reintroduce and i == reset_line_index:
            cumulative_counter = Counter()  # Reset the cumulative counter
            excluded_chars_part2 = excluded_chars_part1.copy()  # Copy the excluded characters from the first part
            if c_selected_part1:
                excluded_chars_part2.discard('c')  # Allow 'c' to be selected again if it was chosen in the first part

        filtered_line = filter_line(line, reintroduce)
        excluded_chars = excluded_chars_part2 if reintroduce else excluded_chars_part1
        line_counter = Counter(c for c in filtered_line if c not in excluded_chars)

        # Update the cumulative counter
        cumulative_counter.update(line_counter)

        frequent_char, candidates = most_frequent_character(cumulative_counter, excluded_chars, text)
        if frequent_char:
            if reintroduce:
                if frequent_char.lower() == 'c' and not c_selected_part2:
                    c_selected_part2 = True  # Mark 'c' as selected in the second part
                    excluded_chars_part2.add(frequent_char)
                elif frequent_char.lower() != 'c':
                    excluded_chars_part2.add(frequent_char)
            else:
                if frequent_char.lower() == 'c' and not c_selected_part1:
                    c_selected_part1 = True  # Mark 'c' as selected in the first part
                    excluded_chars_part1.add(frequent_char)
                elif frequent_char.lower() != 'c':
                    excluded_chars_part1.add(frequent_char)
        result.append((frequent_char, candidates))

    result.reverse()
    return result

def reorder_lines_and_characters(result_chars):
    reordered_result = [
        result_chars[3],  # Line 4
        result_chars[2],  # Line 3
        result_chars[1],  # Line 2
        result_chars[0],  # Line 1
    ] + result_chars[4:7] + [
        result_chars[8],  # Line 9 (swapped with line 8)
        result_chars[7],  # Line 8 (swapped with line 9)
    ] + result_chars[9:]

    inline_characters = "".join([char for char, _ in reordered_result if char])
    return reordered_result, inline_characters

if __name__ == "__main__":
    text = """The steps to run the network are as follows
1) New transactions are broadcasted to all nodes
2) Each node collects new transactions into a block
3) Each node works on finding a difficult proof-of-work for its block
4) When a node finds a proof-of-work
it broadcasts the block to all nodes
5) Nodes accept the block only if all transactions in it are valid and not already spent
6) Nodes express their acceptance of the block by working on creating the next block in the chain
using the hash of the accepted block as the previous hash"""

    lines = text.split("\n")
    result_chars = process_lines(lines)
    reordered_result, inline_characters = reorder_lines_and_characters(result_chars)
    
    print("Most frequent characters in each line (reordered):")
    for i, (char, candidates) in enumerate(reordered_result):
        if char:
            if len(candidates) > 1:
                print(f"Line {i+1}: Candidates: {', '.join(candidates)}. Chosen: {char}")
            else:
                print(f"Line {i+1}: {char}")
        else:
            print(f"Line {i+1}: None")
    
    print("\nInline characters in order:")
    print(inline_characters)