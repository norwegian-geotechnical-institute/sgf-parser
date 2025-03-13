# NGI Python SGF Parser Package

_2025-03-13_

Version 0.0.6

- Converting from Poetry to uv. No functional changes.

_2025-03-10_

Version 0.0.5

- Add support for old WST code (2).
- Rename Dynamic Probing (DP) type from `type` to `dynamic_probing_type`.

_2025-02-27_

Version 0.0.4

- Add `borehole_name` to methods.
- Change the values of the SoundingClass and DPType.

_2025-02-17_

Version 0.0.3

Add support for the methods Pressure Sounding (Tr), Impact sounding (Slb) and Light sounding (Sti).

_2024-10-15_

Version 0.0.2

Fix missing handling of non-standard method codes 9, 71 and 72.

_2024-10-03_

Version 0.0.1

Add support for non-standard SGF codes for SRS/Jb2 71, SRS/Jb3 72 and DP SH B 9.

_2024-08-22_

Version 0.0.1b5

Add support for Dynamic Probing (DP).

_2024-08-08_

Version 0.0.1b4

Fix an edge case where strings are given in the "K" code, e.g. "K=SAND". 
These are not moved to the "T"/remarks column, as "K" is reserved for (integer) comment codes.

_2024-08-06_

Version 0.0.1b3

Fix bug in SGFParser that causes the parser to fail if it contains several comment codes (in "K" column) but no remarks (in "T" column).

_2024-07-29_

Version 0.0.1b2

Support Weight Sounding Test (WST) (Swedish Viktsondering)

_2024-06-21_

Version 0.0.1b1

Update packages.


_2024-05-22_

Version 0.0.1a2

Addition of dissipation test method with limited support.


_2024-04-03_

Version 0.0.1a1 (Alpha Release)

Initial pre-release version of the package.
