import os
import shutil
import subprocess
import sys
from pathlib import Path
from StaticFunctions import get_real_path

def change_version(new_version, file_path=get_real_path("bin/天王寺科学忍具.nsi")):
    """
        更新文本文件中 PRODUCT_VERSION 定义
        :param file_path: 文本文件路径
        :param new_version: 新版本号字符串 (如 "1.2.3")
        """
    # 构建要替换的新行
    new_line = f'!define PRODUCT_VERSION "{new_version}"'
    updated = False

    try:
        # 读取文件所有行
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # 查找并替换目标行
        for i, line in enumerate(lines):
            if line.strip().startswith('!define PRODUCT_VERSION'):
                lines[i] = new_line + '\n'  # 确保有换行符
                updated = True
                print(f"找到并替换第 {i + 1} 行: {line.strip()} → {new_line}")
                break  # 找到第一个匹配项后停止

        # 如果没有找到匹配行
        if not updated:
            print(f"警告: 文件中未找到 !define PRODUCT_VERSION 行")
            # 可选: 在文件末尾添加新行
            # lines.append(new_line + '\n')
            # updated = True

        # 如果有更改，写回文件
        if updated:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(lines)
            print(f"文件更新成功: {file_path}")
        else:
            print("文件未更改")

    except Exception as e:
        print(f"处理文件时出错: {e}")

def main(version):
    # 配置路径
    py_project = Path(get_real_path(""))
    nsis_project = Path(get_real_path("bin"))
    upx_dir = Path(get_real_path("bin/upx-5.0.1-win64"))
    venv_dir = py_project / ".env"

    # 虚拟环境中的 Python 解释器
    venv_python = venv_dir / "Scripts" / "python.exe"

    # 确保目录存在
    if not py_project.exists():
        print(f"错误: Python项目目录不存在 - {py_project}")
        sys.exit(1)

    if not nsis_project.exists():
        print(f"错误: NSIS项目目录不存在 - {nsis_project}")
        sys.exit(1)

    try:
        # 1. 使用PyInstaller构建可执行文件
        print("=" * 50)
        print("步骤 1: 使用PyInstaller构建可执行文件")

        # 验证虚拟环境中的Python解释器
        if not venv_python.exists():
            raise FileNotFoundError(f"虚拟环境Python解释器未找到: {venv_python}")

        # 构建PyInstaller命令
        pyinstaller_cmd = [
            str(venv_python),
            "-m", "PyInstaller",
            "--upx-dir", str(upx_dir),
            str(py_project / "天王寺科学忍具.spec")
        ]

        print(f"执行命令: {' '.join(pyinstaller_cmd)}")
        result = subprocess.run(pyinstaller_cmd, cwd=py_project, check=True)
        print("PyInstaller 构建成功")

        # 2. 使用NSIS构建安装包
        print("\n" + "=" * 50)
        print("步骤 2: 构建NSIS安装程序")
        change_version(version)

        # 直接使用makensis命令（假设已在PATH中）
        nsis_cmd = [get_real_path("bin/NSIS/Bin/makensis.exe"), str(nsis_project / "天王寺科学忍具.nsi")]
        print(f"执行命令: {' '.join(nsis_cmd)}")

        # 在NSIS项目目录执行命令
        subprocess.run(nsis_cmd, cwd=nsis_project, check=True)
        print("NSIS 构建成功")

        # 3. 移动生成的安装程序
        print("\n" + "=" * 50)
        print("步骤 3: 移动安装程序到发布目录")

        installer_src = nsis_project / "天王寺科学忍具Setup.exe"
        if not installer_src.exists():
            raise FileNotFoundError(f"安装程序未生成: {installer_src}")

        # 创建release目录（如果不存在）
        release_dir = py_project / "release"
        release_dir.mkdir(parents=True, exist_ok=True)

        installer_dest = release_dir / f"天王寺科学忍具Setup_V{version}.exe"

        # 移动文件
        shutil.move(str(installer_src), str(installer_dest))
        print(f"安装程序已移动到: {installer_dest}")

        # 4. 清理临时文件
        print("\n" + "=" * 50)
        print("步骤 4: 清理构建临时文件")

        # 删除dist目录
        for dir_name in ["dist"]:
            dir_path = py_project / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"已删除目录: {dir_path}")

        # 完成消息
        print("\n" + "=" * 50)
        print("[所有操作已完成]")
        print(f"安装程序位置: {installer_dest}")

    except subprocess.CalledProcessError as e:
        print(f"\n错误: 命令执行失败 (返回码 {e.returncode})")
        print(f"命令: {e.cmd}")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"\n错误: 文件或目录未找到 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n未知错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 设置控制台编码为 UTF-8 (等效于 chcp 65001)
    os.system("chcp 65001 > nul")
    main("5.10.2_x")
