
from __future__ import print_function, division
import vtk
import sys, os
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt4 import QtCore, QtGui, uic

class LauraApp(QtGui.QMainWindow):
    def __init__(self):
        #Parent constructor
        super(LauraApp,self).__init__()
        self.vtk_widget = None
        self.ui = None
        self.setup()

    def setup(self):
        import laura_gui
        self.ui = laura_gui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.vtk_widget = QVtkLaura(self.ui.vtk_frame)
        self.ui.vtk_layout = QtGui.QHBoxLayout()
        self.ui.vtk_layout.addWidget(self.vtk_widget)
        self.ui.vtk_layout.setContentsMargins(0,0,0,0)
        self.ui.vtk_frame.setLayout(self.ui.vtk_layout)
        self.ui.slider_opacity.valueChanged.connect(self.vtk_widget.change_opacity)
        self.ui.button_select_color.clicked.connect(self.show_color_dialog)

    def initialize(self):
        self.vtk_widget.start()

    def show_color_dialog(self):
        new_color= QtGui.QColorDialog.getColor()
        r,g,b, _ = new_color.getRgb()
        self.vtk_widget.change_prob_color(r,g,b)

class QVtkLaura(QtGui.QFrame):
    def __init__(self,parent):
        super(QVtkLaura,self).__init__(parent)
        interactor = QVTKRenderWindowInteractor(self)
        self.layout = QtGui.QHBoxLayout()
        self.layout.addWidget(interactor)
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.renderer=None
        self.interactor=interactor
        self.render_window=interactor.GetRenderWindow()
        self.rdr=None
        self.b0=None
        self.setup_pipeline()


    def setup_pipeline(self):
        self.renderer = vtk.vtkRenderer()
        self.render_window.AddRenderer(self.renderer)
        self.interactor.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.render_window.SetInteractor(self.interactor)
        self.renderer.SetBackground(0.2,0.2,0.2)
        camara = self.renderer.GetActiveCamera()
        camara.SetPosition(0,1,0)
        camara.SetFocalPoint(1,0,0)
        camara.SetViewUp(0,0,-1)

    def create_outline(self):
        outline = vtk.vtkOutlineFilter()
        self.b0 = self.rdr.GetOutput()
        outline.SetInputConnection(self.rdr.GetOutputPort())
        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        self.outline_actor = vtk.vtkActor()
        self.outline_actor.SetMapper(outline_mapper)
        self.outline_actor.GetProperty().SetColor(1,1,1)
        self.renderer.AddActor(self.outline_actor)


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
        img_data = self.rdr.GetOutput()
        dimensions = img_data.GetDimensions()
        mid_point=int(dimensions[1]/2)
        img.SetSliceIndex(mid_point)
        img.On()

    def iso_surfaces(self):
        min_s, max_s = self.b0.GetScalarRange()
        contours = vtk.vtkContourFilter()
        contours.SetInputData(self.b0)
        contours.GenerateValues(5, (min_s, max_s))
        contours_mapper = vtk.vtkPolyDataMapper()
        contours_mapper.SetInputConnection(contours.GetOutputPort())
        contours_mapper.ScalarVisibilityOff()
        self.contours_actor = vtk.vtkActor()
        self.contours_actor.SetMapper(contours_mapper)
        self.renderer.AddActor(self.contours_actor)


    def opacity(self):
        self.contours_actor.GetProperty().SetOpacity(0.3)
        self.render_window.Render()

    def start(self):
        self.interactor.Initialize()
        self.render_window.Render()
        self.renderer.ResetCamera()
        self.interactor.Start()

    def change_opacity(self, new_opacity):
        self.contours_actor.GetProperty().SetOpacity(new_opacity/100)
        self.render_window.Render()

    def change_prob_color(self,r,g,b):
        self.contours_actor.GetProperty().SetColor(r/255,g/255,b/255)
        self.render_window.Render()

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))

    # Recompile ui
    with open("laura_gui.ui") as ui_file:
        with open("laura_gui.py","w") as py_ui_file:
            uic.compileUi(ui_file,py_ui_file)



    default_img="/Users/LauraGarcia/Documents/IMEXHS/proba_seg1/fdt_paths.nii.gz"
    default_3D="/Users/LauraGarcia/Documents/IMEXHS/proba_seg1/unido.nii.gz"

    if (len(sys.argv) > 2):
        img_3d = sys.argv[1]
        img_prob = sys.argv[2]
    else:
        img_prob = default_img
        img_3d = default_3D



    app = QtGui.QApplication([])
    prob_window = LauraApp()
    prob_window.show()
    prob_window.initialize()
    prob_window.vtk_widget.load_data_3d(img_3d)
    prob_window.vtk_widget.load_data_prob(img_prob)

    app.exec_()