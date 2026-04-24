import ast
import operator as op
from kivy import platform

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

SAFE_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def safe_eval(expression: str):
    try:
        tree = ast.parse(expression, mode="eval")
        def _eval(node):
            if isinstance(node, ast.Expression):
                return _eval(node.body)
            if isinstance(node, (ast.Constant, ast.Num)):
                val = node.value if hasattr(node, 'value') else node.n
                if isinstance(val, (int, float)):
                    return val
                raise ValueError("Faqat raqamlar")
            if isinstance(node, ast.BinOp):
                left = _eval(node.left)
                right = _eval(node.right)
                func = SAFE_OPERATORS.get(type(node.op))
                if func is None:
                    raise ValueError("Ruxsat etilmagan amal")
                return func(left, right)
            if isinstance(node, ast.UnaryOp):
                operand = _eval(node.operand)
                func = SAFE_OPERATORS.get(type(node.op))
                if func is None:
                    raise ValueError("Ruxsat etilmagan amal")
                return func(operand)
            raise ValueError("Ruxsat etilmagan ifoda")
        return _eval(tree)
    except Exception:
        raise ValueError("Xatolik")

class CalculatorApp(App):
    title = "Kalkulyator"

    def build(self):
        self.operators = {"/", "*", "+", "-"}
        self.last_was_operator = False
        self.just_evaluated = False
        self.history = []

        Window.clearcolor = (0.12, 0.12, 0.14, 1)
        if platform not in ("android", "ios"):
            Window.size = (360, 600)
        Window.bind(on_key_down=self._on_keyboard)

        main_layout = BoxLayout(orientation="vertical", padding=12, spacing=10)

        self.history_label = Label(
            text="",
            size_hint=(1, 0.15),
            halign="right",
            valign="top",
            color=(0.6, 0.6, 0.65, 1),
            font_size=16,
        )
        self.history_label.bind(size=self._sync_label_text_size)
        main_layout.add_widget(self.history_label)

        self.display = TextInput(
            multiline=False,
            readonly=True,
            halign="right",
            font_size=48,
            size_hint=(1, 0.15),
            background_color=(0.18, 0.18, 0.22, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0, 0, 0),
            padding=[12, 20, 12, 12],
        )
        main_layout.add_widget(self.display)

        buttons = [
            ["C", "DEL", "%", "/"],
            ["7", "8", "9", "*"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["+/-", "0", ".", "="],
        ]

        grid = GridLayout(cols=4, spacing=8, size_hint=(1, 0.7))
        for row in buttons:
            for label in row:
                btn = Button(
                    text=label,
                    font_size=28,
                    background_normal="",
                    background_color=self._color_for(label),
                    color=(1, 1, 1, 1),
                )
                btn.bind(on_press=self.on_button_press)
                grid.add_widget(btn)
        main_layout.add_widget(grid)

        return main_layout

    def _sync_label_text_size(self, instance, value):
        instance.text_size = (instance.width - 12, instance.height)

    def _color_for(self, label: str):
        if label in self.operators or label == "=":
            return (0.95, 0.55, 0.15, 1)
        if label in {"C", "DEL"}:
            return (0.75, 0.25, 0.25, 1)
        if label in {"%", "+/-"}:
            return (0.40, 0.40, 0.50, 1)
        return (0.28, 0.28, 0.34, 1)

    def on_button_press(self, instance):
        self._handle_input(instance.text)

    def _handle_input(self, text: str):
        current = self.display.text

        if text == "C":
            self.display.text = ""
            self.last_was_operator = False
            self.just_evaluated = False
            return

        if text == "DEL":
            if current and current != "Xatolik":
                new_text = current[:-1]
                self.display.text = new_text
                self.last_was_operator = bool(new_text) and new_text[-1] in self.operators
            return

        if text == "=":
            self._evaluate()
            return

        if text == "+/-":
            self._toggle_sign()
            return

        if text == "%":
            self._apply_percent()
            return

        if self.just_evaluated:
            if text in self.operators:
                self.just_evaluated = False
            else:
                self.display.text = ""
                self.just_evaluated = False
                current = ""

        if current == "Xatolik":
            current = ""
            self.display.text = ""

        if text in self.operators:
            if current == "":
                if text == "-":
                    self.display.text = "-"
                    self.last_was_operator = False
                return
            if self.last_was_operator:
                self.display.text = current[:-1] + text
                return
            self.last_was_operator = True
        else:
            if text == ".":
                parts = self._split_numbers(current)
                if parts and "." in parts[-1]:
                    return
                if not current or current[-1] in self.operators:
                    self.display.text += "0"
                    current = self.display.text
            self.last_was_operator = False

        self.display.text += text

    def _split_numbers(self, text: str):
        buf = ""
        parts = []
        for i, ch in enumerate(text):
            if ch in self.operators and i != 0 and text[i - 1] not in self.operators:
                parts.append(buf)
                buf = ""
            else:
                buf += ch
        parts.append(buf)
        return parts

    def _toggle_sign(self):
        current = self.display.text
        if not current or current == "Xatolik":
            return
        try:
            value = safe_eval(current)
            self.display.text = self._format_number(-value)
            self.last_was_operator = False
        except Exception:
            pass

    def _apply_percent(self):
        current = self.display.text
        if not current or current == "Xatolik":
            return
        try:
            value = safe_eval(current)
            self.display.text = self._format_number(value / 100)
            self.last_was_operator = False
        except Exception:
            self.display.text = "Xatolik"

    def _evaluate(self):
        expression = self.display.text
        if not expression or expression == "Xatolik":
            return
        try:
            result = safe_eval(expression)
            formatted = self._format_number(result)
            self._add_history(expression, formatted)
            self.display.text = formatted
            self.last_was_operator = False
            self.just_evaluated = True
        except ZeroDivisionError:
            self.display.text = "Xatolik"
        except Exception:
            self.display.text = "Xatolik"

    def _format_number(self, value):
        if isinstance(value, float):
            if value.is_integer():
                return str(int(value))
            return f"{value:.10g}"
        return str(value)

    def _add_history(self, expression: str, result: str):
        self.history.append(f"{expression} = {result}")
        self.history = self.history[-10:]
        self.history_label.text = "\n".join(self.history[-3:])

    def _on_keyboard(self, window, key, scancode, codepoint, modifiers):
        if codepoint and codepoint in "0123456789.+-*/%":
            self._handle_input(codepoint)
            return True
        if key in (13, 271):
            self._handle_input("=")
            return True
        if key == 8:
            self._handle_input("DEL")
            return True
        if key == 27:
            self._handle_input("C")
            return True
        return False

if __name__ == "__main__":
    CalculatorApp().run()
