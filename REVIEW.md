# Release Readiness Assessment — escapy 0.1.0

## Overall Verdict

**Near-ready, with a handful of blockers and several recommended improvements.** The architecture is solid, the documentation is above-average for a first release, and the code is clean. The issues below are grouped by severity.

---

## Blockers (must fix before 0.1.0)

### 1. Tests are broken on `master`
DONE

`pytest` fails with an `ImportError` because `test_objects.py` imports `MoveToRoomAndAddToInventoryObject` and `WinMachine` from `escapy.objects`, but these classes were moved to `example/objects.py` in the latest refactor (commit `43cd72e`). The library's `objects.py` no longer contains them.

**Fix:** Either move `MoveToRoomAndAddToInventoryObject` and `WinMachine` back into the library (they seem generally useful), or update the tests to import from the example package / replicate minimal stubs. Since the CI runs `pytest` on PRs, this would fail there too.

### 2. Version not bumped
WONTFIX

`pyproject.toml` and `docs/conf.py` both still say `0.1.0`. Before tagging a release, bump to `0.1.0` in both places. Consider adopting a single source of truth for the version (e.g. `importlib.metadata` or a `__version__` in `__init__.py`) so you only change it in one place.

### 3. `docs/_build/` is committed to the repo
DONE

The `.gitignore` has `docs/_build/` but it appears the build artefacts are already tracked. Run `git rm -r --cached docs/_build` and push. Built HTML should only live on `gh-pages`.

### 4. `__pycache__/` directories are in the file tree
DONE

Several `__pycache__/` directories appear in the workspace. Verify they are not tracked by git (they *shouldn't* be given the `.gitignore`, but double-check with `git ls-files __pycache__`).

---

## High-priority improvements

### 5. Missing `py.typed` marker
DONE

For downstream users who type-check with mypy/pyright, add an empty `src/escapy/py.typed` file and include it in the package data. This signals PEP 561 compliance. Your library makes heavy use of `Protocol` and type aliases — make the most of it.

### 6. `objects.py` has no `__all__`
PLEASE DO

The module re-exports everything imported at the top level (commands, protocols, mixins, events) alongside the actual game-object classes. Adding an explicit `__all__` would prevent accidental pollution when users do `from escapy.objects import *` and make the public API crystal-clear.

### 7. `MessageProvider` relies on `repr()` — fragile API
PLASE DO document the issue, without changing the behaviour

`dict_message_provider` keys messages by `repr(event)`. This means:
- Adding a field to an event dataclass silently breaks all existing message dictionaries.
- The user has to construct a *real event instance* just to get its `repr` string for use as a dict key.
- Repr output is a CPython implementation detail and not guaranteed to be stable.

Consider an alternative keying strategy (e.g. `(event_class_name, **fields)` or a dedicated `event.key` property). At minimum, document this fragility prominently so users know the trade-off.

### 8. `PyGameUi.config` is an untyped `dict`
WONTFIX

The config is a plain `dict` passed to `__init__`, so there's no discoverability or validation — a missing or misspelled key just crashes at runtime. Consider:
- A `@dataclass` or `TypedDict` for the config schema, or
- At least, validation in `__init__` with clear error messages for missing keys.

### 9. No CHANGELOG
PLEASE DO

A `CHANGELOG.md` is expected for published packages. Even a minimal one documenting "0.1.0 — Initial release" sets the right tone and helps users track changes going forward.

---

## Medium-priority improvements

### 10. `requires-python = ">=3.14"` is very restrictive
DONE

Python 3.14 was released very recently and most users are still on 3.12/3.13. The only feature requiring 3.14 is the `type` statement (`type Room = ...`, `type Event = ...`, `type Command = ...`). Consider whether you could replace those with `typing.TypeAlias` assignments to support 3.12+, significantly widening your user base. If you decide to keep 3.14+, document *why* in the README.

### 11. `example/` import structure is broken as a standalone
DONE

`example/main.py` uses `from .objects import ...` (relative import), which means it can only run as a package (`python -m example.main`). But neither the README nor the example itself documents this. Additionally, the README references `main.example.py`, which doesn't exist. Clarify how to actually run the example.

### 12. `escape/` game duplicates `example/` objects privately
DONE

The `escape/` directory (your real game) imports `MoveToRoomAndAddToInventoryObject` and `WinMachine` from `escapy.objects`, which no longer exports them. This will crash at runtime. Either:
- Keep those classes in the library (they're generic enough), or
- Define them locally in `escape/` (and update imports).

### 13. No test coverage for `PyGameUi`
PLEASE DO

The pygame UI module (430 lines) has zero test coverage. While testing pygame rendering is hard, the state-machine logic (`_NormalState` / `_InsertCodeState` / `_InspectState` transitions) and `handle()` dispatch could be tested with mocked surfaces. This is also the module most likely to regress.

### 14. `Game.objects` is typed as `dict[str, object]`
DONE

Using `object` as the value type discards all useful type information. Consider a `GameObject` protocol union or at least `Any` (to signal intent). Downstream type checkers get no help from `object`.

### 15. No error handling in `Game` methods
PLEASE DO

`Game.interact()` and `Game.insert_code()` silently return `[]` when passed unknown IDs. Consider raising `KeyError` or a custom exception for genuinely invalid object IDs (vs. simply not in current room). Silent failures can be painful to debug.

---

## Low-priority / nice-to-have

### 16. Add `[project.urls]` to `pyproject.toml`
DONE

Include `Homepage`, `Documentation`, `Repository`, and `Bug Tracker` URLs so they appear on PyPI.

### 17. Add classifiers to `pyproject.toml`
PLEASE DO

Standard PyPI classifiers (Development Status, License, Programming Language, Topic) help users discover the package.

### 18. Image scaling in the game loop
WONTFIX

There are three `# TODO: remove transform from game loop if too slow` comments in `pygame_ui.py`. For a 0.1.0 this is fine, but consider pre-scaling images on room change or caching scaled surfaces to avoid per-frame re-scales.

### 19. `docs/getting-started.md` layout diagram is slightly wrong
DONE

The diagram shows `objects/` as a directory but in the actual source it's a single file `objects.py`.

### 20. `escape/` should probably be excluded from the package
WONTFIX

The `escape/` directory is your personal game, not part of the library. Make sure `setuptools` doesn't accidentally include it. Currently it probably doesn't (since it's not under `src/`), but adding an explicit `[tool.setuptools.packages.find]` with `where = ["src"]` in `pyproject.toml` makes this unambiguous.

### 21. Missing `__all__` in `pygame/__init__.py`
PLEASE DO

Already present (good). But `messages.py`, `mixins.py`, `events.py`, and `types.py` do not have `__all__`. Consider adding them for consistency.

### 22. `docs/_build/html/` shouldn't be in version control
DONE

(Duplicate of blocker #3 — reinforcing the point.)

### 23. Consider a `Makefile` or task runner
PLEASE DO using Makefile and updating README development section

Common tasks like `pytest`, `ruff check`, `sphinx-build`, and `python -m build` could be wrapped in a `Makefile` or `just`/`task` file for contributor convenience.

---

## What's already great

- **Clean architecture**: The Command → Event → UI pipeline is well-designed and easy to follow.
- **Protocols over inheritance**: Good use of `typing.Protocol` and `@runtime_checkable` for duck typing.
- **Composable commands**: `combine`, `cond`, `chain` are powerful and well-tested.
- **Documentation**: Comprehensive Sphinx docs with both narrative guides and API reference — well above average for a 0.1.0.
- **CI**: GitHub Actions for tests, docs deployment, and release builds are all in place.
- **License**: LGPL properly applied with per-file headers.
- **Pre-commit**: Ruff linting and formatting integrated.
- **Separation of concerns**: Core library has zero pygame dependency.

---

## Suggested priority order

1. Fix broken tests (blocker #1)
2. Bump version to 0.1.0 (#2)
3. Remove `docs/_build` from git (#3)
4. Add `CHANGELOG.md` (#9)
5. Add `py.typed` (#5)
6. Add `__all__` to `objects.py` (#6)
7. Fix `escape/` imports (#12)
8. Fix README example reference (#11)
9. Address `MessageProvider` fragility or document it (#7)
10. Everything else as time permits
