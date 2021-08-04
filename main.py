#sneaky

import monitor
import block


keys_pressed_monitor = monitor.KeysPressedMonitor(
  block.Shortcut.from_string('left','<alt tab>'),
  block.Shortcut.from_string('right','<command quit>'),
)

keys_pressed_monitor.start()


while 1:
  'vibe in the background'
