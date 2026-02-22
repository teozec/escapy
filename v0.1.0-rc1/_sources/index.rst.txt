escapy Documentation
====================

**escapy** is a lightweight Python library for building simple escape-room
style games using `pygame <https://www.pygame.org/>`_.

It provides a clean separation between **game logic** (rooms, objects, events,
commands) and **rendering** (the pygame UI), making it easy to understand,
extend, and swap in alternative UI backends.

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting-started
   architecture
   game-objects
   commands
   events
   protocols
   pygame-ui

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/escapy
   api/escapy.types
   api/escapy.events
   api/escapy.commands
   api/escapy.game
   api/escapy.objects
   api/escapy.mixins
   api/escapy.messages


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
