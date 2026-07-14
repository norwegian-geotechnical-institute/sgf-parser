# NGI Python SGF Parser Package

Version 0.0.13

_2026-07-14_

- Now read the `IC=` header and populate a new `depth` attribute on the Dissipation Test (DT) class `MethodDT`.
- Set 7 days delay on installing new packages.

Version 0.0.12

_2026-07-08_

- Now accept Unicode minus characters in the data.

Version 0.0.11 Yanked

_2025-12-02_

- ~~Change the attribute name `load` to `penetration_force` for the Weight Sounding Test (WST)
  and the Swedish Impact sounding / Slagsondering (Slb) method data.~~

Version 0.0.10

_2025-11-27_

- Add data model for the Impact sounding / Slagsondering (Slb) method

Version 0.0.9

_2025-08-12_

- Better support for importing Dissipation Tests (DT). Still need the code `HM=35`, and we do not handle dissipation
  tests with `HM=7`.

Version 0.0.8

_2025-05-13_

- Reverted the parsing strategy to go line by line, such that K-codes do not overrule the other data.

Version 0.0.7

_2025-04-11_

- Add `SP` as an alias for hammering pressure.
  Affects method Total sounding (TOT) and Soil Rock Sounding (SRS).

Version 0.0.6

_2025-03-13_

- Converting from Poetry to uv. No functional changes.

Version 0.0.5

_2025-03-10_

- Add support for old WST code (2).
- Rename Dynamic Probing (DP) type from `type` to `dynamic_probing_type`.

Version 0.0.4

_2025-02-27_

- Add `borehole_name` to methods.
- Change the values of the SoundingClass and DPType.

Version 0.0.3

_2025-02-17_

- Add support for the methods Pressure Sounding (Tr), Impact sounding (Slb) and Light sounding (Sti).

Version 0.0.2

_2024-10-15_

- Fix missing handling of non-standard method codes 9, 71 and 72.

Version 0.0.1

_2024-10-03_

- Add support for non-standard SGF codes for SRS/Jb2 71, SRS/Jb3 72 and DP SH B 9.

Version 0.0.1b5

_2024-08-22_

- Add support for Dynamic Probing (DP).

Version 0.0.1b4

_2024-08-08_

- Fix an edge case where strings are given in the "K" code, e.g. "K=SAND".
  These are not moved to the "T"/remarks column, as "K" is reserved for (integer) comment codes.

Version 0.0.1b3

_2024-08-06_

- Fix bug in SGFParser that causes the parser to fail if it contains several comment codes (in "K" column) but no
  remarks (in "T" column).

Version 0.0.1b2

_2024-07-29_

- Support Weight Sounding Test (WST) (Swedish Viktsondering)

Version 0.0.1b1

_2024-06-21_

- Update packages.

Version 0.0.1a2

_2024-05-22_

- Addition of dissipation test method with limited support.

Version 0.0.1a1 (Alpha Release)

_2024-04-03_

- Initial pre-release version of the package.
