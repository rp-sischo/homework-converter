#!/usr/bin/env python3
import argparse
import re
from pathlib import Path
import sys
import os
import platform
import subprocess
from turtle import title

# Source - https://stackoverflow.com/a
# Posted by Maxim, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-08, License - CC BY-SA 4.0

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1', 'True'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0', 'False'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


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
	parser.add_argument("course", type=str, help="math course number", default="494")
	parser.add_argument("compile", type=str2bool, nargs='?',
                        const=True, default=False,
                        help="Convert to pdf?")

	args = parser.parse_args(argv)

	inp = Path(args.input)
	if not inp.exists():
		print(f"Input file {inp} not found", file=sys.stderr)
		return 2
        
	title = f"HW{args.number}_Worksheet.tex"
	out_path = Path(title)

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
					if not skip and not out_lines[new_len_lines-1] == page_break:
						out_lines.insert(new_len_lines-1, page_break)
					else:
						skip = False

			i += 1



	new_text = "\n".join(out_lines) + ("\n" if new_text.endswith("\n") else "")

	# Write the output .tex file
	try:
		out_path.write_text(new_text)
	except Exception as e:
		print(f"Error writing output file {out_path}: {e}", file=sys.stderr)
		return 3

	if not args.compile:
		return 0

	# Helper to run a command and capture output. Returns (rc, output) where rc is None if command not found
	def _run(cmd):
		try:
			res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
			return res.returncode, res.stdout
		except FileNotFoundError:
			return None, f"Command not found: {cmd[0]}"

	# Try common TeX engines in order: latexmk, tectonic, pdflatex
	commands = [
		["latexmk", "-pdf", "-silent", str(out_path)],
		["tectonic", str(out_path)],
		["pdflatex", "-interaction=nonstopmode", "-halt-on-error", str(out_path)],
	]

	compiled = False
	for cmd in commands:
		rc, out = _run(cmd)
		if rc is None:
			# command not installed
			continue
		if rc == 0:
			print(f"Successfully built PDF with {cmd[0]}")
			compiled = True
			break
		else:
			print(f"{cmd[0]} failed (exit {rc}). Output:\n{out}", file=sys.stderr)

	if not compiled:
		print("PDF compilation failed. Make sure a TeX engine (latexmk, tectonic, or pdflatex) is installed and on PATH. OR re-name file", file=sys.stderr)
		return 4
	
	# Cleanup auxiliary files generated during compilation
	aux_extensions = [".aux", ".log", ".fls", ".fdb_latexmk", ".toc", ".out"]
	for ext in aux_extensions:
		aux_path = out_path.with_suffix(ext)
		if aux_path.exists():
			try:
				aux_path.unlink()
			except Exception as e:
				print(f"Could not delete auxiliary file {aux_path}: {e}", file=sys.stderr)

	# Open the resulting PDF (best-effort, platform-dependent)
	pdf_path = out_path.with_suffix(".pdf")
	if pdf_path.exists():
		try:
			if platform.system() == "Windows":
				os.startfile(pdf_path)
			elif platform.system() == "Darwin":
				subprocess.run(["open", str(pdf_path)])
			else:
				subprocess.run(["xdg-open", str(pdf_path)])
		except Exception as e:
			print(f"Could not open PDF automatically: {e}", file=sys.stderr)
	else:
		print(f"PDF not found at {pdf_path}", file=sys.stderr)

	return 0



if __name__ == "__main__":
	raise SystemExit(main())

