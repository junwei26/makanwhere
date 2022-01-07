class BotData:
    def __init__(self):
        self.locations = []
        self.cuisines = []
        self.results = []
        self.budget = 5
        self.isRunning = False
        self.searchRadius = 1000
        self.resultDisplayLength = 10

    def reset(self):
        self.locations = []
        self.cuisines = []
        self.results = []
        self.budget = 5
        self.isRunning = False
        self.searchRadius = 1000
        self.resultDisplayLength = 10
        
