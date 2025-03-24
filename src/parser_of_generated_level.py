from constants import *

from main import is_solvable_by_steps

abs_index = 0
index_of_level = 1
start, end = 0, -4
with open("genereted_levels.txt", 'r') as input:
    text = input.read()
    while start != - 1 and end != -1:
        abs_index += 1
        start = text.find('```\n', end + 4)
        end = text.find('```\n', start + 4)
        rows = text[start+4:end].split('\n')
        level = [list(row) for row in rows]
        x = is_solvable_by_steps(level)
        if x > 0:
            with open("generated_levels/g_level{}.txt".format(index_of_level), 'w') as output:
                full_level = "STEPS: " + str(x + 1) + '\n'
                if x + 1 >= 20:
                    full_level += "Difficulty: " + 'Hard' + '\n'
                elif x + 1 >= 13:
                    full_level += "Difficulty: " + 'Medium' + '\n'
                else:
                    full_level += "Difficulty: " + 'Easy' + '\n'
                full_level += text[start+4:end]
                output.write(full_level)
                index_of_level += 1