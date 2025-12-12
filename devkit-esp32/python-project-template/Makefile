ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))

run:
	mpremote cp -r $(ARGS) :
	mpremote reset
	mpremote

deploy:
	mpremote cp -r app/* :

start:
	mpremote reset

%:
	@:
