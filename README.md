# 数据备份工具
通过配置控制并自动备份指定数据。

## 使用方法：

- 在config.json中配置备份路径、备份目标以及检测进程。
- 双击exe文件开始备份。

## 配置格式：

```json
{
    "backupPath":"E:\\备份文件存放路径",
    "backupList":[
        {
            "name":"备份1",
            "path":[
                "C:\\路径1",
                "C:\\路径2"
            ],
            "process":[
                "进程1.exe",
                "进程2.exe"
            ],
            "enabled":true
        },
        {
            "name":"备份2",
            "path":["C:\\路径3"],
            "process":["进程3.exe"],
            "enabled":true
        },
        {
            "name":"备份3",
            "path":["D:\\路径4"],
            "process":[],
            "enabled":true
        }
    ]
}
```



































