#sneaky

import pynput
import abc







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


  def __call__(self, controller):
    for char in self.chars:
      controller.press(char)
    for char in self.chars[::-1]:
      controller.release(char)


  def __iter__(self):
    return iter(self.chars)


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




class PressCharacterBlock(CharacterBlock):
  def __call__(self, controller):
    for char in self.chars:
      controller.press(char)




  
class ReleaseCharacterBlock(CharacterBlock):
  def __call__(self, controller):
    for char in self.chars:
      controller.release(char)




class CharacterBlockChain:
  def __init__(self, *blocks):
    self.blocks = list(blocks)


  def __call__(self, controller):
    for block in self.blocks:
      block(controller)
  

  
    


class QuickConstruct:
  '''holds the quick construct method to get value of keys'''
  @staticmethod
  def character(code):
    if code in pynput.keyboard.Key.__members__:
      return pynput.keyboard.Key[code]
    else:
      return pynput.keyboard.KeyCode.from_char(code)


  @staticmethod
  def character_block(code):
    return CharacterBlock(*[QuickConstruct.character(char) for char in code.split(' ')])


  @staticmethod
  def character_block_chain(code):
    return CharacterBlockChain(*[CharacterBlock(*[QuickConstruct.character(char) for char in chunk.split(' ')]) for chunk in code.split('/')])





class Controller(pynput.keyboard.Controller):
  def call(self, block):
    return block(self)
  


  

class Shortcut:
  def __init__(self, trigger, command):
    self.trigger = trigger
    self.command = command
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
    print(thing)
    self.keys_pressed.add(thing)
    for shortcut in self.shortcuts:
      if not shortcut.suspended:
        if shortcut.trigger.issubset(self.keys_pressed):
          shortcut.command(self.controller)
          shortcut.suspended = True


  def remove_pressed_thing(self, thing):
    self.keys_pressed.remove(thing)
    for shortcut in self.shortcuts:
      if shortcut.suspended:
        if thing in shortcut.trigger:
          shortcut.suspended = False
          



# Collect events until released
keys_pressed_monitor = KeysPressedMonitor(
  Shortcut(
    QuickConstruct.character_block('enter'),
    QuickConstruct.character_block_chain('alt tab/ctrl n/ctrl l/d/o/c/s/./g/o/o/g/l/e/./c/o/m'),
  )
)
keys_pressed_monitor.start()
