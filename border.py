from __future__ import print_function, division
import sip
sip.setapi("QString", 2)
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
        self.vtk_widget = QVtkLaura(self.ui.vtk_frame, self)
        self.ui.vtk_layout = QtGui.QHBoxLayout()
        self.ui.vtk_layout.addWidget(self.vtk_widget)
        self.ui.vtk_layout.setContentsMargins(0,0,0,0)
        self.ui.vtk_frame.setLayout(self.ui.vtk_layout)
        self.ui.slider_opacity.valueChanged.connect(self.vtk_widget.change_opacity)
        self.ui.button_select_color.clicked.connect(self.show_color_dialog)
        self.ui.button_load_3D.clicked.connect(self.dialog_3D)
        self.ui.button_load_proba.clicked.connect(self.dialog_prob)
        self.ui.value_min_proba.valueChanged.connect(self.vtk_widget.change_min_val)

    def initialize(self):
        self.vtk_widget.start()

    def show_color_dialog(self):
        new_color= QtGui.QColorDialog.getColor()
        r,g,b, _ = new_color.getRgb()
        self.vtk_widget.change_prob_color(r,g,b)

    def dialog_3D(self):
        new_file=QtGui.QFileDialog.getOpenFileName(self, "Open 3D Image", "" , "Image Files (*.nii *.nii.gz)")
        self.vtk_widget.change_dialog_3D(new_file)


    def dialog_prob(self):
        new_file2 = QtGui.QFileDialog.getOpenFileName(self, "Open Probabilistic Image", "", "Image Files (*.nii *.nii.gz)")
        self.vtk_widget.change_dialog_prob(new_file2)

    def set_min_val(self,new_val):
        self.ui.value_min_proba.setValue(new_val)




class QVtkLaura(QtGui.QFrame):
    def __init__(self,parent, app):
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
        self.app = app


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
        outline.SetInputData(self.rdr.GetOutput())
        outline_mapper = vtk.vtkPolyDataMapper()
        outline_mapper.SetInputConnection(outline.GetOutputPort())
        self.outline_actor = vtk.vtkActor()
        self.outline_actor.SetMapper(outline_mapper)
        self.outline_actor.GetProperty().SetColor(1,1,1)
        self.outline = outline
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
        self.rdr2=rdr2
        self.b0 = rdr2.GetOutput()
        self.iso_surfaces()
        self.opacity()

    def widget(self):
        img = vtk.vtkImagePlaneWidget()
        img.SetInputData(self.rdr.GetOutput())
        img.SetInteractor(self.interactor)
        img_data = self.rdr.GetOutput()
        dimensions = img_data.GetDimensions()
        mid_point=int(dimensions[1]/2)
        img.SetSliceIndex(mid_point)
        img.On()
        self.img = img

    def iso_surfaces(self):
        min_s, max_s = self.b0.GetScalarRange()
        contours = vtk.vtkContourFilter()
        contours.SetInputData(self.b0)
        contours.GenerateValues(5, (max_s/5, max_s))
        print (max_s)
        contours_mapper = vtk.vtkPolyDataMapper()
        contours_mapper.SetInputConnection(contours.GetOutputPort())
        contours_mapper.ScalarVisibilityOff()
        self.contours_actor = vtk.vtkActor()
        self.contours_actor.SetMapper(contours_mapper)
        self.renderer.AddActor(self.contours_actor)
        self.contours =contours
        self.app.set_min_val(max_s / 5)

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

    def change_dialog_3D(self, load_3d):
        rdr = vtk.vtkNIFTIImageReader()
        rdr.SetFileName(load_3d)
        rdr.Update()
        self.img.SetInputData(rdr.GetOutput())
        self.outline.SetInputData(rdr.GetOutput())
        self.render_window.Render()
        self.rdr = rdr

    def change_dialog_prob(self, load_prob):
        rdr2 =vtk.vtkNIFTIImageReader()
        rdr2.SetFileName(load_prob)
        rdr2.Update()
        info=rdr2.GetOutput()
        min_s, max_s= info.GetScalarRange()
        self.contours.GenerateValues(5, (min_s, max_s))
        self.contours.SetInputData(rdr2.GetOutput())
        self.render_window.Render()
        self.rdr2=rdr2

    def change_min_val(self, value):
        val=self.rdr2.GetOutput()
        minimum, maximum =val.GetScalarRange()
        self.contours.GenerateValues(5, (value, maximum))
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