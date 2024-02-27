
clean:
	@find ./ -iname __pycache__  | xargs rm -rf

package:
	@echo PYPLC_VERSION = \"`python -m setuptools_git_versioning`\">src/pygui/_version.py
	python -m build
	pip install ./dist/pygui-`python -m setuptools_git_versioning`-py3-none-any.whl --force-reinstall

.PHONY: dirs
