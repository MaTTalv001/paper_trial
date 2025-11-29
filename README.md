# PatentFinder - 論文再現実装

Multi-Agent System for Automated Molecular Patent Infringement Assessment

論文: [Intelligent System for Automated Molecular Patent Infringement Assessment](https://arxiv.org/abs/2412.07819) (arXiv:2412.07819v2)

## 概要

PatentFinderは、小分子の特許侵害を自動評価するマルチエージェントシステムです。5つの専門エージェントが協調して特許クレームと分子構造を分析し、解釈可能な侵害レポートを生成します。

## システム構成

### エージェント
1. **Planner** - サブタスク調整・最終レポート作成
2. **Sketch Extractor** - Markush構造抽出 (ダミー実装)
3. **Substituents Matcher** - 置換基マッチング (ダミー実装)
4. **Requirements Examinator** - 要件適合性評価
5. **Fact Checker** - 出力検証・修正

### ツールモデル (ダミー実装)
- MarkushMatcher - 置換基グループ抽出
- MarkushParser - Markush画像→拡張SMILES変換
- RDKit Substructure Matcher - サブ構造マッチング

## セットアップ

### 1. 環境変数の設定

```bash
cp .env.template .env
# .envを編集してAWS認証情報を設定
```

### 2. Docker Composeで起動

```bash
docker compose up --build
```

### 3. ブラウザでアクセス

http://localhost:8501

## 拡張SMILES形式

PatentFinderでは、Markush構造を表現するために拡張SMILES形式を使用します。

```
SMILES<sep>EXTENSION
```

例:
```
*CN(*)CCC1(*)CC(*)(*)OC2(CCCC2)C1<sep><a>0:B[5]</a><a>3:B[3]</a><a>7:D[1]</a><a>10:R[21]</a><a>11:R[22]</a>
```

## 技術スタック

- Python 3.11
- Strands Agents (AWS Bedrock)
- Streamlit
- Docker

## 注意事項

- Sketch ExtractorとSubstituents Matcherはダミー実装です（別途技術検証済み）
- Planner、Requirements Examinator、Fact CheckerはStrands Agentで実装
- 実際の特許侵害判定には専門家の確認が必要です

## ライセンス

研究目的での使用を想定しています。
