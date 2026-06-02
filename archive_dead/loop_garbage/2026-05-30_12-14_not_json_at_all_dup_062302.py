# Keyboard/Joystick Input Message (POST body)
# Each line = one field. Blank lines and lines starting with # are ignored.
# Required keys (order not important):
#   type   = keyboard|joystick
#   device = <uint64>   (U64 class identifier)
#   code   = <int>      (keycode or joystick button/axis)
#   value  = <int>      (0 for release, 1 for press, or axis position -32768..32767)
#
type=keyboard
device=1234567890123456
code=65
value=1
