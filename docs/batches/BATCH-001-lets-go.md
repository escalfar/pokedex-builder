# BATCH-001 — Let's Go Pikachu / Let's Go Eevee

**Feature Branch:** `feature/catalog-game-availability`

**Batch:** 001

**Status:** Completed

**Date:** YYYY-MM-DD

---

# Objective

Implement the first verified section of the game availability catalog by adding support for **Pokémon: Let's Go, Pikachu!** and **Pokémon: Let's Go, Eevee!**

This batch establishes the first production-ready game catalog and introduces support for National Dex ranges to avoid unnecessary repetition in the YAML configuration.

---

# Scope

Files modified:

```text
data/game_availability.yaml
pokedex/game_availability.py
pokedex/catalog_coverage.py
tests/test_game_availability.py
tests/test_catalog_coverage.py
```

---

# Functional Changes

## 1. National Dex Range Support

The game availability engine now supports inclusive National Dex ranges.

Example:

```yaml
national_dex_ranges:
  - [1, 150]
```

instead of writing 150 individual entries.

This significantly reduces duplication while keeping the catalog readable.

---

## 2. Let's Go Availability

The catalog now marks as available:

* National Dex #001–#150
* Alolan regional forms obtainable through in-game NPC trades
* Mewtwo

The following remain excluded:

* Galar forms
* Hisui forms
* Paldea forms
* Any regional form not obtainable in Let's Go

---

## 3. Coverage Engine

The coverage report now understands rules defined through National Dex ranges.

Coverage statistics correctly distinguish between:

* verified TRUE
* verified FALSE
* unknown

when a rule originates from a range.

---

# Validation Rules

Added validation for:

* malformed ranges
* inverted ranges
* duplicated ranges
* overlapping range handling

---

# Tests Added

New tests verify:

* inclusive range behavior
* first and last Pokémon in a range
* values outside the range
* interaction between ranges and explicit exclusions
* coverage calculation using ranges

---

# Design Decisions

## Why ranges?

Without ranges the YAML would contain hundreds of repetitive entries.

Ranges:

* reduce maintenance cost;
* improve readability;
* reduce merge conflicts.

---

## Why explicit exclusions?

Regional forms introduced after Generation VII share National Dex numbers with Kanto species.

A generic range would incorrectly classify them as available.

Explicit exclusions therefore have higher priority than range inclusions.

Priority order:

1. Explicit exclusion
2. Explicit HOME ID inclusion
3. National Dex range

---

# Sources

Availability verified using official game documentation and Pokémon HOME compatibility.

Main references:

* Official Pokémon Let's Go documentation
* Pokémon HOME compatibility
* Bulbapedia
* Serebii

---

# Coverage After Batch

Game completed:

* Let's Go Pikachu / Let's Go Eevee

Coverage status:

```text
Let's Go ............ Verified
Remaining games ..... Pending
```

---

# Known Limitations

This batch only covers Let's Go.

The remaining games will be completed in subsequent batches.

No assumptions are made for games that have not yet been verified.

Unknown values intentionally remain unclassified.

---

# Next Batch

**BATCH-002**

Game:

* Pokémon Legends: Arceus

Objectives:

* Complete all Hisui forms
* Complete all Hisui evolutions
* Validate HOME compatibility
* Add regression tests
* Document every exception
