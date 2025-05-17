import readline


class Completer:
    def __init__(self, options):
        self.options = sorted(options)
    
    def complete(self, text, state):
        if state == 0:
            self.matches = [s for s in self.options if s and s.startswith(text)]
        return self.matches[state] if state < len(self.matches) else None


def setup_autocomplete(options):
    completer = Completer(options)
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")
    readline.set_completer_delims("")


def input_with_autocomplete(prompt, excpetion_message, options=None, validator=None):
    if options:
        setup_autocomplete(options)
    
    while True:
        try:
            user_input = input(prompt).strip()
            if not user_input:
                return None
            if validator and not validator(user_input):
                raise ValueError
            return user_input
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            return None
        except ValueError:
            print(excpetion_message)
