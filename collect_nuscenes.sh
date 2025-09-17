#!/bin/bash

start=$1
end=$2

# 检查参数数量
if [ "$#" -ne 2 ]; then
    echo "用法: $0 <起始值> <终止值>"
    exit 1
fi

# 验证是否为整数
if ! [[ "$start" =~ ^-?[0-9]+$ ]] || ! [[ "$end" =~ ^-?[0-9]+$ ]]; then
    echo "错误: 请输入有效的整数值"
    exit 1
fi

# 确保起始值不大于终止值
if [ "$start" -gt "$end" ]; then
    echo "错误: 起始值不能大于终止值"
    exit 1
fi

python nuscenes_lidarseg.py --point_num "$start" --host "172.17.0.1" --control "replay"
# python nuscenes_lidarseg.py --point_num "$start" --host "172.17.0.1" --isreload

# 主循环遍历并执行Python脚本
current=$((start+1))
while [ "$current" -le "$end" ]; do
    python nuscenes_lidarseg.py --point_num "$current" --host "172.17.0.1"
    current=$((current + 1))
done

echo "所有参数处理完成！"
