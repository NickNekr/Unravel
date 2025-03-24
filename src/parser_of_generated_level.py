from constants import *

from main import is_solvable_by_steps

def check_borders(level):
    x_size = len(level[0])
    y_size = len(level)

    for i in range(y_size):
        if len(level[i]) != x_size:
            return False
        if level[i][0] != '*':
            return False
        if level[i][x_size - 1] != '*':
            return False
        
    for i in range(x_size):
        if level[0][i] != '*':
            return False
        if level[y_size - 1][i] != '*':
            return False

    return True
        
index_of_level = 1
start, end = 0, -4
with open("genereted_levels.txt", 'r') as input:
    text = input.read()
    while start != - 1 and end != -1:
        start = text.find('```\n', end + 4)
        end = text.find('```\n', start + 4)
        rows = text[start+4:end].split('\n')
        level = [list(row) for row in rows]
        if level[0] == []:
            level = level[1:]
        if level[-1] == []:
            level = level[:-1]
        
        if not check_borders(level):
            continue
        x = is_solvable_by_steps(level)
        if x > 0:
            with open("generated_levels/new_level{}.txt".format(index_of_level), 'w') as output:
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