#!/usr/bin/python3

import os
import sys

os.system("clear")

encoded = sys.argv[1]
all_alpha = "" # String of all lowercase english alphabets

for i in range(ord('a'),ord('z')+1):
	all_alpha += chr(i)

print("Encoded => " + encoded)
print("All alphabets => " + all_alpha)
print("Decoded => ",end="")

# This loop iterates over all PAIRS of the alphabets, ignoring the '::'
for i in range(0,len(encoded),2):
	first_char = encoded[i] # Since the first char in all pairs is lowercase
	second_char = encoded[i+1].lower() # Since the second char in all pairs is uppercase
	
	if first_char == ':':
		print(":",end="")
		continue
	
	first_alpha_position = ord(first_char) - ord('a') + 1 
	second_alpha_position = ord(second_char) - ord('a') + 1 
	
	decoded_alpha_position = (first_alpha_position + second_alpha_position) % 26 # The modulo operation takes care of the "imagine the list of alphabets arranged in a circular loop" part I was talking about
	
	decoded_alpha = all_alpha[decoded_alpha_position - 1] # Array indexes start at 0, yes?
	print(decoded_alpha,end="")
print("")
