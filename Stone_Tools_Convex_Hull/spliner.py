from plyfile import PlyData, PlyElement
import os
import numpy as np
import random
import math
from Matching import Matching
from scipy.spatial import ConvexHull
from scipy import interpolate


# Parameters
distanceThreshold = 0.01
numRansacTrials = 100
numRuns = 0

def distance(point, plane):
    return abs(np.dot(plane[1], plane[0] - point))


def checkInliers(points, plane):
    nPnts = points.shape[0]
    inliers = []
    for i in range(nPnts):
        if distance(points[i], plane) < distanceThreshold:
            inliers.append(i)
    return inliers


def estimatePlane(p1, p2, p3):
    n = np.cross(p3 - p1, p2 - p1)
    n = n / np.linalg.norm(n)
    return (p1, n)


def estimatePlaneRansac(points):
    # RANSAC trials
    nPnts = points.shape[0]
    bestInliers = []
    bestPlane = (points[0], points[1])
    for t in range(numRansacTrials):
        ix = random.sample(range(nPnts), 3)
        p1 = points[ix[0]]
        p2 = points[ix[1]]
        p3 = points[ix[2]]
        plane = estimatePlane(p1, p2, p3)
        inliers = checkInliers(points, plane)
        if len(inliers) > len(bestInliers):
            bestInliers = inliers
            bestPlane = plane
            print(len(bestInliers))
    return bestPlane


def project(point, plane):
    norm = plane[1]
    orig = plane[0]
    scale = np.dot(orig, norm) / np.dot(point, norm)
    return scale * point


def write(vertices, colours, filename):
    f = open(filename + ".ply", "w+")
    f.write("ply\n" + "format ascii 1.0\n" + "element vertex " + str(vertices.size/3) + "\n" + "property float x\n" + "property float y\n" + "property float z\n" + "property uchar red\n" + "property uchar green\n" + "property uchar blue\n" + "end_header\n")
    domain = int(vertices.size)/3
    for i in range(int(domain)):
        for j in range(0, 3):
            f.write(str(vertices[i][j]) + " ")
        for p in range(0, 3):
            if p < 2:
                f.write(str(int(255)) + " ")
            else:
                f.write(str(int(0)))
        f.write("\n")
    f.close()



def curvature():
    return

def polar_coordinates(values):
    #given a vector of values
    print("Size of values: " + str(values.size))
    size = int(values.size/3)
    polar = np.zeros((size, 2))
    for i in range(size):
        r = math.sqrt(pow(values[i][1], 2) + pow(values[i][2], 2))
        theta = math.atan(values[i][2]/values[i][1])
        polar[i][0] = r
        polar[i][1] = theta
    return polar





def error():
    i = 0

    errorDistance = 0
    while(i <= 1):

        dynamicI = (interpolate.splev(i, tck_dynamic))
        staticI = (interpolate.splev(i, tck_static))
       # print("Our dynamic value: " + str(dynamicI) + " our static value : " + str(staticI))
       # distanceX = dynamicI[0] - staticI[0]
        #distanceY = dynamicI[1] - staticI[1]
     #   d = np.(distanceX, distanceY)
        dynamicNP = np.array(dynamicI)
        staticNP = np.array(staticI)
        print("Our dynamic: " + str(dynamicNP))
        print("Our static: " + str(staticNP))
        d = dynamicNP - staticNP
        errorDistance += np.linalg.norm(d)
        i += 0.01

def match(src, tgt):
    # Read in source ply data
    print(' - Reading data')
    ply = PlyData.read(src)
    plyTgt = PlyData.read(tgt)

    numVertices = ply['vertex'].count
    srcPts = np.zeros((numVertices, 3))
    dynamicSize = plyTgt['vertex'].count

    #get the convex hull
    srcColours = np.zeros((numVertices, 3))
    dynamic_colours = np.zeros((dynamicSize, 3))
    x = []
    y = []
    for i in range(numVertices):
        srcPts[i][0] = ply['vertex']['x'][i]
        srcPts[i][1] = ply['vertex']['y'][i]
        srcPts[i][2] = ply['vertex']['z'][i]
        srcColours[i][0] = ply['vertex']['red'][i]
        srcColours[i][1] = ply['vertex']['green'][i]
        srcColours[i][1] = ply['vertex']['blue'][i]

        x.append(srcPts[i][1])
        y.append(srcPts[i][2])
    ##compute the spline.
   # tck, u = interpolate.splprep([x, y], s = 0, per=true)
    ##get xi, yi


    # print(x)

    dynamicPoints = np.zeros((dynamicSize, 3))
    dynamic_x = []
    dynamic_y = []
    for i in range(dynamicSize):
        dynamicPoints[i][0] = plyTgt['vertex'][i][0]
        dynamicPoints[i][1] = plyTgt['vertex'][i][1]
        dynamicPoints[i][2] = plyTgt['vertex'][i][2]
        dynamic_x.append(dynamicPoints[i][1])
        dynamic_y.append(dynamicPoints[i][2])
        dynamic_colours[i][0] = plyTgt['vertex']['red'][i]
        dynamic_colours[i][1] = plyTgt['vertex']['green'][i]
        dynamic_colours[i][2] = plyTgt['vertex']['blue'][i]

    x1 = np.array(x)
    x2 = np.array(y)
    dynamic_x = np.array(dynamic_x)
    dynamic_y = np.array(dynamic_y)
    dynamic_x = np.r_[dynamic_x, dynamic_x[0]]
    dynamic_y = np.r_[dynamic_y, dynamic_y[0]]
    x1 = np.r_[x1, x1[0]]
    x2 = np.r_[x2, x2[0]]

    print(x1.size)
    # fit splines to x=f(u) and y=g(u), treating both as periodic. also note that s=0
    # is needed in order to force the spline fit to pass through all the input points.
    tck_static, u_static = interpolate.splprep([x1, x2], s=0, per=True)

    # evaluate the spline fits for 1000 evenly spaced distance values
    xi, yi = interpolate.splev(np.linspace(0, 1, 1000), tck_static)
    tck_dynamic, u_dynamic = interpolate.splprep([dynamic_x, dynamic_y], s=0, per=True)
    dynamic_xi, dynamic_yi = interpolate.splev(np.linspace(0, 1, 1000), tck_dynamic)
    # plot the result

    # print(errorDistance)
    # print(t)
   # t = interpolate.splev(2, tck_dynamic)
    #print("this is our t : " + str(t))
    vertices = np.zeros((1000, 3))
  #  m = Matching(tck_static, tck_dynamic, dynamic_x, dynamic_y, x1, x2)
    m = Matching(srcPts, dynamicPoints, dynamic_colours)
    m.run()


#    m.run()
     # m.print()
    #print("this is our t: " + str(t))
    dynamic_vertices = np.zeros((1000, 3))
    save = np.zeros((100, 3))
    saveColours = np.zeros((100, 3))
    #
    #for i in range(100):
    #    save[i][0] = t[i][0]
     #   save[i][1] = t[i][1]
      #  save[i][2] = 0
      #  saveColours[i][0] = 255


    for i in range(1000):
        vertices[i][1] = xi[i]
        vertices[i][2] = yi[i]
        vertices[i][0] = 0
        dynamic_vertices[i][1] = dynamic_xi[i]
        dynamic_vertices[i][2] = dynamic_yi[i]
        dynamic_vertices[i][0] = 0

   # for i in range(numVertices):
       # tgtPts[i] = srcPts[i]
       # print(srcPts[i])
    # Update the Ply file data
    p = polar_coordinates(vertices)
    print("This is our p: ")
    print(p)
    print(' - Writing data')

    # Write the result
    #write(save, saveColours, "Polar")
    #write(vertices, srcColours, "spline" + str(numRuns))
   # write(dynamic_vertices, dynamic_colours, "dynamic_spline" + str(numRuns))
   # ply.write(vertices)
def matching(dynamic, static):
    # Read in source ply data
    print(' - Reading data')
    staticPly = PlyData.read(static)
    dynamicPly = PlyData.read(dynamic)
    numVertices = staticPly['vertex'].count
    staticSpline = np.zeros((numVertices, 3))
    dynamicSpline = np.zeros((numVertices, 3))

    for i in range(numVertices):
        staticSpline[i][0] = staticPly['vertex']['x'][0]
        staticSpline[i][1] = staticPly['vertex']['y'][1]
        staticSpline[i][2] = staticPly['vertex']['z'][2]
        dynamicSpline[i][0] = dynamicPly['vertex']['x'][0]
        dynamicSpline[i][1] = dynamicPly['vertex']['y'][1]
        dynamicSpline[i][2] = dynamicPly['vertex']['z'][2]


    polarStatic = polar_coordinates(staticSpline)
    polarDynamic = polar_coordinates(dynamicSpline)
    print(polarStatic)
    print(polarDynamic)
    #match = Matching(polarStatic, polarDynamic)
    #match.match()




def approximate_spline():
    for f in os.listdir('output'):
     if os.path.isdir('output/' + f):
        print(f)
        src = 'output/' + f + '/' + f + '_static_point_cloud.ply'
        tgt = 'output/' + f + '/' + f + '_point_cloud_planified.ply'
        spline(src, tgt)
        numRuns += 1


def match_hulls():
    for f in os.listdir('output'):
        if os.path.isdir('output/' + f):


            print(f)
            static =  'output/' + f + '/' + f + '_static_point_cloud.ply'

            dynamic = 'output/' + f + '/' + f + '_dynamic_point_cloud.ply'
            tgt = 'output/' + f + '/' + f + '_point_cloud_planified.ply'

            print(static)
            print(dynamic)
            match(static, dynamic)
             #atch(static, tgt)
match_hulls()