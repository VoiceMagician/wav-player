# wav-player
因为目前主流的软件如QQ音乐、网易云音乐等对于本地音频播放支持较差，当音频文件分布在多个文件夹的时候，主流软件容易出现卡死现象，影响正常播放进度，所以编写了一个专门用于播放多文件夹音频的软件。该项目目的是解决录制深度学习真实数据没有专门适配播放器的问题。

Because the current mainstream software such as QQ Music, NetEase Cloud Music, etc. has poor support for local audio playback, when the audio files are distributed in multiple folders, the mainstream software is prone to stuck, affecting the normal playback progress, so a software specially designed for playing multi-folder audio is written. The aim of this project is to solve the problem that there is no specially adapted player for recording real data for deep learning.

## 特点
1. 支持文件夹内包含多文件夹情况
2. 文件扫描速度更快，可以支持扫描数十万个音频文件而不会卡死
3. 多种音频文件类型支持，wav、flac、MP3等
4. 随时播放暂停以及文件播放索引记录
5. 可以播放任意你想要的采样率，目前支持的有16k、44.1k、48k，根据后续需要可以增加采样率
6. 针对人工头有适配功能，只需要修改成你想要的EQ参数

## 使用方法
1. 打开exe文件
2. 选择播放的采样率, 和文件对应的采样率对齐
3. 选择是否用于人工头播放, 如果是输入1, 否则输入0
4. 复制读取文件夹地址, 选择文件类型
5. 选择开始播放序列号, 一般从0开始, 如果该文件夹之前播放过则取之前最后的序列号
6. 按下键盘p键加回车开始播放, 播放过程可以按p键加回车暂停或继续播放, 过程中可以
按下q键离开
7. 把窗口关闭，现在线程还有问题

## 更新记录
### 2023/11/22
1. 新增人工头适配方案，解决人工头播放声音低沉的问题

### 2023/11/14
1. 新增多种采样率播放，需要在播放前进行选择

### 2023/11/06
1. 新增两种文件播放: wav和flac，但是目前只支持单通道采样率16k音频

### 2023/11/03
1. 初版释放，支持播放mp3文件

## More
如果你想要生成exe文件，请确保配置了mp3相关的依赖，或者关闭mp3选项，dependent文件夹放置类mp3需要的依赖，你可以在生成exe之后将其放置在相同目录下，确保移植到其他设备的兼容性