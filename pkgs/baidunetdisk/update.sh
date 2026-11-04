#!/usr/bin/env nix-shell
#!nix-shell -i bash -p bash -p curl -p jq -p nix -p nix-update
# shellcheck shell=bash
set -euo pipefail

NEW_VERSION=$(curl -fsSL 'https://aur.archlinux.org/rpc/?v=5&type=info&arg[]=baidunetdisk-electron' |
  jq -er '.results[0].Version | select(type == "string")' | sed 's/-[^-]*$//')
if [[ ! $NEW_VERSION =~ ^[0-9]+(\.[0-9]+)+$ ]]; then
  echo "Invalid upstream version: $NEW_VERSION" >&2
  exit 1
fi
if [[ -n ${UPDATE_NIX_OLD_VERSION:-} && $NEW_VERSION != "$UPDATE_NIX_OLD_VERSION" &&
  $(printf '%s\n%s\n' "$NEW_VERSION" "$UPDATE_NIX_OLD_VERSION" | sort -V | head -n 1) == "$NEW_VERSION" ]]; then
  echo "Refusing to downgrade from $UPDATE_NIX_OLD_VERSION to $NEW_VERSION" >&2
  exit 1
fi
exec nix-update "$UPDATE_NIX_ATTR_PATH" --version "$NEW_VERSION"
