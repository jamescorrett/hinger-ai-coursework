class KNN:
    def __init__(self, k=3, metric="euclidean"):
        self.k = k
        self.metric = metric
        self.X_train = None
        self.y_train = None