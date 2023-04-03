def is_lat_letters_all(word):
    if not word or word.__class__.__name__ != 'str':
        return False
    alf = 'abcdefghijklmnopqrstuvwxyz '
    word = word.lower()
    for letter in word:
        if letter not in alf:
            return False
    return True