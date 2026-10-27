#!/usr/bin/env bash
# Bloc géré dans /etc/fstab (entre les marqueurs), points de montage, identifiants SMB.
# Idempotent : le bloc est régénéré et remplacé ; hors bloc, seules les lignes STRICTEMENT
# identiques (aux espaces près) à une ligne du bloc sont retirées (doublons de l’ancienne
# config manuelle). Aucune autre ligne n’est touchée.
set -euo pipefail
source "$DOTFILES_LIB"
need_vars NAS_HOST NAS_SMB_SHARES

block=$(bash "$MODULE_DIR/gen-block.sh")
tmp=$(mktemp)
trap 'rm -f -- "$tmp"' EXIT

BLOCK="$block" awk '
    function norm(s) { gsub(/[ \t]+/, " ", s); sub(/^ /, "", s); sub(/ $/, "", s); return s }
    BEGIN { block = ENVIRON["BLOCK"]; n = split(block, b, "\n"); for (i = 1; i <= n; i++) if (b[i] !~ /^#/) dup[norm(b[i])] = 1 }
    /^# >>> dotfiles nas-mounts/ { skip = 1; next }
    skip && /^# <<< dotfiles nas-mounts/ { skip = 0; next }
    skip { next }
    (norm($0) in dup) { removed++; next }
    { print }
    END {
        print block
        if (removed) printf "%d doublon(s) retiré(s)\n", removed > "/dev/stderr"
    }
' /etc/fstab > "$tmp"

if cmp -s "$tmp" /etc/fstab; then
    success "/etc/fstab déjà à jour"
else
    as_root cp -a /etc/fstab "/etc/fstab.bak-$(date +%Y%m%d-%H%M%S)"
    as_root install -m 644 "$tmp" /etc/fstab
    success "/etc/fstab : bloc nas-mounts écrit (sauvegarde /etc/fstab.bak-*)"
fi

# Points de montage
while read -r _ mnt _; do
    [[ -d "$mnt" ]] || { as_root mkdir -p "$mnt"; info "créé : $mnt"; }
done < <(grep -v '^#' <<<"$block")

[[ -f "$HOME/.smbcredentials-nas" ]] && chmod 600 "$HOME/.smbcredentials-nas"

as_root systemctl daemon-reload
as_root systemctl restart remote-fs.target || warn "remote-fs.target : redémarrage en échec (NAS joignable ?)"
success "partages NAS en automontage (montés au premier accès)"
