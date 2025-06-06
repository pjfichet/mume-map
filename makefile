BINDIR=$(HOME)/.local/bin

install: $(BINDIR)/mumemap

$(BINDIR)/mumemap: mumemap.py
	install -m 755 $< $@

uninstall:
	rm -f $(BINDIR)/mumemap

venv:
	python -m venv venv
	# source venv/bin/activate.fish
	venv/bin/python -m pip install --editable .

