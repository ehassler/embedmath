from setuptools import setup, find_packages
setup(
	name="embedmath",
	version="0.1",
	package_dir={"": "src"},
	packages=find_packages('src'),
	entry_points={
		"console_scripts": [
			"embedmath = embedmath:encode",
			"_embedmath_encoding_filter = embedmath:encoding_filter",
			"unembedmath = embedmath:decode",
			"_embedmath_decoding_filter = embedmath:decoding_filter",
		]
	},

	# Project uses reStructuredText, so ensure that the docutils get
	# installed or upgraded on the target machine
	install_requires=["pandocfilters", "bs4"],

	author="Edgar Hassler",
	author_email="ehassler@gmail.com",
	description="Command line tool to embed mathematics within markdown",

	# Since our test files are bare, don't zip
	zip_safe=False
)
