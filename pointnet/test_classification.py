import argparse
import logging
import os
import sys
import tkinter as tk
from tkinter import filedialog

import numpy as np
import torch
from tqdm import tqdm
import importlib

from data_utils.ModelNetDataLoader import ModelNetDataLoader
from net_work import LidarServer

# 定义全局变量存储文件路径和预测结果
selected_file = None
predicted_class_name = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = BASE_DIR
sys.path.append(os.path.join(ROOT_DIR, 'models'))


def parse_args():
    '''PARAMETERS'''
    parser = argparse.ArgumentParser('Testing')
    parser.add_argument('--use_cpu', action='store_true', default=False, help='use cpu mode')
    parser.add_argument('--gpu', type=str, default='0', help='specify gpu device')
    parser.add_argument('--batch_size', type=int, default=24, help='batch size in training')
    parser.add_argument('--num_category', default=40, type=int, choices=[10, 40],
                        help='training on ModelNet10/40')
    parser.add_argument('--num_point', type=int, default=1024, help='Point Number')
    parser.add_argument('--log_dir', type=str, required=True, help='Experiment root')
    parser.add_argument('--use_normals', action='store_true', default=False, help='use normals')
    parser.add_argument('--use_uniform_sample', action='store_true', default=False, help='use uniform sampling')
    parser.add_argument('--num_votes', type=int, default=3, help='Aggregate classification scores with voting')
    return parser.parse_args()


def test(model, loader, num_class=40, vote_num=1):
    mean_correct = []
    classifier = model.eval()
    class_acc = np.zeros((num_class, 3))

    for j, (points, target) in tqdm(enumerate(loader), total=len(loader)):
        if not args.use_cpu:
            points, target = points.cuda(), target.cuda()

        points = points.transpose(2, 1)
        vote_pool = torch.zeros(target.size()[0], num_class).cuda()

        for _ in range(vote_num):
            pred, _ = classifier(points)
            vote_pool += pred
        pred = vote_pool / vote_num
        pred_choice = pred.data.max(1)[1]

        for cat in np.unique(target.cpu()):
            classacc = pred_choice[target == cat].eq(target[target == cat].long().data).cpu().sum()
            class_acc[cat, 0] += classacc.item() / float(points[target == cat].size()[0])
            class_acc[cat, 1] += 1
        correct = pred_choice.eq(target.long().data).cpu().sum()
        mean_correct.append(correct.item() / float(points.size()[0]))

    class_acc[:, 2] = class_acc[:, 0] / class_acc[:, 1]
    class_acc = np.mean(class_acc[:, 2])
    instance_acc = np.mean(mean_correct)
    return instance_acc, class_acc


def preprocess_file(file_path):
    points = np.loadtxt(file_path, delimiter=',')  # 假设每行包含点的六个特征，以逗号分隔
    points = points[:, :6]  # 选择每行的前 6 个数字作为点的特征
    points = points.transpose()  # 调整数组形状以符合模型的输入要求
    points = torch.from_numpy(points.astype(np.float32)).unsqueeze(0)  # 转换为 PyTorch 张量并添加批量维度
    return points


def read_point_cloud_file(file_path):
    points = []
    with open(file_path, 'r') as file:
        for line in file:
            values = line.strip().split(',')
            if len(values) == 6:  # 假设每行应该包含 6 个特征值
                point = [float(value) for value in values]
                points.append(point)
            else:
                print(f"Ignoring line with invalid number of values: {values}")

    return np.array(points)


def detect_single_sample(model, sample_points_file, num_class):
    model.eval()

    # 读取样本点云数据文件
    sample_points = read_point_cloud_file(sample_points_file)

    # 转换样本点云数据格式为模型所需格式
    points = torch.from_numpy(sample_points.astype(np.float32)).unsqueeze(0).transpose(2, 1)

    # 检测单个样本
    with torch.no_grad():
        if not args.use_cpu:
            points = points.cuda()

        pred, _ = model(points)
        pred_choice = pred.data.max(1)[1]
        predicted_class = pred_choice.item()
    return predicted_class


def load_shape_names_file(file_path):
    with open(file_path, 'r') as file:
        shape_names = [line.strip() for line in file]
    return shape_names


def main(args):
    def log_string(str):
        logger.info(str)
        print(str)

    '''HYPER PARAMETER'''
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu

    '''CREATE DIR'''
    experiment_dir = 'log/classification/' + args.log_dir

    '''LOG'''
    args = parse_args()
    logger = logging.getLogger("Model")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler('%s/eval.txt' % experiment_dir)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    log_string('PARAMETER ...')
    log_string(args)

    '''DATA LOADING'''
    log_string('Load dataset ...')
    data_path = 'data/modelnet40_normal_resampled/'

    test_dataset = ModelNetDataLoader(root=data_path, args=args, split='test', process_data=False)
    testDataLoader = torch.utils.data.DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False, num_workers=10)

    '''MODEL LOADING'''
    num_class = args.num_category
    model_name = os.listdir(experiment_dir + '/logs')[0].split('.')[0]
    model = importlib.import_module(model_name)

    classifier = model.get_model(num_class, normal_channel=args.use_normals)
    if not args.use_cpu:
        classifier = classifier.cuda()

    checkpoint = torch.load(str(experiment_dir) + '/checkpoints/best_model.pth')
    classifier.load_state_dict(checkpoint['model_state_dict'])

    # 加载 ModelNet 类别名称文件
    shape_names_file_path = os.path.join(data_path, 'modelnet40_shape_names.txt')
    shape_names = load_shape_names_file(shape_names_file_path)

    # 启动服务器
    server = LidarServer()

    def handle_client(client_socket):
        global selected_file

        with client_socket, client_socket.makefile('rb') as f:
            with open('lidardata_received.pcd', 'w') as output_file:
                print(f"Receiving and saving data...")
                while True:
                    # Receive each line from client
                    data = f.readline().decode('utf-8').strip()
                    if not data:
                        break  # End of file

                    # Write each line to file
                    output_file.write(data + '\n')

        # Set the received file path for classification
        selected_file = 'lidardata_received.pcd'

        print("File transfer complete.")

        # Perform prediction on the received file
        predicted_class = detect_single_sample(classifier, selected_file, num_class)
        class_name = shape_names[predicted_class]
        print(f"Predicted class for the received file: {class_name}")

    server.start_server("192.168.43.27", 12345, handle_client)


if __name__ == '__main__':
    args = parse_args()
    main(args)
