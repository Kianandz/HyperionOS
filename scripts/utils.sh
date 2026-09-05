#!/usr/bin/env bash

# -----------------------------------------------------------------------------
# Module: Shared Utilities & Logging Functions
# -----------------------------------------------------------------------------

readonly C_GREEN='\033[0;32m'
readonly C_CYAN='\033[0;36m'
readonly C_YELLOW='\033[1;33m'
readonly C_RED='\033[0;31m'
readonly C_RESET='\033[0m'

readonly APP_DIR="/HyperionOS"
readonly APP_USER="hyperion"

PKG_MANAGER=""

log_info() { echo -e "${C_CYAN}[INFO]${C_RESET} $1"; }
log_success() { echo -e "${C_GREEN}[SUCCESS]${C_RESET} $1"; }
log_warn() { echo -e "${C_YELLOW}[WARN]${C_RESET} $1"; }
log_err() { echo -e "${C_RED}[ERROR]${C_RESET} $1" >&2; exit 1; }