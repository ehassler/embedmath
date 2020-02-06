from sys import argv as _argv
from sys import stderr as _stderr
import os.path as _path
from .filters import EncodingFilter as _EncodingFilter
from .filters import DecodingFilter as _DecodingFilter
from pandocfilters import toJSONFilter as _toJSONFilter
from subprocess import run as _run
import multiprocessing as _mp
from tempfile import TemporaryDirectory as _TD


def _has_pandoc():
	try:
		out = _run(['pandoc', '--version'], timeout=1, capture_output=True, text=True)
		return out.stdout.split('\n')[0]
	except FileNotFoundError:
		return False


def _has_latex():
	try:
		out = _run(['latex', '--version'], timeout=1, capture_output=True, text=True)
		return out.stdout.split('\n')[0]
	except FileNotFoundError:
		return False


def _has_dvisvgm():
	try:
		out = _run(['dvisvgm', '--version'], timeout=1, capture_output=True, text=True)
		return out.stdout.split('\n')[0]
	except FileNotFoundError:
		return False


def _test_ready():
	messages = []
	if not _has_pandoc():
		messages.append('pandoc')
	if not _has_latex():
		messages.append('latex (e.g. texlive)')
	if not _has_dvisvgm():
		messages.append('dvisvgm (part of latex)')
	if messages:
		print('embedmath requires {}'.format(', '.join(messages)), file=_stderr)
		exit(1)


def encode():
	_test_ready()
	try:
		_argv.pop(0)
		target = _argv.pop(0)
		if len(_argv) > 0:
			raise IndexError()
	except IndexError:
		print('"embedmath <filename>" requires exactly one filename.', file=_stderr)
		exit(1)
	target = _path.join(_path.curdir, target)
	if not _path.exists(target):
		print('{} file not found'.format(repr(target)), file=_stderr)
		exit(1)
	with _TD() as cd:
		dest = _path.join(cd, 'temp.md')
		_run(['pandoc', target, '-f', 'markdown', '-t', 'markdown', '-s', '-o', dest, '--filter', '_embedmath_encoding_filter'], timeout=30, text=True)
		with open(dest, 'rt') as fp:
			print(fp.read())
	exit(0)


def decode():
	_test_ready()
	try:
		_argv.pop(0)
		target = _argv.pop(0)
		if len(_argv) > 0:
			raise IndexError()
	except IndexError:
		print('"unembedmath <filename>" requires exactly one filename.', file=_stderr)
		exit(1)
	target = _path.join(_path.curdir, target)
	if not _path.exists(target):
		print('{} file not found'.format(repr(target)), file=_stderr)
		exit(1)
	with _TD() as cd:
		dest = _path.join(cd, 'temp.md')
		_run(['pandoc', target, '-f', 'markdown', '-t', 'markdown', '-s', '-o', dest, '--filter', '_embedmath_decoding_filter'], timeout=30, text=True)
		with open(dest, 'rt') as fp:
			print(fp.read())
	exit(0)


def encoding_filter():
	filter = _EncodingFilter()
	_toJSONFilter(filter)


def decoding_filter():
	filter = _DecodingFilter()
	_toJSONFilter(filter)
