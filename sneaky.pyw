#sneaky

import pynput
import abc




class Controller(pynput.keyboard.Controller):
  def call(self, block):
    return block(self)



class Block(abc.ABC):
  '''A group of characters'''

  @abc.abstractmethod
  def __init__(self):
    '''creates a new group of characters'''


  @abc.abstractmethod
  def __call__(self):
    '''uses pynput to simulate the keypresses that this class represents'''





class CharacterBlock(Block):
  def __init__(self, *chars):
    self.chars = list(chars)


  def __call__(self, controller:Controller):
    for char in self.chars:
      controller.press(char)
    for char in self.chars[::-1]:
      controller.release(char)


  def __iter__(self):
    return iter(self.contents)


  def __str__(self):
    return f'CharacterBlock({self.chars})'


  def add(self, character):
    if character not in self.chars:
      self.chars.append(character)


  def remove(self, character):
    while character in self.chars:
      self.chars.remove(character)
  

  def issubset(self, other):
    return set(self).issubset(set(other))
  

  def issuperset(self, other):
    return set(self).issuperset(set(other))

  

  
    


class QuickConstruct:
  '''holds the quick construct method to get value of keys'''
  @staticmethod
  def character(code):
    if code in pynput.keyboard.Key.__members__:
      return pynput.keyboard.Key[code]
    else:
      return pynput.keyboard.KeyCode.from_char(code)

    


class CharacterCollection:
  def __init__(self, *characters):
    self.contents = set(characters)


  @staticmethod
  def quick_construct(*codes):
    return CharacterCollection(*[Key.quick_construct(code) for code in codes])
  


  

class Shortcut:
  def __init__(self, trigger:CharacterCollection, result):
    self.trigger = trigger
    self.result = result
    self.suspended = False




class KeyboardListener(pynput.keyboard.Listener):
  def __init__(self, target, **listener_init_args):
    super().__init__(
      on_press=self.on_press,
      on_release=self.on_release,
      **listener_init_args,
    )
    self.target = target
    
    
  def on_press(self, key):
    print(key == pynput.keyboard.KeyCode.from_char('space'))
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
  def __init__(self, *shortcuts:Shortcut):
    self.keys_pressed = CharacterBlock()
    self.shortcuts = list(shortcuts)
    self.controller = Controller()


  def start(self):
    KeyboardListener(self).start()
    MouseListener(self).start()


  def add_pressed_thing(self, thing):
    self.keys_pressed.add(thing)
    print(self.keys_pressed)


  def remove_pressed_thing(self, thing):
    self.keys_pressed.remove(thing)



# Collect events until released
keys_pressed_monitor = KeysPressedMonitor(
  Shortcut(
    CharacterBlock(),
    None
  )
)
keys_pressed_monitor.start()
