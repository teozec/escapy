# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-02-28

### Added

- Core game engine (`Game`) with room navigation, inventory, and object interaction.
- Command system with composable factory functions: `pick`, `put_in_hand`, `simple_lock`, `key_lock`, `ask_for_code`, `locked`, `inspect`, `reveal`, `move_to_room`, `add_to_inventory`, `no_op`.
- Higher-order command combinators: `combine`, `cond`, `chain`.
- Event dataclasses for all game-state changes (`PickedUpEvent`, `UnlockedEvent`, `MovedToRoomEvent`, etc.).
- Protocol-based interfaces: `GameProtocol`, `Interactable`, `InventoryInteractable`, `Placeable`, `Unlockable`, `Decodable`, `GameUiProtocol`.
- Mixin classes: `UnlockableMixin`, `DecodableMixin`.
- Ready-made game objects: `PickableObject`, `SelfSimpleLock`, `SelfKeyLock`, `SelfAskCodeLock`, `MoveToRoom`, `InspectableObject`, `PickableInspectableObject`.
- `dict_message_provider` for mapping events to display strings.
- Pygame-based UI (`PyGameUi`) with room rendering, inventory sidebar, message bar, code-input overlay, and inspect overlay.
- Sphinx documentation with narrative guides and API reference.
- GitHub Actions CI for tests, docs deployment, and release builds.

[Unreleased]: https://github.com/teozec/escapy/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/teozec/escapy/releases/tag/v0.1.0
