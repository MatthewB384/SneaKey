#sneaky

import pynput.keyboard

import block


class KeyboardController(pynput.keyboard.Controller):
  def __init__(self):
    super().__init__()
    self.keys_pressed = block.CharacterCollection()

    
  def tap(self, key):
    self.keys_pressed.add(key)
    super().tap(key)
    self.keys_pressed.remove(key)


  def press(self, key):
    self.keys_pressed.add(key)
    super().press(key)


  def release(self, key):
    self.keys_pressed.remove(key)
    super().release(key)


  def release_all(self):
    for key in self.keys_pressed.copy():
      self.release(key)
  

class KeyboardListener(pynput.keyboard.Listener):
  def __init__(self, target, **listener_init_args):
    super().__init__(
      on_press=self.on_press,
      on_release=self.on_release,
      **listener_init_args,
    )
    self.target = target
    
    
  def on_press(self, key):
    self.target.press_key(key)


  def on_release(self, key):
    self.target.unpress_key(key)


class Monitor:
  def __init__(self, *shortcuts):
    self.shortcut_collection = block.ShortcutCollection(*shortcuts)
    self.keys_pressed = block.CharacterCollection()
    self.keyboard_controller = KeyboardController()
    self.keyboard_listener = KeyboardListener(self)
    self.running = False


  def __enter__(self):
    self.start()
    return self
    


  def __exit__(self, exc_type, exc_val, exc_tb):
    self.keyboard_controller.release_all()
    self.stop()


  def start(self):
    self.keyboard_listener.start()
    self.running = True


  def stop(self):
    self.keyboard_listener.stop()
    self.running = False


  def get_shortcuts(self, suspended=None, triggered=None, contains=[], not_contains=[]):
    triggered_by = {} if triggered is None else {self.keys_pressed:triggered}
    return self.shortcut_collection.get_shortcuts(
      suspended=suspended, triggered_by=triggered_by, contains=contains, not_contains=not_contains
    )


  def press_key(self, thing):
    self.keys_pressed.add(thing)


  def unpress_key(self, thing):
    triggered = self.get_shortcuts(triggered=True)
    
    executable = triggered.get_shortcuts(suspended=False, contains=[thing])
    if executable:
      max(executable)(self)
      for shortcut in triggered:
        shortcut.suspended = True
          
    self.keys_pressed.remove(thing)
    
    for shortcut in self.get_shortcuts(suspended=True, triggered=False):
      shortcut.suspended = False


  @classmethod
  def from_string(cls, code):
    return cls(*block.ShortcutCollection.from_string(code))


  @classmethod
  def from_file(cls, file_name):
    with open(file_name) as file:
      return cls.from_string(file.read())
