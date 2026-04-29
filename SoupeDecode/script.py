import os
import sys

os.system("clear")

with open("teste.txt","rt") as file:
	for name in file:
		nomes = name
#		print(nomes.replace("SMB                      10.67.182.56    445    DC01             2071: SOUPEDECODE",""))
		N1 = nomes.replace("SMB","")
		N2 = N1.replace("                      ","")
		N3 = N2.strip(" ")
		N4 = N3[46:].replace("SOUPEDECODE\\","").replace("$ (SidTypeUser)","").replace("(SidTypeUser)","").replace("\n","")
		print(N4)
		with open("/home/nanoxsec/CTF/SoupeDecode/usernames.txt","at") as f:
			f.write(N4+"\n")
file.close()
f.close()
