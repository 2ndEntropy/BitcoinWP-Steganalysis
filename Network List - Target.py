from collections import Counter
import string
import random
import winsound
import itertools
from collections import deque
import math

def filter_line(line, letters_to_remove):
    return "".join(c for c in line if c.lower() not in letters_to_remove and c.isalpha())

def replace_letter(line, swap_from, swap_to):
    return line.replace(swap_from, swap_to).replace(swap_from.upper(), swap_to.upper())

def remove_punctuation(line):
    return line.translate(str.maketrans('', '', string.punctuation))

def most_frequent_character(counter, excluded_chars, text):
    filtered_counter = {char: count for char, count in counter.items() if char not in excluded_chars and char.isalpha()}
    
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

def generate_standard_name(lines, target_name):
    letters_to_remove_part1 = "aslonge"
    reintroduced_letters = ["s", "c"]
    swap_from = "f"
    swap_to = "r"
    reset_line_index = len(lines) - 3  # 3rd line from the bottom
    
    # Ensure no more than two letters in the target string are reintroduced
    reintroduced_count = 0
    for letter in target_name.lower():
        if letter in letters_to_remove_part1 and letter not in reintroduced_letters:
            if reintroduced_count < 2:
                reintroduced_letters.append(letter)
                reintroduced_count += 1
            else:
                break

    result_chars = process_lines(lines, letters_to_remove_part1, reintroduced_letters, reset_line_index, swap_from, swap_to)
    _, inline_characters = reorder_lines_and_characters(result_chars)

    return inline_characters, letters_to_remove_part1, reintroduced_letters, swap_from, swap_to

def generate_targeted_rules(target_name, text, letters_to_remove, reintroduced_letters, swap_from, swap_to):
    # Convert to list if necessary
    if isinstance(reintroduced_letters, tuple):
        reintroduced_letters = list(reintroduced_letters)
    # Ensure no more than two letters in the target string are reintroduced
    reintroduced_count = len(reintroduced_letters)
    for letter in target_name.lower():
        if letter in letters_to_remove and letter not in reintroduced_letters:
            if reintroduced_count < 2:
                reintroduced_letters.append(letter)
                reintroduced_count += 1
            else:
                break
    return letters_to_remove, reintroduced_letters, swap_from, swap_to

def simulated_annealing_acceptance(current_score, new_score, temperature):
    if new_score > current_score:
        return True
    else:
        return math.exp((new_score - current_score) / temperature) > random.random()

def generate_unique_names_until_target(lines, target_name, text, max_attempts=10000000, initial_temperature=1000, cooling_rate=0.003):
    reset_line_index = len(lines) - 3  # 3rd line from the bottom

    text_letters = set(filter(str.isalpha, text.lower()))
    target_letters = set(filter(str.isalpha, target_name.lower()))
    text_counter = Counter(filter(str.isalpha, text.lower()))
    target_counter = Counter(filter(str.isalpha, target_name.lower()))

    # Letters that appear more frequently in the input text than in the target name
    letters_to_remove_candidates = [char for char in text_counter if (text_counter[char] > target_counter.get(char, 0))]
    
    # Ensure 'e' is always in the list of letters to remove if it is a candidate
    if 'e' in letters_to_remove_candidates:
        letters_to_remove_candidates.insert(0, 'e')

    reintroduced_letters = list(target_letters)

    # Ensure no more than two letters in the target string are reintroduced
    reintroduced_count = len(reintroduced_letters)
    for letter in target_name.lower():
        if letter in letters_to_remove_candidates and letter not in reintroduced_letters:
            if reintroduced_count < 2:
                reintroduced_letters.append(letter)
                reintroduced_count += 1
            else:
                break

    # Prioritize removing letters not in the target string
    letters_to_remove_candidates = sorted(letters_to_remove_candidates, key=lambda x: x in target_letters)

    # Remove duplicates while maintaining order
    letters_to_remove_candidates = list(dict.fromkeys(letters_to_remove_candidates))

    # Letters that are part of the target name
    reintroduced_letters_candidates = list(target_letters)
    
    # Letters that are in the input text but not in the target name
    letters_not_in_target = [char for char in text_letters if char not in target_letters]

    best_match_percentage = 0
    best_match = None
    attempts = 0
    last_update_attempt = 0
    temperature = initial_temperature
    top_50_results = []

    print("Starting the process to generate unique names until the target is reached.")
    print(f"Letters to remove candidates: {letters_to_remove_candidates}")
    print(f"Reintroduced letters candidates: {reintroduced_letters_candidates}")
    print(f"Letters not in target: {letters_not_in_target}")

    # Track the history of changed letters
    change_history = deque(maxlen=5000)  # Max length set to a high number to track history

    def get_combinations(candidates):
        # Ensure 'e' is included in every combination if present
        return [combo for combo in itertools.combinations(candidates, 7) if 'e' in combo]

    def frequency_based_letter_selection(letters_to_remove_candidates, text_counter, target_counter):
        # Sort letters by their frequency difference (text frequency - target frequency)
        sorted_letters = sorted(letters_to_remove_candidates, key=lambda x: text_counter[x] - target_counter.get(x, 0), reverse=True)
        return sorted_letters

    while attempts < max_attempts:
        # Use frequency-based selection instead of random shuffling
        letters_to_remove_candidates = frequency_based_letter_selection(letters_to_remove_candidates, text_counter, target_counter)

        combinations_to_try = get_combinations(letters_to_remove_candidates)

        for letters_to_remove in combinations_to_try:
            for reintroduced_letters in itertools.combinations(reintroduced_letters_candidates, 2):
                for swap_from in letters_not_in_target:
                    for swap_to in target_letters - {swap_from}:

                        letters_to_remove_part1, reintroduced_letters, swap_from, swap_to = generate_targeted_rules(target_name, text, letters_to_remove, reintroduced_letters, swap_from, swap_to)
                        result_chars = process_lines(lines, letters_to_remove_part1, reintroduced_letters, reset_line_index, swap_from, swap_to)
                        _, inline_characters = reorder_lines_and_characters(result_chars)
                        
                        distance = sum(1 for a, b in zip(inline_characters, target_name) if a != b) + abs(len(inline_characters) - len(target_name))
                        match_percentage = ((len(target_name) - distance) / len(target_name)) * 100

                        if simulated_annealing_acceptance(best_match_percentage, match_percentage, temperature):
                            best_match_percentage = match_percentage
                            best_match = (inline_characters, letters_to_remove_part1, reintroduced_letters, swap_from, swap_to, match_percentage)
                            print(f"New best match found: {inline_characters}, Match: {match_percentage:.2f}%")
                            print(f"Rules: Letters removed: {letters_to_remove_part1}, Reintroduced letters: {', '.join(reintroduced_letters)}, Swapped: {swap_from} -> {swap_to}")

                            if match_percentage == 100:
                                winsound.MessageBeep(winsound.MB_OK)
                                print(f"\n100% match found after {attempts} attempts:")
                                print(f"Name: {inline_characters}, Letters removed: {letters_to_remove_part1}, Reintroduced letters: {', '.join(reintroduced_letters)}, Swapped: {swap_from} -> {swap_to}")
                                return [best_match]

                        top_50_results.append((inline_characters, match_percentage))
                        top_50_results = sorted(top_50_results, key=lambda x: x[1], reverse=True)[:50]

                        attempts += 1
                        temperature *= 1 - cooling_rate
                        if attempts >= max_attempts:
                            winsound.MessageBeep(winsound.MB_ICONHAND)
                            return [best_match]

                        if attempts - last_update_attempt >= 10000:
                            print(f"Current attempt number: {attempts}")
                            last_update_attempt = attempts

        if attempts % 5000 == 0:
            print(f"\nTop 50 results of the last 5000 attempts:")
            for rank, result in enumerate(top_50_results, 1):
                print(f"{rank}. Name: {result[0]}, Match: {result[1]:.2f}%")

    winsound.MessageBeep(winsound.MB_ICONHAND)
    return [best_match]

def print_summary(standard_name, found_names):
    print("\nStandard name:")
    name, letters_removed, reintroduced, swap_from, swap_to = standard_name
    print(f"Name: {name}\nLetters removed: {letters_removed}\nReintroduced letters: {', '.join(reintroduced)}\nSwapped: {swap_from} -> {swap_to}")

    if found_names and found_names[0] is not None:
        print("\nTop match found:")
        for i, found_name in enumerate(found_names, 1):
            name, letters_removed, reintroduced, swap_from, swap_to, match_percentage = found_name
            print(f"{i}. Name: {name}\n   Letters removed: {letters_removed}\n   Reintroduced letters: {', '.join(reintroduced)}\n   Swapped: {swap_from} -> {swap_to}\n   Match: {match_percentage:.2f}%")
    else:
        print("\nNo matches found.")

if __name__ == "__main__":
    import sys

    # Inform the user about the program and how to terminate it early
    print("\nThis program attempts to generate a target 9-character string by iterating through different rules and combinations.")
    print("The program will run up to 10,000,000 attempts unless it finds a 100% match.")
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
    standard_name = generate_standard_name(lines, target_name)
    print("Standard name generated:")
    print_summary(standard_name, [])

    found_names = generate_unique_names_until_target(lines, target_name, text)
    print_summary(standard_name, found_names)
