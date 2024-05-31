import pandas as pd
import re
import itertools

df = pd.read_csv('hsk_cleaned.csv')

df_hsk1 = df[df['Level'] == '1']
df_hsk2 = df[df['Level'] == '2']
df_hsk3 = df[df['Level'] == '3']
df_hsk4 = df[df['Level'] == '4']
df_hsk5 = df[df['Level'] == '5']
df_hsk6 = df[df['Level'] == '6']
df_hsk7_9 = df[df['Level'] == '7-9']

hsk1_hanzi_set = set(list(''.join([word for word in (df_hsk1['Simplified'] + df_hsk1['Traditional'])])))
hsk2_hanzi_set = set(list(''.join([word for word in (df_hsk2['Simplified'] + df_hsk2['Traditional'])])))
hsk3_hanzi_set = set(list(''.join([word for word in (df_hsk3['Simplified'] + df_hsk3['Traditional'])])))
hsk4_hanzi_set = set(list(''.join([word for word in (df_hsk4['Simplified'] + df_hsk4['Traditional'])])))
hsk5_hanzi_set = set(list(''.join([word for word in (df_hsk5['Simplified'] + df_hsk5['Traditional'])])))
hsk6_hanzi_set = set(list(''.join([word for word in (df_hsk6['Simplified'] + df_hsk6['Traditional'])])))
hsk7_9_hanzi_set = set(list(''.join([word for word in (df_hsk7_9['Simplified'] + df_hsk7_9['Traditional'])])))
hsk_hanzi_set = set(list(''.join([word for word in (df['Simplified'] + df['Traditional'])])))

hsk1_word_set = set(list(df_hsk1['Simplified']) + list(df_hsk1['Traditional']))
hsk2_word_set = set(list(df_hsk2['Simplified']) + list(df_hsk2['Traditional']))
hsk3_word_set = set(list(df_hsk3['Simplified']) + list(df_hsk3['Traditional']))
hsk4_word_set = set(list(df_hsk4['Simplified']) + list(df_hsk4['Traditional']))
hsk5_word_set = set(list(df_hsk5['Simplified']) + list(df_hsk5['Traditional']))
hsk6_word_set = set(list(df_hsk6['Simplified']) + list(df_hsk6['Traditional']))
hsk7_9_word_set = set(list(df_hsk7_9['Simplified']) + list(df_hsk7_9['Traditional']))
hsk_word_set = set(list(df['Simplified']) + list(df['Traditional']))

# for a given hanzi, return the lowest level that it appears in
def get_hanzi_level(hanzi):
    if hanzi in hsk1_hanzi_set:
        return '1'
    if hanzi in hsk2_hanzi_set:
        return '2'
    if hanzi in hsk3_hanzi_set:
        return '3'
    if hanzi in hsk4_hanzi_set:
        return '4'
    if hanzi in hsk5_hanzi_set:
        return '5'
    if hanzi in hsk6_hanzi_set:
        return '6'
    if hanzi in hsk7_9_hanzi_set:
        return '7-9'
    return 'Unknown'


def is_hanzi(char):
    # hanzi are between U+4E00 and U+9FFF
    return ord(char) <= 40959 and ord(char) >= 19968


def is_all_hanzi(string):
    return all([is_hanzi(char) for char in list(string)])

# this function was written by ChatGPT
def escape_regex(string):
    regex_reserved_chars = r'\^$.|?*+(){}[]'
    escaped_string = re.sub(f'([{re.escape(regex_reserved_chars)}])', r'\\\1', string)
    return escaped_string


# split text into chunks of Hanzi split by non-Hanzi characters
def split_into_hanzi_chunks(text):
    if is_all_hanzi(text):
        return [text]
    
    chunks = []
    
    if not isinstance(text, str):
        return []
    
    non_hanzi_characters = []
    
    for char in list(text):
        if not is_hanzi(char):
            non_hanzi_characters.append(escape_regex(char))
    
    regex_split_string = '|'.join(list(set(non_hanzi_characters)))
    split_string = re.split(regex_split_string, text)
    
    for string in split_string:
        if len(string) > 0:
            chunks.append(string)
            
    return chunks


# reverse of the function above
def split_into_non_hanzi_chunks(text):
    chunks = []
    
    if not isinstance(text, str):
        return []
    
    curr_chunk = ''
    
    for char in list(text):
        if not is_hanzi(char):
            curr_chunk += char
        if is_hanzi(char) and curr_chunk != '':
            chunks.append(curr_chunk)
            curr_chunk = ''
            
    return chunks

    
def get_hsk_word_level(word):
    if len(word) == 1:
        return get_hanzi_level(word)
    if word in hsk1_word_set:
        return '1'
    elif word in hsk2_word_set:
        return '2'
    elif word in hsk3_word_set:
        return '3'
    elif word in hsk4_word_set:
        return '4'
    elif word in hsk5_word_set:
        return '5'
    elif word in hsk6_word_set:
        return '6'
    elif word in hsk7_9_word_set:
        return '7-9'
    return 'Unknown'


def word_in_hsk(word):
    return word in hsk_word_set or word in hsk_hanzi_set

   
# for a string s, returns the length of the longest of s[:1], s[:2], s[:3], s[:4] that is an hsk word
# if none of those prefix substrings are in the hsk word set, then it returns the shortest substring (s[:1])

# in simpler terms, given a string, what is the prefix substring of the string that should be considered the next token
def get_next_token_length(string):
    next_possible_tokens = []
    
    for i in range(1, min([len(string), 5])):
        next_possible_tokens.append(string[:i])
        
    while len(next_possible_tokens) > 0:
        popped_token = next_possible_tokens.pop()
        if get_hsk_word_level(popped_token) != 'Unknown':
            return len(popped_token)
        
    return 1


def tokenize_hanzi_string(string):

    tokens = []

    while len(string) > 0:

        next_index = get_next_token_length(string)
        next_token = string[:next_index]
        tokens.append(next_token)
        string = string[next_index:]

    return tokens


def parse_text(text):
    tokens = []
    hanzi_chunks = split_into_hanzi_chunks(text)
    non_hanzi_chunks = split_into_non_hanzi_chunks(text)
    
    if len(hanzi_chunks) == 0:
        chunks = non_hanzi_chunks
    elif len(non_hanzi_chunks) == 0:
        chunks = hanzi_chunks
    # interweave the two chunks depending on which type of chunk (hanzi or non-hanzi)
    # appears in the text
    elif is_hanzi(text[0]):
        chunks = [chunk for chunk in itertools.chain(*itertools.zip_longest(hanzi_chunks, non_hanzi_chunks)) if chunk is not None]
    else:
        chunks = [chunk for chunk in itertools.chain(*itertools.zip_longest(non_hanzi_chunks, hanzi_chunks)) if chunk is not None]
    
    for chunk in chunks:
        # is this a hanzi chunk? If so, get tokens for it and append them to overall token list
        if is_hanzi(chunk[0]):
            chunk_tokens = tokenize_hanzi_string(chunk)
            tokens.extend(chunk_tokens)
        else:
            non_hanzi_token = [chunk, 'Not Hanzi']
            tokens.append(non_hanzi_token)
            
    return tokens