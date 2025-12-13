ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

run:
	mpremote rm -r :
	mpremote cp -r $(ARGS) :
	mpremote reset
	mpremote

dev:
	mpremote cp -r $(ARGS) :
	mpremote reset
	mpremote

deploy:
	mpremote rm -r :
	mpremote cp -r app/* :

start:
	mpremote reset

%:
	@:
