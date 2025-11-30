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
    """全エージェントの結果を統合して最終レポートを作成（非ストリーミング）"""
    agent = create_planner_agent()
    
    prompt = f"""以下の情報に基づいて、特許侵害評価の最終レポートを作成してください:

## クエリ分子
SMILES: {query_molecule}

## 特許情報
{patent_info[:2000]}...

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

上記の全ての分析結果を統合し、包括的な侵害レポートを作成してください。
"""
    result = agent(prompt)
    return str(result)

async def plan_and_coordinate_stream(
    query_molecule: str,
    patent_info: str,
    sketch_result: dict,
    matcher_result: dict,
    examinator_result: str,
    fact_check_result: str
):
    """全エージェントの結果を統合して最終レポートを作成（ストリーミング）"""
    agent = create_planner_agent()
    
    prompt = f"""以下の情報に基づいて、特許侵害評価の最終レポートを作成してください:

## クエリ分子
SMILES: {query_molecule}

## 特許情報
{patent_info[:2000]}...

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

上記の全ての分析結果を統合し、包括的な侵害レポートをMarkdown形式で作成してください。
以下の構成で出力してください:

# 特許侵害評価レポート

## 1. クエリ分子の構造
## 2. 特許Markush構造とR基定義
## 3. R基適合性分析
## 4. 最終判定
## 5. 判定理由
"""
    
    async for event in agent.stream_async(prompt):
        if hasattr(event, 'data'):
            yield event.data
        elif isinstance(event, str):
            yield event
        elif hasattr(event, 'content'):
            yield event.content
