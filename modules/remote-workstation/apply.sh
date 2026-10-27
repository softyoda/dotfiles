#!/usr/bin/env bash
# Pour chaque « nom=user@hôte[:/chemin] » de REMOTE_WORKSTATIONS :
#   ~/.config/remote-workstations/<nom>.conf  → lu par remote-ws-mount@<nom>.service et remote-ws-run
#   ~/Mounts/<nom>                            → montage sshfs du dossier personnel distant
#   raccourci dans les Emplacements de Dolphin
set -euo pipefail
source "$DOTFILES_LIB"
need_vars REMOTE_WORKSTATIONS REMOTE_WS_KEY

key="${REMOTE_WS_KEY/#\~/$HOME}"
conf_dir="$HOME/.config/remote-workstations"
units_dir="$HOME/.config/systemd/user"
places="$HOME/.local/share/user-places.xbel"
stamp=$(date +%Y%m%d)
mkdir -p "$conf_dir"

# ─── Clé SSH ────────────────────────────────────────────────────────────────
if [[ ! -f "$key" ]]; then
    mkdir -p "$(dirname "$key")" && chmod 700 "$(dirname "$key")"
    ssh-keygen -q -t ed25519 -N "" -C "$USER@$(hostname)" -f "$key"
    success "clé SSH créée : $key"
fi

# allow_other (sshfs en utilisateur) exige user_allow_other
grep -qx 'user_allow_other' /etc/fuse.conf 2>/dev/null || ensure_line_root 'user_allow_other' /etc/fuse.conf

# ─── Machines ───────────────────────────────────────────────────────────────
for entry in $REMOTE_WORKSTATIONS; do
    name="${entry%%=*}" target="${entry#*=}"
    remote="${target%%:*}"                       # user@hôte
    host="${remote#*@}" user="${remote%@*}"
    [[ "$target" == *:* ]] && rpath="${target#*:}" || rpath="/home/$user"
    mnt="$HOME/Mounts/$name"
    unit="remote-ws-mount@$name.service"

    cat > "$conf_dir/$name.conf" <<EOF
# Généré par le module dotfiles remote-workstation
HOST="$host"
REMOTE="$remote"
REMOTE_PATH="$rpath"
MOUNT="$mnt"
KEY="$key"
EOF
    mkdir -p "$mnt"

    # Ancienne config manuelle (<nom>-mount.service, unité .mount, menu <nom>-run) → désactivée
    for old in "$name-mount.service" "$(systemd-escape -p --suffix=mount "$mnt")"; do
        if [[ -f "$units_dir/$old" ]]; then
            systemctl --user disable --now "$old" 2>/dev/null || true
            mv "$units_dir/$old" "$units_dir/$old.bak-$stamp"
            warn "ancienne unité $old désactivée (sauvegarde .bak-$stamp)"
        fi
    done
    old_menu="$HOME/.local/share/kio/servicemenus/$name-run.desktop"
    [[ -f "$old_menu" ]] && mv "$old_menu" "$old_menu.bak-$stamp" && warn "ancien menu $name-run.desktop remplacé par « Machine distante »"

    enable_user "$unit" || warn "$unit : démarrage en échec ($host éteint ? clé non autorisée ?)"

    # Emplacement Dolphin (ajouté une fois ; fermer Dolphin avant si besoin)
    if [[ -f "$places" ]] && ! grep -qF "href=\"file://$mnt\"" "$places"; then
        sed -i "s#</xbel>#  <bookmark href=\"file://$mnt\">\n  <title>$name</title>\n  <info>\n   <metadata owner=\"http://freedesktop.org\">\n    <bookmark:icon name=\"network-server\"/>\n   </metadata>\n  </info>\n </bookmark>\n</xbel>#" "$places"
        info "Emplacement Dolphin ajouté : $name"
    fi

    # Clé déjà autorisée ?
    if ssh -i "$key" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=5 \
           -o StrictHostKeyChecking=accept-new "$remote" true 2>/dev/null; then
        success "$name : connexion SSH par clé OK"
    else
        warn "$name : clé non autorisée ou machine injoignable. Une fois, depuis un terminal :"
        echo "      ssh-copy-id -i $key.pub $remote"
    fi
done

# ─── Lanceur Whisper (optionnel) ────────────────────────────────────────────
if [[ -n "${REMOTE_WS_WHISPER:-}" ]]; then
    wname="${REMOTE_WS_WHISPER%%:*}" wpath="${REMOTE_WS_WHISPER#*:}"
    wremote=$(sed -n 's/^REMOTE="\(.*\)"$/\1/p' "$conf_dir/$wname.conf")
    cat > "$HOME/.local/share/applications/$wname-whisper-watch.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Whisper Diarization Watch ($wname)
Comment=Ouvre le watchfolder interactif sur $wname via SSH
Exec=konsole --hold -e ssh -t -i $key -o IdentitiesOnly=yes $wremote bash $wpath
Icon=audio-x-generic
Terminal=false
Categories=AudioVideo;Audio;
Keywords=whisper;diarization;transcription;$wname;
EOF
    success "lanceur Whisper ($wname) installé"
fi

has kbuildsycoca6 && kbuildsycoca6 >/dev/null 2>&1 || true
