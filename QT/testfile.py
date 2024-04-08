import sys
import open3d as o3d
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QInputDialog, QColorDialog, QDoubleSpinBox, \
    QPushButton
from PyQt5.QtGui import QIcon
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Setup UI
        self.setWindowTitle("Point Cloud Processing Tool")
        self.setGeometry(100, 100, 800, 600)
        self.setupActions()

        # Initialize Open3D visualization
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window()

        self.pcd_path = None

    def setupActions(self):
        load_action = self.create_action("Load PCD File", self.load_pcd_file)
        save_action = self.create_action("Save PCD File", self.save_pcd_file)

        extract_ISS_action = self.create_action("Extract ISS Key Points", self.extract_ISS_key_points)

        self.add_button("Change Point Cloud Color", self.change_point_cloud_color)
        self.add_button("Change Point Cloud Size", self.change_point_cloud_size)

    def create_action(self, name, function):
        action = self.menuBar().addMenu(name)
        action.triggered.connect(function)
        return action

    def add_button(self, name, function):
        button = QPushButton(name)
        button.clicked.connect(function)
        self.setCentralWidget(button)

    def load_pcd_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PCD File", "", "PCD Files (*.pcd)")
        if file_path:
            self.pcd_path = file_path
            self.visualize_point_cloud()

    def save_pcd_file(self):
        if self.pcd_path:
            # Add saving logic here
            print("Save PCD file placeholder")
        else:
            print("No point cloud data loaded to save")

    def visualize_point_cloud(self):
        self.vis.clear_geometries()
        pcd = o3d.io.read_point_cloud(self.pcd_path)
        self.vis.add_geometry(pcd)
        self.vis.run()

    def change_point_cloud_color(self):
        if self.pcd_path:
            color_dialog = QColorDialog.getColor()
            if color_dialog.isValid():
                color = color_dialog.getRgbF()

                pcd = o3d.io.read_point_cloud(self.pcd_path)
                if hasattr(pcd, 'points'):
                    pcd.paint_uniform_color(color)
                    self.visualize_point_cloud()
            else:
                print("Invalid color selected")
        else:
            print("No point cloud data loaded to change color")

    def change_point_cloud_size(self):
        if self.pcd_path:
            custom_dialog = QInputDialog(self)
            custom_dialog.setInputMode(QInputDialog.DoubleInput)
            custom_dialog.setWindowTitle("Change Point Cloud Size")
            custom_dialog.setDoubleRange(0.1, 100.0)
            custom_dialog.setDoubleValue(1.0)

            if custom_dialog.exec_():
                size = custom_dialog.doubleValue()

                pcd = o3d.io.read_point_cloud(self.pcd_path)
                if hasattr(pcd, 'points'):
                    pcd.scale(size, center=pcd.get_center())
                    self.visualize_point_cloud()
            else:
                print("Invalid point cloud size entered")
        else:
            print("No point cloud data loaded to change size")

    def extract_ISS_key_points(self):
        if self.pcd_path:
            pcd = o3d.io.read_point_cloud(self.pcd_path)
            key_points = pcd.compute_ISS_keypoints()

            key_points_pcd = o3d.geometry.PointCloud()
            key_points_pcd.points = o3d.utility.Vector3dVector(np.asarray(pcd.points)[key_points])

            key_points_pcd.paint_uniform_color([1.0, 0.0, 0.0])

            self.vis.clear_geometries()
            self.vis.add_geometry(pcd)
            self.vis.add_geometry(key_points_pcd)
            self.vis.run()
        else:
            print("No point cloud data loaded to extract key points")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())