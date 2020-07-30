## 简介
本项目展示使用[AnalyticDB PostgreSQL版](https://cn.aliyun.com/product/gpdb)搭建基于AI算法的视频, 图像, 文本等非结构化数据分析的的系统.
目前demo包含:

    1. 基于内容的以图搜图
    2. 人脸识别/人脸检索
    3. 商品属性识别和多维度搜索
    4. 单轮问答系统
    
    
介绍文档:
    [<<使用AnalyticDB轻松实现以图搜图和人脸检索>>](https://developer.aliyun.com/article/765982?spm=a2c6h.13148508.0.0.7f4d4f0eAsgEzv)
    
## 使用方法:
1. 首先需要获取AnalyticDB PostgreSQL版连接信息 获得AnalyticDB连接串. 可以加入下方钉钉群1元试用. 
2. 运行demo

```commandline
cd $PROJ_DIR
pip install -r requirements.txt
cp config/config_template config/config.yml
# 将链接信息填入config.yml
python app.py
```
然后就可以使用chrome浏览器打开 localhost:<demo_端口号> 来访问demo服务.

有问题可以加入AnalyticDB的向量团队钉钉沟通群。

<img src="doc/DingTalkQR.png" height="256"/>

## License
MIT License

