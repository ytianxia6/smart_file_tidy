"""自定义分类器示例"""

from src.core.classifier import SmartClassifier
from src.ai import ClaudeAdapter
from src.models import FileInfo, Operation, OperationType
from pathlib import Path


class CustomClassifier(SmartClassifier):
    """自定义分类器 - 添加特定业务规则"""
    
    def _apply_rules(self, file: FileInfo, user_request: str) -> Operation:
        """应用自定义规则"""
        file_path = Path(file.path)
        
        # 规则1：按年份分类文档
        import re
        year_match = re.search(r'20\d{2}', file.name)
        if year_match and file.extension == '.pdf':
            year = year_match.group(0)
            target_dir = file_path.parent / f'documents_{year}'
            target = target_dir / file.name
            
            return Operation(
                type=OperationType.MOVE,
                source=file.path,
                target=str(target),
                reason=f'按年份分类：{year}',
                confidence=0.9
            )
        
        # 规则2：大文件单独存放
        if file.size > 50 * 1024 * 1024:  # 大于50MB
            target_dir = file_path.parent / 'large_files'
            target = target_dir / file.name
            
            return Operation(
                type=OperationType.MOVE,
                source=file.path,
                target=str(target),
                reason='大文件单独存放',
                confidence=1.0
            )
        
        # 没有匹配的规则，返回None让AI处理
        return None


def use_custom_classifier():
    """使用自定义分类器"""
    from src.utils import ConfigManager
    
    config = ConfigManager()
    ai_config = config.get_ai_config('claude')
    ai_adapter = ClaudeAdapter(**ai_config)
    
    # 使用自定义分类器
    classifier = CustomClassifier(ai_adapter)
    
    # 创建测试文件信息
    files = [
        FileInfo.from_path('/path/to/report_2023.pdf'),
        FileInfo.from_path('/path/to/large_video.mp4'),
    ]
    
    # 分类
    operations = classifier.classify_batch(
        files=files,
        user_request="整理文件",
        context={}
    )
    
    for op in operations:
        print(f"{op.type.value}: {op.source} -> {op.target}")
        print(f"  原因: {op.reason}\n")


if __name__ == '__main__':
    print("自定义分类器示例\n")
    print("此示例展示如何扩展SmartClassifier添加自定义规则")
    print("=" * 50)
    
    # use_custom_classifier()
