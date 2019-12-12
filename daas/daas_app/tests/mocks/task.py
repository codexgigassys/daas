class MockTask:
    def __init__(self):
        self.is_finished = False
        self.is_queued = True
        self.is_started = False
        self.is_failed = False
        self.id = 1

    def process(self):
        if self.is_queued:
            self.is_queued = False
            self.is_started = True
        else:
            Exception('invalid status change')

    def finish(self):
        if self.is_started:
            self.is_started = False
            self.is_finished = True
        else:
            Exception('invalid status change')

    def fail(self):
        if self.is_started:
            self.is_started = False
            self.is_failed = True
        else:
            Exception('invalid status change')

    def cancel(self):
        pass
