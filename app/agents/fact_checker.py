"""Fact Checker Agent - 他エージェントの出力を検証・修正するエージェント

論文より: Fact Checker verifies agents' outputs against original claims 
and corrects discrepancies for accuracy

論文の設定: GPT-4oをtemperature=0.2で使用（一貫性と正確性のため）
"""
import os
from strands import Agent
from prompts import EXTENDED_SMILES_DEFINITION, FACT_CHECKER_PROMPT_TEMPLATE

MODEL_ID = os.getenv("MODEL_ID", "jp.anthropic.claude-haiku-4-5-20251001-v1:0")

# 論文Appendix Aに基づくプロンプト
FACT_CHECKER_PROMPT = FACT_CHECKER_PROMPT_TEMPLATE.format(
    extended_smiles_definition=EXTENDED_SMILES_DEFINITION
)

def create_fact_checker_agent() -> Agent:
    """Fact Checkerエージェントを作成"""
    return Agent(
        model=MODEL_ID,
        system_prompt=FACT_CHECKER_PROMPT
    )

def check_facts(
    target_smiles: str,
    block_text: str,
    input_is_protected: bool,
    input_reasoning: str
) -> str:
    """各エージェントの出力を検証
    
    Args:
        target_smiles: 対象分子のSMILES文字列
        block_text: 特許PDFブロックテキスト
        input_is_protected: 侵害判定結果
        input_reasoning: 分析推論
    
    Returns:
        検証結果（Markdown形式の文字列）
    """
    agent = create_fact_checker_agent()
    
    prompt = f"""以下の情報に基づいて、侵害分析の推論を検証してください:

# 対象分子:
{target_smiles}

# 特許PDFブロック:
{block_text[:3000]}

# 侵害分析結果:
侵害: {"保護されている" if input_is_protected else "保護されていない"}

分析: {input_reasoning[:2000]}

上記の分析で使用されたすべての証拠が特許文書に記載されていることを確認してください。
出力はMarkdown形式で、見出しや箇条書きを使って読みやすく整形してください。

## 検証結果

### 証拠の確認
（各証拠について検証）

### 検証済み事実
（確認された事実のリスト）

### 結論
（検証結果の要約）
"""
    
    result = agent(prompt)
    return str(result)
