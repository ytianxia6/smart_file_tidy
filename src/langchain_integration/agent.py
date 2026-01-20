"""文件整理Agent - 核心智能决策引擎"""

from typing import Dict, Any, List, Optional, Tuple
import json
import re

from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .llm_factory import LLMFactory
from .prompts import SYSTEM_PROMPT
from .tools import (
    FileScannerTool,
    FileAnalyzerTool,
    FileOperatorTool,
    ValidationTool
)
from .content_analyzer import ContentAnalyzer


class FileOrganizerAgent:
    """文件整理Agent - 使用LangChain工具执行文件整理任务"""
    
    def __init__(
        self,
        llm_provider: str,
        config: Dict[str, Any],
        dry_run: bool = False,
        verbose: bool = True
    ):
        """
        初始化文件整理Agent
        
        Args:
            llm_provider: LLM提供商（claude, openai, custom, local）
            config: LLM配置字典
            dry_run: 是否仅模拟操作
            verbose: 是否显示详细信息
        """
        self.llm_provider = llm_provider
        self.config = config
        self.dry_run = dry_run
        self.verbose = verbose
        
        # 创建LLM
        self.llm = LLMFactory.create_llm(llm_provider, config)
        
        # 创建内容分析器
        self.content_analyzer = ContentAnalyzer(self.llm)
        
        # 创建工具集
        self.tools = self._create_tools(dry_run)
        
        # 会话历史
        self.chat_history: List[Any] = []
        
        if verbose:
            print(f"[Agent] 已初始化，使用 {llm_provider} 提供商")
            print(f"[Agent] 可用工具: {[t.name for t in self.tools]}")
    
    def _create_tools(self, dry_run: bool):
        """创建工具列表"""
        return [
            FileScannerTool(),
            FileAnalyzerTool(),
            FileOperatorTool(dry_run=dry_run),
            ValidationTool()
        ]
    
    def _is_paper_organization_task(self, user_request: str) -> bool:
        """
        判断是否为论文整理任务
        
        Args:
            user_request: 用户需求描述
            
        Returns:
            是否为论文整理任务
        """
        # 如果用户明确提到非论文内容，则不是论文任务
        non_paper_keywords = ['图片', '照片', '视频', '音乐', '代码', '文档']
        if any(keyword in user_request for keyword in non_paper_keywords):
            return False
        
        # 默认情况（空需求或通用整理需求）视为论文整理
        paper_keywords = ['论文', 'paper', 'pdf', '学术', '文献']
        generic_keywords = ['整理', '分类', '组织', 'organize', 'tidy']
        
        # 明确提到论文相关
        if any(keyword in user_request for keyword in paper_keywords):
            return True
        
        # 通用整理需求，默认为论文整理（这是本项目的核心目标）
        if any(keyword in user_request for keyword in generic_keywords) or not user_request.strip():
            return True
        
        # 空需求也默认为论文整理
        return True
    
    def organize_files(
        self,
        directory: str,
        user_request: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行文件整理任务
        
        Args:
            directory: 目标目录
            user_request: 用户需求描述
            context: 额外上下文信息
            
        Returns:
            执行结果字典
        """
        try:
            if self.verbose:
                print(f"\n[Agent] 开始处理任务...")
                print(f"[Agent] 目录: {directory}")
                print(f"[Agent] 需求: {user_request}")
            
            # 检测是否为论文整理任务（默认行为）
            is_paper_task = self._is_paper_organization_task(user_request)
            
            # 构建完整的提示
            if is_paper_task:
                full_prompt = f"""{SYSTEM_PROMPT}

📚 任务类型：学术论文整理（默认模式）

目标目录：{directory}
用户需求：{user_request}

⚠️ 重要：你必须真正执行操作，不要只给建议！

请按照以下步骤执行：

1️⃣ 扫描文件
   使用 file_scanner 工具扫描目录：{directory}

2️⃣ 识别论文
   对每个 PDF 文件使用 file_analyzer 工具分析，参数 check_if_paper=True
   识别哪些是学术论文（查看 paper_check.likely_paper 字段）

3️⃣ 创建论文文件夹
   使用 file_operator 工具创建文件夹：
   操作类型：create_folder
   文件夹名：Papers 或 学术论文（根据文件内容语言选择）
   路径：{directory}/Papers 或 {directory}/学术论文

4️⃣ 移动论文文件
   对每个识别出的论文，使用 file_operator 工具移动：
   操作类型：move
   源路径：原文件完整路径
   目标路径：论文文件夹路径

5️⃣ 总结结果
   报告：
   - 扫描了多少文件
   - 识别了多少论文
   - 成功移动了多少文件
   - 具体移动了哪些文件

⚠️ 你必须使用 ReAct 格式调用工具！

第一步示例：
Thought: 我需要先扫描目录了解有哪些文件
Action: file_scanner
Action Input: {{"directory": "{directory}"}}

记住：
- 必须使用 "Thought -> Action -> Action Input" 格式
- 不要描述步骤，要实际输出工具调用
- 每次收到 Observation 后，继续输出下一个 Thought + Action + Action Input
- 完成所有操作后才输出 Final Answer

现在请开始执行，从第一个 Thought 开始。
"""
            else:
                full_prompt = f"""{SYSTEM_PROMPT}

目标目录：{directory}
用户需求：{user_request}

⚠️ 你必须使用 ReAct 格式调用工具！

第一步示例：
Thought: 我需要先扫描目录了解文件情况
Action: file_scanner
Action Input: {{"directory": "{directory}"}}

记住：
- 必须使用 "Thought -> Action -> Action Input" 格式
- 不要描述步骤，要实际输出工具调用
- 每次收到 Observation 后，继续输出下一个 Thought + Action + Action Input

现在请开始执行，从第一个 Thought 开始。
"""
            
            if context:
                full_prompt += f"\n\n额外信息：{context}"
            
            # 执行任务
            result = self._execute_with_tools(full_prompt)
            
            # 保存到历史
            self.chat_history.append({
                'input': user_request,
                'output': result
            })
            
            return {
                'success': True,
                'output': result,
                'directory': directory,
                'dry_run': self.dry_run
            }
            
        except Exception as e:
            if self.verbose:
                print(f"[Agent] 错误: {e}")
            return {
                'success': False,
                'error': str(e),
                'directory': directory
            }
    
    def _find_tool(self, tool_name: str):
        """
        根据名称查找工具
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具实例
            
        Raises:
            ValueError: 如果工具不存在
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        raise ValueError(f"未找到工具: {tool_name}，可用工具: {[t.name for t in self.tools]}")
    
    def _parse_react_output(self, text: str) -> Tuple[Optional[str], Optional[Dict[str, Any]], Optional[str]]:
        """
        解析 LLM 的 ReAct 格式输出
        
        Args:
            text: LLM 的输出文本
            
        Returns:
            (action_name, action_input, thought) 元组
            如果没有找到工具调用，action_name 为 None
        """
        if not text:
            return None, None, None
        
        # 提取 Thought
        thought = None
        thought_match = re.search(r'Thought:\s*(.+?)(?=Action:|Final Answer:|$)', text, re.DOTALL | re.IGNORECASE)
        if thought_match:
            thought = thought_match.group(1).strip()
        
        # 检查是否是最终答案
        if 'Final Answer:' in text or 'Final Answer：' in text:
            return "Final Answer", {}, thought
        
        # 提取 Action
        action_match = re.search(r'Action:\s*(\w+)', text, re.IGNORECASE)
        if not action_match:
            return None, None, thought
        
        action_name = action_match.group(1).strip()
        
        # 提取 Action Input (JSON格式)
        action_input = {}
        input_match = re.search(r'Action Input:\s*(\{.+?\})', text, re.DOTALL | re.IGNORECASE)
        
        if input_match:
            try:
                json_str = input_match.group(1).strip()
                action_input = json.loads(json_str)
            except json.JSONDecodeError as e:
                if self.verbose:
                    print(f"[Agent] JSON解析失败: {e}")
                    print(f"[Agent] JSON字符串: {json_str}")
                # 尝试修复常见的JSON错误
                try:
                    # 替换单引号为双引号
                    json_str_fixed = json_str.replace("'", '"')
                    action_input = json.loads(json_str_fixed)
                except:
                    return None, None, thought
        
        return action_name, action_input, thought
    
    def _execute_with_tools(self, prompt: str, max_iterations: int = 15) -> str:
        """
        使用工具执行任务（ReAct 模式）
        
        不依赖 function calling，使用 ReAct 格式解析工具调用
        """
        # 初始化消息历史
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        messages.append(HumanMessage(content=prompt))
        
        iterations = 0
        final_response = ""
        
        while iterations < max_iterations:
            iterations += 1
            
            if self.verbose:
                print(f"\n{'='*60}")
                print(f"[Agent] 迭代 {iterations}/{max_iterations}")
                print(f"{'='*60}")
            
            try:
                # 调用 LLM（不使用 bind_tools）
                response = self.llm.invoke(messages)
                
                # 提取响应内容
                if hasattr(response, 'content'):
                    content = response.content
                else:
                    content = str(response)
                
                if self.verbose:
                    print(f"\n[Agent] LLM响应:\n{content[:500]}...")
                
                # 解析 ReAct 输出
                action_name, action_input, thought = self._parse_react_output(content)
                
                if self.verbose and thought:
                    print(f"\n[Agent] 💭 Thought: {thought[:200]}")
                
                # 检查是否是最终答案
                if action_name == "Final Answer":
                    final_response = content
                    if self.verbose:
                        print(f"\n[Agent] ✅ 任务完成")
                    break
                
                # 如果没有工具调用，可能是 LLM 直接给出了答案
                if not action_name or not action_input:
                    if self.verbose:
                        print(f"\n[Agent] ⚠️  未检测到工具调用，可能任务已完成")
                    final_response = content
                    break
                
                # 执行工具调用
                if self.verbose:
                    print(f"\n[Agent] 🔧 Action: {action_name}")
                    print(f"[Agent] 📝 Action Input: {json.dumps(action_input, ensure_ascii=False, indent=2)}")
                
                try:
                    # 查找并执行工具
                    tool = self._find_tool(action_name)
                    tool_result = tool._run(**action_input)
                    
                    if self.verbose:
                        # 显示工具结果的摘要
                        result_preview = str(tool_result)[:300]
                        print(f"\n[Agent] 📊 Observation: {result_preview}...")
                    
                    # 将工具结果添加到消息历史
                    messages.append(AIMessage(content=content))
                    
                    # 添加 Observation 并提醒继续使用 ReAct 格式
                    observation_message = f"""Observation: {tool_result}

现在，请继续思考下一步操作，必须使用 ReAct 格式：
Thought: [你的思考]
Action: [工具名称]
Action Input: [JSON参数]

如果所有任务都已完成，请输出：
Thought: 所有操作已完成
Final Answer: [总结结果]"""
                    
                    messages.append(HumanMessage(content=observation_message))
                    
                except ValueError as e:
                    # 工具不存在
                    error_msg = f"错误: {str(e)}"
                    if self.verbose:
                        print(f"\n[Agent] ❌ {error_msg}")
                    messages.append(AIMessage(content=content))
                    messages.append(HumanMessage(content=f"""Observation: {error_msg}

请使用正确的工具名称重试，必须使用 ReAct 格式：
Thought: [你的思考]
Action: [正确的工具名称]
Action Input: [JSON参数]"""))
                    
                except Exception as e:
                    # 工具执行失败
                    error_msg = f"工具执行失败: {str(e)}"
                    if self.verbose:
                        print(f"\n[Agent] ❌ {error_msg}")
                    messages.append(AIMessage(content=content))
                    messages.append(HumanMessage(content=f"""Observation: {error_msg}

请分析错误原因并继续，必须使用 ReAct 格式：
Thought: [你的思考]
Action: [工具名称]
Action Input: [JSON参数]"""))
                
                # 继续下一轮迭代
                continue
                
            except Exception as e:
                if self.verbose:
                    print(f"\n[Agent] ❌ 迭代错误: {e}")
                    import traceback
                    traceback.print_exc()
                # 尝试返回当前结果
                final_response = f"执行过程中出现错误: {str(e)}"
                break
        
        # 如果达到最大迭代次数
        if iterations >= max_iterations and not final_response:
            final_response = "已达到最大迭代次数，任务可能未完全完成"
            if self.verbose:
                print(f"\n[Agent] ⚠️  {final_response}")
        
        return final_response or "任务执行完成"
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        分析单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            分析结果
        """
        return self.content_analyzer.analyze_file_content(file_path)
    
    def classify_files(
        self,
        directory: str,
        categories: List[str]
    ) -> Dict[str, Any]:
        """
        将目录中的文件分类到指定类别
        
        Args:
            directory: 目标目录
            categories: 类别列表
            
        Returns:
            分类结果
        """
        try:
            prompt = f"""请扫描目录 {directory} 中的文件，并将它们分类到以下类别：

类别：{', '.join(categories)}

步骤：
1. 使用 file_scanner 扫描目录
2. 分析文件内容
3. 将文件分配到最合适的类别
4. 为每个类别创建文件夹
5. 将文件移动到对应的类别文件夹
6. 汇总分类结果

请开始执行。
"""
            
            result = self._execute_with_tools(prompt)
            
            return {
                'success': True,
                'output': result,
                'categories': categories,
                'directory': directory
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def suggest_organization(self, directory: str) -> Dict[str, Any]:
        """
        分析目录并提出整理建议
        
        Args:
            directory: 目标目录
            
        Returns:
            整理建议
        """
        try:
            prompt = f"""请分析目录 {directory} 并提出整理建议。

步骤：
1. 使用 file_scanner 扫描目录，获取文件信息
2. 分析文件的类型、命名模式、内容特征
3. 识别潜在的分类维度（按类型、按时间、按主题等）
4. 提出具体的整理方案和文件夹结构
5. 说明每种方案的优缺点

注意：只分析和建议，不要实际执行操作。
"""
            
            result = self._execute_with_tools(prompt)
            
            return {
                'success': True,
                'suggestions': result,
                'directory': directory
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def chat(self, message: str) -> str:
        """
        与Agent对话
        
        Args:
            message: 用户消息
            
        Returns:
            Agent回复
        """
        try:
            # 构建消息历史
            messages = [SystemMessage(content=SYSTEM_PROMPT)]
            
            # 添加历史消息
            for item in self.chat_history[-5:]:  # 只保留最近5轮
                messages.append(HumanMessage(content=str(item.get('input', ''))))
                messages.append(AIMessage(content=str(item.get('output', ''))))
            
            # 添加当前消息
            messages.append(HumanMessage(content=message))
            
            # 调用LLM
            response = self.llm.invoke(messages)
            
            # 提取响应
            if hasattr(response, 'content'):
                reply = response.content
            else:
                reply = str(response)
            
            # 保存到历史
            self.chat_history.append({
                'input': message,
                'output': reply
            })
            
            return reply
            
        except Exception as e:
            return f"对话出错: {str(e)}"
    
    def clear_memory(self):
        """清除会话记忆"""
        self.chat_history.clear()
    
    def get_chat_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.chat_history.copy()
