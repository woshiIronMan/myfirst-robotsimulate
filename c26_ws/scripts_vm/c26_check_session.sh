#!/bin/bash
echo "--- sessions ---"
loginctl list-sessions --no-legend
for s in $(loginctl list-sessions --no-legend | awk '{print $1}'); do
  echo "session $s: $(loginctl show-session $s -p Type -p Name -p Seat -p TTY | tr '\n' ' ')"
done
echo "--- gdm config files ---"
ls -la /etc/gdm3/ /etc/gdm/ 2>/dev/null | head -20
echo "--- wayland enable grep ---"
grep -rn 'WaylandEnable' /etc/gdm3/ /etc/gdm/ 2>/dev/null
echo "--- udev wayland rules ---"
ls /usr/lib/udev/rules.d/61-gdm.rules /etc/udev/rules.d/61-gdm.rules 2>/dev/null
echo "--- gdm pkg ---"
dpkg -l | grep -iE '^ii\s+gdm' | awk '{print $2, $3}'
echo "--- session type per user env ---"
tr '\0' '\n' < /proc/$(pgrep -u xue -f gnome-shell | head -1)/environ 2>/dev/null | grep -E 'XDG_SESSION_TYPE|WAYLAND_DISPLAY|DISPLAY='
