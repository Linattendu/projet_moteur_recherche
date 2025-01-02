# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
mot_cle = 'diseases'
regex = pattern = r'(\b\w+\b\s*){0,' + str(5) + r'}' + re.escape(mot_cle) + r'(\s*\b\w+\b){0,' + str(5) + r'}'

test_str = "fist thing to do is you is mostly about infectious diseases but you can do it for a lon time my dear you make smoething"

matches = re.finditer(regex, test_str, re.MULTILINE)

for matchNum, match in enumerate(matches, start=1):
    
    print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
    
    match = match.group()
    print("match = match.group() ",match)
    
    

# Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.
