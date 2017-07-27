#!/usr/bin/python3

def main():
	header = ['\\begin{table}[!htb]\n', '\t\\centering\n', '\t\\begin{tabular}{|c|c|c|c|c|c|c|}\n']
	separator = '\n' #'\t\t\\hline\n'
	line = '\t\t{}& {}& {}& {}& {}& {}& {} \\tabularnewline\n'
	tail = [separator, '\t\\end{tabular}\n', '\t\\caption{Materias Aprobadas} \\label{tab:matApr}\n', '\\end{table}\n']
	# I must read the file and split it and save it in a line and then go for a ride wiiiii
	with open('materiasAprobadas') as f:
		data = f.read().split('\n')
	
	with open('table', 'w') as f:
		f.writelines(header)
		[f.writelines([separator, line.format(*lne.split('\t'))]) for lne in data]
		f.writelines(tail)

if __name__ == '__main__':
	main()