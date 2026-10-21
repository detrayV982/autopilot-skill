#!/bin/bash
# Restore script - TCL 40S350G Google TV
# Re-enables everything disabled during debloat, turns the system screensaver back on,
# removes the Projectivy accessibility setting, and restores the original launcher.
# Run: bash ~/tv-backup/restore.sh            (does the restore)
#      bash ~/tv-backup/restore.sh --dry-run  (prints what it would do, changes nothing)

TV="192.0.2.10:5555"
DRY_RUN=0
if [ "$1" = "--dry-run" ]; then
  DRY_RUN=1
fi

# Runs an adb shell command on the TV, or only prints it in dry-run mode.
run_on_tv() {
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [dry-run] adb -s $TV shell $*"
    return 0
  fi
  adb -s "$TV" shell "$@" 2>&1
}

if [ "$DRY_RUN" -eq 1 ]; then
  echo "DRY RUN: nothing will be changed on the TV."
else
  echo "Connecting to TV..."
  adb connect "$TV"
  if ! adb -s "$TV" shell echo ok 2>/dev/null | grep -q ok; then
    echo "ERROR: Cannot reach TV at $TV. Make sure it's on and ADB debugging is enabled."
    exit 1
  fi
fi

# These are the packages that are disabled on the TV right now.
# (com.tcl.smartalexa, com.tcl.usercenter, com.tcl.autopair were disabled once but are enabled again.)
PACKAGES=(
  # Batch 1 - unused streaming apps
  "com.google.android.youtube.tvmusic"
  "com.google.android.youtube.tvunplugged"
  "com.google.android.videos"
  "com.google.android.play.games"
  "com.nbaimd.gametime.nba2011"
  "com.bamnetworks.mobile.android.gameday.atbat"
  "com.tubitv"
  "com.fubo.firetv.screen"
  "com.discovery.discoveryplus.androidtv"
  "com.spotify.tv.android"
  # Batch 2 - TCL bloatware and setup junk
  "com.tcl.esticker"
  "com.tcl.tv.plus"
  "com.tcl.channelplus"
  "com.tcl.messagebox"
  "com.tcl.copydatatotv"
  "com.tcl.useragreement"
  "com.tcl.factory.view"
  "com.tcl.initsetup"
  "com.android.printspooler"
  "com.android.providers.calendar"
  "com.google.android.syncadapters.calendar"
  "com.google.android.tungsten.setupwraith"
  "com.google.android.onetimeinitializer"
  # Batch 3 - remaining TCL bloat and unused Google services
  "com.tcl.t_solo"
  "com.tcl.ui_mediaCenter"
  "com.tcl.suspension"
  "com.tcl.tv.tclchannel"
  "com.tcl.partnercustomizer"
  "com.tcl.common.shortcutmenu"
  "com.android.backupconfirm"
  "com.android.soundpicker"
  "com.android.htmlviewer"
  "com.google.android.apps.nbu.smartconnect.tv"
  # Google TV ambient-mode screensaver (disabled so it stops covering Projectivy)
  "com.google.android.apps.tv.dreamx"
  # Launcher swap
  "com.google.android.apps.tv.launcherx"
)

echo "Re-enabling ${#PACKAGES[@]} packages..."
for pkg in "${PACKAGES[@]}"; do
  result=$(run_on_tv pm enable --user 0 "$pkg")
  echo "  $pkg: $result"
done

echo ""
echo "Turning the system screensaver back on..."
run_on_tv settings put secure screensaver_enabled 1

echo ""
echo "Clearing the Projectivy accessibility service setting..."
run_on_tv settings delete secure enabled_accessibility_services
run_on_tv settings put secure accessibility_enabled 0

echo ""
echo "Restoring original launcher..."
run_on_tv cmd package set-home-activity com.google.android.apps.tv.launcherx/.home.HomeActivity
echo "  Done."

echo ""
if [ "$DRY_RUN" -eq 1 ]; then
  echo "Dry run finished. No changes were made."
else
  echo "Reboot the TV to confirm everything is back to normal."
fi
