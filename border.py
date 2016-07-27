
from __future__ import print_function, division
import vtk
import os
import sys

class laura:
    def __init__(self):
        self.renderer=None
        self.interactor=None
        self.render_window=None
        self.rdr=None
        self.b0=None
        self.setup_pipeline()


    def setup_pipeline(self):
        self.renderer = vtk.vtkRenderer()
        self.render_window=vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.render_window.SetInteractor(self.interactor)
        self.renderer.SetBackground(0.2,0.2,0.2)
        camara = self.renderer.GetActiveCamera()
        camara.SetPosition(0,1,0)
        camara.SetFocalPoint(1,0,0)
        camara.SetViewUp(0,0,-1)
        self.render_window.Start()
        self.interactor.Initialize()
        self.render_window.Render()

    def create_outline(self):
        outline = vtk.vtkOutlineFilter()
        self.b0 = self.rdr.GetOutput()
        outline.SetInputConnection(self.rdr.GetOutputPort())
        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        self.outline_actor = vtk.vtkActor()
        self.outline_actor.SetMapper(outline_mapper)
        self.outline_actor.GetProperty().SetColor(1,1,1)

    def load_data_3d(self, img_3d):
        rdr = vtk.vtkNIFTIImageReader()
        rdr.SetFileName(img_3d)
        rdr.Update()
        rdr.GetOutput()
        self.rdr=rdr
        print(rdr.GetOutput())
        outline_actor = self.create_outline()
        self.renderer.AddActor(outline_actor)
        self.widget()
        self.renderer.ResetCamera()
        self.render_window.Render()

    def load_data_prob(self, img_prob):
        rdr2 = vtk.vtkNIFTIImageReader()
        rdr2.SetFileName(img_prob)
        rdr2.Update()
        self.b0 = rdr2.GetOutput()
        self.iso_surfaces()
        self.opacity()

    def widget(self):
        img = vtk.vtkImagePlaneWidget()
        img.SetInputConnection(self.rdr.GetOutputPort())
        img.SetInteractor(self.interactor)
        img.SetSliceIndex(250)
        img.On()

    def iso_surfaces(self):
        min_s, max_s = self.b0.GetScalarRange()
        contours = vtk.vtkContourFilter()
        contours.SetInputData(self.b0)
        contours.GenerateValues(5, (min_s, max_s))
        contours_mapper = vtk.vtkPolyDataMapper()
        contours_mapper.SetInputConnection(contours.GetOutputPort())
        self.contours_actor = vtk.vtkActor()
        self.contours_actor.SetMapper(contours_mapper)
        self.renderer.AddActor(self.contours_actor)


    def opacity(self):
        self.contours_actor.GetProperty().SetOpacity(0.3)
        self.render_window.Render()

    def start(self):
        self.renderer.AddActor(self.outline_actor)
        self.render_window.Render()
        self.renderer.ResetCamera()
        self.interactor.Start()

if __name__ == "__main__":
    default_img="/Users/LauraGarcia/Documents/IMEXHS/proba_seg1/fdt_paths.nii.gz"
    default_3D="/Users/LauraGarcia/Documents/IMEXHS/proba_seg1/unido.nii.gz"
    prob= laura()
    if (len(sys.argv) > 2):
        img_3d = sys.argv[1]
        img_prob = sys.argv[2]
    else:
        img_prob = default_img
        img_3d = default_3D
    prob.load_data_3d(img_3d)
    prob.load_data_prob(img_prob)
    prob.start()
