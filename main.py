import os
from open3D import displaySettings
os.environ['PYTHONHTTPSVERIFY'] = '0'

#引入QT界面
import sys
from QT import second
from PyQt5.QtWidgets import QApplication,QMainWindow,QWidget
from PyQt5.QtGui import QWindow
from PyQt5.QtCore import QTimer
import win32gui

# 主程序
if __name__ == "__main__":

    # #开启TCP网络服务接收点云数据
    # #netWork.net_work()
    #
    # file_path = 'C:\\Users\\Bamboo\\Desktop\\rabbit.pcd'
    # cloud = displaySettings.load_point_cloud_from_file(file_path)
    # centered_points, center = displaySettings.centerize_point_cloud(cloud)
    #
    # print("点云中的点数：", len(cloud.points))
    # displaySettings.visualize_point_cloud(cloud)

    # 实例化，传参
    app = QApplication(sys.argv)

    # 创建对象
    mainWindow = QMainWindow()

    # 创建ui，引用demo1文件中的Ui_MainWindow类
    ui = second.Ui_MainWindow()
    # 调用Ui_MainWindow类的setupUi，创建初始组件
    ui.setupUi(mainWindow)
    # 创建窗口
    mainWindow.show()
    # 进入程序的主循环，并通过exit函数确保主循环安全结束(该释放资源的一定要释放)
    sys.exit(app.exec_())