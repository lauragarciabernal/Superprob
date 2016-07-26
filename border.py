from __future__ import print_function, division
import vtk
import os
import sys


class Laurota:
    def __init__(self):
        self.renderer = None
        self.interactor = None
        self.render_window = None
        self.setup_pipeline()

    def leer_datos(self, directory):
        os.chdir(directory)
        pl3d = vtk.vtkMultiBlockPLOT3DReader()
        xyx_file="combxyz.bin"
        q_file= "combq.bin"
        pl3d.SetXYZFileName(xyx_file)
        pl3d.SetQFileName(q_file)
        pl3d.SetScalarFunctionNumber(100)
        pl3d.SetVectorFunctionNumber(202)
        pl3d.Update()
        blocks = pl3d.GetOutput()
        b0=blocks.GetBlock(0)
        print(b0)
        return b0

    def setup_pipeline(self):
        self.renderer = vtk.vtkRenderer()
        self.render_window=vtk.vtkRenderWindow()
        self.render_window.AddRenderer(self.renderer)
        self.interactor = vtk.vtkRenderWindowInteractor()
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.render_window.SetInteractor(self.interactor)
        self.renderer.SetBackground(0.2,0.2,0.2)
        self.interactor.Initialize()

    def create_outline(self, datos):
        outline = vtk.vtkStructuredGridOutlineFilter()
        outline.SetInputData(datos)
        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        outline_actor = vtk.vtkActor()
        outline_actor.SetMapper(outline_mapper)
        outline_actor.GetProperty().SetColor(1,1,1)
        return outline_actor

    def load_data(self, directory):
        b0 = self.leer_datos(directory)
        outline_actor = self.create_outline(b0)
        self.renderer.AddActor(outline_actor)
        self.render_window.Render()
        self.renderer.ResetCamera()
        self.render_window.Render()

    def start(self):
        self.interactor.Start()

    def hola(self):
        print("Hola, soy laura")

if __name__ == "__main__":
    default_dir="/Users/LauraGarcia/Downloads/volume"
    laurita = Laurota()
    if(len(sys.argv)>1):
        dir = sys.argv[1]
    else:
        dir = default_dir
    laurita.load_data(dir)
    laurita.start()