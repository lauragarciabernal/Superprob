
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

    def leer_datos(self, img):
        rdr = vtk.vtkNIFTIImageReader()
        rdr.SetFileName(img)
        rdr.Update()
        rdr.GetOutput()
        self.rdr=rdr
        print(rdr.GetOutput())

    def setup_pipeline(self):
        self.renderer = vtk.vtkRenderer()
        self.render_window=vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.render_window.SetInteractor(self.interactor)
        self.renderer.SetBackground(0.2,0.2,0.2)
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

    def load_data(self, img):
        self.leer_datos(img)
        outline_actor = self.create_outline()
        self.renderer.AddActor(outline_actor)
        self.renderer.ResetCamera()
        self.render_window.Render()
        self.render_window.Start()
        self.widget()
        self.iso_surfaces()
        self.opacity()

    def widget(self):
        img = vtk.vtkImagePlaneWidget()
        img.SetInputConnection(self.rdr.GetOutputPort())
        img.SetInteractor(self.interactor)
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
        self.renderer.ResetCamera()
        self.render_window.Render()
        self.interactor.Start()

if __name__ == "__main__":
    default_img="/Users/LauraGarcia/Documents/IMEXHS/proba_seg1/fdt_paths.nii.gz"
    prob= laura()
    if (len(sys.argv) > 1):
        dir = sys.argv[1]
    else:
        img2 = default_img
    prob.load_data(img2)
    prob.start()
