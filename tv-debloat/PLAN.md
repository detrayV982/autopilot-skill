# TV project plan

Re-read this file after every compaction. It is the source of truth for this task.

## Where things stand (about 8 PM, Oct 20)

- TV: TCL 40S350G, Google TV, Android 11, ADB at 192.0.2.10:5555.
- 36 apps are disabled in 3 batches, plus the stock launcher (com.google.android.apps.tv.launcherx). All 37 are in change_log.txt, and restore.sh re-enables the same 37 (checked: the lists match exactly).
- Projectivy Launcher is installed, Premium is unlocked, and it's the default home screen. It came back on its own after the reboot test at 5:43 PM. HDMI 1 and HDMI 2 show on its home screen.
- Projectivy's wallpaper Uri is file:///sdcard/Download/wallpaper_japan.mp4 and the Video toggle is on, but the home screen shows a still frame instead of a moving video (it showed the red city earlier and the Japanese village now).
- Both videos should play fine on this TV: H.264 High 4.1, 1920x1080, 30 fps, about 9 Mbps, no audio track. wallpaper_japan.mp4 is 30 seconds (34725503 bytes). wallpaper_tv.mp4 is 60 seconds.
- change_log.txt stops at the reboot test. Nothing after 5:43 PM was logged.

All the work above is already done, except getting the video to play (that's step 2). Don't redo any of it: no new backup, no interview, no re-disabling packages, no reinstalling or re-buying Projectivy, no re-pushing or re-encoding the videos unless step 2 says to. Change something that's already done only if a test in step 4 shows it's broken, and log why. Running a test again (like the reboot in step 4) is fine; that's checking, not redoing.

## How to work

- I'm away from the computer. Work through every step below without stopping to ask me anything, and don't use AskUserQuestion. When there's a choice, pick the option that's reversible and closest to what I asked for, write the choice and the reason in change_log.txt, and keep going.
- Treat this as production. Nothing counts as done until you've tested it. If a test fails, fix it and test again. If something still fails after 3 real attempts, undo that change, write down what happened, and move on to the next step.
- Stop and wait for me only if the TV stays unreachable over ADB for 10 minutes (retry `adb connect` every minute), a step would cost money, or a step would need uninstalling an app, clearing app data, or a factory reset. Never do those three things.
- Log every change in change_log.txt with a timestamp, the command, and the result.
- Don't delete anything in ~/tv-backup.
- Never force-stop Projectivy (`am force-stop`). It crashes Projectivy's accessibility service, Android turns the service off, and only a reboot clears that. To restart Projectivy, reboot the TV, then check `settings get secure enabled_accessibility_services` still lists Projectivy's service and turn it back on if it doesn't.

## Screenshots (this is what crashed the last session)

- TV screenshots are already 1280x720, so `sips -Z 1280` did nothing and every _small.png is an identical 1 to 1.5 MB PNG. Don't make any more _small.png files.
- Before viewing a screenshot, convert it: `sips -s format jpeg -s formatOptions 50 -Z 960 in.png --out in.jpg`. Check it's under 200 KB with `ls -l`, and view only the JPEG.
- Use text checks first (dumpsys, logcat, ls, pm). Look at a screenshot only when text can't answer the question.
- A screenshot can't show motion. To check whether the video is playing, take two screencaps 3 seconds apart with no input in between and compare them with `md5 -q` without viewing them. Different hashes mean something on screen is moving. Some TVs don't capture video layers in screencap, so if the hashes match, also check logcat for a video decoder (video/avc) running for Projectivy before deciding it isn't playing.

## Steps

### 1. Catch up the log

Add everything done after 5:43 PM to change_log.txt, based on what's on the TV now: Projectivy's package name and version, the files in /sdcard/Download with sizes, the wallpaper settings, and anything else that changed. Diff `pm list packages -d` against the log. If they don't match, record the difference and fix restore.sh to match what's actually disabled.

### 2. Get the video background moving (DONE at 8:44 PM, don't redo)

Solved: Projectivy only plays video while its accessibility service is enabled and bound. The original /sdcard/Download/wallpaper_japan.mp4, picked through Projectivy's "Pick image/video", is moving. The safe, 720, and webp versions weren't needed. The details are in change_log.txt. Only come back to this step if a later test shows the video stopped. The notes below are kept for reference.


Projectivy now shows a still frame of the Japanese village, so it can read the file. The problem is playback, not file access. Granting permissions, retyping the Uri, the file picker, and the share intent have all been tried without the video moving, so don't repeat them. Work through this in order and stop at the first thing that moves. Spend no more than about 45 minutes on this step in total.

a. Find out why it isn't playing. Make sure Projectivy's accessibility service is enabled and bound, clear logcat, press Home, wait 15 seconds, then save logcat lines for Projectivy's PID plus anything mentioning MediaCodec, ExoPlayer, OMX, c2., video/avc, Surface, or errors to ~/tv-backup/video_debug.txt. Also check `getprop ro.config.low_ram`, the three animation scales (`settings get global animator_duration_scale`, `transition_animation_scale`, `window_animation_scale`), and every Projectivy setting that mentions video, animation, idle, performance, or power saving. Write what you find in change_log.txt.

b. If (a) points at something, fix it (for example an animation scale set to 0, or a Projectivy setting that pauses or disables video) and check again.

c. Test with a known-good clip to tell "this file" apart from "this TV". These files are already made and checked in ~/tv-backup, so don't re-encode anything:
   - test_motion.mp4: 10-second 1280x720 test pattern with a running counter, H.264 Main 4.0, no B-frames, no audio. The md5 motion check is reliable for it.
   - wallpaper_japan_safe.mp4: the village at 1920x1080, H.264 Main 4.0, no B-frames, about 4 Mbps, no audio, 30 seconds.
   - wallpaper_japan_safe_720.mp4: the same at 1280x720, about 2.5 Mbps.
   - wallpaper_japan_720.webp: animated WebP of the first 10 seconds, 1280x720, 15 fps, loops forever.
   - wallpaper_japan_still.jpg: a 1920x1080 still frame of the village.

   Push test_motion.mp4 to /sdcard/Download/ and point Projectivy at it.
   - If the test clip moves, the original village file is the problem. Push wallpaper_japan_safe.mp4, point Projectivy at it, and check. If that won't move, try wallpaper_japan_safe_720.mp4.
   - If the test clip doesn't move either, the TV or Projectivy is blocking video. Projectivy also supports animated images, so push wallpaper_japan_720.webp and point Projectivy at it. If it moves but navigation lags badly (step 4 has the frame-drop check), drop it.

d. If nothing moves after all that, push wallpaper_japan_still.jpg and set it as the wallpaper with the Video toggle off, so the home screen looks right. Put exactly what you tried and what logcat showed in the report, then move on to step 3.

Whichever option works, point Projectivy back at the final file (not the test clip), confirm it's still moving after a reboot and after opening and leaving an app, and log the final file name and settings. If a system chooser dialog is left open on the TV at any point, close it.

### 3. Put the apps in my order

APP ORDER (left to right):

1. YouTube
2. Hulu
3. Netflix
4. HBO Max
5. Crunchyroll
6. Prime Video
7. Paramount+
8. Apple TV
9. Peacock
10. Disney+
11. BrowseHere

Any other apps (Twitch, Play Store, and so on) go after BrowseHere in any order. Don't hide anything.

Set the app row to exactly that order using Projectivy's own move option. Don't change other Projectivy settings. Check the final order with one screenshot, and check it again after the reboot test in step 4.

### 4. Test everything

Drive the TV with adb keyevents. Check what's on screen with `dumpsys activity activities` (look at the resumed activity) instead of screenshots wherever you can. Streaming apps can screenshot black because of DRM, which is normal.

- Open every app in the row, then come back home, once with Home and once with Back. Record pass or fail for each app.
- Switch to HDMI 1 and HDMI 2 from the launcher, and back. The screen may be black if nothing is plugged in, so check the resumed activity.
- Simulate remote buttons that have a keycode (KEYCODE_SETTINGS, KEYCODE_TV_INPUT, KEYCODE_SEARCH or KEYCODE_ASSIST). If one is broken because of something we disabled (com.tcl.common.shortcutmenu is a likely suspect for the settings button), re-enable that package, retest, and log it. List the physical buttons you can't simulate (Netflix, YouTube, and so on) in the report under "Vaughn to check by hand", with what should happen.
- Find out what com.tcl.autopair does from its manifest (dumpsys package). If it handles pairing the remote and doesn't show ads or popups, re-enable it and log why.
- Performance with the video on:
  - Frame drops: `dumpsys gfxinfo <projectivy pkg> reset`, scroll the home screen with the D-pad for 30 seconds, then read the janky frame percentage.
  - Memory: `dumpsys meminfo <projectivy pkg>` now, and again after 15 minutes that include a few app switches. Flag it if memory grows more than 30%.
  - Wake locks: with the home screen idle, check `dumpsys power` and confirm Projectivy holds no wake lock.
  - Screensaver: it was turned off earlier (screensaver_enabled=0 and com.google.android.apps.tv.dreamx disabled) because it covered the launcher. Leave it off, skip this test, and list it in the report under changes I should know about.
- Reboot with `adb reboot`, reconnect, and confirm Projectivy comes up on its own, the video is moving, and the app order held. Before touching anything after the reboot, check whether Projectivy's accessibility service is still enabled and bound on its own. If a normal reboot turns it off, the video will stop every time the TV restarts. Find a lasting fix if there is one, test it with a second reboot, and if there isn't one, put it at the top of the report with the exact steps to turn it back on.
- With the video playing, also check that the accessibility service is still bound after the 15-minute memory test. This TV reports ro.config.low_ram=true, so Android may kill it under memory pressure.

### 5. Check restore.sh

- Add a --dry-run option that prints what it would do without changing anything, and run it.
- Make sure it matches whatever is disabled now, including dreamx and any changes from step 4, and that it sets screensaver_enabled back to 1.
- Test the real enable path on one harmless package (com.android.htmlviewer): enable it, confirm it's enabled, disable it again, confirm, and log both steps.
- Don't run the full restore.

### 6. Clean up

Stop any background shells you started that are still running. Confirm nothing on the TV depends on this Mac (no http:// wallpaper URIs, nothing streamed from here).

### 7. Report

Write ~/tv-backup/REPORT.md with:

- What changed since 5:43 PM.
- A table of every test from step 4: the test, pass or fail, and the numbers.
- "Vaughn to check by hand": anything you couldn't test yourself, with what should happen.
- Anything still broken, and what you tried.
- Where the backup, log, and restore script are, and how to run the restore.
- What a TV software update might undo, and how to redo it.

Then post a short summary in the chat.
