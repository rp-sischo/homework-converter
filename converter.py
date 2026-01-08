#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
import sys
import os
import platform
import subprocess
from turtle import title

def formatting_key(number: str, k):
	# This is where you can add more formatting keys for different courses
	format = ""
	flags = 0
	if number == "494":
		format = str(r'Problem [0-9]*\.')
		flags = 10
	if k == 1:
		return format
	if k == 2:
		return flags

def main(argv=None):
	parser = argparse.ArgumentParser(description="Read a .tex file, edit it, and write a new .tex file.")
	parser.add_argument("input", help="Input .tex file")
	parser.add_argument("number", help="Homework assignment number")
	parser.add_argument("--course", help="math course number", default="494")

	args = parser.parse_args(argv)

	inp = Path(args.input)
	if not inp.exists():
		print(f"Input file {inp} not found", file=sys.stderr)
		return 2
        
	title = "HW" + args.number + "_Worksheet.tex"
	out_path = open(title, 'w')

	new_text = inp.read_text()

	# Insert blank lines after lines that contain specific literals or match regexes
	lines = new_text.splitlines()
	out_lines = []

	i = 0
	skip = False
	go_back = False
	page_break = "\\newpage"
	
	while i < len(lines):
			line = lines[i]
			out_lines.append(line)
			new_len_lines = len(out_lines)

			if re.search(r'following problem', line) is not None:
				go_back = True
			while go_back:
				m = 1
				if lines[i-m] == "":
					out_lines.insert(new_len_lines-m, page_break)
					go_back = False
					skip = True
				m += 1

			if re.match(formatting_key(args.course, 1), line, flags=formatting_key(args.course, 2)) is not None:
					if not skip:
						out_lines.insert(new_len_lines-1, page_break)
					else:
						skip = False

			i += 1



	new_text = "\n".join(out_lines) + ("\n" if new_text.endswith("\n") else "")

	if out_path:
		out_path.write(new_text)
	else:
		# print to stdout
		sys.stdout.write(new_text)

	os.system('latexmk -pdf /workspaces/' + title)

	return 0


if __name__ == "__main__":
	raise SystemExit(main())

