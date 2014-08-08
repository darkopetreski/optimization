import pulp
import math

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
        self.W = W
        self.w = w
        self.b = b
        
        
    def solve(self):
        """
        Round the solution to ingeger. 
        then check if the patterns matches the total number. if not
        find the difference and do the same thing to the difference untill
        we meet the desired quantities
        """
        
        qLeft = list(self.b)
        
        patternsData = self.solvePartial(qLeft)
        qLeft = self.getLeftQuantities(patternsData)
        
        #print "-----------------------"
        #print patternsData
        #print qLeft
        #print "-----------------------"
        
        #print " === " , self.solvePartial(qLeft)
        
        #patternsData.extend(self.solvePartial(qLeft))
        #qLeft = self.getLeftQuantities(patternsData)
        #print "-----------------------"
        #print patternsData
        #print qLeft
        #print "-----------------------"
        
        while not self.isQuantityEmpty(qLeft):
            
            newPatterns = self.solvePartial(qLeft)
            
            #print "new patterns"
            #print newPatterns
            
            patternsData.extend(newPatterns)
            qLeft = self.getLeftQuantities(patternsData)
            
            #print "------------------------------------------------"
            #print "quantities still not empty."
            #print qLeft
            #print "pattenrs"
            #print patternsData
            #print ""
            #print ""
            
        return patternsData
        
        
    def getLeftQuantities(self, patterns):
        leftQuantities = list(self.b) # make a copy of the list
        for i, p in enumerate(patterns):
            nrPatters = p[0]
            patterns = p[1]
            
            for c, q in enumerate(self.b):
                leftQuantities[c] = leftQuantities[c] - nrPatters * patterns[c]
                
        return leftQuantities
    
    
    def isQuantityEmpty(self, quantities):
        for q in quantities:
            if q>0:
                return False
        return True
    
    
    def formatPatterns(self, patterns):
        """
        """
        formated = []
        for i, p in enumerate(patterns):
            tmp = []
            tmp.append(p[0]) # nr of patterns used
            
            tmpPat = []
            for c, q in enumerate(self.b):
                if p[1][c] > 0:
                    tmpPat.append("%smm X %s"%(self.w[c], p[1][c]))
                
            tmp.append(tmpPat)
            
            formated.append(tmp)
            
        return formated
    
    
    def solvePartial(self, b):
        
        patterns = self.getInitialPatterns(b)
        
        nesto = 10
        while (nesto > 1.00000001):            
            pi = self.getShadowPrices(patterns, b)
            knapsack = self.knapsack(pi, self.w, self.W, b)
            patterns.append(knapsack[0])
            nesto = knapsack[1]
            
            #print "next iteration"
            #print pi
            #print knapsack
            #print "objective ", nesto
            #print patterns
            #print ""
            #print ""
            
        #print "---------------------------------------------"
        #print "biram nekolku patterni od mnozestvoto"    
        #print patterns    
        
        return self.pickPatterns(patterns, b)
        
        
    def getInitialPatterns(self, b):
        """
        @param W  int, the lenght of the stock
        @param w  list of needed widths
        @return list of patterns. Each pattern has lenght len(w)
        
        Example W = 10, w=[2, 3 5] 
        will return
        [ [5, 0, 0], [0, 3, 0], [0, 0, 2]  ] 
        """
        
        listSize = len(self.w)
        patterns = []
        for i, width in enumerate(self.w):
            pat = [0] * listSize
            pat[i] = int(self.W/width)
            if (pat[i]>b[i]):
                pat[i] = b[i]
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
        
        #problem.writeLP("/tmp/shadow.lp")[0.33333333, [0, 3, 0, 0]], [0.4, [0, 0, 5, 0]]
        status = problem.solve()
        
        return [c.pi for name, c in problem.constraints.items()]
    
    
    def pickPatterns(self, allPatterns, quantities):
        
        problem = pulp.LpProblem("PickPatterns", pulp.LpMinimize)
        
        nrPatterns = len(allPatterns)
        nrRows = len(quantities)
        
        
#TODO:   ogranicuvane na x na pulp.LpInteger dava pogresni rezultati
# no ako ne ja ognrancis ima slucai (toj od vikipedia) kade sto vraca solucina od samo decimalni pa
# zaokruzeno na integer vraca prasno resenie i algoritmot ne zvrsvuva nikogas

        x = []
        for c in range(nrPatterns):
            x.append(pulp.LpVariable("x%d"%c , 0, None, pulp.LpInteger))
        
        problem += sum([var for var in x])
        
        for r in range(nrRows):
            constraints = []
            for c in range(nrPatterns):
                constraints.append(x[c] * allPatterns[c][r]);
            problem += sum(constraints) >= quantities[r]
        
        
        #print problem
        
        #print problem
        
        status = problem.solve()
        #status = problem.solve(pulp.GLPK(msg = 0))
        if self.LOG:
            print problem
        
        
        #print [pulp.value(a) for a in x]
        
        chosenPatterns = []
        pickedNumbers =  [pulp.value(a) for a in x]
        for r in range(len(pickedNumbers)):
            nrPickedPatterns = math.floor(pickedNumbers[r])
            if (nrPickedPatterns > 0):
                chosenPatterns.append([nrPickedPatterns, allPatterns[r]])
        
        return chosenPatterns;
   

if __name__ == "__main__":
    
    W = 10
    w = [6, 5, 4, 3, 2]
    q = [1, 1, 1, 1, 2]
    
    #W = 100
    #w = [14, 31, 36, 45]
    #q = [211,395,610,97]
    
    #W = 10
    #w = [1]
    #q = [12]
    
    #W = 5600
    #w = [1380,1520,1560,1710,1820,1880,1930,2000,2050,2100,2140,2150,2200]
    #q = [22,25,12,14,18,18,20,10,12,14,16,18,20]
    
    #W = 5600
    #w = [1380,1520,1560,1710,1880,2000,2050,2150,2200]
    #q = [1, 1, 1, 1, 1, 1, 1, 1, 1]
    
    
    import sys
    c = CuttingStock(W, w, q)
    patterns = c.solve()
    for p in c.formatPatterns(patterns):
        print p
    sys.exit(0)
    
    
    #testPatterns = [ [0,0,0,2], [0,0,2,0], [0,2,1,0], [2,0,2,0] ]
    #c.pickPatterns(testPatterns, q)
    
    #sys.exit(0)
    
    #patterns = c.getInitialPatterns(W, w, q)
    #print "initial patterns"
    #print patterns
    
    #nesto = 10
    #while (nesto > 1.00000001):
    #    
    #    print ""
    #    print "Next iteration"
    #    
    #    pi = c.getShadowPrices(patterns, q)
    #    print "shaddow prices of the patterns"
    #    print pi
   # 
   #     knapsack = c.knapsack(pi, w, W, q)
   #     print "new pattern"
    #    print knapsack
   # 
    #    nesto = knapsack[1]
    #    patterns.append(knapsack[0])
    #    print "now patterns are"
     #   print patterns
        
    #c.pickPatterns(patterns, q)
    
    #sys.exit(0)
    
    
    #pi = c.getShadowPrices([[7,0,0,0], [0,3,0,0], [0,0,2,0], [0,0,0,2], [2,0,2,0], [0,2,1,0]], q)
    #pi = c.getShadowPrices([[7,0,0,0], [0,3,0,0], [0,0,2,0], [0,0,0,2], [2,0,2,0], [0,2,1,0]], q)
    
    #print pi;
    #print c.knapsack(pi, w, W)
    
    #sys.exit(0)
    
    #W, w, b = getInputData();
    #print "Stock length     ", W
    #print "Order lengths    ", w
    #print "Order quantities ", b
    
    #CuttingStock.LOG = True
    
    #c = CuttingStock(W, w, b); 
    #c.solve();
    
    #print c.knapsack([1.0/2, 1.0/2, 1.0/3, 1.0/7], [45, 36, 31, 14], 100)
 
