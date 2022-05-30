init:
	python3 -m pip install -r requirements.txt

avatars:
	python3 repo_to_avatars.py

whatsapp:
	python3 whatsapp_to_stats.py

uninstall:
	pip uninstall botline -y

.PHONY: init
