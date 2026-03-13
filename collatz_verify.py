from __future__ import annotations

import json
import os
import time
from datetime import datetime
from typing import Dict, Set


class CollatzVerifier:
    """考拉兹猜想验证器，使用 JSON 文件存储已验证的数和中间大数"""
    
    def __init__(self, json_path: str = "collatz_cache.json", config_path: str = "config.json"):
        self.json_path = json_path
        self.config_path = config_path
        self.verified_up_to: int = 0
        self.large_numbers: Set[int] = set()
        self.batch_size: int = 10000
        self._load_config()
        self._load_cache()
    
    def _load_config(self) -> None:
        """从配置文件加载设置"""
        if not os.path.exists(self.config_path):
            # 创建默认配置文件
            default_config = {
                "batch_size": 10000,
                "save_interval_seconds": 60,
                "log_progress": True
            }
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            print(f"已创建默认配置文件：{self.config_path}")
            print(f"默认配置：{default_config}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.batch_size = config.get('batch_size', 10000)
                self.save_interval = config.get('save_interval_seconds', 60)
                self.log_progress = config.get('log_progress', True)
        except (json.JSONDecodeError, IOError) as e:
            print(f"读取配置文件失败：{e}，使用默认配置")
            self.batch_size = 10000
            self.save_interval = 60
            self.log_progress = True
    
    def _load_cache(self) -> None:
        """从 JSON 文件加载缓存数据"""
        if not os.path.exists(self.json_path):
            print("未找到缓存文件，将从 1 开始验证")
            return
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.verified_up_to = data.get('verified_up_to', 0)
                self.large_numbers = set(data.get('large_numbers', []))
                print(f"从缓存加载：已验证到 {self.verified_up_to}, 缓存大数 {len(self.large_numbers)} 个")
        except (json.JSONDecodeError, IOError) as e:
            print(f"读取缓存失败：{e}，将从头开始验证")
            self.verified_up_to = 0
            self.large_numbers = set()
    
    def _save_cache(self) -> None:
        """保存缓存数据到 JSON 文件"""
        # 清理小于当前已验证数的历史数据
        old_count = len(self.large_numbers)
        self.large_numbers = {n for n in self.large_numbers if n > self.verified_up_to}
        cleaned_count = old_count - len(self.large_numbers)
        
        data = {
            'verified_up_to': self.verified_up_to,
            'large_numbers': sorted(list(self.large_numbers)),
            'last_updated': datetime.now().isoformat()
        }
        
        # 使用紧凑格式保存 JSON（移除换行和缩进以压缩文件大小）
        with open(self.json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'), ensure_ascii=False)
        
        if self.log_progress:
            if cleaned_count > 0:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 清理了 {cleaned_count} 个过期的缓存数字")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 缓存已保存：已验证到 {self.verified_up_to:,}, "
                  f"缓存大数 {len(self.large_numbers):,} 个")
    
    def verify_single(self, n: int) -> bool:
        """
        验证单个数字 n 是否满足考拉兹猜想
        返回 True 表示满足猜想，False 表示不满足（理论上不会出现）
        """
        if n <= 0:
            raise ValueError("n 必须是正整数")
        
        # 如果这个数已经在缓存的大数集合中，直接跳过
        if n in self.large_numbers:
            return True
        
        original_n = n
        visited_larger_numbers: Set[int] = set()
        
        while n != 1:
            # 优化点 1: 如果出现小于原始 n 的数，说明已经验证过
            if n < original_n:
                # 将路径上出现的大于原始 n 的数加入缓存
                self.large_numbers.update(visited_larger_numbers)
                return True
            
            # 优化点 2: 如果遇到缓存中的大数，直接成功
            if n in self.large_numbers:
                self.large_numbers.update(visited_larger_numbers)
                return True
            
            # 记录路径上大于原始 n 的数
            if n > original_n:
                visited_larger_numbers.add(n)
            
            # 执行考拉兹变换
            if n % 2 == 0:
                n = n // 2
            else:
                n = 3 * n + 1
        
        # 成功到达 1，将路径上的大数加入缓存
        self.large_numbers.update(visited_larger_numbers)
        return True
    
    def run_infinite(self) -> None:
        """无限循环验证"""
        print("\n" + "="*60)
        print("🚀 开始无限循环验证考拉兹猜想")
        print("="*60)
        print(f"起始位置：从 {self.verified_up_to + 1} 开始")
        print(f"批量大小：每 {self.batch_size:,} 个数保存一次")
        print(f"按 Ctrl+C 停止验证\n")
        
        start_time = time.time()
        last_save_time = start_time
        
        try:
            n = self.verified_up_to + 1
            batch_count = 0
            
            while True:
                if not self.verify_single(n):
                    print(f"\n❌ 发现不满足猜想的数：{n:,}")
                    print(f"这是在第 {n:,} 个数发现的！")
                    return
                
                batch_count += 1
                
                # 定期保存缓存
                current_time = time.time()
                if batch_count >= self.batch_size or (current_time - last_save_time) >= self.save_interval:
                    self.verified_up_to = n
                    self._save_cache()
                    
                    elapsed = current_time - start_time
                    nums_per_sec = n / elapsed if elapsed > 0 else 0
                    
                    if self.log_progress:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📊 进度统计:")
                        print(f"   当前数字：{n:,}")
                        print(f"   验证速度：{nums_per_sec:,.0f} 个数/秒")
                        print(f"   运行时间：{elapsed/3600:.2f} 小时 ({elapsed/60:.1f} 分钟)")
                        print(f"   内存占用：{len(self.large_numbers):,} 个大数缓存\n")
                    
                    batch_count = 0
                    last_save_time = current_time
                
                n += 1

        # control + C
        except KeyboardInterrupt:
            print("\n\n⚠️  用户中断验证")
            self.verified_up_to = n - 1
            self._save_cache()
            print("✅ 最终缓存已保存")
            print(f"最终状态：已验证到 {self.verified_up_to:,}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'verified_up_to': self.verified_up_to,
            'large_numbers_count': len(self.large_numbers),
            'max_large_number': max(self.large_numbers) if self.large_numbers else 0
        }


def main() -> None:
    print("="*60)
    print("🔢 考拉兹猜想验证工具")
    print("="*60)
    
    verifier = CollatzVerifier(
        json_path="output/collatz_cache.json",
        config_path="json/config.json"
    )
    
    # 显示当前状态
    stats = verifier.get_stats()
    print(f"\n📊 当前验证状态:")
    print(f"   已验证到：{stats['verified_up_to']:,}")
    print(f"   缓存大数数量：{stats['large_numbers_count']:,}")
    print(f"   最大缓存大数：{stats['max_large_number']:,}\n")
    
    # 开始无限循环验证
    verifier.run_infinite()


if __name__ == "__main__":
    main()
