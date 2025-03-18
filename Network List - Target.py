from collections import Counter
import string
import random

def filter_line(line, letters_to_remove):
    return "".join(c for c in line if c.lower() not in letters_to_remove)

def replace_letter(line, swap_from, swap_to):
    return line.replace(swap_from, swap_to).replace(swap_from.upper(), swap_to.upper())

def remove_punctuation(line):
    return line.translate(str.maketrans('', '', string.punctuation))

def most_frequent_character(counter, excluded_chars, text):
    filtered_counter = {char: count for char, count in counter.items() if char not in excluded_chars and char != ' '}
    
    if not filtered_counter:
        return None, []

    max_count = max(filtered_counter.values())
    candidates = [char for char in filtered_counter if filtered_counter[char] == max_count]
    closest_char = None
    for char in reversed(text):
        if char in candidates:
            closest_char = char
            break

    return closest_char, candidates

def process_lines(lines, letters_to_remove_part1, reintroduced_letters, reset_line_index, swap_from, swap_to):
    result = []
    excluded_chars_part1 = set(letters_to_remove_part1)
    excluded_chars_part2 = set()
    text = "".join(lines).replace(" ", "").lower()
    cumulative_counter = Counter()
    reintroduced_selected = {letter: False for letter in reintroduced_letters}
    num_lines = len(lines)

    for i, line in enumerate(reversed(lines)):
        line = remove_punctuation(line)
        line = replace_letter(line, swap_from, swap_to)
        reintroduce = i >= reset_line_index

        if reintroduce and i == reset_line_index:
            cumulative_counter = Counter()
            excluded_chars_part2 = excluded_chars_part1.copy()
            for letter in reintroduced_letters:
                excluded_chars_part2.discard(letter)

        filtered_line = filter_line(line, letters_to_remove_part1 if not reintroduce else "")
        excluded_chars = excluded_chars_part2 if reintroduce else excluded_chars_part1
        line_counter = Counter(c for c in filtered_line if c not in excluded_chars)
        cumulative_counter.update(line_counter)

        frequent_char, candidates = most_frequent_character(cumulative_counter, excluded_chars, text)
        if frequent_char:
            if reintroduce:
                if frequent_char.lower() in reintroduced_letters and not reintroduced_selected[frequent_char.lower()]:
                    reintroduced_selected[frequent_char.lower()] = True
                excluded_chars_part2.add(frequent_char)
            else:
                if frequent_char.lower() in reintroduced_letters and not reintroduced_selected[frequent_char.lower()]:
                    reintroduced_selected[frequent_char.lower()] = True
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

def generate_standard_name(lines):
    letters_to_remove_part1 = "aslonge"
    reintroduced_letters = ["s", "c"]
    swap_from = "f"
    swap_to = "r"
    reset_line_index = len(lines) - 3  # 3rd line from the bottom

    result_chars = process_lines(lines, letters_to_remove_part1, reintroduced_letters, reset_line_index, swap_from, swap_to)
    _, inline_characters = reorder_lines_and_characters(result_chars)

    return inline_characters, letters_to_remove_part1, reintroduced_letters, swap_from, swap_to

def generate_targeted_rules(target_name, text):
    all_letters = set(string.ascii_lowercase)
    text_letters = set(text.lower())
    target_letters = set(target_name.lower())
    letters_to_remove = list((all_letters - target_letters) & text_letters)
    reintroduced_letters = random.sample(list(target_letters & text_letters), 2)
    swap_from = random.choice(list((all_letters - target_letters) & text_letters))
    swap_to = random.choice(list((target_letters & text_letters) - set(reintroduced_letters)))
    return letters_to_remove, reintroduced_letters, swap_from, swap_to

def generate_unique_names_until_target(lines, target_name, text, max_attempts=1000000):
    used_rules = set()
    reset_line_index = len(lines) - 3  # 3rd line from the bottom
    closest_matches = []
    top_10_intermediate = []

    attempts = 0
    while attempts < max_attempts:
        letters_to_remove, reintroduced_letters, swap_from, swap_to = generate_targeted_rules(target_name, text)
        letters_to_remove_part1 = ''.join(random.sample(letters_to_remove, 7))
        rule_key = (letters_to_remove_part1, tuple(reintroduced_letters), swap_from, swap_to)

        if rule_key in used_rules:
            continue

        used_rules.add(rule_key)
        result_chars = process_lines(lines, letters_to_remove_part1, reintroduced_letters, reset_line_index, swap_from, swap_to)
        _, inline_characters = reorder_lines_and_characters(result_chars)
        
        distance = sum(1 for a, b in zip(inline_characters, target_name) if a != b) + abs(len(inline_characters) - len(target_name))
        match_percentage = ((len(target_name) - distance) / len(target_name)) * 100

        if match_percentage == 100:
            print(f"\n100% match found after {attempts} attempts:")
            print(f"Name: {inline_characters}, Letters removed: {letters_to_remove_part1}, Reintroduced letters: {', '.join(reintroduced_letters)}, Swapped: {swap_from} -> {swap_to}")
            return [(inline_characters, letters_to_remove_part1, reintroduced_letters, swap_from, swap_to, match_percentage)]

        if attempts % 10000 == 0 and attempts > 0:
            top_10_intermediate = sorted(closest_matches, key=lambda x: x[5], reverse=True)[:10]
            print(f"\nTarget: {target_name}")
            print(f"Top 10 matches after {attempts} attempts:")
            for i, found_name in enumerate(top_10_intermediate, 1):
                name, letters_removed, reintroduced, swap_from, swap_to, match_percentage = found_name
                print(f"{i}. Name: {name}, Letters removed: {letters_removed}, Reintroduced letters: {', '.join(reintroduced)}, Swapped: {swap_from} -> {swap_to}, Match: {match_percentage:.2f}%")
            
            closest_matches = []

        closest_matches.append((inline_characters, letters_to_remove_part1, reintroduced_letters, swap_from, swap_to, match_percentage))
        closest_matches = sorted(closest_matches, key=lambda x: x[5], reverse=True)[:100]

        attempts += 1

    return closest_matches, top_10_intermediate

def print_summary(standard_name, found_names, top_10_intermediate):
    print("\nStandard name:")
    name, letters_removed, reintroduced, swap_from, swap_to = standard_name
    print(f"Name: {name}\nLetters removed: {letters_removed}\nReintroduced letters: {', '.join(reintroduced)}\nSwapped: {swap_from} -> {swap_to}")

    if found_names:
        print("\nTop 10 matches:")
        for i, found_name in enumerate(found_names[:10], 1):
            name, letters_removed, reintroduced, swap_from, swap_to, match_percentage = found_name
            print(f"{i}. Name: {name}\n   Letters removed: {letters_removed}\n   Reintroduced letters: {', '.join(reintroduced)}\n   Swapped: {swap_from} -> {swap_to}\n   Match: {match_percentage:.2f}%")
    else:
        print("\nNo matches found.")

if __name__ == "__main__":
    import sys

    # Inform the user about the program and how to terminate it early
    print("\nThis program attempts to generate a target 9-character string by iterating through different rules and combinations.")
    print("The program will run up to 1,000,000 attempts unless it finds a 100% match.")
    print("You can terminate the program early by pressing 'Ctrl+C'.")

    if len(sys.argv) < 2:
        target_name = input("Enter a 9-character target string: ").strip()
    else:
        target_name = sys.argv[1]

    if len(target_name) != 9:
        print("Error: The target string must be exactly 9 characters long.")
        sys.exit(1)
    
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
    standard_name = generate_standard_name(lines)
    print("Standard name generated:", standard_name[0])
    found_names, top_10_intermediate = generate_unique_names_until_target(lines, target_name, text)
    print_summary(standard_name, found_names, top_10_intermediate)
