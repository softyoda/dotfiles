#!/bin/bash
# Allow overriding base dir; default to conventional user install
TD_BASE_DIR="${TD_BASE_DIR:-$HOME/.local/share/touchdesigner-linux}"
RUNNER_DIR="${TD_BASE_DIR%/}/runner"
WINE_PREFIX="${TD_BASE_DIR%/}/prefix"
USE_NVIDIA_DGPU="N"

# Graphics & Display fixes for Wayland (KDE Plasma 6)
# Forces standalone window initialization through XWayland and avoids GLXMakeCurrent timing bugs.
export WAYLAND_DISPLAY=""
export __GL_YIELD="USLEEP"

find_touchdesigner_exe() {
    find "$WINE_PREFIX/drive_c" -type f -iname 'TouchDesigner.exe' 2>/dev/null | sort -V | tail -n 1
}

# Support version-specific shortcuts via argument (--exe) or env override.
TOUCHDESIGNER_EXE_OVERRIDE_ARG=""
if [[ "$1" == "--exe" ]] && [ -n "$2" ]; then
    TOUCHDESIGNER_EXE_OVERRIDE_ARG="$2"
    shift 2
elif [[ "$1" == --exe=* ]]; then
    TOUCHDESIGNER_EXE_OVERRIDE_ARG="${1#--exe=}"
    shift
fi

if [ -n "$TOUCHDESIGNER_EXE_OVERRIDE_ARG" ] && [ -f "$TOUCHDESIGNER_EXE_OVERRIDE_ARG" ]; then
    TOUCHDESIGNER_EXE="$TOUCHDESIGNER_EXE_OVERRIDE_ARG"
elif [ -n "$TOUCHDESIGNER_EXE_OVERRIDE" ] && [ -f "$TOUCHDESIGNER_EXE_OVERRIDE" ]; then
    TOUCHDESIGNER_EXE="$TOUCHDESIGNER_EXE_OVERRIDE"
else
    TOUCHDESIGNER_EXE="$(find_touchdesigner_exe)"
fi

if [ -z "$TOUCHDESIGNER_EXE" ]; then
    echo "Error: TouchDesigner.exe not found in Wine prefix."
    exit 1
fi

# On hybrid laptops, optionally offload rendering to NVIDIA dGPU.
if command -v nvidia-smi >/dev/null 2>&1; then
    if [ "$USE_NVIDIA_DGPU" = "Y" ] || [ "$USE_NVIDIA_DGPU" = "y" ]; then
        export __NV_PRIME_RENDER_OFFLOAD=1
        export __GLX_VENDOR_LIBRARY_NAME=nvidia
        export __VK_LAYER_NV_optimus=NVIDIA_only
        export DRI_PRIME=1
    fi
fi

# Handle optional .toe file argument
EXTRA_ARGS=()
if [ -n "$1" ]; then
    INPUT_PATH="$1"
    # Decode file:// URI if passed by desktop environment
    if [[ "$INPUT_PATH" == file://* ]]; then
        INPUT_PATH="${INPUT_PATH#file://}"
        INPUT_PATH="$(python3 -c "import sys, urllib.parse; print(urllib.parse.unquote(sys.argv[1]))" "$INPUT_PATH" 2>/dev/null || { echo "Warning: python3 not available; .toe file URI path may contain encoded characters" >&2; echo "$INPUT_PATH"; })"
    fi
    # Map Linux path to Wine Z: drive
    WINE_PATH="z:${INPUT_PATH//\//\\}"
    EXTRA_ARGS=("$WINE_PATH")
fi

# Before launching, check if .toe files need the wine_ui_fixes patch
TOE_EXPAND="$(find "$WINE_PREFIX/drive_c" -type f -iname 'toeexpand.exe' 2>/dev/null | head -n1 || true)"
TOE_COLLAPSE="$(find "$WINE_PREFIX/drive_c" -type f -iname 'toecollapse.exe' 2>/dev/null | head -n1 || true)"
FIX_FILE="$TD_BASE_DIR/wine_ui_fixes.tox"

# Patch a single .toe file: checks if already patched, and if not, merges wine_ui_fixes
check_and_patch_toe() {
    local TOE_PATH="$1"
    [ -f "$TOE_PATH" ] || return 0
    local TOE_BASE TOE_DIR DIR_PATH TOC_PATH WINE_TOE
    TOE_BASE="$(basename "$TOE_PATH")"
    TOE_DIR="$(dirname "$TOE_PATH")"
    DIR_PATH="$TOE_DIR/${TOE_BASE}.dir"
    TOC_PATH="$TOE_DIR/${TOE_BASE}.toc"
    WINE_TOE="z:${TOE_PATH//\//\\}"

    # Check if already patched
    rm -rf "$DIR_PATH" "$TOC_PATH" 2>/dev/null || true
    WINEPREFIX="$WINE_PREFIX" "$RUNNER_DIR/bin/wine64" "$TOE_EXPAND" "$WINE_TOE" >/dev/null 2>&1 || true
    local NEEDS_PATCH=false
    if [ ! -d "$DIR_PATH/wine_ui_fixes" ]; then
        NEEDS_PATCH=true
    fi
    rm -rf "$DIR_PATH" "$TOC_PATH" 2>/dev/null || true

    if [ "$NEEDS_PATCH" = true ]; then
        # Backup centralisé (nom unique basé sur le chemin complet)
        BACKUP_DIR="$TD_BASE_DIR/backups"
        mkdir -p "$BACKUP_DIR" 2>/dev/null || true
        # Transforme /home/user/proj/file.toe en _home_user_proj_file.toe.bak (unique même si même nom de fichier)
        local UNIQUE_BAK_NAME="${TOE_PATH//\//_}.bak"
        cp -f "$TOE_PATH" "$BACKUP_DIR/$UNIQUE_BAK_NAME" 2>/dev/null || true
        # Expand target .toe
        WINEPREFIX="$WINE_PREFIX" "$RUNNER_DIR/bin/wine64" "$TOE_EXPAND" "$WINE_TOE" >/dev/null 2>&1 || true
        if [ -d "$DIR_PATH" ]; then
            # Merge fix
            local MERGE_TMP="$(mktemp -d "/tmp/td_merge_toe.XXXXXX" 2>/dev/null || true)"
            if [ -n "$MERGE_TMP" ]; then
                local MERGE_FIX="$MERGE_TMP/fix.tox"
                cp -f "$FIX_FILE" "$MERGE_FIX" 2>/dev/null || true
                local WINE_MFIX="z:${MERGE_FIX//\//\\}"
                WINEPREFIX="$WINE_PREFIX" "$RUNNER_DIR/bin/wine64" "$TOE_EXPAND" "$WINE_MFIX" >/dev/null 2>&1 || true
                if [ -d "$MERGE_FIX.dir" ]; then
                    cp -rf "$MERGE_FIX.dir/"* "$DIR_PATH/" 2>/dev/null || true
                fi
                rm -rf "$MERGE_TMP" 2>/dev/null || true
            fi
            # Add fix entries to .toc
            for entry in "${FIX_ENTRIES[@]}"; do
                echo "$entry" >> "$TOC_PATH"
            done
            WINEPREFIX="$WINE_PREFIX" "$RUNNER_DIR/bin/wine64" "$TOE_COLLAPSE" "$WINE_TOE" >/dev/null 2>&1 || true
        fi
        rm -rf "$DIR_PATH" "$TOC_PATH" 2>/dev/null || true
    fi
}

if [ -n "$TOE_EXPAND" ] && [ -n "$TOE_COLLAPSE" ] && [ -f "$FIX_FILE" ]; then
    # Read fix .toc entries once (shared across all patches)
    FIX_TMPDIR="$(mktemp -d "/tmp/td_fix_launcher.XXXXXX" 2>/dev/null || true)"
    if [ -n "$FIX_TMPDIR" ]; then
        FIX_COPY="$FIX_TMPDIR/fix.tox"
        cp -f "$FIX_FILE" "$FIX_COPY" 2>/dev/null || true
        WINE_FIX_COPY="z:${FIX_COPY//\//\\}"
        WINEPREFIX="$WINE_PREFIX" "$RUNNER_DIR/bin/wine64" "$TOE_EXPAND" "$WINE_FIX_COPY" >/dev/null 2>&1 || true

        if [ -d "$FIX_COPY.dir" ]; then
            # Read fix entries
            FIX_ENTRIES=()
            while IFS= read -r entry; do
                [ -z "$entry" ] && continue
                [[ "$entry" == \#* ]] && continue
                [ "$entry" = ".build" ] && continue
                FIX_ENTRIES+=("$entry")
            done < "$FIX_COPY.toc"

            # Patch NewProject.toe files in drive_c (TouchDesigner default templates)
            while IFS= read -r -d '' NP_TOE; do
                check_and_patch_toe "$NP_TOE"
            done < <(find "$WINE_PREFIX/drive_c" -type f -iname 'NewProject.toe' -print0 2>/dev/null || true)

            # Check the startup mode defined in pref.txt and patch custom template if set
            PREF_FILE="$WINE_PREFIX/drive_c/users/steamuser/AppData/Local/Derivative/TouchDesigner099/pref.txt"
            if [ -f "$PREF_FILE" ]; then
                STARTUP_MODE=$(grep -E '^general\.startupfilemode' "$PREF_FILE" 2>/dev/null | head -n1 | cut -f2 | tr -d '\r' || true)
                if [ "$STARTUP_MODE" = "2" ]; then
                    CUSTOM_TOE=$(grep -E '^general\.startupfilename' "$PREF_FILE" 2>/dev/null | head -n1 | cut -f2- | tr -d '\r' || true)
                    if [ -n "$CUSTOM_TOE" ]; then
                        PATCH_CUSTOM_TOE="${CUSTOM_TOE#z:}"
                        PATCH_CUSTOM_TOE="${PATCH_CUSTOM_TOE#Z:}"
                        PATCH_CUSTOM_TOE="${PATCH_CUSTOM_TOE//\\/\/}"
                        [ -f "$PATCH_CUSTOM_TOE" ] && check_and_patch_toe "$PATCH_CUSTOM_TOE"
                    fi
                fi
            fi

            # Patch the .toe file passed as argument (double-click or CLI), if not already patched
            if [ -n "$INPUT_PATH" ] && [[ "$INPUT_PATH" == *.toe ]]; then
                check_and_patch_toe "$INPUT_PATH"
            fi
        fi
        rm -rf "$FIX_TMPDIR" 2>/dev/null || true
    fi
fi

# Nettoyage automatique des backups de plus de 30 jours
BACKUP_DIR="$TD_BASE_DIR/backups"
if [ -d "$BACKUP_DIR" ]; then
    find "$BACKUP_DIR" -name '*.bak' -type f -mtime +30 -delete 2>/dev/null || true
fi

# 1. On prépare l'environnement d'exécution
PATH="$RUNNER_DIR/bin:$PATH"
export WINEPREFIX="$WINE_PREFIX"

# 2. On remplace le processus Bash par Wine (Supprime le besoin de l'arrière-plan &)
exec "$RUNNER_DIR/bin/wine64" "$TOUCHDESIGNER_EXE" "${EXTRA_ARGS[@]}"
