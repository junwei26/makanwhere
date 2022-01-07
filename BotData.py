class BotData:
    locations = []
    cuisines = []
    results = []
    budget = 5
    isRunning = False
    searchRadius = 1000
    resultDisplayLength = 10

    def __init__(self):
        pass

    def reset(self):
        self.locations = []
        self.cuisine = []
        self.budget = 5
        self.isRunning = False
        searchRadius = 500
        resultDisplayLength = 10
        
