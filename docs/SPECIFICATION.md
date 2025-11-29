# PatentFinder 仕様書

## 1. 概要

### 1.1 プロジェクト目的
論文「Intelligent System for Automated Molecular Patent Infringement Assessment」(arXiv:2412.07819v2) の再現実装。小分子の特許侵害を自動評価するマルチエージェントシステムを構築する。

### 1.2 実装範囲
- **実装対象**: Planner, Requirements Examinator, Fact Checker（Strands Agentで実装）
- **ダミー実装**: Sketch Extractor, Substituents Matcher（別途技術検証済みのため）
- **未実装**: MarkushMatcher, MarkushParser, RDKit Substructure Matcher（ニューラルネットワークモデル）

### 1.3 技術スタック
- Python 3.11
- Strands Agents（AWS Bedrock経由でLLM呼び出し）
- Streamlit（Web UI）
- Docker / Docker Compose

---

## 2. アーキテクチャ

### 2.1 システム構成図

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Web UI                         │
│                      (app/main.py)                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Planner Agent                          │
│              (サブタスク調整・レポート作成)                    │
└─────────────────────────────────────────────────────────────┘
          │              │              │              │
          ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Sketch     │ │ Substituents │ │ Requirements │ │    Fact      │
│  Extractor   │ │   Matcher    │ │  Examinator  │ │   Checker    │
│   (ダミー)    │ │   (ダミー)    │ │  (Strands)   │ │  (Strands)   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

### 2.2 ディレクトリ構成

```
patentfinder/
├── app/
│   ├── agents/
│   │   ├── __init__.py           # エージェントモジュールのエクスポート
│   │   ├── planner.py            # Plannerエージェント
│   │   ├── sketch_extractor.py   # Sketch Extractor（ダミー）
│   │   ├── substituents_matcher.py # Substituents Matcher（ダミー）
│   │   ├── examinator.py         # Requirements Examinator
│   │   └── fact_checker.py       # Fact Checker
│   ├── prompts/
│   │   └── __init__.py           # プロンプト定義（論文Appendix Aより）
│   ├── main.py                   # Streamlit UIエントリーポイント
│   └── sample_data.py            # サンプルデータ（論文Case Studyより）
├── docs/
│   └── SPECIFICATION.md          # 本仕様書
├── .env.template                 # 環境変数テンプレート
├── .gitignore                    # Git除外設定
├── docker-compose.yml            # Docker Compose設定
├── Dockerfile                    # Dockerイメージ定義
├── README.md                     # プロジェクト説明
└── requirements.txt              # Python依存関係
```

---

## 3. エージェント仕様

### 3.1 Planner Agent

**役割**: サブタスクを各エージェントに割り当て、結果を統合して最終的な侵害レポートを作成

**論文での設定**:
- モデル: GPT-4o
- Temperature: 0.2（一貫性と正確性のため）

**入力**:
- クエリ分子（SMILES形式）
- 特許情報（クレームテキスト）
- 各エージェントの出力結果

**出力**:
- 包括的な侵害レポート（JSON形式）

**実装ファイル**: `app/agents/planner.py`

### 3.2 Sketch Extractor（ダミー実装）

**役割**: 特許文書からコアMarkush構造と関連するクレーム要件を抽出

**論文での実装**:
- MarkushParserモデル（Swin Transformer + BART）を使用
- 画像から拡張SMILES形式に変換

**ダミー実装の出力**:
```python
{
    "core_markush_smiles": "*CN(*)CCC1(*)CC(*)(*)OC2(CCCC2)C1<sep><a>0:B[5]</a>...",
    "substituent_positions": [...],
    "claim_requirements": {
        "B[5]": "optionally substituted thiophenyl",
        ...
    }
}
```

**実装ファイル**: `app/agents/sketch_extractor.py`

### 3.3 Substituents Matcher（ダミー実装）

**役割**: クエリ分子の置換基グループをMarkush構造と照合

**論文での実装**:
- MarkushMatcherモデル（T5ベース、MolT5-largeで初期化）
- RDKit Substructure Matcherアルゴリズム
- Vision-LLM（GPT-4o）で検証

**ダミー実装の出力**:
```python
{
    "r_group_mapping": {
        "B5": "c1ccnnc1",    # Pyridazine ring
        "B3": "[H][H]",      # Hydrogen
        "D1": "c1ccccn1",    # Pyridine ring
        ...
    },
    "tanimoto_similarity": 0.929
}
```

**実装ファイル**: `app/agents/substituents_matcher.py`

### 3.4 Requirements Examinator

**役割**: クエリ分子が特許のR基要件を満たすか評価

**論文での設定**:
- モデル: OpenAI-o1
- Temperature: 1.0（推論を促進するため）

**プロンプトの要点**（論文Appendix Aより）:
- 各R基の値をクレーム要件テキストと一つずつ比較
- 「保護されている」結論は慎重に（1つでも不適合なら保護されない）
- ステップバイステップの推論を明確に

**実装ファイル**: `app/agents/examinator.py`

### 3.5 Fact Checker

**役割**: 他エージェントの出力を元の特許文書と照合し、不整合を修正

**論文での設定**:
- モデル: GPT-4o
- Temperature: 0.2

**プロンプトの要点**（論文Appendix Aより）:
- 推論で使用された証拠が特許PDFに存在するか確認
- 関連するブロックインデックスを特定
- 必要に応じてロールバックを実行

**実装ファイル**: `app/agents/fact_checker.py`

---

## 4. 拡張SMILES形式

### 4.1 形式定義

```
SMILES<sep>EXTENSION
```

### 4.2 タグの種類

| タグ | 説明 | 例 |
|------|------|-----|
| `<a>` | 原子インデックスとR基名のマッピング | `<a>0:B[5]</a>` |
| `<r>` | 環インデックスとR基名のマッピング | `<r>0:R[23]</r>` |
| `<c>` | 円インデックスとR基名のマッピング | `<c>0:CIRCLE</c>` |
| `<dum>` | 接続点を示す特殊トークン | `<a>0:<dum></a>` |

### 4.3 例

```
*CN(*)CCC1(*)CC(*)(*)OC2(CCCC2)C1<sep><a>0:B[5]</a><a>3:B[3]</a><a>7:D[1]</a><a>10:R[21]</a><a>11:R[22]</a>
```

- `*` はR基の接続点（アスタリスク）
- 原子インデックスはアスタリスクの出現順（0から開始）

---

## 5. サンプルデータ

### 5.1 NOT PROTECTED例（論文Figure 2より）

**クエリ分子**:
```
c1ccc([C@]2(CCNCc3ccnnc3)CCOC3(CCCC3)C2)nc1
```

**R基マッピング**:
```json
{
    "B5": "c1ccnnc1",    // Pyridazine ring ← NOT thiophenyl
    "B3": "[H][H]",      // Hydrogen ✓
    "D1": "c1ccccn1",    // Pyridine ring ✓
    "R21": "[H][H]",     // Hydrogen ✓
    "R22": "[H][H]"      // Hydrogen ✓
}
```

**判定**: NOT PROTECTED（B5がthiophenylではなくpyridazinyl）

### 5.2 PROTECTED例

**クエリ分子**:
```
c1ccc([C@]2(CCNCc3cccs3)CCOC3(CCCC3)C2)nc1
```

**R基マッピング**:
```json
{
    "B5": "c1cccs1",     // Thiophenyl ✓
    ...
}
```

**判定**: PROTECTED（全R基が要件を満たす）

---

## 6. 環境設定

### 6.1 環境変数

```bash
AWS_ACCESS_KEY_ID=<your-access-key>
AWS_SECRET_ACCESS_KEY=<your-secret-key>
AWS_DEFAULT_REGION=ap-northeast-1
MODEL_ID=jp.anthropic.claude-haiku-4-5-20251001-v1:0
```

### 6.2 Docker設定

- ベースイメージ: `python:3.11-slim`
- ポート: 8501（Streamlit）
- ボリューム: `./app:/app`

---

## 7. 処理フロー

```
1. ユーザー入力
   ├── クエリ分子（SMILES）
   └── 特許クレーム（テキスト）
           │
           ▼
2. Step 1: Sketch Extractor（ダミー）
   └── Markush構造とクレーム要件を抽出
           │
           ▼
3. Step 2: Substituents Matcher（ダミー）
   └── R基マッピングを生成
           │
           ▼
4. Step 3: Requirements Examinator
   └── 各R基の要件適合性を評価
           │
           ▼
5. Step 4: Fact Checker
   └── 推論の証拠を検証
           │
           ▼
6. Step 5: Planner
   └── 最終侵害レポートを作成
           │
           ▼
7. 結果表示
   └── INFRINGES / NOT_INFRINGES
```

---

## 8. 今後の拡張

### 8.1 ダミー実装の置き換え

1. **MarkushParser**: Swin Transformer + BARTモデルの実装
2. **MarkushMatcher**: T5ベースモデルの実装
3. **RDKit統合**: サブ構造マッチングアルゴリズムの実装

### 8.2 機能追加

1. 特許PDF直接入力対応
2. バッチ処理機能
3. 結果のエクスポート機能（PDF/JSON）

---

## 9. 参考文献

- 論文: [arXiv:2412.07819v2](https://arxiv.org/abs/2412.07819)
- コード: [GitHub](https://github.com/syr-cn/patentfinder_code_private)
- データセット: [MolPatent-240](https://github.com/syr-cn/patentfinder_code_private/tree/master/patent_finder/data)
- MarkushMatcherモデル: [OSF](https://osf.io/ftq9g)
- MarkushParserデータ: [OSF](https://osf.io/jsqa3)

---

## 10. 作成履歴

| 日付 | 内容 |
|------|------|
| 2024-11-30 | 初版作成 |
| - | 論文PDF/Markdownから仕様を抽出 |
| - | 5エージェント構成で実装 |
| - | Strands Agentでプランナー、検証エージェントを実装 |
| - | 論文Appendix Aのプロンプトを日本語化して適用 |
| - | Docker Compose環境を構築 |
| - | Streamlit UIを実装 |
