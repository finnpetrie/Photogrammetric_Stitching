import math
from scipy import interpolate
from scipy.spatial import ConvexHull
import sympy as sp
import numpy as np


class Matching:
    def __init__(self, staticPoints, dynamicPoints, dynColours):
        self.staticPoints = staticPoints
        self.dynColours = dynColours
        self.dynamicPoints = dynamicPoints
        c = np.delete(staticPoints, 0 , 1)
        self.staticConvex = ConvexHull(c)
        

    
    
        
        
    def __call__(self):
        self.write("BeforeMatched")
        theta = 0
        minTheta = 0
        minError = math.inf
        
        while(theta <= 360):
            #setup polar coords
            self.polar()
           # self.rotate(theta)
            #self.interpolate()
            e = self.interpolate(self.staticPolar)

            if(e < minError):
                minError = e
                print(e)
                minTheta = theta
            theta += 1
            self.rotate(1)

        #self.areaMin()
        self.rotate(minTheta)
        self.write("Matched")

    def between_coords(self, polarCoords, theta):
        for i in range(1, len(polarCoords)):
            if(theta <= polarCoords[i][1]):
                if(theta >= polarCoords[i-1][1]):
                    return i
        return 0
    
    def staticCentroid(self):
        centroid = np.zeros((3, 1))
        amount = int(len(self.staticPoints))
        for i in range(amount):
            centroid[1] += self.staticPoints[i][1]
            centroid[2] += self.staticPoints[i][2]
        
        centroid[1] /= (amount)
        centroid[2] /= amount
        return centroid
   
    def dynamicCentroid(self):
        centroid = np.zeros((3, 1))
        amount = int(len(self.dynamicPoints))
        for i in range(amount):
            centroid[1] += self.dynamicPoints[i][1]
            centroid[2] += self.dynamicPoints[i][2]
        
        centroid[1] /= (amount)
        centroid[2] /= amount
        return centroid


    def centreStatic(self):
        centroid = self.staticCentroid()
        amount = int(len(self.staticPoints))
        for i in range(amount):
            #print(centroid)
            self.staticPoints[i][1] -= centroid[1]
            self.staticPoints[i][2] -= centroid[2]

    def centreDynamic(self):
        centroid = self.dynamicCentroid()
        amount = int(len(self.dynamicPoints))
        for i in range(amount):
            #print(centroid)
            self.dynamicPoints[i][1] -= centroid[1]
            self.dynamicPoints[i][2] -= centroid[2]

    def interpolate(self, polarCoords):
        domain = len(polarCoords)
        lineEq = np.zeros((domain, 2))
        #pass the equation of the line through these points
        dynamic_domain = len(self.dynamicPolar)
        dynLine = np.zeros((dynamic_domain, 2))    

        for i in range(1, domain):
            #interpolate a line from point a to point b
            x2 = int(polarCoords[i][2])
            x1 = int(polarCoords[i-1][2]) 
            #print(x2)

            m = (self.staticPoints[x2][2] - self.staticPoints[x1][2])/(self.staticPoints[x2][1] - self.staticPoints[x1][1])
            lineEq[i][0] = m
            b = m*(-self.staticPoints[x1][1]) + self.staticPoints[x1][2]
            lineEq[i][1] = b
        
    
        for i in range(1, dynamic_domain):
            x2 = int(self.dynamicPolar[i][2])
            x1 = int(self.dynamicPolar[i-1][2])

            m = (self.dynamicPoints[x2][2] - self.dynamicPoints[x1][2])/(self.dynamicPoints[x2][1] - self.dynamicPoints[x1][1])
            dynLine[i][0] = m
            b = m*(-self.dynamicPoints[x1][1]) + self.dynamicPoints[x1][2]
            dynLine[i][1] = b


        #at angle t, evaluate in terms of our bounds index
        interp = np.zeros((360, 3))
        interpDynamic = np.zeros((360, 3))
        for t in range(360):
            #interpolate
            theta = np.radians(t)
           # print(theta)
            #find what points theta lies between
            boundIndex = self.between_coords(polarCoords, theta)
            #theta is greated than the ith angle in our polarCoords
            #it follows that 
            x = polarCoords[boundIndex][0]*np.cos(theta)
            y = x*lineEq[boundIndex][0] + lineEq[boundIndex][1]
            interp[t][0] = x
            interp[t][1] = y
            

            dyn_bound_index = self.between_coords(self.dynamicPolar, theta)
            dyn_x = self.dynamicPolar[dyn_bound_index][0]*np.cos(theta)
            dyn_y = dyn_x*dynLine[dyn_bound_index][0] + dynLine[dyn_bound_index][1]
            interpDynamic[t][0] = dyn_x
            interpDynamic[t][1] = dyn_y
           # print("Dynamic x " + str(dyn_x))
            #print("Dynamic y " + str(dyn_y))
            
            #print("our bound index: " + str(boundIndex))
            
        e = self.error_t(interp, interpDynamic)
        #print(e)
        return e
        # self.writePly("dynamic_interp", interpDynamic)
        # self.writePly("interp", interp)

                
    def error_t(self, static_interp, dynamic_interp):
        error = 0
        for i in range(360):

            error_x = static_interp[i][1] - dynamic_interp[i][1]
            error_y = static_interp[i][2] - dynamic_interp[i][2]
            error += np.sqrt(error_x **2 + error_y ** 2)
        return error

    def neg_to_pos(self, angle):
        theta = angle
        while(theta < 0):
            theta += np.radians(360)
        
        return theta

    def polar(self):
       # print(self.staticPoints.size)
        staticSize = len(self.staticPoints)
        dynamicSize = len(self.dynamicPoints)
        polarStatic = np.zeros((staticSize, 3))
       # print(polarStatic)
        #print("This is the size of our static: " + str(staticSize))
        polarDynamic = np.zeros((dynamicSize, 3))

        for i in range(staticSize):
            x, y = self.staticPoints[i][1], self.staticPoints[i][2]
            r = np.sqrt(x**2 + y**2)

            phi = np.arctan2(y, x)
            if(phi < 0):
                phi = self.neg_to_pos(phi)
           # print(ratio)
           # print("This is r: " + str(r))
            polarStatic[i][0] = r
            polarStatic[i][1] = phi
            polarStatic[i][2] = i
           # print("This is theta: " + str(phi))
            
       # print(polarStatic)
       # print("\n\n")
        #sort according to theta
        polarStatic = polarStatic[polarStatic[:,1].argsort()]
        for i in range(dynamicSize):
            x, y= self.dynamicPoints[i][1], self.dynamicPoints[i][2]
            r = np.sqrt(x**2 + y **2)
            phi = np.arctan2(y, x)
            if(phi < 0):
                phi = self.neg_to_pos(phi)
                
            polarDynamic[i][0] = r
            polarDynamic[i][1] = phi
            polarDynamic[i][2] = i
        #print(polarStatic)
        polarDynamic = polarDynamic[polarDynamic[:,1].argsort()]

        self.dynamicPolar = polarDynamic
        self.staticPolar = polarStatic
        #self.cartesian(polarStatic)
       # self.cartesian(polarDynamic)
        
        
    def writePly(self, filename, ply):
        f = open(filename + ".ply", "w+")
        f.write("ply\n" + "format ascii 1.0\n" + "element vertex " + str(len(ply))
            + "\n" + "property float x\n" + "property float y\n" + "property float z\n" + "property uchar red\n" + "property uchar green\n" + "property uchar blue\n" + "end_header\n")
        domain = int(len(ply))
        for i in range(int(domain)):
            for j in range(0, 3):
                f.write(str(ply[i][j]) + " ")
            for p in range(0, 3):
                if p < 2:
                    f.write(str(int(255)) + " ")
                else:
                    f.write(str(int(0)))
            f.write("\n")
        f.close()

    def cartesian(self, polar):
        size = len(polar)
        cartesian = np.zeros((size, 3))
        for i in range(size):
            x = polar[i][0]*math.cos(polar[i][1])
            y = polar[i][0]*math.sin(polar[i][1])
            cartesian[i][1] = x
            cartesian[i][2] = y
        
        self.writePly("plyTest", cartesian)
        
    def run(self):
        self.compareArea = self.staticConvex.area
        theta = 0
        minTheta = 0
        minArea = math.inf
        print("in run")
        while(theta <= 360):
            self.rotate(theta)
            area = self.areaMin()
            areaCom = abs(area-self.compareArea)
            print(areaCom)
            if(areaCom < minArea):
                minArea = areaCom
                minTheta = theta
            theta += 0.1
        print("our min area: " + str(minArea))
        self.rotate(minTheta)
        self.write("Matched")
    
    def setup_splines(self):
        staticX = self.staticPoints[:, 1]
        staticY = self.staticPoints[:, 2]
        #rint(staticX)
       #print(self.staticPoints)
        dynamicX = self.dynamicPoints[:, 1]
        dynamicY = self.dynamicPoints[:, 2]
      # print(dynamicX)
      # print(dynamicY)
        staticX = np.array(staticX)
        staticY = np.array(staticY)

        dynamicX = np.array(dynamicX)
        dynamicY = np.array(dynamicY)

        staticX = np.r_[staticX, staticX[0]]
        staticY = np.r_[staticY, staticY[0]]
        dynamicX = np.r_[dynamicX, dynamicX[0]]
        dynamicY = np.r_[dynamicY, dynamicY[0]]
        #rint(dynamicX)
      # print(dynamicY)
        self.tck_static, self.u_static = interpolate.splprep([staticX, staticY], s=0, per=True)
        self.tck_dynamic, self.u_dynanic = interpolate.splprep([dynamicX, dynamicY], s=0, per=True)

     #  print(staticX)

    def print(self):
        print("dynamic spline co-efficients: " +  str(self.dSpline[1]))
        print("static spline co-efficients: " + str(self.sSpline[1]))

    def evaluate(self, theta):

            v = np.zeros(2)
            v[0] = np.cos(theta)
            v[1] = np.sin(theta)
            print(np.linalg.norm(v))
            #x1 = interpolate.splev(theta, self.dSpline)
           # x2 = interpolate.splev(theta, self.sSpline)
            x1 = interpolate.splev(v, self.dSpline)

            print("Our x1 following evaluation: " + str(x1))

            return x1
           # x1 = interpolate.splev(theta, self.dSpline)
           # print(str(x1) + " = our x1")
           # print(str(x2) + " = our x2")
          #  d = np.subtract(x1, x2)
           # print(d)
           # print(np.linalg.norm(d))
           # x1 = 0

            #t1 = sqrt(pow(x1, 2)+ pow(y1, 2))
           # t2 = sqrt(pow(x2, 2) + pow(y2, 2))

            #subtract t2*v2 - t1*v1
            #cal magnitude - add to total error
            #solve for t

    def spline(self):
        self.tck_static, self.u_static = interpolate.splprep([self.staticX, self.staticY], s=0, per=True)
        self.tck_dynamic, self.u_dynamic = interpolate.splprep([self.dynamicX, self.dynamicY], s=0, per=True)



    def areaMin(self):
        con = np.concatenate((self.staticPoints, self.dynamicPoints), axis=0)
        con = np.delete(con, 0, 1)
        #print(con)
        c = ConvexHull(con)
       # print(c.area)
        return c.area

    def rotate(self, angle):
        theta = np.radians(angle)
        c, s = np.cos(theta), np.sin(theta)

        R = np.zeros((2, 2))
        R[0][0] = c
        R[0][1] = -s
        R[1][0] = s
        R[1][1] = c

        for i in range(0, len(self.dynamicPoints)):

            omitZ = np.zeros((2, 1))
            omitZ[0] = self.dynamicPoints[i][1]
            omitZ[1] = self.dynamicPoints[i][2]
            rot_D = np.matmul(R, omitZ)

            self.dynamicPoints[i][1] = rot_D[0]
            self.dynamicPoints[i][2] = rot_D[1]

    def error(self):
        i = 0
        errorDistance = 0
        while i <= 1:
            dynamicI = (interpolate.splev(i, self.tck_dynamic))
            staticI = (interpolate.splev(i, self.tck_static))
            # print("Our dynamic value: " + str(dynamicI) + " our static value : " + str(staticI))
            # distanceX = dynamicI[0] - staticI[0]
            # distanceY = dynamicI[1] - staticI[1]
            #   d = np.(distanceX, distanceY)
            dynamicNP = np.array(dynamicI)
            staticNP = np.array(staticI)
          # print("Our dynamic: " + str(dynamicNP))
           #print("Our static: " + str(staticNP))
            d = dynamicNP - staticNP
            errorDistance += np.linalg.norm(d)
            i += 0.01
        return errorDistance

    def write(self, filename):
        f = open(filename + ".ply", "w+")
        f.write("ply\n" + "format ascii 1.0\n" + "element vertex " + str(len(self.dynamicPoints)
           ) + "\n" + "property float x\n" + "property float y\n" + "property float z\n" + "property uchar red\n" + "property uchar green\n" + "property uchar blue\n" + "end_header\n")
        domain = int(len(self.dynamicPoints))
        for i in range(int(domain)):
            for j in range(0, 3):
                f.write(str(self.dynamicPoints[i][j]) + " ")
            for p in range(0, 3):
                if p < 2:
                    f.write(str(int(255)) + " ")
                else:
                    f.write(str(int(0)))
            f.write("\n")
        f.close()