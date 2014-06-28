import pulp

class CuttingStock:
    """
    """
    LOG = False
    
    def __init__(self, W , w, b):
        """
        W - int, length of the stocks needed to be cut
        w - list of lengths that we need
        b - list of quantities for each length. 
        """
        self.W = w
        self.w = w
        self.b = b
        
        
    def solve(self):
        pass
        
        
        
    def getInitialPatterns(self, W, w):
        """
        @param W  int, the lenght of the stock
        @param w  list of needed widths
        @return list of patterns. Each pattern has lenght len(w)
        
        Example W = 10, w=[2, 3 5] 
        will return
        [ [5, 0, 0], [0, 3, 0], [0, 0, 2]  ] 
        """
        listSize = len(w)
        patterns = []
        for i, width in enumerate(w):
            pat = [0] * listSize
            pat[i] = int(W/width)
            patterns.append(pat)
        
        return patterns
        
    #TODO: dali e potrebna ovaa funkcija ? 
    #def multiplyLengthsQuantities(self, w, b):
    #    """
    #    @param w: list, lengths that we need, ex. [1, 2]
    #    @param b: list, quantities for each length,  ex. [3, 4]
    #    @return:  list, repeated widths, ex.[1 1 1 2 2 2 2]
    #    """
    #    result = []
    #    for i in range(len(w)):
    #        for j in range(b[i]):
    #            result.append(w[i])
    #            
    #    return result
        
        
    def knapsack(self, f, d, b):
        """
        max z: f1X1 + ... + frXr
               d1X1 + ... + frXr <= b
               X1 .. Xr >=0, integer
               
        @param f, list of parameters to be maximized
        @param d, list of objective parameters
        @param b, int boundary of the objective
        @return (x, z)
                 x list of values
                 z, the maximized value
        """
        problem = pulp.LpProblem("Knapsakc", pulp.LpMaximize)
        
        nrCols = len(f)
        
        x = []
        for r in range(nrCols):
            # Create variables Xi, int, >=0
            x.append(pulp.LpVariable("x%d"%r , 0, None, pulp.LpInteger))
        
        problem += sum( d[r] * x[r] for r in range(nrCols)) <= b
        problem += sum( f[r] * x[r] for r in range(nrCols))
        
        #status = problem.solve(pulp.GLPK(msg = 0))
        status = problem.solve()
        if self.LOG:
            print problem
            
        return ([pulp.value(a) for a in x], pulp.value(problem.objective))
        
        
    def getShadowPrice(self):
        """
        """
        problem = pulp.LpProblem("Shadow", pulp.LpMinimize)
        x1 = pulp.LpVariable("x1")
        x2 = pulp.LpVariable("x2")
        x3 = pulp.LpVariable("x3")
        x4 = pulp.LpVariable("x4")
        
        c1 = 7*x1 >= 211
        c2 = 3*x2 >= 395
        c3 = 2*x3 >= 610
        c4 = 2*x4 >= 97
        
        problem += x1 + x2 + x3 + x4
        problem += c1
        problem += c2
        problem += c3
        problem += c4
        
        status = problem.solve()
        
        return [c4.pi, c3.pi, c2.pi, c1.pi]
        
def getInputData():
    """
    Returns:
        (W, w, b)
         W - int, length of the stocks needed to be cut
         w - list of lengths that we need
         b - list of quantities for each length. 
    The size of the w and b must be the same.
    """
    
    # length of the stock rods
    W = 10; 
    # list of lengths of the desired orders
    w = [6, 5, 4, 3, 2]    
    # list of quantities for each ordered length
    b = [1, 1, 1, 1, 1]
    
    return (W, w, b)


if __name__ == "__main__":
    
    
    
    import sys
    c = CuttingStock(None, None, None)
    pi = c.getShadowPrice()
    print c.knapsack(pi, [45, 36, 31, 14], 100)
    
    sys.exit(0)
    
    W, w, b = getInputData();
    print "Stock length     ", W
    print "Order lengths    ", w
    print "Order quantities ", b
    
    CuttingStock.LOG = True
    
    c = CuttingStock(W, w, b); 
    c.solve();
    
    print c.knapsack([1.0/2, 1.0/2, 1.0/3, 1.0/7], [45, 36, 31, 14], 100)
    
    