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
        
        
        
    def getInitialPatterns(self, W, w, q):
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
            #if (pat[i]>q[i]):
            #    pat[i] = q[i]
            patterns.append(pat)
        
        return patterns
    
        
    def knapsack(self, f, d, b, quantities):
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
            x.append(pulp.LpVariable("x%d"%r , 0, quantities[r], pulp.LpInteger))
        
        problem += sum( d[r] * x[r] for r in range(nrCols)) <= b
        problem += sum( f[r] * x[r] for r in range(nrCols))
        
        #status = problem.solve(pulp.GLPK(msg = 0))
        #problem.writeLP("/tmp/knapsack.lp")
        status = problem.solve()
        if self.LOG:
            print problem
           
        return ([pulp.value(a) for a in x], pulp.value(problem.objective))
        
        
    def getShadowPrices(self, patterns, b):
        """
        Get shadow prices from the matrig (list of patterns)
        
        @param patterns list of patterns. each pattern has length w
        @param b, list of quantities with length w
        
        @return list of shaddow prices 
        """
        nrPatterns = len(patterns)
        patternLength = len(patterns[0])
        
        problem = pulp.LpProblem("Shadow", pulp.LpMinimize)
        
        x = []
        for r in range(nrPatterns):
            # Create variables Xi
            x.append(pulp.LpVariable("x%d"%r, 0))
        
        problem += sum([var for var in x])
        
        for i in range(patternLength):
            # list of constraints
            problem += sum([ x[r] * patterns[r][i] for r in range(nrPatterns) ]) >= b[i], "c%d"%i
        
        #problem.writeLP("/tmp/shadow.lp")
        status = problem.solve()
        
        return [c.pi for name, c in problem.constraints.items()]
    
    
    def pickPatterns(self, allPatterns, quantities):
        
        problem = pulp.LpProblem("PickPatterns", pulp.LpMinimize)
        
        nrPatterns = len(allPatterns)
        nrRows = len(quantities)
        
        x = []
        for c in range(nrPatterns):
            x.append(pulp.LpVariable("x%d"%c , 0, None))
        
        problem += sum([var for var in x])
        
        for r in range(nrRows):
            constraints = []
            for c in range(nrPatterns):
                constraints.append(x[c] * allPatterns[c][r]);
            problem += sum(constraints) >= quantities[r]
        
        
        #print problem
        
        status = problem.solve()
        #status = problem.solve(pulp.GLPK(msg = 0))
        if self.LOG:
            print problem
        
        print x
        print [pulp.value(a) for a in x]
        print allPatterns
        return
    
        return ([pulp.value(a) for a in x], pulp.value(problem.objective))
        
        
        
        
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
    
    W = 10
    w = [6, 5, 4, 3, 2]
    q = [1,1, 1, 1, 1]
    #W = 100
    #w = [14, 31, 36, 45]
    #q = [211,395,610,97]

    
    import sys
    c = CuttingStock(W, w, q);
    
    #testPatterns = [ [0,0,0,2], [0,0,2,0], [0,2,1,0], [2,0,2,0] ]
    #c.pickPatterns(testPatterns, q)
    
    #sys.exit(0)
    
    patterns = c.getInitialPatterns(W, w, q)
    print "initial patterns"
    print patterns
    
    nesto = 10
    while (nesto > 1.00001):
        
        print ""
        print "Next iteration"
        
        pi = c.getShadowPrices(patterns, q)
        print "shaddow prices of the patterns"
        print pi
    
        knapsack = c.knapsack(pi, w, W, q)
        print "new pattern"
        print knapsack
    
        nesto = knapsack[1]
        patterns.append(knapsack[0])
        print "now patterns are"
        print patterns
        
    c.pickPatterns(patterns, q)
    
    sys.exit(0)
    
    
    #pi = c.getShadowPrices([[7,0,0,0], [0,3,0,0], [0,0,2,0], [0,0,0,2], [2,0,2,0], [0,2,1,0]], q)
    pi = c.getShadowPrices([[7,0,0,0], [0,3,0,0], [0,0,2,0], [0,0,0,2], [2,0,2,0], [0,2,1,0]], q)
    
    print pi;
    print c.knapsack(pi, w, W)
    
    sys.exit(0)
    
    W, w, b = getInputData();
    print "Stock length     ", W
    print "Order lengths    ", w
    print "Order quantities ", b
    
    CuttingStock.LOG = True
    
    c = CuttingStock(W, w, b); 
    c.solve();
    
    print c.knapsack([1.0/2, 1.0/2, 1.0/3, 1.0/7], [45, 36, 31, 14], 100)
 
