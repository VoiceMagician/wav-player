# 多文件文件播放脚本
# 生成程序代码: Pyinstaller -F .\main.py
# 教程:
# 1. 打开exe文件
# 2. 复制读取文件夹地址, 选择文件类型
# 3. 选择开始播放序列号, 一般从0开始, 如果该文件夹之前播放过则取之前最后的序列号
# 4. 按下键盘p键加回车开始播放, 播放过程可以按p键加回车暂停或继续播放, 过程中可以
# 按下q键离开
# 5. 把窗口关闭，现在线程还有问题
from scipy.io.wavfile import read
from pathlib import Path
from pydub import AudioSegment
from scipy import signal

import numpy as np
import sounddevice as sd
import soundfile as sf
import threading
import time
import sys

file_type = ['wav', 'mp3', 'flac']
is_pause = True
sample_rate = 16000 # 采样率
support_fs = [16000, 44100, 48000] # 多采样率
stream_out = []
buffer = []
play_file_index = 0
frame_move = 256

# 查询设备
def query_devices(device, kind):
    try:
        caps = sd.query_devices(device, kind=kind)
    except ValueError:
        sys.exit(1)
    return caps

def playorpause():
    global is_pause
    while(1):
        key = input("按下p+回车键暂停/播放, q+回车键退出")
        if ('p' == key):
            if is_pause:
                is_pause = False
                print("继续播放")
            else:
                is_pause = True
                print("暂停播放")
        elif ('q' == key):
            print('退出程序')
            sys.exit(1)

def output_play():
    global play_file_index
    while(1):
        if not (is_pause): # 没有暂停时候进行播放
            if find_type == file_type[0]:   # wav
                (fs_rir, data) = read(file_list[play_file_index])
            elif find_type == file_type[1]: # mp3
                song = AudioSegment.from_mp3(file_list[play_file_index])
                data = np.array(song.get_array_of_samples())
            elif find_type == file_type[2]: # flac
                data, fs = sf.read(file_list[play_file_index])
            if ('int16' == data.dtype):
                data = (data / 32768)
            # TODO:后面适配多通道
            if (len(data.shape) != 1):
                data = data[:, 0] # 多通道变单通道, 取第0通道
            if (True == sound_change):
                for i in range(len(b_list)): # eq
                    data = signal.filtfilt(b_list[i], a_list[i], data)
                data = data * 5 # 幅度补偿
                if (np.max(np.abs(data)) > 1): # 归一化
                    data = data / np.max(np.abs(data))
            data = data.astype(np.float32)
            print("\r序列号: {}, 文件名称: {}, 文件长度: {}s".format(\
                play_file_index, file_list[play_file_index], int(len(data)/sample_rate)),\
                end='')
            frames_num = int(len(data) / frame_move)
            for i in range(frames_num):
                stream_out.write(data[int(i*frame_move):int((i+1)*frame_move)])
            play_file_index = play_file_index + 1
            if (play_file_index >= files_num):
                print('\n所有文件播放完毕')
                break
            #if buffer != []:
            #    while len(buffer) > 10: # 防止缓冲过大
            #        del(buffer[0])
            #    frame = buffer[0] # 获取缓冲中的第一帧
            #    del(buffer[0]) # 删除第一帧
            #    stream_out.write(frame) # 输出播放器
            #print(file_list[play_file_index])
            #sd.play(file_list[play_file_index], sample_rate)
            #sd.wait()
            #play_file_index = play_file_index + 1

# 获取所有音频文件
def files_find(check_path, file_type='wav'):
    all_files = []
    for path in Path(check_path).rglob('*.'+file_type):
        all_files.append(str(path.resolve()))
    print('找到文件个数为:', len(all_files))

    return all_files

def peak_filter_iir(f0, gain=0., Q=1., fs=192000):
    """
    根据PEQ参数设计二阶IIR数字peak滤波器，默认采样率192k
    :param f0: 中心频率
    :param gain: 峰值增益，正值为peak filter,负值为notch filter
    :param Q: 峰值带宽
    :param fs: 系统采样率
    :return: 双二阶滤波器系数b, a
    """
    A = np.sqrt(10 ** (gain / 20))
    w0 = 2 * np.pi * f0 / fs
    alpha = np.sin(w0) / (2 * Q)

    b0 = 1 + alpha * A
    b1 = -2 * np.cos(w0)
    b2 = 1 - alpha * A
    a0 = 1 + alpha / A
    a1 = -2 * np.cos(w0)
    a2 = 1 - alpha / A
    b = np.array([b0, b1, b2])
    a = np.array([a0, a1, a2])

    #h = np.hstack((b / a[0], a / a[0])) # sos 类型

    return b, a

if __name__ == '__main__':
    print("多文件播放程序-V0.3")
    # 可供选择的输出方式
    device_list = sd.query_devices()
    #print(device_list)
    ##print('选择你想要播放的设备:')
    #play_device_index = input('选择你想要播放的设备: ')
    #choose_device = device_list[int(play_device_index)]
    #print('设备名称:', choose_device['name'])
    #caps = query_devices(choose_device, "output")
    # 默认输出
    caps = sd.default.device[1]
    print('默认播放设备名称:', device_list[caps]['name'])
    print('选择想要播放的采样率')
    for i in range(len(support_fs)):
        print(str(i), support_fs[i])
    fs_type = input('请选择: ')
    sample_rate = support_fs[int(fs_type)]
    frame_move = int(0.008 * sample_rate)
    print('采样率选择:', sample_rate, 'Hz')
    channel = 1
    stream_out = sd.OutputStream(
        device=None,
        samplerate=sample_rate,
        channels=channel)
    stream_out.start()

    # EQ 只使用与16k
    sound_change = False
    flag = input('是否用于人工头播放(是请输入1):')
    if ('1' == flag):
        sound_change = True
        print('开启人工头适配')
    fc_0 = 31.25
    fc_list = np.zeros(9)
    fc_list[0] = fc_0
    for i in range(1, len(fc_list)):
        fc_list[i] = fc_list[i-1] * 2
    Q = np.sqrt(2)
    Gain_list = [0, 0, -3, -4, -6, -9, 0, 3, 6]
    b_list = []
    a_list = []
    for i in range(len(Gain_list)):
        if (0 != Gain_list[i]):
            b, a = peak_filter_iir(fc_list[i], Gain_list[i], Q, sample_rate)
            b_list.append(b)
            a_list.append(a)
    if len(b_list) != len(a_list):
        print('check a and b data')

    folder_path = input('输入文件夹地址: ')
    folder_path = folder_path.strip() # 去除前后空格
    print('--文件类型--')
    for i in range(len(file_type)):
        print(str(i), file_type[i])
    type_num = input('请选择: ')
    find_type = file_type[int(type_num)]
    print('选择文件类型:', find_type)
    file_list = files_find(folder_path, find_type)
    #files_find(r'E:\Dataset_download\Speech\zhvoice\zhaidatatang', 'mp3')
    files_num = len(file_list)
    if 0 == len(file_list):
        print('请检查文件夹路径是否正确')
    play_file_index = int(input('选择文件开始播放序列号: '))

    threads = []
    threads.append(threading.Thread(target=playorpause))
    threads.append(threading.Thread(target=output_play))

    for thread in threads:
        thread.start()