"""Substituents Matcher Agent - 置換基グループをマッチングするエージェント

論文より: Substituents Matcher identifies and validates substituent groups 
in Markush expressions relative to the query molecule

構成:
1. RDKit Substructure Matcher（ルールベース）→ r_group_mapping
2. MarkushMatcher（ニューラルネットワーク、T5ベース）→ nn_result
3. LLMエージェント（GPT-4o with vision）→ 両結果を検証・統合
"""


def rdkit_substructure_match(query_molecule: str, markush_structure: dict) -> dict:
    """
    ダミーのRDKitサブ構造マッチング
    
    実際の実装では:
    - RDKitを使用してMarkush骨格とクエリ分子をマッチング
    - 各R基の接続点から置換基を抽出
    """
    # クエリ分子からB5の値を判定（ダミー実装）
    if "cccs" in query_molecule or "ccsc" in query_molecule:
        # thiophenyl（硫黄含有）→ PROTECTED
        b5_value = "c1cccs1"
        b5_desc = "Thiophene ring"
    elif "ccnnc" in query_molecule:
        # pyridazinyl（窒素含有）→ NOT PROTECTED
        b5_value = "c1ccnnc1"
        b5_desc = "Pyridazine ring"
    else:
        b5_value = "unknown"
        b5_desc = "Unknown substituent"
    
    return {
        "method": "RDKit Substructure Matcher",
        "skeleton_match": True,
        "r_group_mapping": {
            "B5": b5_value,
            "B3": "[H][H]",
            "D1": "c1ccccn1",
            "R21": "[H][H]",
            "R22": "[H][H]"
        },
        "b5_description": b5_desc,
        "confidence": 0.6,
        "notes": "ルールベースマッチング完了。"
    }


def markush_matcher_nn(query_molecule: str, markush_structure: dict) -> dict:
    """
    ダミーのMarkushMatcher（ニューラルネットワーク）
    
    実際の実装では:
    - T5ベースモデル（MolT5-largeで初期化）
    - 入力: 分子SMILES + Markush構造
    - 出力: R基マッピング（JSON形式）
    """
    # クエリ分子からB5の値を判定（ダミー実装）
    if "cccs" in query_molecule or "ccsc" in query_molecule:
        b5_value = "C1=CC=CS1"  # NNモデルの出力形式
        b5_desc = "Thiophene ring"
    elif "ccnnc" in query_molecule:
        b5_value = "CC1C=NN=CC=1"
        b5_desc = "Pyridazine ring"
    else:
        b5_value = "unknown"
        b5_desc = "Unknown substituent"
    
    return {
        "method": "MarkushMatcher (Neural Network)",
        "skeleton_match": True,
        "r_group_mapping": {
            "B5": b5_value,
            "B3": "[H]",
            "D1": "C1N=CC=CC=1",
            "R21": "[H]",
            "R22": "[H]"
        },
        "b5_description": b5_desc,
        "confidence": 0.85,
        "notes": "ニューラルネットワークによる予測。"
    }


def match_substituents(query_molecule: str, markush_structure: dict) -> dict:
    """
    置換基マッチングの統合処理
    
    1. RDKitでルールベースマッチング
    2. MarkushMatcherでNNベースマッチング
    3. 両結果を統合（実際はLLMエージェントが検証・統合）
    """
    # Step 1: RDKitによるルールベースマッチング
    rdkit_result = rdkit_substructure_match(query_molecule, markush_structure)
    
    # Step 2: MarkushMatcherによるNNベースマッチング
    nn_result = markush_matcher_nn(query_molecule, markush_structure)
    
    # Step 3: 結果の統合
    verified_mapping = {}
    for key in rdkit_result["r_group_mapping"]:
        rdkit_value = rdkit_result["r_group_mapping"].get(key, "")
        verified_mapping[key] = rdkit_value
    
    # B5の値に基づいて説明を設定
    if "cccs" in query_molecule or "ccsc" in query_molecule:
        b5_verified = "c1cccs1"
        b5_nn = "C1=CC=CS1"
        b5_desc = "Thiophene ring（チオフェン環）- 硫黄含有5員環"
        b5_status = "両手法で一致（thiophenyl）"
    elif "ccnnc" in query_molecule:
        b5_verified = "c1ccnnc1"
        b5_nn = "CC1C=NN=CC=1"
        b5_desc = "Pyridazine ring（ピリダジン環）- 窒素含有6員環"
        b5_status = "両手法で一致（pyridazinyl）"
    else:
        b5_verified = "unknown"
        b5_nn = "unknown"
        b5_desc = "Unknown substituent"
        b5_status = "不明"
    
    return {
        "query_molecule": query_molecule,
        "markush_string": markush_structure.get("core_markush_smiles", ""),
        "skeleton_match": rdkit_result["skeleton_match"] and nn_result["skeleton_match"],
        
        # 両方の結果を保持
        "rdkit_result": rdkit_result,
        "nn_result": nn_result,
        
        # 検証済みの統合結果
        "r_group_mapping": verified_mapping,
        
        # 詳細な置換基分析
        "substituent_analysis": [
            {
                "group_id": "B[5]",
                "atom_index": 0,
                "rdkit_value": b5_verified,
                "nn_value": b5_nn,
                "verified_value": b5_verified,
                "description": b5_desc,
                "match_status": b5_status
            },
            {
                "group_id": "B[3]",
                "atom_index": 3,
                "rdkit_value": "[H][H]",
                "nn_value": "[H]",
                "verified_value": "[H][H]",
                "description": "Hydrogen（水素）",
                "match_status": "両手法で一致"
            },
            {
                "group_id": "D[1]",
                "atom_index": 7,
                "rdkit_value": "c1ccccn1",
                "nn_value": "C1N=CC=CC=1",
                "verified_value": "c1ccccn1",
                "description": "Pyridine ring（ピリジン環）",
                "match_status": "両手法で一致（表記の違いのみ）"
            },
            {
                "group_id": "R[21]",
                "atom_index": 10,
                "rdkit_value": "[H][H]",
                "nn_value": "[H]",
                "verified_value": "[H][H]",
                "description": "Hydrogen（水素）",
                "match_status": "両手法で一致"
            },
            {
                "group_id": "R[22]",
                "atom_index": 11,
                "rdkit_value": "[H][H]",
                "nn_value": "[H]",
                "verified_value": "[H][H]",
                "description": "Hydrogen（水素）",
                "match_status": "両手法で一致"
            }
        ],
        
        "tanimoto_similarity": 0.929,
        "verification_notes": f"RDKitとMarkushMatcherの両結果を比較検証。B5 = {b5_desc}",
        "status": "dummy_matched"
    }
