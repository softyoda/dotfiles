# Ordi pro — Windows

Aide-mémoire pour remonter le poste de travail Windows. Pas de module `dotctl`
ici (il cible Linux) : tout se fait à la main en suivant cette page.

## Applications (winget)

```powershell
winget install -e --accept-package-agreements --accept-source-agreements `
  AltSnap.AltSnap ALCPU.CoreTemp namazso.OpenHashTab NickeManarin.ScreenToGif `
  ImageMagick.Q16-HDRI AntSoftware.AntRenamer MediaTab.MediaTab Agisoft.TextureDeLighter `
  KeeperSecurity.KeeperDesktop 7zip.7zip SlackTechnologies.Slack Mozilla.Firefox `
  VideoLAN.VLC OBSProject.OBSStudio nomacs.nomacs XnSoft.XnConvert XnSoft.XnViewMP `
  Microsoft.PowerToys ONLYOFFICE.DesktopEditors Iterate.Cyberduck `
  LibreHardwareMonitor.LibreHardwareMonitor f3d-app.f3d CodecGuide.K-LiteCodecPack.Mega `
  CloudCompare.CloudCompare Google.EarthPro Agisoft.Metashape.Professional `
  OSGeo.QGIS OSGeo.QGIS_LTR Anaconda.Anaconda3 GitHub.GitHubDesktop `
  Microsoft.Azure.StorageExplorer BlenderFoundation.Blender VictorIX.BlenderLauncher `
  EpicGames.EpicGamesLauncher HulubuluSoftware.AdvancedRenamer Parsec.Parsec `
  TortoiseSVN.TortoiseSVN Gyan.FFmpeg Comfy.ComfyUI-Desktop CLechasseur.PathCopyCopy `
  ShareX.ShareX RawTherapee.RawTherapee DuongDieuPhap.ImageGlass voidtools.Everything.Alpha `
  Cognirush.MassImageCompressor 3Dconnexion.3DxWare.10 AntibodySoftware.WizTree `
  VSCodium.VSCodium OpenJS.NodeJS.LTS Microsoft.WSL Paseo.Paseo yt-dlg.yt-dlg
```

`winget install` accepte plusieurs identifiants à la suite ; `--id` répété n'est pas valide.

Hors winget, à télécharger à la main :

- **DaVinci Resolve** — formulaire obligatoire chez Blackmagic :
  <https://www.blackmagicdesign.com/support/family/davinci-resolve-and-fusion>

## Firefox

Un seul réglage `about:config` à reporter :

| Préférence | Valeur | Effet |
|---|---|---|
| `toolkit.tabbox.switchByScrolling` | `true` | changer d'onglet à la molette sur la barre d'onglets |

**uBlock Origin** (<https://addons.mozilla.org/firefox/addon/ublock-origin/>) :
Tableau de bord → *Listes de filtres* → cocher toute la catégorie **Nuisances**
(EasyList / AdGuard / uBlock : bannières cookies, notifications, newsletters,
widgets sociaux et de chat, suggestions IA, bannières d'applis mobiles,
pop-ups superposées). Pas de filtres perso, pas de règles dynamiques.

## PowerToys

Modules activés : AlwaysOnTop, Awake, Color Picker, Crop And Lock, FancyZones,
File Locksmith, Find My Mouse, Hosts, Image Resizer, Measure Tool,
Mouse Highlighter, Paste As Plain Text, Peek, PowerRename, PowerToys Run,
Registry Preview, Shortcut Guide, Text Extractor, extensions de l'Explorateur.
Désactivés : Mouse Jump, Mouse Pointer Crosshairs, Mouse Without Borders,
Quick Accent, Video Conference Mute.

Raccourcis :

| Module | Raccourci |
|---|---|
| **Measure Tool** | **Win+Shift+M** (modifié ; défaut Win+Ctrl+Shift+M) |
| Always On Top | Win+Ctrl+T |
| Color Picker | Win+Shift+C |
| Text Extractor | Win+Shift+T |
| PowerToys Run | Alt+Espace |
| Peek | Ctrl+Espace |
| Shortcut Guide | Win+Shift+/ (touche `:` en AZERTY) |
| FancyZones — éditeur | Win+Shift+` (touche `ù` en AZERTY) |
| FancyZones — fenêtre suivante / précédente de la zone | Win+PgSuiv / Win+PgPréc |

**FancyZones** :

- Disposition **Colonnes**, 5 zones (6 sur l'écran le plus large), appliquée
  à chaque écran principal et à chaque bureau virtuel.
- **« Afficher l'espacement » désactivé** : aucune marge ni contour entre les
  zones, les fenêtres se touchent.
- Maj + glisser pour aimanter, changement rapide de disposition activé,
  bascule entre fenêtres d'une même zone activée.

## Windows 11 : menu contextuel classique

Rétablit l'ancien menu du clic droit (sans « Afficher plus d'options »).
Dans un terminal, sans droits admin (c'est une clé `HKCU`) :

```bat
reg.exe add "HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32" /f /ve
```

Puis redémarrer l'Explorateur (`taskkill /f /im explorer.exe & start explorer.exe`)
ou se déconnecter/reconnecter. Pour annuler : supprimer la clé
`HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}`.

## Windows 11 : réglages de l'Explorateur et de l'affichage

**Explorateur** : ouvrir sur *Ce PC* au lieu d'*Accueil*, afficher les extensions
de fichiers (décocher « Masquer les extensions des fichiers dont le type est
connu ») et les fichiers cachés :

```powershell
$k='HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced'
Set-ItemProperty $k LaunchTo 1      # 1 = Ce PC, 2 = Accueil
Set-ItemProperty $k HideFileExt 0   # afficher les extensions
Set-ItemProperty $k Hidden 1        # afficher les fichiers cachés
```

**Écran** : résolution personnalisée **3840×1532 à 60 Hz**, avec la mise à
l'échelle Windows à **100 %** (*Paramètres → Système → Affichage → Échelle*).
La résolution se crée dans le Panneau de configuration NVIDIA
(*Affichage → Modifier la résolution → Personnaliser… → Créer une résolution
personnalisée*). Cette section n'apparaît que si un écran est branché sur la
carte NVIDIA, pas sur la carte mère ni sur un écran virtuel de bureau à distance.
Le panneau est une application du Microsoft Store (`9NF8H0H7WMLT`), absente du
pilote : à installer à part.

## Windows 11 : débloat, pubs et télémétrie

À faire après l'installation, sans toucher aux paramètres de l'organisation.

**Applications retirées** (`Remove-AppxPackage`) : Bing Actualités, Bing Météo,
Bing Search, Clipchamp, Teams, Photos OneDrive, Get Help, Feedback Hub,
Dev Home, Power Automate, To Do, Phone Link, Zune Music, Quick Assist,
paquet Web Experience (widgets), et les composants Xbox (Gaming Overlay,
Identity Provider, TCUI, Speech To Text Overlay). Ces derniers sont à réinstaller
si on utilise la Xbox Game Bar ou des jeux du Store.

```powershell
$pat='Clipchamp|BingNews|BingWeather|BingSearch|GetHelp|WindowsFeedbackHub|DevHome|PowerAutomate|Todos|YourPhone|ZuneMusic|QuickAssist|MSTeams|WebExperience|OneDrive.Photos'
Get-AppxPackage | ? { $_.Name -match $pat -and -not $_.NonRemovable } | Remove-AppxPackage
```

**OneDrive** : `winget uninstall -e --id Microsoft.OneDrive`.

**AMD Adrenalin** : inutile si la carte est NVIDIA, à désinstaller
(`winget uninstall` sur *AMD Radeon Software* et *AMD Software*). Garder
*AMD Chipset Software*.

**Menu Démarrer sans recherche web ni pubs** (sans droits admin, clés `HKCU`) :

| Clé (`HKCU:\Software\Microsoft\Windows\CurrentVersion\…`) | Valeur | Effet |
|---|---|---|
| `Search\BingSearchEnabled` | `0` | pas de Bing dans la recherche |
| `Search\CortanaConsent` | `0` | pas de Cortana |
| `SearchSettings\IsDynamicSearchBoxEnabled` | `0` | pas de contenu dynamique dans la zone de recherche |
| `SearchSettings\IsAADCloudSearchEnabled`, `IsMSACloudSearchEnabled` | `0` | pas de recherche cloud |
| `Search\SearchboxTaskbarMode` | `0` | pas de zone de recherche dans la barre des tâches |
| `AdvertisingInfo\Enabled` | `0` | pas d'identifiant publicitaire |
| `Privacy\TailoredExperiencesWithDiagnosticDataEnabled` | `0` | pas d'expériences personnalisées |
| `Explorer\Advanced\Start_IrisRecommendations`, `Start_AccountNotifications` | `0` | pas de recommandations dans Démarrer |
| `Explorer\Advanced\ShowSyncProviderNotifications` | `0` | pas de pubs OneDrive/Office dans l'Explorateur |
| `Explorer\Advanced\ShowTaskViewButton`, `ShowCopilotButton` | `0` | barre des tâches épurée |

Dans `ContentDeliveryManager`, mettre à `0` : `ContentDeliveryAllowed`,
`OemPreInstalledAppsEnabled`, `PreInstalledAppsEnabled`,
`PreInstalledAppsEverEnabled`, `SilentInstalledAppsEnabled`, `SoftLandingEnabled`,
`SystemPaneSuggestionsEnabled`, `RotatingLockScreenEnabled`,
`RotatingLockScreenOverlayEnabled`, `SubscribedContentEnabled`,
`FeatureManagementEnabled` et toutes les `SubscribedContent-*Enabled`.

**Télémétrie et suivi** (PowerShell **administrateur**, clés `HKLM:\SOFTWARE\Policies\Microsoft\…`, `DWord`) :

- `Windows\DataCollection` : `AllowTelemetry=0`, `DoNotShowFeedbackNotifications=1`, `AllowCommercialDataPipeline=0` ;
- `Windows\AppCompat` : `AITEnable=0`, `DisableInventory=1`, `DisablePCA=1` ;
- `SQMClient\Windows` : `CEIPEnable=0` ; `Windows\Windows Error Reporting` : `Disabled=1` ;
- `Windows\System` : `PublishUserActivities=0`, `EnableActivityFeed=0`, `UploadUserActivities=0` ;
- `Windows\AdvertisingInfo` : `DisabledByGroupPolicy=1` ;
- `Windows\Windows Search` : `DisableWebSearch=1`, `ConnectedSearchUseWeb=0`, `AllowCortana=0`, `AllowSearchToUseLocation=0` ;
- `Windows\Explorer` : `DisableSearchBoxSuggestions=1` ;
- `Windows\WindowsCopilot` : `TurnOffWindowsCopilot=1` ; `Windows\WindowsAI` : `DisableAIDataAnalysis=1` ;
- `Windows\CloudContent` : `DisableWindowsConsumerFeatures`, `DisableSoftLanding`, `DisableWindowsSpotlightFeatures`, `DisableTailoredExperiencesWithDiagnosticData` à `1` ;
- `OneDrive` : `DisableFileSyncNGSC=1` ; `Windows\GameDVR` : `AllowGameDVR=0`.

Services à désactiver : `DiagTrack` et `dmwappushservice`
(`Stop-Service` puis `Set-Service -StartupType Disabled`). Tâches planifiées à
désactiver (`schtasks /Change /TN … /Disable`) : *Microsoft Compatibility
Appraiser*, *ProgramDataUpdater*, *Consolidator*, *UsbCeip*, *DmClient*,
*DmClientOnScenarioDownload*. Redémarrer ensuite.

Limites : `Policies\Microsoft\Dsh\AllowNewsAndInterests` est protégée par Windows
même en administrateur (désactiver *Widgets* dans les paramètres de la barre des
tâches). Une grosse mise à jour de Windows peut remettre certains réglages :
rejouer alors ces commandes.

## À faire plus tard

À reprendre une fois ces outils stabilisés :

- [ ] **SpaceMouse over WAN — SpaceMouse Link** (bêta, Server sur le PC où la
  SpaceMouse est branchée, Client sur le poste qui exécute le logiciel 3D).
  <https://github.com/softyoda/apollo-desktop-kit/tree/HEAD/components/spacemouse> ·
  [releases](https://github.com/softyoda/apollo-desktop-kit/releases)
- [ ] **Bureau multi-écrans à distance — Apollo + Apollo Fleet Launcher + Moonlight**.
  <https://github.com/softyoda/apollo-desktop-kit> ·
  [guide hôte Windows](https://github.com/softyoda/apollo-desktop-kit/blob/HEAD/docs/windows-host.md) ·
  [Apollo](https://github.com/ClassicOldSong/Apollo) ·
  [Apollo Fleet Launcher](https://github.com/drajabr/Apollo-Fleet-Launcher)
- [ ] **Presse-papiers partagé — CrossPaste**.
  [guide](https://github.com/softyoda/apollo-desktop-kit/blob/HEAD/docs/clipboard.md) ·
  <https://github.com/CrossPaste/crosspaste-desktop>
- [ ] **Synchronisation de fichiers** entre les postes : outil à choisir.
- [ ] Prérequis réseau pour Apollo, CrossPaste et la synchro : accès VPN
  (à confirmer). SpaceMouse Link n'en a pas besoin. Voir le
  [guide réseau](https://github.com/softyoda/apollo-desktop-kit/blob/HEAD/docs/network.md).
