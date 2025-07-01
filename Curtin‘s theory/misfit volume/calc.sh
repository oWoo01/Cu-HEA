#!/usr/bin/bash

input_file="lc.txt"
output_file="averaged_lc.txt"

# 临时存储前四列和对应的平均第五列
declare -A data_map

# 读取文件行
while read -r line; do
    # 跳过空行
    [[ -z "$line" ]] && continue
    
    # 使用空格分割每行
    read -r col1 col2 col3 col4 col5 <<< $(echo "$line")
    
    # 将前四列组合成一个键 (可以根据实际情况修改分隔符)
    key="$col1 $col2 $col3 $col4"
    
    # 如果这个组合已经存在，将第五列的值加到该组合下
    if [[ -n "${data_map[$key]}" ]]; then
        # 计算当前组合的总和与数量
        total=$(echo "${data_map[$key]}" | cut -d, -f1)
        count=$(echo "${data_map[$key]}" | cut -d, -f2)
        total=$(echo "$total + $col5" | bc)
        count=$((count + 1))
        data_map[$key]="$total,$count"
    else
        # 如果该组合第一次出现，初始化总和与数量
        data_map[$key]="$col5,1"
    fi
done < "$input_file"

# 输出结果到临时文件
temp_file=$(mktemp)

{
    for key in "${!data_map[@]}"; do
        # 获取总和与数量
        total=$(echo "${data_map[$key]}" | cut -d, -f1)
        count=$(echo "${data_map[$key]}" | cut -d, -f2)
        # 计算平均值
        avg=$(echo "scale=6; $total / $count" | bc)
        # 输出前四列和计算出来的平均值
        echo "$key $avg"
    done
} > "$temp_file"

# 对临时文件进行排序
sort -k1,1n -k3,3n -k4,4n "$temp_file" > "$output_file"

# 删除临时文件
rm "$temp_file"

echo "处理完成，结果已输出到 $output_file"
