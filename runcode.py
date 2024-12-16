if __name__ == "__main__":
    # Example code for testing
    class EngineMock:
        def __init__(self):
            self.params = {
                'orderid': '',
                'substitutos': '',
                'token': ''
            }
            self.result = {}

        def log(self, message):
            print(message)

        def result_set(self, result):
            self.result = result

    engine = EngineMock()
    Run(engine)
