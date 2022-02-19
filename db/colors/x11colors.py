'''The x11colors module'''

X11_COLORS_FILEPATH = 'rgb.txt'
OUTPUT_FILENAME = 'library.py'

def parse(filepath=X11_COLORS_FILEPATH):
	colors = dict()
	with open(filepath) as infp:
		lines = infp.readlines()[1:]
		for i in range(1, len(lines)):
			line = lines[i].split()
			R, G, B = map(lambda x: int(x), line[:3])
			hex = '#' + ('%02x' % R) + ('%02x' % G) + ('%02x' % B)
			name = ' '.join(line[3:])
			colors[name] = (hex, (R, G, B))
	
	# max_namelen = max(len(name) for name in colors.keys())
	# print(max_namelen)  # 22
	
	# dump to a Python file!
	with open(OUTPUT_FILENAME, 'a') as outfp:
		outfp.write('\nX11COLORS = {\n')
		for name, (hex, (R, G, B)) in colors.items():
			name = "'" + name + "'"
			outfp.write(
				f"\t{name:<24}\t:\t('{hex}', ({R}, {G}, {B})),\n"
			)
		outfp.write('}\n')


##############################################################################
### main ###
############

def main():
	parse()

if __name__ == '__main__': main()
