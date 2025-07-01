#!/bin/bash
# 用法: ./pinning_time.sh <input_file> <timestep> <Nfreq> <output> [threshold]
# 示例: ./pinning_time.sh grid_fault.out 0.004 50 pinning_time.txt 0

input="$1"
output="$4"
threshold="${5:-0}"

if [ -f "$output" ]; then
	rm "$output"
	touch "$output"
else
	touch "$output"
fi

awk -v timestep="$2" -v Nfreq="$3" -v threshold=$threshold '
BEGIN {
	dt=timestep*Nfreq

    skip_lines=3        # 跳过前三行注释
    current_chunks=0    # 当前时间步的chunk数量
    remaining_chunks=0  # 剩余待处理的chunk行数
	print "ChunkID Coord1 Coord2 pinning_time"
}

# 跳过前三行注释
NR <= skip_lines { 
	next
}

# 处理时间步头部行（例如 "1000 100 5000"）
!/^ / {
    current_step=$1
	current_chunks=$2   # 提取该时间步的chunk数量
    remaining_chunks=current_chunks
    next
}

# 处理每个chunk行（例如 "0 0 10 5"）
remaining_chunks > 0 {
    # 提取坐标和v_hcp（格式为：ChunkID Coord1 Coord2 Ncount v_hcp）
	sub(/^[ \t]+/, "")	# 去掉行首空格

    id=$1      # 第1列为Chunk ID
    coord1=$2  
    coord2=$3  
    v_hcp=$5   

    # 生成唯一标识
    key=id " " coord1 " " coord2

    # 统计v_hcp > 0的次数
    if (v_hcp > threshold) {
        count[key]++
    }

    # 标记该chunk至少出现过一次
    total[key] = 1
    remaining_chunks--
}

END {
    # 输出结果
    for (key in total) {
        if (count[key] == 0) {
            # 从未出现v_hcp > 0的chunk，输出-1
            printf "%s -1\n", key
        } else {
            # 计算总停留时间 = 次数 × 时间步长dt
            printf "%s %.4f\n", key, count[key] * dt
        }
    }
}
' "$input" > "$output"

head -n 1 "$output" > temp_file
tail -n +2 "$output" | sort -n -k1,1 >> temp_file

mv temp_file "$output"
