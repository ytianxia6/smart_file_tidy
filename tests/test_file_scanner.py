"""测试文件扫描器"""

import pytest
from pathlib import Path
from src.core.file_scanner import FileScanner


def test_scan_directory(temp_dir, sample_files):
    """测试目录扫描"""
    scanner = FileScanner()
    files = scanner.scan_directory(str(temp_dir))
    
    assert len(files) == len(sample_files)
    assert all(Path(f.path).exists() for f in files)


def test_scan_with_extension_filter(temp_dir, sample_files):
    """测试扩展名过滤"""
    scanner = FileScanner()
    files = scanner.scan_directory(str(temp_dir), extensions={'.pdf'})
    
    assert len(files) == 2  # test.pdf 和 report.pdf
    assert all(f.extension == '.pdf' for f in files)


def test_scan_recursive(temp_dir):
    """测试递归扫描"""
    # 创建子目录和文件
    subdir = temp_dir / 'subdir'
    subdir.mkdir()
    (subdir / 'nested.txt').write_text('nested content')
    (temp_dir / 'root.txt').write_text('root content')
    
    scanner = FileScanner()
    
    # 非递归
    files_non_recursive = scanner.scan_directory(str(temp_dir), recursive=False)
    assert len(files_non_recursive) == 1
    
    # 递归
    files_recursive = scanner.scan_directory(str(temp_dir), recursive=True)
    assert len(files_recursive) == 2


def test_extract_metadata_pdf(temp_dir):
    """测试PDF元数据提取"""
    # 创建简单PDF（需要实际PDF库）
    pdf_file = temp_dir / 'test.pdf'
    pdf_file.write_bytes(b'%PDF-1.4\n')  # 最简PDF头
    
    scanner = FileScanner()
    metadata = scanner.extract_metadata(str(pdf_file))
    
    assert 'mime_type' in metadata


def test_group_by_extension(temp_dir, sample_files):
    """测试按扩展名分组"""
    scanner = FileScanner()
    files = scanner.scan_directory(str(temp_dir))
    
    groups = scanner.group_by_extension(files)
    
    assert '.pdf' in groups
    assert len(groups['.pdf']) == 2
    assert '.txt' in groups
    assert len(groups['.txt']) == 1
