"""Planner Agent - サブタスクを調整し、最終的な侵害レポートを作成するエージェント

論文より: Planner coordinates subtasks among agents and compiles 
a comprehensive infringement report

論文の設定: GPT-4oをtemperature=0.2で使用（一貫性と正確性のため）
"""
import os
from strands import Agent
from prompts import EXTENDED_SMILES_DEFINITION, PLANNER_PROMPT_TEMPLATE

MODEL_ID = os.getenv("MODEL_ID", "jp.anthropic.claude-haiku-4-5-20251001-v1:0")

# 論文Appendix Aに基づくプロンプト
PLANNER_PROMPT = PLANNER_PROMPT_TEMPLATE.format(
    extended_smiles_definition=EXTENDED_SMILES_DEFINITION
)

def create_planner_agent() -> Agent:
    """Plannerエージェントを作成"""
    return Agent(
        model=MODEL_ID,
        system_prompt=PLANNER_PROMPT
    )

def plan_and_coordinate(
    query_molecule: str,
    patent_info: str,
    sketch_result: dict,
    matcher_result: dict,
    examinator_result: str,
    fact_check_result: str
) -> str:
    """全エージェントの結果を統合して最終レポートを作成
    
    Args:
        query_molecule: クエリ分子のSMILES文字列
        patent_info: 特許情報テキスト
        sketch_result: Sketch Extractorの結果
        matcher_result: Substituents Matcherの結果
        examinator_result: Requirements Examinatorの結果
        fact_check_result: Fact Checkerの結果
    
    Returns:
        侵害レポート（JSON形式の文字列）
    """
    agent = create_planner_agent()
    
    prompt = f"""以下の情報に基づいて、特許侵害評価の最終レポートを作成してください:

## クエリ分子
SMILES: {query_molecule}

## 特許情報
{patent_info[:2000]}...  # 長すぎる場合は切り詰め

## Sketch Extractor結果
コアMarkush構造: {sketch_result.get('core_markush_smiles', 'N/A')}
クレーム要件: {sketch_result.get('claim_requirements', {})}

## Substituents Matcher結果
R基マッピング: {matcher_result.get('r_group_mapping', {})}
骨格マッチ: {matcher_result.get('skeleton_match', False)}

## Requirements Examinator結果
{examinator_result}

## Fact Checker結果
{fact_check_result}

上記の全ての分析結果を統合し、以下を含む包括的な侵害レポートを作成してください:
1. クエリ分子の構造
2. 特許で保護されているコアMarkushの構造とR基定義
3. 各R基の値と特許要件との適合性
4. 最終的な侵害判定と理由
"""
    result = agent(prompt)
    return str(result)
