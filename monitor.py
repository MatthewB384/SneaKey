#sneaky

import pynput

import block


class KeyboardController(pynput.keyboard.Controller):
  pass


class MouseController(pynput.keyboard.Controller):
  pass


class KeyboardListener(pynput.keyboard.Listener):
  def __init__(self, target, **listener_init_args):
    super().__init__(
      on_press=self.on_press,
      on_release=self.on_release,
      **listener_init_args,
    )
    self.target = target
    
    
  def on_press(self, key):
    self.target.add_pressed_thing(key)


  def on_release(self, key):
    self.target.remove_pressed_thing(key)


class MouseListener(pynput.mouse.Listener):
  def __init__(self, target, **listener_init_args):
    super().__init__(
      on_click=self.on_click,
      **listener_init_args,
    )
    self.target = target


  def on_click(self, x, y, button, pressed):
    if pressed:
      self.target.add_pressed_thing(button)
    else:
      self.target.remove_pressed_thing(button)


class KeysPressedMonitor:
  def __init__(self, *shortcuts):
    self.shortcut_collection = block.ShortcutCollection(*shortcuts)
    self.keys_pressed = block.CharacterCollection()
    self.keyboard_controller = KeyboardController()
    self.mouse_controller = MouseController()
    self.keyboard_listener = KeyboardListener(self)
    self.mouse_listener = MouseListener(self)


  def start(self):
    self.keyboard_listener.start()
    self.mouse_listener.start()


  def stop(self):
    self.keyboard_listener.stop()
    self.mouse_listener.stop()


  def get_shortcuts(self, suspended=None, triggered=None, contains=[], not_contains=[]):
    if triggered is None:
      triggered_by = {}
    else:
      triggered_by = {self.keys_pressed:triggered}
    return self.shortcut_collection.get_shortcuts(
      suspended=suspended, triggered_by=triggered_by, contains=contains, not_contains=not_contains
    )


  def add_pressed_thing(self, thing):
    self.keys_pressed.add(thing)


  def remove_pressed_thing(self, thing):
    triggered = self.get_shortcuts(triggered=True)
    executable = triggered.get_shortcuts(suspended=False, contains=[thing])
    
    if executable:
      max(executable)(self)
      for shortcut in triggered:
        shortcut.suspended = True
          
    self.keys_pressed.remove(thing)
    
    for shortcut in self.get_shortcuts(suspended=True, triggered=False):
      shortcut.suspended = False
          
