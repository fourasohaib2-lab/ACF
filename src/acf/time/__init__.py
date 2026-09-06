"""
acf.time - Frame cursor over an externally-supplied time sequence.

What this module actually provides: `TimeManager`, a plain index cursor
(`current`/`next`/`previous`/`first`/`last`/`count`) over a list handed to it
via `load()`. It does no date/time parsing, no timezone or calendar
handling, and has no NumPy or other scientific-stack dependency - pure
Python standard library. Its one real caller is
`acf.animation.animation_engine.AnimationEngine`, which uses it to step
through animation frames.

For an actual physical time axis (calendar-aware, used by the 4D field
model), see `acf.model4d.time_axis.TimeAxis` instead - a different class in
a different module, despite the similar name.
"""
