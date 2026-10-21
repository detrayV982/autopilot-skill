# TV project report (TCL 40S350G, Google TV, Android 11)

Run: Oct 20, about 8:22 PM to 10:10 PM. TV at 192.0.2.10:5555. Full details are in `change_log.txt`.

## Read this first

1. **Projectivy's accessibility service is not bound after a reboot.** After a normal `adb reboot` the service is still in `enabled_accessibility_services`, but Android resets `accessibility_enabled` to 0, so the service is not running. I found no lasting fix that is inside what I was approved to do.
   - **The video wallpaper still played after the reboot.** I changed nothing after the reboot and checked first. The video was moving, and the ExoPlayer wake lock was cycling with the 30-second loop. The reason is that Projectivy's file picker copied the video into its own storage (`file:///data/user/0/com.spocky.projengmenu/files/background`) and saved the Video setting. Playback does not need the service once that is saved.
   - **What the service does need:** it has to be bound while you change the Video toggle or pick a new wallpaper. Otherwise the toggle flips back to OFF. This is what broke the earlier attempts.
   - **To bind it again** from the Mac (about 10 seconds):
     ```
     adb connect 192.0.2.10:5555
     SVC=com.spocky.projengmenu/com.spocky.projengmenu.services.ProjectivyAccessibilityService
     adb shell settings delete secure enabled_accessibility_services
     adb shell settings put secure accessibility_enabled 0
     sleep 3
     adb shell settings put secure enabled_accessibility_services $SVC
     adb shell settings put secure accessibility_enabled 1
     ```
     Check with `adb shell dumpsys accessibility | grep "Bound services"`. Without the delete-then-put cycle, setting only `accessibility_enabled 1` did not bind it.
   - **Possible lasting fix (not done):** `adb shell pm grant com.spocky.projengmenu android.permission.WRITE_SECURE_SETTINGS` would let Projectivy re-enable its own service. It was not on my approved list, so I did not run it. Undo with `pm revoke`.
   - **Never run `am force-stop com.spocky.projengmenu`.** It crashes the service, and only a reboot clears that.
2. **Projectivy holds a wake lock while the video plays** (`ExoPlayer:WakeLockManager`, partial). That fails the "no wake lock" check. I did not test standby, so check by hand that the TV sleeps and wakes normally.
3. **The screensaver is off on purpose.** `settings put secure screensaver_enabled 0` and `com.google.android.apps.tv.dreamx` is disabled. The Google TV ambient screen was covering Projectivy. `restore.sh` turns both back on.

## What changed since 5:43 PM

- **Video wallpaper now plays.** Root cause: the accessibility service was not bound when the Video setting was saved, and I had also force-stopped Projectivy, which crashed the service. I rebooted, re-bound it, and picked `wallpaper_japan.mp4` through "Pick image/video". The test clip `test_motion.mp4` confirmed the TV and Projectivy can play video. I did not need the safe, 720 or WebP versions.
- **App row reordered** with long-press > Reorder. The dock shows: YouTube, Hulu, Netflix, HBO Max, Crunchyroll, Prime Video, Paramount+, Apple TV, Peacock, Disney+, BrowseHere, then Safety Guard, TCL Home, TV, Twitch, Works with Alexa, Play Store. The order was checked again after the reboot.
- **Play Store turned back on** in TV Apps > Manage apps (it had been toggled off earlier) and moved to the end of the row. The plan says to hide nothing.
- **`com.tcl.autopair` re-enabled.** It has no UI, only boot and START_AUTOPAIR/START_SILENTPAIR receivers plus Bluetooth permissions, so it handles remote pairing. No ads or popups.
- **`com.tcl.common.shortcutmenu`:** I enabled it to test the TV_INPUT and ASSIST keys, saw no change, and disabled it again.
- **`restore.sh` rewritten** with `--dry-run`. It now lists the 35 packages disabled today (matches `pm list packages -d` exactly), adds dreamx, drops autopair, smartalexa and usercenter (all enabled now), sets `screensaver_enabled` back to 1, and clears the accessibility setting.
- The log had been missing `dreamx`, the screensaver setting and the accessibility setting. They are now written down.
- Files on the TV: `/sdcard/Download/wallpaper_japan.mp4` (34,725,503 bytes), `wallpaper_tv.mp4` (69,689,056), `test_motion.mp4` (189,441).

## Step 4 test results

| Test | Result | Numbers / notes |
|---|---|---|
| YouTube, Hulu, Netflix, HBO Max, Crunchyroll, Prime Video, Paramount+, Apple TV, Peacock, Disney+, BrowseHere: open from the row, return with Home | PASS (11 of 11) | Each opened its own app (resumed activity checked) and Home returned to Projectivy |
| Same apps, return with Back | PARTIAL | YouTube, Paramount+ and Disney+ returned with 1 Back; Apple TV with 2. Hulu, Netflix, HBO Max, Crunchyroll, Prime Video, Peacock and BrowseHere stayed in the app after 2 Backs. That is app behavior on login, profile or exit screens. Home always worked |
| HDMI 1 from launcher | PASS | Opens `com.tcl.tv/.TVActivity`; Home returns |
| HDMI 2 from launcher | PASS | Same; Back stays in TVActivity, Home returns |
| KEYCODE_SETTINGS | PASS | Opens Android TV Settings |
| KEYCODE_SEARCH | PASS | Opens Google search |
| KEYCODE_TV_INPUT, KEYCODE_ASSIST, KEYCODE_GUIDE, KEYCODE_TV | NO ACTION | Stays on Projectivy. Re-enabling shortcutmenu changed nothing, so it is not from our changes. Not known to be broken, see "by hand" |
| Frame drops (30 s of D-pad scrolling, video on) | PASS | 4,151 frames, 369 janky (8.89%), 50th 10 ms, 90th 13 ms, 95th 24 ms, 99th 30 ms. No re-encode needed |
| Memory, 15 minutes with 6 app switches | PASS | Projectivy PSS 99,926 KB to 115,676 KB (+15.8%, limit 30%). Free RAM stayed 355 MB or more |
| Accessibility service during the 15 minutes | PASS | Bound at all 7 samples |
| Wake lock with video on | FAIL | `ExoPlayer:WakeLockManager` partial wake lock held by Projectivy while the video plays |
| Screensaver | SKIPPED | Off on purpose, as the plan says |
| Reboot: Projectivy comes up on its own | PASS | Resumed activity was Projectivy's home |
| Reboot: video moving | PASS | Clean-crop md5 differed on every capture; codec registered; wake lock cycling each loop |
| Reboot: app order held | PASS | All 17 items in order |
| Reboot: accessibility service bound on its own | FAIL | `accessibility_enabled` reset to 0. See "Read this first" |

## Vaughn to check by hand

- **Physical remote buttons** with no keycode I could send (Netflix, YouTube, and similar app buttons): they should open that app.
- **Source/input button, mic or Assistant button, Guide button:** their keycodes did nothing on Projectivy's home. If a physical button should open the input list or Assistant and doesn't, tell me which one.
- **Standby:** turn the TV off and on with the remote. It should wake to Projectivy with the video playing and the app order unchanged.
- **Bluetooth pairing:** pair a new device in Android settings. autopair is back on and Settings is untouched.
- **HDMI with a real device plugged in:** the picture should show and Home should return to Projectivy.
- **Wallpaper changes:** editing the file in `/sdcard/Download` will not update the wallpaper. Pick the new file again in Projectivy (Settings > Appearance > Wallpaper > Configure > Pick image/video).

## Still broken or unsolved

- Accessibility service not bound after every reboot (details above). Video is not affected.
- Partial wake lock while the video plays.
- TV_INPUT, ASSIST, GUIDE and TV keys do nothing on the Projectivy home screen (cause unknown).
- Back does not leave most streaming apps from their first screen.

## Where things are

- Backup, log and restore script: `~/tv-backup/` (`change_log.txt`, `restore.sh`, `restore_dryrun.txt`, `packages_all.txt`, `default_launcher.txt`, `video_debug.txt`, the videos, test clips and screenshots).
- To restore the original setup: `bash ~/tv-backup/restore.sh --dry-run` to preview, then `bash ~/tv-backup/restore.sh`, then reboot the TV. Nothing is uninstalled, so the original launcher comes back.
- I tested the real enable and disable path on `com.android.htmlviewer` (enable, confirm, disable, confirm). I did not run the full restore.

## What a TV software update might undo

- It may re-enable the disabled packages, including the stock launcher and `dreamx`, and bring back the ambient screen and the stock home screen.
- It may reset the default home app or the accessibility settings.
- **To redo:** run the `pm disable-user --user 0` commands for the packages in `restore.sh`, set `settings put secure screensaver_enabled 0`, set Projectivy as home again, and re-bind the accessibility service with the commands above.

## Settings shortcut

**Result: partly done. There is no one-press Settings icon, but Pair accessory is 16 D-pad presses from the gear.** I changed no Projectivy setting and no package state.

- **What the top-right icons open now** (resumed activity checked): Wi-Fi opens `com.android.tv.settings/.connectivity.NetworkActivity`. The notifications icon opens Projectivy's own notifications side panel. The gear opens Projectivy's Settings side panel (`SettingsActivity`), which has an "Android settings" entry that opens `com.android.tv.settings/.MainSettings`.
- **TCL panels:** `com.tcl.dashboard` is the TCL Home smart-home app, not a settings panel. `com.tcl.settings` is still installed. Its `com.tcl.settings.action.QUICKSETTINGS` shows no panel, and `com.tcl.settings.action.BT_PAIR` opens a bare `BluetoothPairActivity`. I did not wire either into Projectivy.
- **Projectivy has no setting for what the gear opens.** Appearance > Status Bar > Icons only shows or hides the icons. The stock-launcher-style direct jump is therefore not possible. I did not re-enable the stock launcher.
- **Pairing path, tested:** gear > Enter (1), Down x4 to "Android settings" (4), Enter (1), Down x7 to Remotes & Accessories (7), Right (1), Down to "Pair accessory" (1), Enter (1). **That is 16 presses to the pairing prompt**, and 18 to start the scan (Right to OK, Enter). This build calls it "Pair accessory", not "Pair remote or accessory". I stopped at the prompt and cancelled it.
- **Shorter ways:** `KEYCODE_SETTINGS` (the remote's settings button, if it has one) opens Android TV Settings directly. The Wi-Fi icon is 3 or fewer presses from the gear to Network settings but does not reach Bluetooth.
- **WRITE_SECURE_SETTINGS grant failed:** `pm grant` returned `SecurityException: Package com.spocky.projengmenu has not requested permission android.permission.WRITE_SECURE_SETTINGS`. Projectivy does not declare it, so it can't be granted and can't help. Nothing was granted, so nothing to revoke. After a reboot, `accessibility_enabled` was still 0 and no service was bound, the same as before. The video was still moving (screencap hashes differed, wake lock held). The re-bind commands in "Read this first" are still the only fix.
- **restore.sh:** no package changed state, so it is unchanged. `--dry-run` was rerun and finished with no changes.

## Remote buttons

**Result: not fixed. The YouTube, Netflix, Prime Video and Apple TV buttons are handled only by the stock launcher, which stays disabled. No package state changed in the end.**

| Button | Scan code | Raw key | Keycode | What the system does | Handler | Result |
|---|---|---|---|---|---|---|
| YouTube | 0xc0057 | KEY_DISPLAY_OFF | 4065 | `startYouTube` broadcasts `com.google.global_button.ACTION_LAUNCH_APP` | `launcherx/.globalbutton.GlobalButtonLaunch_Receiver` (disabled) | FAIL |
| Netflix | 0xc0051 | KEY_VIDEO_PREV | 4062 | `startNetflix`, same broadcast | same | FAIL |
| Prime Video | 0xc005f | KEY_PRIMEVIDEO | 4099 | `startPrimeVideo`, same broadcast | same | FAIL |
| Apple TV | 0xc0086 | KEY_APPLETV | 4160 | `startAppleTV`, same broadcast | same | FAIL |
| Settings | 0xc0055 | KEY_FORWARDMAIL | 4077 | Only a usage-stats broadcast. No launch call | none found | FAIL |

- **Why:** the remote (`BT_RC813_M1`) sends TCL private keycodes. `TclPhoneWindowManager` (in `/system_ext/framework/tcl-service.jar`) turns the four app keys into an explicit broadcast to the stock launcher's receiver. With `com.google.android.apps.tv.launcherx` disabled, nothing receives it. `dumpsys window policy` has one global key mapping (GUIDE to the launcher), no GLOBAL_BUTTON handlers for these keys, and the key layout is the stock Generic.kl.
- **Tested:** enabled `com.tcl.common.shortcutmenu` and rebooted, then `com.tcl.partnercustomizer` and rebooted. Injected 4065, 4062, 4099, 4160 and 4077 each time. Nothing happened either time. Both are disabled again, and the disabled list matches what it was before this task. `restore.sh` is unchanged and `--dry-run` was rerun.
- **Injected keys match the real ones:** the log shows the same handler path for an injected key and a real press, so I expect no difference when you press the real buttons.
- **Settings button (4077):** the system doesn't act on it at all, and I found no package that does. `KEYCODE_SETTINGS` (176) still opens Settings when injected, but this remote doesn't send it.
- **Only fix:** re-enable `com.google.android.apps.tv.launcherx`. I didn't, as instructed. Re-enabling it can bring back the stock home screen and the ambient screen, and the TV may need Projectivy set as home again. Nothing I found can stand in for it. The broadcast is addressed to that receiver by name, so another app can't pick it up, and an accessibility remapper is ruled out because of the reboot reset.
- **Best alternative:** open the apps from Projectivy's row. YouTube, Netflix, Prime Video and Apple TV are all in the first 8 slots. For Settings, use the gear > "Android settings", 16 presses to Pair accessory as noted above.
- **Left for you to check by hand:** press the real Settings button once. If it opens Settings after all, tell me.
