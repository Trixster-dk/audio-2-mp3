# Audio 2 MP3 - Plan

Version 1.1.1 - 2026-09-27

## Goal

A reliable desktop converter from common audio formats to MP3 that never loses
or overwrites user files.

## Current status

Version 1.1.0 is done: safe output naming, atomic writes, a robust dependency
check, locked controls during conversion and translation fallback. See
`CHANGELOG.md`.

## Next steps

See `TODO.md`.

## Rollback

Every release is a Git commit. Roll back with `git checkout <commit> -- .`
(1.0.0 = `695a970`). Runtime files (`settings.json`, `converter_log.txt`) are
not touched by updates.
