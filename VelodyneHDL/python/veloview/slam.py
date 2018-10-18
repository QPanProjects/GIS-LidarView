#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paraview.simple as smp
import applogic

import PythonQt

from PythonQt import QtGui
from paraview import vtk
from PythonQt.paraview import vvSlamConfigurationDialog

# global variable
slam = None
currentFrame = None

def configure():
    """Let the user configure a slam instance for a given source, which must already be open
     and return [start, stop] the intervall frames on which the slam should be launch
    """
    # get data
    source = applogic.getReader().GetClientSideObject()

    # execute the gui
    slamDialog = vvSlamConfigurationDialog(applogic.getMainWindow())
    if not slamDialog.exec_():
        return -1, -1

    global slam
    # Instanciation of a new vtkSlamAlgorithm
    if slam is not None:
        smp.Delete(slam)
    slam = smp.Slam()

    # initialize the nb of laser and their mapping
    NLaser = source.GetNumberOfChannels()
    laserIdMapping = range(NLaser * 2)
    source.GetLaserIdMapping(laserIdMapping)
    slam.GetClientSideObject().SetSensorCalibration(laserIdMapping, NLaser)

    slam.GetClientSideObject().Set_DisplayMode(True)

    # Set parameter selected by the user

    # mode
    if slamDialog.frameMode == vvSlamConfigurationDialog.FRAME_RANGE:
        start = slamDialog.frameStart
        stop = slamDialog.frameStop
    elif slamDialog.frameMode == vvSlamConfigurationDialog.ALL_FRAMES:
        start = applogic.app.scene.StartTime
        stop = applogic.app.scene.EndTime

    stop = min(stop, source.GetNumberOfFrames() - 1)

    motionModel = 0
    if slamDialog.MotionModel:
        motionModel = 1
    if slamDialog.MotionModelAndGPS:
        motionModel = 2

    # General
    slam.GetClientSideObject().Set_RollingGrid_Grid_NbVoxel([slamDialog.NbVoxel,slamDialog.NbVoxel,slamDialog.NbVoxel])
    slam.GetClientSideObject().Set_AngleResolution(slamDialog.AngleResolution * vtk.vtkMath.Pi() / 180)
    slam.GetClientSideObject().Set_MaxDistanceForICPMatching(slamDialog.MaxDistanceForICPMatching)
    slam.GetClientSideObject().Set_Lambda0(slamDialog.Lambda0)
    slam.GetClientSideObject().Set_LambdaRatio(slamDialog.LambdaRatio)
    slam.GetClientSideObject().Set_FastSlam(slamDialog.FastSlam)
    slam.GetClientSideObject().SetMotionModel(motionModel)
    slam.GetClientSideObject().SetUndistortion(slamDialog.Undistortion)
    slam.GetClientSideObject().SetMaxVelocityAcceleration(slamDialog.MaxVelocityAcc)
    slam.GetClientSideObject().SetMaxAngleAcceleration(slamDialog.MaxAngleAcc)

    # Keypoint
    slam.GetClientSideObject().Set_Keypoint_MaxEdgePerScanLine(slamDialog.Keypoint_MaxEdgePerScanLine)
    slam.GetClientSideObject().Set_Keypoint_MaxPlanarsPerScanLine(slamDialog.Keypoint_MaxPlanarsPerScanLine)
    slam.GetClientSideObject().Set_Keypoint_MinDistanceToSensor(slamDialog.Keypoint_MinDistanceToSensor)
    slam.GetClientSideObject().Set_Keypoint_EdgeSinAngleThreshold(slamDialog.Keypoint_EdgeSinAngleThreshold)
    slam.GetClientSideObject().Set_Keypoint_PlaneSinAngleThreshold(slamDialog.Keypoint_PlaneSinAngleThreshold)
    slam.GetClientSideObject().Set_Keypoint_EdgeDepthGapThreshold(slamDialog.Keypoint_EdgeDepthGapThreshold)
    # Egomotion
    slam.GetClientSideObject().Set_EgoMotionLMMaxIter(slamDialog.EgoMotion_LMMaxIter)
    slam.GetClientSideObject().Set_EgoMotionICPMaxIter(slamDialog.EgoMotion_ICPMaxIter)
    slam.GetClientSideObject().Set_EgoMotionLineDistanceNbrNeighbors(slamDialog.EgoMotion_LineDistance_k)
    slam.GetClientSideObject().Set_EgoMotionLineDistancefactor(slamDialog.EgoMotion_LineDistance_factor)
    slam.GetClientSideObject().Set_EgoMotionPlaneDistanceNbrNeighbors(slamDialog.EgoMotion_PlaneDistance_k)
    slam.GetClientSideObject().Set_EgoMotionPlaneDistancefactor1(slamDialog.EgoMotion_PlaneDistance_factor1)
    slam.GetClientSideObject().Set_EgoMotionPlaneDistancefactor2(slamDialog.EgoMotion_PlaneDistance_factor2)
    slam.GetClientSideObject().Set_EgoMotionMaxLineDistance(slamDialog.EgoMotion_Line_Max_Distance)
    slam.GetClientSideObject().Set_EgoMotionMaxPlaneDistance(slamDialog.EgoMotion_Plane_Max_Distance)
    slam.GetClientSideObject().Set_EgoMotionMinimumLineNeighborRejection(slamDialog.EgoMotionMinimalLineNeighborRejection)
    # Mapping
    slam.GetClientSideObject().Set_MappingLMMaxIter(slamDialog.Mapping_LMMaxIter)
    slam.GetClientSideObject().Set_MappingICPMaxIter(slamDialog.Mapping_ICPMaxIter)
    slam.GetClientSideObject().Set_MappingLineDistanceNbrNeighbors(slamDialog.Mapping_LineDistance_k)
    slam.GetClientSideObject().Set_MappingLineDistancefactor(slamDialog.Mapping_LineDistance_factor)
    slam.GetClientSideObject().Set_MappingPlaneDistanceNbrNeighbors(slamDialog.Mapping_PlaneDistance_k)
    slam.GetClientSideObject().Set_MappingPlaneDistancefactor1(slamDialog.Mapping_PlaneDistance_factor1)
    slam.GetClientSideObject().Set_MappingPlaneDistancefactor2(slamDialog.Mapping_PlaneDistance_factor2)
    slam.GetClientSideObject().Set_MappingMaxLineDistance(slamDialog.Mapping_Line_Max_Distance)
    slam.GetClientSideObject().Set_MappingMaxPlaneDistance(slamDialog.Mapping_Plane_Max_Distance)
    slam.GetClientSideObject().Set_MappingMinimumLineNeighborRejection(slamDialog.MappingMinimalLineNeighborRejection)
    slam.GetClientSideObject().Set_MappingLineMaxDistInlier(slamDialog.MappingMaxDistanceInlierRejection)

    return start, stop


def stream():
    """ launch the slam on the reader current output
    """
    # get data
    source = applogic.getReader().GetClientSideObject()

    #If no data are available
    if not source :
        return

    source.Open()

    # get the current frame
    polyData = source.GetOutput()#source.GetFrame(currentFrame)
    # compute the SLAM for the current frame
    slam.GetClientSideObject().AddFrame(polyData)

    # get the transformation computed
    Tworld = range(6)
    slam.GetClientSideObject().GetWorldTransform(Tworld)
    t = polyData.GetPointData().GetArray("adjustedtime").GetTuple1(0) * 1e-6

    # convert in degree
    rx = Tworld[0] * 180 / vtk.vtkMath.Pi()
    ry = Tworld[1] * 180 / vtk.vtkMath.Pi()
    rz = Tworld[2] * 180 / vtk.vtkMath.Pi()
    tx = Tworld[3]
    ty = Tworld[4]
    tz = Tworld[5]

    # add the transform
    source.AddTransform(rx, ry, rz, tx, ty, tz, t)

    # update slam
    slam.GetClientSideObject().Update()
    smp.Show(slam[0],applogic.app.mainView)
    smp.Render()

    # Enable to visualize the debug array
    smp.SetActiveSource(slam)

    # close file
    source.Close()

    updateChartView()


def launch():
    """ Launche the slam with a gui and save the result
    """

    # get data
    source = applogic.getReader().GetClientSideObject()
    positionSource = applogic.getPosition()

    #If no data are available
    if not source :
        return


    source.Open()

    # let the user configure a new slam instance
    start, stop = configure()

    # Clam the end frame if user settled it over
    # the maximum of frames contained in the data
    stop = min(stop, source.GetNumberOfFrames() - 1)

    # If a position source is available
    # provide it to the slam algorithm
    if positionSource is not None:
        slam.GetClientSideObject().SetExternalSensorMeasures(positionSource.GetClientSideObject().GetInterpolator())

    # check if the user press on cancel
    if start ==-1:
        return

    # instanciate the progress box
    progressDialog = QtGui.QProgressDialog("Computing slam algorithm...", "Abort Slam", start, start + (stop - start), None)
    progressDialog.setModal(True)
    progressDialog.show()

    # iteration
    frameCount = 0
    for i in range(int(start), int(stop)+1):
        # get the current frame
        polyData = source.GetFramePointer(i, 0)
        # compute the SLAM for the current frame
        slam.GetClientSideObject().AddFrame(polyData)

        # update the ui
        if (progressDialog.wasCanceled):
            break

        frameCount = frameCount + 1
        progressDialog.setValue(i)

    # close file
    source.Close()

    # create Linear Interpolator()
    # and fill it with the slam outputted
    # transform parameters
    source.SetInterpolator(slam.GetClientSideObject().GetInterpolator())

    #source.SetInterpolator(slam.GetClientSideObject().GetInterpolator())
    slam.GetClientSideObject().Update()

    # Reset reader as active source so we can use the paraview toolbox to visualize the different array: density, ...
    smp.SetActiveSource(applogic.getReader())

    # Display Slam output in the overhead viewer
    smp.Show(slam[1], applogic.app.overheadView)

    # get the slam
    applogic.app.slamSave = slam

def updateChartView():
    """ Update the chartView with the slam output:
        the sensor position: X, Y, Z and orientation: pitch, roll, yaw
    """

    def setDockTitle(objName, title):
        """ helper function """
        dock = applogic.findQObjectByName(applogic.getMainWindow().children(), objName)
        dock.windowTitle = title


    # looking for the Slam
    global slam
    source = slam

    if source is  None:
        return

    # get the first port of the filter which is the trajectory
    source = source[1]

    # get the chart view
    chartViews = applogic.getChartViewProxies()

    # Add Orientation from Slam
    chartViews[1].LeftAxisTitle = "orientation (rad)"
    chartViews[1].BottomAxisTitle = "GPS time (s)"
    mychart = smp.Show(source,chartViews[1])
    mychart.SeriesVisibility.SetData(['pitch', 'roll', 'yaw'])
    setDockTitle('dockSlam_PitchRollYaw', 'Sensor Angles')
    smp.Render()

    # Add Position from Slam
    chartViews[0].LeftAxisTitle = "position (m)"
    chartViews[0].BottomAxisTitle = "GPS time (s)"
    mychart = smp.Show(source,chartViews[0])
    mychart.SeriesVisibility.SetData(['Points_X', 'Points_Y', 'Points_Z'])
    setDockTitle('dockSlam_XYZ', 'Sensor Position')
    smp.Render()
