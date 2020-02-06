from bs4 import BeautifulSoup
from subprocess import run
import re
from sys import stderr
from tempfile import TemporaryDirectory
import base64
from pandocfilters import RawInline, RawBlock
import json
import sys


class EncodingFilter:
	"""
	Pandoc filter to convert math to svg images
	"""

	"""
	Default LATEX document to use to render things.
	"""
	LATEX_DOC = '\n'.join([
		s.strip() for s in r'''
			\documentclass{{article}}
			\pagestyle{{empty}}
			\usepackage{{amsmath}}
			\usepackage{{amssymb}}
			\begin{{document}}
			{}
			\end{{document}}
		'''.splitlines()
	]).strip()

	"""
	Pattern for use in removing namespaces from SVG tags
	"""
	_nspat = re.compile(r'\{[^}]+\}')

	"""
	Ensure fonts are unique to their block since dvisvgm does funky stuff in there
	"""
	_font_face = re.compile(r'(@font-face\{font-family:([^;]+);.*?\}),?')

	def __init__(self):
		self._i = 0

	def _block(self):
		self._i += 1
		return self._i

	def render_tex_to_string(self, tex: str, inline: bool = False) -> str:
		if inline:
			scale = 1.0
		else:
			scale = 1.2

		# Generate the temp dir and render guys
		with TemporaryDirectory() as cd:
			tex_path = '{}/target.tex'.format(cd)
			svg_path = '{}/target.svg'.format(cd)
			with open(tex_path, 'wt') as fp:
				fp.write(self.__class__.LATEX_DOC.format(tex))
			result = run(["latex", 'target.tex'], cwd=cd, timeout=1, capture_output=True, text=True)
			if result.stderr:
				print(result.stderr, file=stderr)
			result = run(["dvisvgm", 'target.dvi', '--font-format=woff,autohint', '--scale={}'.format(scale), '--exact'], cwd=cd, timeout=1, capture_output=True, text=True)
			if result.stderr:
				print(result.stderr, file=stderr)
			with open(svg_path, 'rt') as fp:
				content = fp.read()
		return content

	def render_tex_to_encoded_img_url(self, tex: str, inline: bool = False) -> str:
		content = self.render_tex_to_string(tex, inline)
		if inline:
			return '<img embedmath-tex={} src="data:image/svg+xml;base64,{}">'.format(
				json.dumps(tex),
				base64.b64encode(content.encode()).decode()
			)
		else:
			return '<p align="center" style="clear: both;" embedmath-tex={}><img src="data:image/svg+xml;base64,{}"></p>'.format(
				json.dumps(tex),
				base64.b64encode(content.encode()).decode()
			)

	# def render_tex_to_xmlsvg(self, tex, inline=False):
	# 	content, tex = self.render_tex_to_string(tex, inline)
	# 	content = content.splitlines()
	# 	if content[0].startswith('<?xml'):
	# 		content.pop(0)
	# 	content = ''.join(content)
	#
	# 	# Depending on inline or not, wrap in a paragraph tag
	# 	if not inline:
	# 		content = '<p align="center" style="clear: both;">{}</p>'.format(content)
	#
	# 	# Remove namespace portions of all tags
	# 	root_node = ET.fromstring(content)
	# 	for elem in root_node.getiterator():
	# 		match = self.__class__._nspat.match(elem.tag)
	# 		if match:
	# 			elem.tag = elem.tag[match.end():]
	#
	# 	# Make ids unique and give the root node the id and a version of the original tex string
	# 	ident = 'embedmath_style{}'.format(self._block())
	# 	root_node.set('id', ident)
	# 	root_node.set('embedmath-tex', tex)
	# 	if root_node.tag.lower() == 'p':
	# 		node = root_node.find('svg')
	# 	else:
	# 		node = root_node
	# 	g = node.find('g')
	# 	g.attrib.pop('id')
	# 	style = node.find('style')
	#
	# 	# Clean up styles
	# 	if style:
	# 		style_text = style.text.strip()
	# 		fonts = self.__class__._font_face.findall(style_text)
	# 		style_text = self.__class__._font_face.sub('', style_text).strip()
	# 		for font_def, font_name in fonts:
	# 			style_text = '{}\n{}'.format(font_def, style_text)
	# 			new_font_name = '{}_{}'.format(font_name, ident)
	# 			style_text = style_text.replace(
	# 				'font-family:{};'.format(font_name),
	# 				'font-family:{};'.format(new_font_name)
	# 			)
	# 		style_text = re.sub(r'\btext\.', '#{} text.'.format(ident), style_text)
	# 		style.text = style_text
	#
	# 	return ET.tostring(root_node, method='html', encoding='unicode')

	def __call__(self, key, value, format, meta):
		if key == 'Math':
			props, content = value
			if props['t'] == 'InlineMath':
				inline = True
				tex = '${}$'.format(content)
			elif props['t'] == 'DisplayMath':
				inline = False
				tex = '$${}$$'.format(content)
			else:
				raise Exception('Unknown type {}'.format(repr(props['t'])))
			svg = self.render_tex_to_encoded_img_url(tex, inline=inline)
			return RawInline('html', svg)


class DecodingFilter:
	def __init__(self):
		self._delete_everything = False

	def __call__(self, key, value, format, meta):
		# When we hit the block opening element that has a embedmath-tex attr, keep deleting until the next block
		if self._delete_everything:
			if key == 'RawBlock':
				self._delete_everything = False
			return []
		# Our HTML rendered math is one of these nodes that's also HTML
		if key not in ('RawInline', 'RawBlock'):
			return
		kind, content = value
		if kind != 'html':
			return
		# Parse it
		soup = BeautifulSoup(content, 'html.parser')
		node = list(soup.childGenerator())[0]
		if node.get('embedmath-tex', None) is not None:
			tex = json.loads('"{}"'.format(node['embedmath-tex']))
			node.replace_with(tex)
			if key == 'RawBlock':
				self._delete_everything = True
		if key == 'RawInline':
			return RawInline('markdown', str(soup))
		elif key == 'RawBlock':
			return RawBlock('markdown', str(soup))
		else:
			raise TypeError('Unhandled key {}'.format(repr(key)))
