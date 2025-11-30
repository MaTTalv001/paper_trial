"""Requirements Examinator Agent - 特許要件との適合性を評価するエージェント

論文より: Requirements Examinator assesses whether the query molecule 
meets the patent's substituent group requirements

論文の設定: OpenAI-o1をtemperature=1.0で使用（推論を促進するため）
"""
import os
from strands import Agent
from prompts import EXTENDED_SMILES_DEFINITION, REQUIREMENTS_EXAMINATOR_PROMPT_TEMPLATE

MODEL_ID = os.getenv("MODEL_ID", "jp.anthropic.claude-haiku-4-5-20251001-v1:0")

# 論文Appendix Aに基づくプロンプト
EXAMINATOR_PROMPT = REQUIREMENTS_EXAMINATOR_PROMPT_TEMPLATE.format(
    extended_smiles_definition=EXTENDED_SMILES_DEFINITION
)

def create_examinator_agent() -> Agent:
    """Requirements Examinatorエージェントを作成"""
    return Agent(
        model=MODEL_ID,
        system_prompt=EXAMINATOR_PROMPT
    )

def examine_requirements(
    markush_string: str,
    molecule_string: str,
    match_result: dict,
    claim_text: str
) -> str:
    """置換基グループが特許要件を満たすか検証
    
    Args:
        markush_string: Markush構造の拡張SMILES文字列
        molecule_string: クエリ分子のSMILES文字列
        match_result: Substituents Matcherからのマッチング結果
        claim_text: 特許クレームテキスト
    
    Returns:
        検証結果（Markdown形式の文字列）
    """
    agent = create_examinator_agent()
    r_group_mapping = match_result.get("r_group_mapping", {})
    
    prompt = f"""以下の情報に基づいて、クエリ分子が特許の保護範囲に含まれるか検証してください:

**Markushクレーム**: '{markush_string}'

**現在のサブ構造マッチング結果:**
{r_group_mapping}

**クエリ分子**:
{molecule_string}

**クレーム要件テキスト:**
{claim_text}

各R基について、クレーム要件との適合性を詳細に分析し、最終的な判定を提供してください。
出力はMarkdown形式で、見出しや箇条書きを使って読みやすく整形してください。

## 分析結果

### R基適合性チェック
（各R基について分析）

### 最終判定
（PROTECTED または NOT PROTECTED）

### 判定理由
（詳細な理由）
"""
    
    result = agent(prompt)
    return str(result)
