#sneaky

from pynput.keyboard import Key, Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener


class CharacterCollection:
  def __init__(self, *characters):
    self.contents = set(characters)

  def __issubset__(self, other_set):
    return self.contents.__issubset__(other_set)

  def __issuperset__(self, other_set):
    return self.contents.__issuperset__(other_set)


  

class Command:
  def __init__(self, trigger:CharacterCollection, result):
    self.trigger = trigger
    self.result = result
    self.suspended = False



class Listenerer(KeyboardListener, MouseListener):
  def __init__(self, *commands, **listener_init_args):
    super(Listenerer, self).__init__(
      on_press=self.on_press,
      on_release=self.on_release,
      on_click=self.on_click,
      **listener_init_args
    )
    self.pressed = set()
    self.commands = list(commands)


  def add_pressed_thing(self, thing):
    print('pressed', thing, repr(thing), type(thing))
    self.pressed.add(thing)


  def remove_pressed_thing(self, thing):
    if thing not in self.pressed:
      return
    self.pressed.remove(thing)
    
    
  def on_press(self, key):
    self.add_pressed_thing(key)


  def on_release(self, key):
    self.remove_pressed_thing(key)


  def on_click(self, x, y, button, pressed):
    if pressed:
      self.add_pressed_thing(button)
    else:
      self.remove_pressed_thing(button)



# Collect events until released
listener = Listenerer(
  Command(CharacterCollection(),None),
)
listener.start()
