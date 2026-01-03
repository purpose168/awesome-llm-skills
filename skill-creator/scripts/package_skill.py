#!/usr/bin/env python3
"""
技能打包器 - 创建技能文件夹的可分发zip文件

用法：
    python utils/package_skill.py <path/to/skill-folder> [output-directory]

示例：
    python utils/package_skill.py skills/public/my-skill
    python utils/package_skill.py skills/public/my-skill ./dist
"""

import sys
import zipfile
from pathlib import Path
from quick_validate import validate_skill


def package_skill(skill_path, output_dir=None):
    """
    将技能文件夹打包成zip文件。

    参数：
        skill_path: 技能文件夹的路径
        output_dir: zip文件的可选输出目录（默认为当前目录）

    返回：
        创建的zip文件的路径，如果出错则返回None
    """
    skill_path = Path(skill_path).resolve()

    # 验证技能文件夹是否存在
    if not skill_path.exists():
        print(f"❌ 错误：未找到技能文件夹：{skill_path}")
        return None

    if not skill_path.is_dir():
        print(f"❌ 错误：路径不是目录：{skill_path}")
        return None

    # 验证SKILL.md是否存在
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"❌ 错误：在{skill_path}中未找到SKILL.md")
        return None

    # 打包前运行验证
    print("🔍 正在验证技能...")
    valid, message = validate_skill(skill_path)
    if not valid:
        print(f"❌ 验证失败：{message}")
        print("   请在打包前修复验证错误。")
        return None
    print(f"✅ {message}\n")

    # 确定输出位置
    skill_name = skill_path.name
    if output_dir:
        output_path = Path(output_dir).resolve()
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = Path.cwd()

    zip_filename = output_path / f"{skill_name}.zip"

    # 创建zip文件
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 遍历技能目录
            for file_path in skill_path.rglob('*'):
                if file_path.is_file():
                    # 计算zip内的相对路径
                    arcname = file_path.relative_to(skill_path.parent)
                    zipf.write(file_path, arcname)
                    print(f"  已添加：{arcname}")

        print(f"\n✅ 已成功将技能打包到：{zip_filename}")
        return zip_filename

    except Exception as e:
        print(f"❌ 创建zip文件时出错：{e}")
        return None


def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法：python utils/package_skill.py <path/to/skill-folder> [output-directory]")
        print("\n示例：")
        print("  python utils/package_skill.py skills/public/my-skill")
        print("  python utils/package_skill.py skills/public/my-skill ./dist")
        sys.exit(1)

    # 获取技能路径和输出目录
    skill_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"📦 正在打包技能：{skill_path}")
    if output_dir:
        print(f"   输出目录：{output_dir}")
    print()

    # 打包技能
    result = package_skill(skill_path, output_dir)

    # 根据结果退出
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
