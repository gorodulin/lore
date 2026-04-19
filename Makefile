.PHONY: help test install ruff vulture skylos

help:
	@echo "Available targets:"
	@echo "  help     - Show this help message"
	@echo "  install  - Install dependencies with uv"
	@echo "  test     - Run tests with pytest and check coverage"
	@echo "  ruff     - Run ruff linter"
	@echo "  vulture  - Find unused code with vulture"
	@echo "  skylos   - Run skylos static analysis and security checks"

test:
	@scripts/find_missing_tests lore tests
	uv run ruff check .
	uv run pytest -q
	$(MAKE) vulture
	$(MAKE) skylos
	@uv tool install --force --reinstall . -q

install:
	uv sync --all-extras

ruff:
	uv run ruff check .

vulture:
	uv run vulture lore/ scripts/vulture_whitelist.py --min-confidence 60 --exclude lore/matchers/find_tool_contexts_for_prefixes.py

skylos:
	@json=$$(uv run skylos . --json --secrets --confidence 80 --exclude-folder .claude-plugins-official --exclude-folder tests --exclude-folder scripts 2>/dev/null); \
	json=$$(echo "$$json" | jq 'if .unused_functions then .unused_functions |= [.[] | select(.name | test("^(ensure_lore_server|find_tool_contexts_for_prefixes|FactStore\\.)") | not)] else . end'); \
	unused=$$(echo "$$json" | jq -r '.unused_functions // [] | length'); \
	imports=$$(echo "$$json" | jq -r '.unused_imports // [] | length'); \
	security=$$(echo "$$json" | jq -r '.security_issues // [] | length'); \
	total=$$((unused + imports + security)); \
	if [ $$total -gt 0 ]; then \
		echo "Skylos: $$unused unused functions, $$imports unused imports, $$security security issues"; \
		echo "$$json" | jq -r '.unused_functions[]? | "  \(.file):\(.line) - \(.name)"'; \
		echo "$$json" | jq -r '.unused_imports[]? | "  \(.file):\(.line) - \(.name)"'; \
		echo "$$json" | jq -r '.security_issues[]? | "  \(.file):\(.line) - \(.type)"'; \
		exit 1; \
	fi
