#import discord
#from feature.music import YTDLSource as player

# filename = player.from_url("https://www.youtube.com/watch?v=4JkIs37a2JE", loop=None, stream=True)
# discord.FFmpegPCMAudio(executable="dll/ffmpeg.exe", source=filename)
import random

def add_spelling_mistakes(text, mistake_percentage):
    # Define the layout of the QWERTY keyboard
    keyboard = [['q','w','e','r','t','y','u','i','o','p','[',']','\\'],
                ['a','s','d','f','g','h','j','k','l',';','\''],
                ['z','x','c','v','b','n','m',',','.','/']]
    
    # Calculate the number of mistakes to add
    num_mistakes = int(len(text) * (mistake_percentage / 100))
    
    # Create a list of indices to randomly choose from
    indices = list(range(len(text)))
    
    # Randomly select indices to add mistakes to
    for i in random.sample(indices, num_mistakes):
        # Get the current character and its position on the keyboard
        current_char = text[i]
        current_row = 0
        current_col = 0
        for row_idx, row in enumerate(keyboard):
            if current_char in row:
                current_row = row_idx
                current_col = row.index(current_char)
                break
                
        # Determine the adjacent keys on the keyboard
        adjacent_keys = []
        if current_col > 0:
            adjacent_keys.append(keyboard[current_row][current_col-1])
        if current_col < len(keyboard[current_row])-1:
            adjacent_keys.append(keyboard[current_row][current_col+1])
        if current_row > 0:
            adjacent_keys.append(keyboard[current_row-1][current_col])
        if current_row < len(keyboard)-1:
            adjacent_keys.append(keyboard[current_row+1][current_col])
        
        # Determine the probability of each type of mistake
        random_num = random.random()
        if random_num < 0.7:
            # Replace the character with a random adjacent key
            replacement_char = random.choice(adjacent_keys)
            text = text[:i] + replacement_char + text[i+1:]
        elif random_num < 0.9 and len(adjacent_keys) > 1:
            # Swap the character with another adjacent key
            swap_char = random.choice(adjacent_keys)
            swap_index = i + (1 if swap_char == text[i+1:i+2] else -1)
            text = text[:i] + swap_char + text[swap_index] + text[i+1:]
        else:
            # Replace the character with a random key
            replacement_char = random.choice([c for row in keyboard for c in row])
            text = text[:i] + replacement_char + text[i+1:]
    
    return text

print(add_spelling_mistakes("OMG, are you okay? 😱", 5))