*** Сборка wheel
Перед сборкой сделать commit, в конце CHANGE: major|minor|patch 
git-versioner --tag --save
python -m build --wheel
