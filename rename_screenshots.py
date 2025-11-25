import os
import random
from datetime import datetime, timedelta


def generate_timestamp(base_time):
    """生成时间戳格式: HHMMSSddmmm (时分秒日毫秒前3位)"""
    return base_time.strftime("%H%M%S%d%f")[:-3]


def rename_files_in_screenshots():
    """重命名screenshots目录下的所有文件，手动计算时间偏移"""
    screenshots_dir = "screenshots"

    if not os.path.exists(screenshots_dir):
        print(f"目录 {screenshots_dir} 不存在")
        return

    files = [
        f
        for f in os.listdir(screenshots_dir)
        if os.path.isfile(os.path.join(screenshots_dir, f))
    ]

    if not files:
        print(f"目录 {screenshots_dir} 中没有文件")
        return

    print(f"找到 {len(files)} 个文件需要重命名")

    base_time = datetime.now()
    total_offset_microseconds = 0

    for index, file_name in enumerate(files, 1):
        old_path = os.path.join(screenshots_dir, file_name)

        if index > 1:
            seconds_offset = random.randint(10, 30)
            microseconds_offset = random.randint(0, 999999)
            total_offset_microseconds += seconds_offset * 1000000 + microseconds_offset

        current_time = base_time + timedelta(microseconds=total_offset_microseconds)

        timestamp = generate_timestamp(current_time)
        new_file_name = f"{timestamp}_{file_name}"
        new_path = os.path.join(screenshots_dir, new_file_name)

        if os.path.exists(new_path):
            print(f"[{index}/{len(files)}] 跳过: {file_name} (目标文件已存在)")
            continue

        try:
            os.rename(old_path, new_path)
            if index == 1:
                offset_info = "基准时间"
            else:
                total_seconds = total_offset_microseconds / 1000000
                offset_info = f"累计偏移: +{total_seconds:.6f}秒"
            print(
                f"[{index}/{len(files)}] 重命名成功: {file_name} -> {new_file_name} ({offset_info})"
            )
        except Exception as e:
            print(f"[{index}/{len(files)}] 重命名失败: {file_name}, 错误: {e}")
            continue

    print("\n所有文件处理完成!")


if __name__ == "__main__":
    rename_files_in_screenshots()
