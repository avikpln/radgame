'''The quotes module'''

import csv

# TODO: quotes_akhiltak.csv (QUOTE;AUTHOR;GENRE)
QUOTES_FILEPATH = 'quotes_JakubPetriska.csv'  # "AUTHOR","QUOTE"
OUTPUT_FILENAME = '../../library.py'

def parse(filepath=QUOTES_FILEPATH):
	quotes = list()
	with open(QUOTES_FILEPATH, 'r') as incsvfile:
		reader = csv.reader(incsvfile, delimiter=',')
		next(reader)  # skip header
		quotes = [row for row in reader if len(row) > 0]
	
	# max_authorlen = max(len(author) for (author, _) in quotes)
	# print(max_authorlen)  # 28
	
	# dump to a Python file!
	with open(OUTPUT_FILENAME, 'a') as outfp:
		outfp.write('\nQUOTES = [\n')
		for author, text  in quotes:
			if len(author) == 0:
				author = 'Unknown'
			author = '"' + author + '"'
			text = '"' + text + '"'
			outfp.write(
				f"\t[{author:<30}\t,\t{text}],\n"
			)
		outfp.write(']\n')


##############################################################################
### main ###
############

def main():
	parse()

if __name__ == '__main__': main()
