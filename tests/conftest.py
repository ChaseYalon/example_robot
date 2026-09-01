import sys, os

# project root, so `import components` / `import constants` resolve
_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, _ROOT)

# vendored git submodules (each repo nests its package one level down)
for _p in ("vendor/smartunits", "vendor/lemonlib"):
    sys.path.insert(0, os.path.join(_ROOT, _p))
