
clean:
	@find ./ -iname __pycache__  | xargs rm -rf

package:
	git-versioner --tag --save
	python -m build
	pip install ./dist/pygui-`git-versioner --short --python`-py3-none-any.whl --force-reinstall

.PHONY: dirs
