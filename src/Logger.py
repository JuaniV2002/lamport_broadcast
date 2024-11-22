

# (Opcional) Registra eventos y errores
class Logger:
    @staticmethod
    def log_event(event):
        print(f"Event: {event}")

    @staticmethod
    def log_error(error):
        print(f"Error: {error}")