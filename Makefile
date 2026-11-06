.PHONY: test scene sweep verify sheet bundle all docker

test scene sweep verify sheet all docker:
	python tasks.py $@
bundle:
	python tasks.py bundle --folder out/production --team $(TEAM)
