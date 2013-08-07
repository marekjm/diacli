check:
	#check dependencies
	python3 -c 'import clap, diaspy'

update:
	cp ./diacli.py ./diacli
	chmod +x ./diacli
	mv ./diacli ~/.local/bin/
	cp ./ui.json ~/.diacli/

install:
	make check
	mkdir ~/.diacli
	touch ~/.diacli/conf.json
	make update
