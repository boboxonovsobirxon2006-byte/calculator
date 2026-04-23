from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

class CalculatorApp(App):
    def build(self):
        self.operators = ["/", "*", "+", "-"]
        self.last_was_operator = False

        # Asosiy vertikal joylashuv
        main_layout = GridLayout(cols=1, padding=10, spacing=10)

        # Natija chiqadigan oyna (font_size ni biroz kichraytirdim moslashuv uchun)
        self.display = TextInput(
            multiline=False,
            readonly=True,
            halign="right",
            font_size=45,
            input_filter=None
        )
        main_layout.add_widget(self.display)

        # Tugmalar tartibi
        buttons = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            [".", "0", "C", "+"],
        ]

        for row in buttons:
            row_layout = GridLayout(cols=4, spacing=10)
            for label in row:
                btn = Button(text=label)
                btn.bind(on_press=self.on_button_press)
                row_layout.add_widget(btn)
            main_layout.add_widget(row_layout)

        # Pastki qatordagi maxsus tugmalar
        bottom_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=80)
        
        del_btn = Button(text="DEL", background_color=(0.7, 0.2, 0.2, 1))
        del_btn.bind(on_press=self.on_button_press)
        
        equals_btn = Button(text="=", background_color=(0.2, 0.7, 0.2, 1))
        equals_btn.bind(on_press=self.on_equal)
        
        bottom_layout.add_widget(del_btn)
        bottom_layout.add_widget(equals_btn)
        
        main_layout.add_widget(bottom_layout)

        return main_layout

    def on_button_press(self, instance):
        text = instance.text
        current = self.display.text

        if text == "C":
            self.display.text = ""
            self.last_was_operator = False
            return

        if text == "DEL":
            if current:
                new_text = current[:-1]
                self.display.text = new_text
                self.last_was_operator = True if new_text and new_text[-1] in self.operators else False
            return

        if text in self.operators:
            if current == "" or self.last_was_operator:
                return
            self.last_was_operator = True
        else:
            if text == ".":
                # Oxirgi son ichida nuqta borligini tekshirish
                parts = current.replace('+', ' ').replace('-', ' ').replace('*', ' ').replace('/', ' ').split()
                if parts and "." in parts[-1]:
                    return
            self.last_was_operator = False

        self.display.text += text

    def on_equal(self, instance):
        try:
            # Hisoblash va natijani chiqarish
            if self.display.text:
                result = str(eval(self.display.text))
                self.display.text = result
                self.last_was_operator = False
        except Exception:
            self.display.text = "Xatolik"

if __name__ == "__main__":
    CalculatorApp().run()
