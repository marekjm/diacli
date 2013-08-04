check:
	#check dependencies
	python3 -c 'import clap, diaspy'


install:
	make check
	cp ./diacli.py ./diacli
	chmod +x ./diacli
	mv ./diacli ~/.local/bin/
	mkdir ~/.diacli
	echo "" > ~/.diacli/conf.json
