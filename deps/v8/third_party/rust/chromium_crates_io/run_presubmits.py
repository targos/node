#!/usr/bin/env vpython3

# Copyright 2025 The Chromium Authors
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

# This script checks for issues in the following files and directories
# (including interactions between them):
#
# * `//third_party/rust/chromium_crates_io/Cargo.lock` and
# * `//third_party/rust/chromium_crates_io/gnrt_config.toml`.
# * `//third_party/rust/chromium_crates_io/patches/`.
#
# We don't surface these issues earlier (by reporting a fatal error from `gnrt
# vendor`, `gnrt gen`, `gn gen`, or failing the builds), because we want to
# avoid friction when new teams experiment with using Rust.  Some of these
# issues may also happen during the crate update rotation and in this case we
# want to allow the `tools/crate/create_update_cl.py` to continue creating CLs
# (that other script uses `git cl upload ... --bypass-hooks`).
#
# This script is typically not invoked directly, but instead is invoked as part
# of `//third_party/rust/PRESUBMIT.py`

import os
import sys
import toml

import crate_utils

GNRT_CONFIG_RELATIVE_PATH = "third_party/rust/chromium_crates_io/gnrt_config.toml"
GNRT_CONFIG_PATH = os.path.join(crate_utils.CHROMIUM_DIR,
                                GNRT_CONFIG_RELATIVE_PATH)
CARGO_TOML_RELATIVE_PATH = "third_party/rust/chromium_crates_io/Cargo.toml"
CARGO_TOML_FILEPATH = os.path.join(crate_utils.CHROMIUM_DIR,
                                   CARGO_TOML_RELATIVE_PATH)
PATCHES_DIR = os.path.join(crate_utils.CRATES_DIR, "patches")


def _GetCratesConfigDict(gnrt_config):
    if gnrt_config and isinstance(gnrt_config, dict):
        crates = gnrt_config.get("crate")
        if crates and isinstance(crates, dict):
            return crates
    return dict()


def _GetCrateConfigForCrateName(crate_name, gnrt_config):
    crates = _GetCratesConfigDict(gnrt_config)
    crate_cfg = crates.get(crate_name)
    if crate_cfg and isinstance(crate_cfg, dict):
        return crate_cfg
    return dict()


def _GetRealCrateNames(crate_ids):
    non_placeholder_crate_ids = filter(
        lambda crate_id: not crate_utils.IsPlaceholderCrate(crate_id),
        crate_ids)
    return set(
        map(crate_utils.ConvertCrateIdToCrateName, non_placeholder_crate_ids))


def _GetExtraKvForCrateName(crate_name, gnrt_config):
    crate_cfg = _GetCrateConfigForCrateName(crate_name, gnrt_config)
    extra_kv = crate_cfg.get("extra_kv")
    if extra_kv and isinstance(extra_kv, dict):
        return extra_kv
    return dict()


def _CheckTomlTableIsSorted(toml_table):
    """Checks whether the entries in `cargo_toml` are sorted.

       Returns an error message if a problem is detected.
       Returns an empty string if there are no problems.
    """
    assert isinstance(toml_table, dict)

    # The following toml:
    #
    #     ```
    #     [toml_table]
    #     bar = "4.5.6"
    #     foo = "1.2.3"
    #
    #     [toml_table.baz]
    #     version = "7.8.9"
    #     ```
    #
    # Will result in:
    #
    # * `simple_keys == ['bar', 'foo']`
    # * `elaborate_keys == ['baz']`
    simple_keys = []
    elaborate_keys = []
    first_elaborate_key = None
    for (key, value) in toml_table.items():
        if not isinstance(value, str):
            first_elaborate_key = key
        if first_elaborate_key:
            if isinstance(value, str):
                return ("Simple string entries should appear before table "
                        f"entries: `{key}` should appear after "
                        f"`{first_elaborate_key}`.")
            elaborate_keys.append(key)
        else:
            simple_keys.append(key)

    for a, b in zip(simple_keys, simple_keys[1:]):
        if a > b:
            return f"`{b}` should appear before `{a}`."
    for a, b in zip(elaborate_keys, elaborate_keys[1:]):
        if a > b:
            return f"`{b}` should appear before `{a}`."

    return ""


def CheckCargoTomlIsSorted(crate_toml):
    """Checks whether the entries in `cargo_toml` are sorted.

       This tries to implement a subset of ordering behavior of `cargo-sort`.

       Returns an error message if a problem is detected.
       Returns an empty string if there are no problems.
    """
    deps = crate_toml.get("dependencies", None)
    if not isinstance(deps, dict):
        return "Malformed `Cargo.toml` file?  `dependencies` is not a table."
    problem = _CheckTomlTableIsSorted(deps)
    if problem:
        return ("Please sort `[dependencies]` table in "
                f"`{CARGO_TOML_RELATIVE_PATH}`.  Example problem: {problem}")

    return ""


def CheckGnrtConfigTomlIsSorted(_crate_ids, gnrt_config):
    """Checks whether the entries in `gnrt_config.toml` are sorted.

       Returns an error message if a problem is detected.
       Returns an empty string if there are no problems.
    """
    crates = _GetCratesConfigDict(gnrt_config)
    problem = _CheckTomlTableIsSorted(crates)
    if problem:
        return ("Please sort `[crates]` table in "
                f"`{GNRT_CONFIG_RELATIVE_PATH}`.  Example problem: {problem}")

    return ""


def CheckNonapplicableGnrtConfigEntries(crate_ids, gnrt_config):
    """Checks that each crate entry in `gnrt_config.toml` corresponds
       to an actual depedency of `chromium_crates_io/Cargo.toml`.

       Returns an error message if a problem is detected.
       Returns an empty string if there are no problems.
    """
    real_crate_names = _GetRealCrateNames(crate_ids)

    crates_cfg_dict = _GetCratesConfigDict(gnrt_config)
    configured_crate_names = set(crates_cfg_dict.keys())

    nonapplicable_config_entries = configured_crate_names - real_crate_names
    if nonapplicable_config_entries:
        return (f"Some entries in `{GNRT_CONFIG_RELATIVE_PATH}` are not "
                "needed, because they don't apply to actual crates: "
                f'{", ".join(sorted(nonapplicable_config_entries))}')

    return ""


def CheckNonapplicablePatches(crate_ids, gnrt_config):
    """Checks that each directory under `chromium_crates_io/patches/`
       corresponds to an actual depedency of `chromium_crates_io/Cargo.toml`.

       Returns an error message if a problem is detected.
       Returns an empty string if there are no problems.
    """
    real_crate_names = _GetRealCrateNames(crate_ids)

    patched_crate_names = set(
        filter(lambda filename: filename != "README.md",
               os.listdir(PATCHES_DIR)))

    nonapplicable_patches = patched_crate_names - real_crate_names
    if nonapplicable_patches:
        return (f"Some files/directories under `{PATCHES_DIR}` are not "
                "needed, because they don't apply to actual crates: "
                f'{", ".join(sorted(nonapplicable_patches))}')

    return ""


def CheckNonapplicablePatches(crate_ids, gnrt_config):
    """Checks that each directory under `chromium_crates_io/patches/`
       corresponds to an actual depedency of `chromium_crates_io/Cargo.toml`.

       Returns an error message if a problem is detected.
       Returns an empty string if there are no problems.
    """
    real_crate_names = _GetRealCrateNames(crate_ids)

    patched_crate_names = set(
        filter(lambda filename: filename != "README.md",
               os.listdir(PATCHES_DIR)))

    nonapplicable_patches = patched_crate_names - real_crate_names
    if nonapplicable_patches:
        return f"Some files/directories under `{PATCHES_DIR}` are not " + \
                "needed, because they don't apply to actual crates: " + \
               f'{", ".join(sorted(nonapplicable_patches))}'

    return ""


def CheckExplicitAllowUnsafeForAllCrates(crate_ids, gnrt_config):
    """Checks that `gnrt_config.toml` has `allow_unsafe = ...` for each crate.

       Returns an error message if a problem is detected.
       Returns an empty string if there are no problems.
    """
    result = []
    for crate_id in sorted(crate_ids):
        crate_name = crate_utils.ConvertCrateIdToCrateName(crate_id)

        # Ignore the root package and placeholder crates.
        if crate_name == "chromium": continue
        if crate_utils.IsPlaceholderCrate(crate_id): continue

        # Ignore crates that specify `allow_unsafe`.
        extra_kv = _GetExtraKvForCrateName(crate_name, gnrt_config)
        if "allow_unsafe" in extra_kv:
            continue

        # Report a problem for all other crates.
        if not result:  # Is is the **first** problematic `crate_name`?
            result.append("ERROR: Please ensure that `gnrt_config.toml` "
                          "explicitly specifies `allow_unsafe = ...` for all "
                          "crates that `chromium_crates_io` depends on.  "
                          "This helps `//third_party/rust/OWNERS` to check at "
                          "a glance if a given crate contains `unsafe` Rust "
                          "code.")
            result.append("")
        result += [
            f"    [crate.{crate_name}.extra_kv]",
            f"    allow_unsafe = false (or true if needed)",
        ]

    return "\n".join(result)


def CheckMultiversionCrates(crate_ids, gnrt_config):
    """Checks that a bug tracks each crate with multiple versions.

       This check has been discussed in https://crbug.com/404867240.  Having 2
       or more different versions of a crate in Chromium's dependency tree is
       undesirable in general.  So we want to detect when a 2nd version is
       imported, and require opening a bug + recording the bug in
       `gnrt_config.toml` for the given crate.

       Returns an error message if a problem is detected.
       Returns an empty string if there are no problems.
    """

    # Group `crate_id`s by their `crate_name`.
    crate_name_to_list_of_crate_ids = dict()
    for crate_id in crate_ids:
        crate_name = crate_utils.ConvertCrateIdToCrateName(crate_id)
        if crate_name not in crate_name_to_list_of_crate_ids:
            crate_name_to_list_of_crate_ids[crate_name] = []
        crate_name_to_list_of_crate_ids[crate_name] += [crate_id]

    result = []
    for (crate_name, crate_ids) in crate_name_to_list_of_crate_ids.items():
        # Ignore crates where we depend only on a single version.
        if len(crate_ids) == 1:
            continue

        # Ignore crates that already have a bug to track cleaning up a
        # multiversion situation.
        extra_kv = _GetExtraKvForCrateName(crate_name, gnrt_config)
        if "multiversion_cleanup_bug" in extra_kv:
            continue

        # Report a problem for other multiversion crates.
        if not result:  # Is is the **first** problematic `crate_name`?
            result.append("ERROR: Transitive dependency graph includes "
                          "multiple versions of the same crate.  Please "
                          "open a bug to track removing one of the "
                          "versions and put a link to the bug into "
                          "`gnrt_config.toml` like this:")
            result.append("")

        result += [
            f"    # TODO: Remove multiple versions of the `{crate_name}` crate:",
            f"    # {', '.join(sorted(crate_ids))}",
            f"    [crate.{crate_name}.extra_kv]",
            f'    multiversion_cleanup_bug = "https://crbug.com/<bug number>"\n',
        ]

    return "\n".join(result)


def main():
    success = True

    def CheckResult(result):
        nonlocal success
        if result:
            if not success:
                # Add a separator if this is a 2nd, 3rd, or later problem.
                print()
                print("-" * 72)
                print()
            success = False
            print(result)

    with open(CARGO_TOML_FILEPATH) as f:
        cargo_toml = toml.load(f)
        result = CheckCargoTomlIsSorted(cargo_toml)
        CheckResult(result)

    crate_ids = crate_utils.GetCurrentCrateIds()
    gnrt_config = toml.load(open(GNRT_CONFIG_PATH))

    def RunChecks(check_impl):
        nonlocal crate_ids
        nonlocal gnrt_config
        result = check_impl(crate_ids, gnrt_config)
        CheckResult(result)

    RunChecks(CheckGnrtConfigTomlIsSorted)
    RunChecks(CheckExplicitAllowUnsafeForAllCrates)
    RunChecks(CheckMultiversionCrates)
    RunChecks(CheckNonapplicableGnrtConfigEntries)
    RunChecks(CheckNonapplicablePatches)

    if success:
        return 0
    else:
        return -1


if __name__ == '__main__':
    sys.exit(main())
