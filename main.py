#sneaky

import monitor


with monitor.Monitor.from_file('demo.pog') as monitor:
  while monitor.running:
    'vibe in the background'
