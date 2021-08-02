#sneaky

from pynput.keyboard import Key, Listener

class Listenerer(Listener):
  def __init__(self):
    super().__init__(
      on_press=self.on_press,
      on_release=self.on_release,
      on_click=self.on_click
    )
    self.pressed = set()

  def on_press(self, key):
    print(self.pressed)
    self.pressed.add(key)

  def on_release(self, key):
    if key in self.pressed:
      self.pressed.remove(key)

  def on_click(self, x, y, button, pressed):
    if pressed:
      self.pressed.add(button)
    else:
      if button in self.pressed:
        self.pressed.remove(button)

    

#Listener(on_press=on_press,on_release=on_release).__enter__().join()

# Collect events until released
with Listenerer() as listener:
    listener.join()
