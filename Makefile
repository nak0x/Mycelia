update-framework:
	@echo "Updating all app/framework folders in interaction-* subfolders..."
	find . -type d -path './interaction-*/app/framework' | while read target; do \
		echo "Replacing $$target with devkit/python-esp32-template/app/framework..."; \
		rm -rf "$$target"; \
		mkdir -p "$$target"; \
		cp -r devkit/python-esp32-template/app/framework/* "$$target"/; \
	done

