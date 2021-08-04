import abc
import time

import pynput


class Character(pynput.keyboard._win32.KeyCode):
  keys = {
    '\n': pynput.keyboard.Key.enter,
    'rcmd': pynput.keyboard.Key.cmd_r,
    'lcmd': pynput.keyboard.Key.cmd_l,
    'rctrl': pynput.keyboard.Key.ctrl_r,
    'lctrl': pynput.keyboard.Key.ctrl_l,
    'ralt': pynput.keyboard.Key.alt_r,
    'lalt': pynput.keyboard.Key.alt_l,
    'ctrlalt': pynput.keyboard.Key.alt_gr,
    'rshift': pynput.keyboard.Key.shift_r,
  }


  @classmethod
  def from_string(cls, code:str=''):
    if code in cls.keys:
      return cls.keys[code]
    elif code in pynput.keyboard.Key.__members__:
      return pynput.keyboard.Key[code]
    else:
      return pynput.keyboard.KeyCode.from_char(code)
  

class Block(abc.ABC):
  'An entity that can be placed in a chain and called when necessary'

  @abc.abstractmethod
  def __init__(self):
    '''creates a new group of characters'''


  @abc.abstractmethod
  def __call__(self, controller):
    '''uses pynput to simulate the keypresses that this class represents'''


  @classmethod
  @abc.abstractmethod
  def from_string(cls, code=''):
    '''constructs an instance of the class from a construction code string'''


class CharacterBlock(Block):
  def __init__(self, *chars):
    self.chars = list(chars)


  def __call__(self, keys_pressed_monitor):
    for char in self.chars:
      keys_pressed_monitor.keyboard_controller.press(char)
    for char in self.chars[::-1]:
      keys_pressed_monitor.keyboard_controller.release(char)


  def __iter__(self):
    return iter(self.chars)


  def __str__(self):
    return f'CharacterBlock({" ".join(map(str, self.chars))})'


  @classmethod
  def from_string(cls, code=''):
    '''character block contruct code should be characters separated by spaces'''
    return cls(*[Character.from_string(char) for char in code.split()])


class CharacterCollection(CharacterBlock):
  def __iter__(self):
    return iter(self.chars)


  def __lt__(self, other):
    return len(self.chars).__lt__(len(other.chars))


  def __gt__(self, other):
    return len(self.chars).__gt__(len(other.chars))


  def __str__(self):
    return f'CharacterCollection({" ".join(map(str, self.chars))})'

  
  def issubset(self, other):
    return set(self).issubset(set(other))


  def add(self, character):
    if character not in self.chars:
      self.chars.append(character)


  def remove(self, character):
    while character in self.chars:
      self.chars.remove(character)
  


class PressCharacterBlock(CharacterBlock):
  def __call__(self, keys_pressed_monitor):
    for char in self.chars:
      keys_pressed_monitor.keyboard_controller.press(char)


  def __str__(self):
    return f'PressCharacterBlock({" ".join(map(str, self.chars))})'

  
class ReleaseCharacterBlock(CharacterBlock):
  def __call__(self, keys_pressed_monitor):
    for char in self.chars:
      keys_pressed_monitor.keyboard_controller.release(char)


  def __str__(self):
    return f'ReleaseCharacterBlock({" ".join(map(str, self.chars))})'


class CommandBlock(Block):
  commands = {
    'sleep': lambda keys_pressed_monitor, seconds: time.sleep(float(seconds)),
    'print': lambda keys_pressed_monitor, *params: print(' '.join(params)),
    'quit': lambda keys_pressed_monitor: keys_pressed_monitor.stop()
  }
  
  def __init__(self, command):
    self.command = command


  def __call__(self, keys_pressed_monitor):
    self.command(keys_pressed_monitor)


  def __str__(self):
    return f'CommandBlock({self.command})'


  @classmethod
  def from_string(cls, code=''):
    '''command block construct code should look like "command_name *arguments
separated by spaces"'''
    func_key, *params = code.split(' ')
    if func_key in cls.commands:
      func = cls.commands[func_key]
    else:
      func = eval(func_key)
    return cls(
      lambda keys_pressed_monitor, params=params: func(
        keys_pressed_monitor, *params
      )
    )


class BlockChain:
  def __init__(self, *blocks):
    self.blocks = list(blocks)


  def __call__(self, keys_pressed_monitor):
    for block in self.blocks:
      block(keys_pressed_monitor)


  def __str__(self):
    return f'BlockChain({" ".join(map(str, self.blocks))})'


  @classmethod
  def from_string(cls, code=''):
    '''block chain construct code should consist of regular characters and block
construction code separated by <>. Block construction code may start with a
prefix in constr_def_prefixes to yield the corresponding type of object'''
    blocks = []
    for idx, frag in enumerate(code.replace('<','>').split('>')):
      if not idx%2:
        blocks += [CharacterBlock.from_string(letter) for letter in frag]
      elif (split_frag := frag.split(' '))[0] in class_names:
        blocks.append(class_names[split_frag[0]].from_string(' '.join(split_frag[1:])))
      else:
        blocks.append(CharacterBlock.from_string(frag))
    return cls(*blocks)


class Shortcut:
  def __init__(self, trigger:CharacterBlock, command:BlockChain):
    self.trigger = trigger
    self.command = command
    self.suspended = False


  def __iter__(self):
    return self.trigger.__iter__()
    

  def __lt__(self, other):
    return self.trigger.__lt__(other.trigger)
    

  def __gt__(self, other):
    return self.trigger.__gt__(other.trigger)


  def __call__(self, keys_pressed_monitor):
    return self.command(keys_pressed_monitor)


  def __str__(self):
    return f'Shortcut(trigger={self.trigger}, command={self.command})'


  def __repr__(self):
    return f'Shortcut(trigger={self.trigger}, command={self.command})'


  def triggered_by(self, character_collection):
    return self.trigger.issubset(character_collection)


  @classmethod
  def from_string(cls, trigger_code, output_code):
    '''trigger code should be character_block construction code, output_code should
  be block_chain construction code'''
    return cls(
      CharacterCollection.from_string(trigger_code),
      BlockChain.from_string(output_code)
    )


  def fits_pattern(self, suspended=None, triggered_by={}, contains=[], not_contains=[]):
    if suspended is not None and self.suspended != suspended:
      return False
    for character_collection in triggered_by:
      if self.triggered_by(character_collection) != triggered_by[character_collection]:
        return False
    for character in contains:
      if character not in self:
        return False
    for character in not_contains:
      if character in self:
        return False
    return True


class ShortcutCollection:
  def __init__(self, *shortcuts):
    self.shortcuts = list(shortcuts)


  def __iter__(self):
    return iter(self.shortcuts)


  def __bool__(self):
    return bool(self.shortcuts)


  def get_shortcuts(self, suspended=None, triggered_by={}, contains=[], not_contains=[]):
    return ShortcutCollection(*[shortcut for shortcut in self.shortcuts if shortcut.fits_pattern(
      suspended=suspended, triggered_by=triggered_by, contains=contains, not_contains=not_contains
    )])
  

class_names = {
  'block': Block,
  'characters': CharacterBlock,
  'press': PressCharacterBlock,
  'release': ReleaseCharacterBlock,
  'command': CommandBlock,
  'chain': BlockChain,
  'shortcut': Shortcut
}
