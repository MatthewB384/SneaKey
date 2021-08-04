import abc
import time

import pynput

char_codes ={
  'ralt': pynput.keyboard.Key.alt_r,
  'lalt': pynput.keyboard.Key.alt_l,
  'ctrlalt': pynput.keyboard.Key.alt_gr,
  'cap': pynput.keyboard.Key.caps_lock,
  'caps': pynput.keyboard.Key.caps_lock,
  'rcmd': pynput.keyboard.Key.cmd_r,
  'rctrl': pynput.keyboard.Key.ctrl_r,
  'lctrl': pynput.keyboard.Key.ctrl_l,
  'del': pynput.keyboard.Key.delete,
  'pgdn': pynput.keyboard.Key.page_down,
  'pgup': pynput.keyboard.Key.page_up,
  'printscr': pynput.keyboard.Key.print_screen,
  'rshift': pynput.keyboard.Key.shift_r,
  '\n': pynput.keyboard.Key.enter,
  ' ': pynput.keyboard.Key.space,
}

def char(code):
  if code in char_codes:
    return char_codes[code]
  elif code in pynput.keyboard.Key.__members__:
    return pynput.keyboard.Key[code]
  else:
    return pynput.keyboard.KeyCode.from_char(code)
  

class Block(abc.ABC):
  'An entity that can be placed in a chain and called when necessary'


  @abc.abstractmethod
  def __init__(self):
    '''creates a new block'''


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


  def __iter__(self):
    return iter(self.chars)


  def __repr__(self):
    return f'CharacterBlock({", ".join(map(str, self.chars))})'


  def copy(self):
    return self.__class__(*self.chars)


  @classmethod
  def from_string(cls, code=''):
    chars = []
    for idx, frag in enumerate(code.split('`')):
      if idx%2:
        chars.append(char(frag))
      else:
        chars += [char(letter) for letter in frag]
    return cls(*chars)


class MultiPressBlock(CharacterBlock):
  def __call__(self, monitor):
    for char in self.chars:
      monitor.keyboard_controller.press(char)


  def __repr__(self):
    return f'MultiPressBlock({", ".join(map(str, self.chars))})'


class MultiReleaseBlock(CharacterBlock):
  def __call__(self, monitor):
    for char in self.chars:
      monitor.keyboard_controller.release(char)


  def __repr__(self):
    return f'MultiReleaseBlock({", ".join(map(str, self.chars))})'
        


class MultiTapBlock(CharacterBlock):
  def __call__(self, monitor):
    for char in self.chars:
      monitor.keyboard_controller.press(char)
    for char in self.chars[::-1]:
      monitor.keyboard_controller.release(char)


  def __repr__(self):
    return f'MultiTapBlock({", ".join(map(str, self.chars))})'


def TypingBlock(CharacterBlock):
  def __call__(self, monitor):
    for char in self.chars:
      monitor.tap(char)


  def __repr__(self):
    return f'TypingBlock({", ".join(map(str, self.chars))})'


class CommandBlock(Block):
  commands = {
    'sleep': lambda monitor, seconds: time.sleep(float(seconds)),
    'print': lambda monitor, *params: print(' '.join(params)),
  }

  
  def __init__(self, command):
    self.command = command


  def __call__(self, monitor):
    self.command(monitor)


  def __repr__(self):
    return f'CommandBlock({self.command})'


  @classmethod
  def from_string(cls, code):
    key, *params = code.split('`')
    func = cls.commands[key] if key in cls.commands else eval(key)
    return cls(lambda monitor, params=params: func(monitor, *params))


class QuitBlock(CommandBlock):
  def __init__(self):
    pass


  def __call__(self, monitor):
    monitor.stop()


  def __repr__(self):
    return f'QuitBlock()'


  @classmethod
  def from_string(cls, code):
    return cls()


class BlockChain:
  def __init__(self, *blocks):
    self.blocks = list(blocks)


  def __call__(self, monitor):
    for block in self.blocks:
      block(monitor)


  def __repr__(self):
    return f'BlockChain({", ".join(map(str, self.blocks))})'


#example blockchain construction code:
# multitap``cmd`r|genericcommand`sleep`0.1|typing`chrome www.youtube.com/watch?v=dQw4w9WgXcQ`enter`

  @classmethod
  def from_string(cls, code=''):
    blocks = []
    for idx, frag in enumerate(code.split('|')):
      blocktype, _, code = frag.partition('`')
      blocks.append(block_names[blocktype].from_string(code))
    return cls(*blocks)
  


class CharacterCollection(CharacterBlock):
  def __call__(self, controler):
    pass

  
  def __lt__(self, other):
    return len(self.chars).__lt__(len(other.chars))


  def __gt__(self, other):
    return len(self.chars).__gt__(len(other.chars))


  def __repr__(self):
    return f'CharacterCollection({", ".join(map(str, self.chars))})'

  
  def issubset(self, other):
    return set(self).issubset(set(other))


  def add(self, character):
    if character not in self.chars:
      self.chars.append(character)


  def remove(self, character):
    while character in self.chars:
      self.chars.remove(character)


class Shortcut:
  def __init__(self, trigger:CharacterBlock, command:BlockChain):
    self.trigger = trigger
    self.command = command
    self.suspended = False


  def __iter__(self):
    return iter(self.trigger)
    

  def __lt__(self, other):
    return self.trigger.__lt__(other.trigger)
    

  def __gt__(self, other):
    return self.trigger.__gt__(other.trigger)


  def __call__(self, monitor):
    return self.command(monitor)


  def __repr__(self):
    return f'Shortcut(trigger={self.trigger}, command={self.command})'


  def triggered_by(self, character_collection):
    return self.trigger.issubset(character_collection)
  

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


  @classmethod
  def from_strings(cls, trigger_code, output_code):
    return cls(
      CharacterCollection.from_string(trigger_code),
      BlockChain.from_string(output_code)
    )


  @classmethod
  def from_string(cls, code):
    trigger_code, output_code = code.split('||')
    return cls(
      CharacterCollection.from_string(trigger_code),
      BlockChain.from_string(output_code)
    )



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


  @classmethod
  def from_string(cls, code):
    shortcuts = [Shortcut.from_string(chunk) for chunk in code.split('|||')]
    return cls(*shortcuts) 
  

block_names = {
  'block': Block,
  'character': CharacterBlock,
  'press': MultiPressBlock,
  'release': MultiReleaseBlock,
  'tap': MultiTapBlock,
  'typing': TypingBlock,
  'command': CommandBlock,
  'quit': QuitBlock
}


