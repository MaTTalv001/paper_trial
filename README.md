# PatentFinder - 論文再現実装

Multi-Agent System for Automated Molecular Patent Infringement Assessment

論文: [Intelligent System for Automated Molecular Patent Infringement Assessment](https://arxiv.org/abs/2412.07819) (arXiv:2412.07819v2)

## 概要

PatentFinderは、小分子の特許侵害を自動評価するマルチエージェントシステムです。5つの専門エージェントが協調して特許クレームと分子構造を分析し、解釈可能な侵害レポートを生成します。

## システム全体フロー

```mermaid
flowchart TD
    subgraph Input["ユーザー入力"]
        U1[クエリ分子<br/>SMILES形式]
        U2[特許文書<br/>PDF/テキスト]
    end

    subgraph SE["Step 1: Sketch Extractor"]
        SE_OUT[コアMarkush構造<br/>+ クレーム要件]
    end

    subgraph SM["Step 2: Substituents Matcher"]
        SM_OUT[R基マッピング<br/>検証済み]
    end

    subgraph RE["Step 3: Requirements Examinator"]
        RE_OUT[適合性評価<br/>PROTECTED/NOT PROTECTED]
    end

    subgraph FC["Step 4: Fact Checker"]
        FC_OUT[証拠検証結果]
    end

    subgraph PL["Step 5: Planner"]
        PL_OUT[侵害レポート]
    end

    U2 --> SE --> SE_OUT
    U1 --> SM
    SE_OUT --> SM --> SM_OUT
    SM_OUT --> RE
    SE_OUT --> RE --> RE_OUT
    RE_OUT --> FC
    U2 --> FC --> FC_OUT
    SE_OUT --> PL
    SM_OUT --> PL
    RE_OUT --> PL
    FC_OUT --> PL --> PL_OUT
```

## 各エージェントの詳細フロー

### Step 1: Sketch Extractor

```mermaid
flowchart LR
    subgraph Input
        PDF[特許PDF]
    end
    
    subgraph Tools
        PARSER[PDF Parser<br/>文書セグメンテーション]
        OCSR[MarkushParser<br/>Swin Transformer + BART]
    end
    
    subgraph Process
        SEG[ページ要素を検出<br/>YOLO]
        EXTRACT[Markush画像を抽出]
        CONVERT[拡張SMILESに変換]
        CLAIM[クレーム要件を抽出]
    end
    
    subgraph Output
        MARKUSH[コアMarkush構造<br/>拡張SMILES形式]
        REQ[R基定義<br/>クレーム要件]
    end
    
    PDF --> PARSER --> SEG --> EXTRACT
    EXTRACT --> OCSR --> CONVERT --> MARKUSH
    PDF --> CLAIM --> REQ
```

**入出力:**
| 項目 | 内容 |
|------|------|
| **入力** | 特許文書（PDF/テキスト） |
| **出力** | コアMarkush構造（拡張SMILES）、R基定義、クレーム要件 |
| **ツール** | MarkushParser（Swin Transformer + BART）、PDF Parser、YOLO |

### Step 2: Substituents Matcher

```mermaid
flowchart TB
    subgraph Input
        MOL[クエリ分子<br/>SMILES]
        MARKUSH[コアMarkush構造]
    end
    
    subgraph "並列処理"
        subgraph RDKit["RDKit Substructure Matcher"]
            RD1[骨格マッチング]
            RD2[置換基抽出]
            RD3[r_group_mapping]
        end
        
        subgraph NN["MarkushMatcher (T5)"]
            NN1[SMILES入力]
            NN2[Transformer処理]
            NN3[nn_result]
        end
    end
    
    subgraph LLM["LLMエージェント (GPT-4o)"]
        V1[両結果を比較]
        V2[化学的等価性を検証]
        V3[エラー修正]
        V4[統合マッピング作成]
    end
    
    subgraph Output
        OUT[検証済みR基マッピング]
    end
    
    MOL --> RDKit
    MARKUSH --> RDKit
    RD1 --> RD2 --> RD3
    
    MOL --> NN
    MARKUSH --> NN
    NN1 --> NN2 --> NN3
    
    RD3 --> LLM
    NN3 --> LLM
    V1 --> V2 --> V3 --> V4 --> OUT
```

**入出力:**
| 項目 | 内容 |
|------|------|
| **入力** | クエリ分子（SMILES）、コアMarkush構造 |
| **出力** | 検証済みR基マッピング（RDKit結果 + NN結果 + 統合結果） |
| **ツール** | RDKit、MarkushMatcher（T5ベース）、GPT-4o（検証用） |

**2つのマッチング手法:**

| 手法 | 特徴 | Accuracy | Tanimoto |
|------|------|----------|----------|
| RDKit | ルールベース、単純な置換基に有効 | ≈0% | 低い |
| MarkushMatcher | T5ベースNN、高精度 | 66.8% | 92.9% |

→ **両方の結果をLLMが検証・統合**

### Step 3: Requirements Examinator

```mermaid
flowchart TB
    subgraph Input
        MAP[R基マッピング]
        REQ[クレーム要件]
        MOL[クエリ分子]
    end
    
    subgraph Process["LLMエージェント (OpenAI-o1, temp=1.0)"]
        P1[各R基の値を取得]
        P2[対応するクレーム要件を参照]
        P3[化学構造を比較]
        P4[適合/不適合を判定]
        P5[全R基の結果を集約]
    end
    
    subgraph Output
        EVAL[各R基の適合性評価]
        VERDICT[最終判定<br/>PROTECTED / NOT PROTECTED]
    end
    
    MAP --> P1
    REQ --> P2
    MOL --> P3
    P1 --> P3
    P2 --> P3
    P3 --> P4 --> P5
    P5 --> EVAL
    P5 --> VERDICT
```

**入出力:**
| 項目 | 内容 |
|------|------|
| **入力** | R基マッピング、クレーム要件、クエリ分子 |
| **出力** | 各R基の適合性評価、最終判定 |
| **モデル** | OpenAI-o1（temperature=1.0、推論促進） |

### Step 4: Fact Checker

```mermaid
flowchart TB
    subgraph Input
        REASONING[前ステップの推論]
        PATENT[特許文書（原文）]
    end
    
    subgraph Process["LLMエージェント (GPT-4o, temp=0.2)"]
        F1[推論で使用された<br/>証拠を抽出]
        F2[各証拠を特許文書と照合]
        F3{証拠は<br/>文書に存在?}
        F4[検証済みとしてマーク]
        F5[ハルシネーションとして検出]
        F6{ロールバック<br/>必要?}
    end
    
    subgraph Output
        VERIFIED[検証済み事実リスト]
        HALLUC[検出されたハルシネーション]
        ROLLBACK[ロールバック指示]
    end
    
    REASONING --> F1 --> F2 --> F3
    PATENT --> F2
    F3 -->|Yes| F4 --> VERIFIED
    F3 -->|No| F5 --> HALLUC
    F5 --> F6
    F6 -->|Yes| ROLLBACK
    F6 -->|No| VERIFIED
```

**入出力:**
| 項目 | 内容 |
|------|------|
| **入力** | Requirements Examinatorの出力、特許文書（原文） |
| **出力** | 証拠検証結果、ハルシネーション検出、ロールバック指示 |
| **モデル** | GPT-4o（temperature=0.2、正確性重視） |

**重要**: Fact Checkerは**侵害判定の正誤を判断しない**。**推論の根拠が特許文書に実在するか**を検証する。

### Step 5: Planner

```mermaid
flowchart TB
    subgraph Input
        SE_R[Sketch Extractor結果]
        SM_R[Substituents Matcher結果]
        RE_R[Requirements Examinator結果]
        FC_R[Fact Checker結果]
    end
    
    subgraph Process["LLMエージェント (GPT-4o, temp=0.2)"]
        P1[全結果を収集]
        P2[情報を構造化]
        P3[侵害レポート作成]
    end
    
    subgraph Output
        REPORT[侵害レポート]
        VERDICT[最終判定<br/>INFRINGES / NOT_INFRINGES]
    end
    
    SE_R --> P1
    SM_R --> P1
    RE_R --> P1
    FC_R --> P1
    P1 --> P2 --> P3
    P3 --> REPORT
    P3 --> VERDICT
```

**入出力:**
| 項目 | 内容 |
|------|------|
| **入力** | 全エージェントの出力 |
| **出力** | 包括的な侵害レポート、最終判定 |
| **モデル** | GPT-4o（temperature=0.2） |

## データフロー詳細

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant SE as Sketch Extractor
    participant RDKit as RDKit
    participant NN as MarkushMatcher
    participant SM as Substituents Matcher<br/>(LLM)
    participant RE as Requirements Examinator
    participant FC as Fact Checker
    participant PL as Planner

    User->>SE: 特許文書
    SE->>SE: PDF解析 + OCSR
    SE-->>SM: コアMarkush構造
    SE-->>RE: クレーム要件
    
    User->>RDKit: クエリ分子
    User->>NN: クエリ分子
    
    par 並列処理
        RDKit->>RDKit: ルールベースマッチング
        RDKit-->>SM: r_group_mapping
    and
        NN->>NN: NNベースマッチング
        NN-->>SM: nn_result
    end
    
    SM->>SM: 両結果を検証・統合
    SM-->>RE: 検証済みR基マッピング
    
    RE->>RE: 各R基の適合性評価
    RE-->>FC: 判定結果 + 推論
    
    User->>FC: 特許文書（原文）
    FC->>FC: 証拠の検証
    FC-->>PL: 検証結果
    
    SE-->>PL: Markush構造
    SM-->>PL: R基マッピング
    RE-->>PL: 適合性評価
    PL->>PL: レポート統合
    PL->>User: 侵害レポート
```

## 具体例

### 入力

**クエリ分子:**
```
c1ccc([C@]2(CCNCc3ccnnc3)CCOC3(CCCC3)C2)nc1
```

**特許クレーム（抜粋）:**
```
B5 is an optionally substituted thiophenyl
B3 is H or optionally substituted alkyl
D1 is an optionally substituted aryl
R21 and R22 are independently H or CH3
```

### Step 2: Substituents Matcher の出力

```json
{
  "rdkit_result": {
    "r_group_mapping": {
      "B5": "c1ccnnc1",
      "B3": "[H][H]",
      "D1": "c1ccccn1"
    }
  },
  "nn_result": {
    "r_group_mapping": {
      "B5": "CC1C=NN=CC=1",
      "B3": "[H]",
      "D1": "C1N=CC=CC=1"
    }
  },
  "r_group_mapping": {
    "B5": "c1ccnnc1",
    "B3": "[H][H]",
    "D1": "c1ccccn1"
  },
  "verification_notes": "RDKitとNNの結果を比較検証。表記の違いはあるが化学的に等価。"
}
```

### Step 3: Requirements Examinator の出力

```markdown
## R基適合性チェック

### B5 (Atom Index 0)
- **分子中の値**: c1ccnnc1 (Pyridazine ring)
- **クレーム要件**: optionally substituted thiophenyl
- **評価**: ❌ 不適合
  - Pyridazine: 6員環、2つの窒素
  - Thiophenyl: 5員環、硫黄含有
  - 構造的に異なる

### B3, D1, R21, R22
- **評価**: ✅ 適合

### 最終判定: NOT PROTECTED
```

### Step 4: Fact Checker の出力

```markdown
## 証拠の確認

### 「B5 = thiophenyl」の根拠
- Claim 1: "B5 is an optionally substituted thiophenyl"
- ✅ 特許文書に存在

### 結論
- すべての証拠が特許文書に裏付けられている
- 「NOT PROTECTED」という判定は正当
```

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

```
SMILES<sep>EXTENSION
```

例:
```
*CN(*)CCC1(*)CC(*)(*)OC2(CCCC2)C1<sep><a>0:B[5]</a><a>3:B[3]</a><a>7:D[1]</a><a>10:R[21]</a><a>11:R[22]</a>
```

| タグ | 説明 | 例 |
|------|------|-----|
| `<a>` | 原子インデックスとR基名 | `<a>0:B[5]</a>` |
| `<r>` | 環インデックスとR基名 | `<r>0:R[23]</r>` |
| `<dum>` | 接続点 | `<a>0:<dum></a>` |

## 実装状況

| エージェント | 実装 | ツール |
|-------------|------|--------|
| Sketch Extractor | ダミー | MarkushParser, PDF Parser, YOLO |
| Substituents Matcher | ダミー | RDKit, MarkushMatcher, GPT-4o |
| Requirements Examinator | Strands Agent | OpenAI-o1 (temp=1.0) |
| Fact Checker | Strands Agent | GPT-4o (temp=0.2) |
| Planner | Strands Agent | GPT-4o (temp=0.2) |

## 参考文献

- 論文: [arXiv:2412.07819v2](https://arxiv.org/abs/2412.07819)
- コード: [GitHub](https://github.com/syr-cn/patentfinder_code_private)
- データセット: [MolPatent-240](https://github.com/syr-cn/patentfinder_code_private/tree/master/patent_finder/data)
