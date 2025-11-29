"""サンプルデータ - 論文のCase Study (Figure 2, Appendix C)に基づく"""

# サンプルクエリ分子（論文Figure 2より - NOT PROTECTED）
SAMPLE_QUERY_MOLECULE = "c1ccc([C@]2(CCNCc3ccnnc3)CCOC3(CCCC3)C2)nc1"

# サンプル特許クレーム（論文Appendix Cに基づく実際の特許クレーム形式）
SAMPLE_PATENT_CLAIM = """
Claims (36)
-----------
What is claimed is:

1. A compound having a formula of

\\begin{molecule}
\\caption{C1(*)(*)OC2(CCCC2)CC(*)(CCN(C*)*) C1<sep><a>1:R[21]</a><a>2:R[22]</a><a>11:D[1]</a><a>16:B</a><a>17:B</a>}
\\end{molecule}

or a pharmaceutically acceptable salt thereof, wherein:
- R21 and R22 are independently H or CH3;
- D1 is an optionally substituted aryl;
- B3 is H or optionally substituted alkyl; and
- B5 is an optionally substituted thiophenyl,
wherein a hydrogen is replaced with a deuterium.

2. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein D1 is an optionally substituted phenyl or an optionally substituted pyridyl.

3. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein D1 is pyridyl.

4. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein D1 is 2-pyridyl.

5. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein B5 is an optionally substituted thiophenyl selected from the group consisting of

\\begin{molecule}
\\caption{*c1cccs1}
\\end{molecule}

and

\\begin{molecule}
\\caption{*c1ccsc1}
\\end{molecule}

6. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein B5 is

\\begin{molecule}
\\caption{*C1SC=CC=1<sep><a>0:<dum></a><r>0:R[23]</r><r>0:R[30]</r>}
\\end{molecule}

or

\\begin{molecule}
\\caption{C1=CSC=C(*)C=1<sep><r>0:R[24]</r><r>0:R[30]</r><a>5:<dum></a>}
\\end{molecule}

wherein R23, R24, and R30 are each independently H, OH, cycle, aryl, branched or unbranched alkyl alcohol, halo, branched or unbranched alkyl, amide, cyano, alkoxy, haloalkyl, aklylsulfonyl, nitrite, alkylsulfanyl; or R23 and R24 together form an aryl or cycle that is attached to one or more of the atoms of B5.

7. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein B3 is H.

8. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein B3 is methyl.

9. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein B3 is ethyl.

10. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein R21 is H.

11. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein R22 is H.

12. The compound of claim 1, or a pharmaceutically acceptable salt thereof, wherein both R21 and R22 are H.

---

Core Markush Structure (Formula IX):
*CN(*)CCC1(*)CC(*)(*)OC2(CCCC2)C1<sep><a>0:B[5]</a><a>3:B[3]</a><a>7:D[1]</a><a>10:R[21]</a><a>11:R[22]</a>

R-Group Definitions (from Google Patent Database):
- B[5]: optionally substituted thiophenyl (任意に置換されたチオフェニル)
  - Allowed: *c1cccs1, *c1ccsc1 (thiophene derivatives)
  - NOT allowed: pyridazinyl, pyridinyl, or other heteroaryl groups
- B[3]: H or optionally substituted alkyl (Hまたは任意に置換されたアルキル)
- D[1]: optionally substituted aryl (任意に置換されたアリール)
  - Includes: phenyl, pyridyl (2-pyridyl specifically mentioned in claim 4)
- R[21]: independently H or CH3 (独立してHまたはCH3)
- R[22]: independently H or CH3 (独立してHまたはCH3)

---

Example Analysis (from paper Figure 2):

Query Molecule: c1ccc([C@]2(CCNCc3ccnnc3)CCOC3(CCCC3)C2)nc1

R-Group Mapping Extracted by Chemical Software:
{
    "B5": "c1ccnnc1",    // Pyridazine ring (ピリダジン環)
    "B3": "[H][H]",      // Hydrogen (水素)
    "D1": "c1ccccn1",    // Pyridine ring (ピリジン環)
    "R21": "[H][H]",     // Hydrogen (水素)
    "R22": "[H][H]"      // Hydrogen (水素)
}

Analysis Result:
- B5 (Atom Index 0): Pyridazinyl (c1ccnnc1)
  - Definition in Claims: "an optionally substituted thiophenyl"
  - Assessment: Pyridazinyl is a six-membered aromatic ring containing two adjacent nitrogen atoms.
    Thiophenyl refers to a five-membered aromatic ring containing a sulfur atom (thiophene).
    The pyridazinyl group is structurally and functionally different from the thiophenyl group.
  - Conclusion: **Does NOT align with the claim requirements**

- B3 (Atom Index 3): Hydrogen ([H][H])
  - Definition in Claims: "H or optionally substituted alkyl"
  - Conclusion: **Aligns with the claim requirements**

- D1 (Atom Index 7): Pyridyl (c1ccccn1)
  - Definition in Claims: "an optionally substituted aryl" (Claims 2-4 specify pyridyl)
  - Conclusion: **Aligns with the claim requirements**

- R21 and R22 (Atom Indices 10 and 11): Both Hydrogen ([H][H])
  - Definition in Claims: "independently H or CH3"
  - Conclusion: **Align with the claim requirements**

Final Prediction: **NOT PROTECTED**
Reason: The B5 substituent (pyridazinyl) does not meet the specific definitions provided for B5 in the claims (must be thiophenyl).
"""

# 拡張SMILES形式の説明
EXTENDED_SMILES_EXPLANATION = """
## 拡張SMILES形式について

PatentFinderでは、Markush構造を表現するために拡張SMILES形式を使用します。

### 形式:
`SMILES<sep>EXTENSION`

### 例:
`*CN(*)CCC1(*)CC(*)(*)OC2(CCCC2)C1<sep><a>0:B[5]</a><a>3:B[3]</a><a>7:D[1]</a><a>10:R[21]</a><a>11:R[22]</a>`

### 解説:
- `*` はR基の接続点（アスタリスク）
- `<sep>` はSMILESとEXTENSIONの区切り
- `<a>0:B[5]</a>` は「原子インデックス0がB[5]というR基に対応」を意味
- 原子インデックスはSMILES文字列中のアスタリスクの出現順（0から開始）

### タグの種類:
- `<a>`: 原子インデックスとR基名のマッピング
- `<r>`: 環インデックスとR基名のマッピング
- `<c>`: 円インデックスとR基名のマッピング
- `<dum>`: 接続点を示す特殊トークン

### R基マッピング例:
```json
{
    "B5": "c1ccnnc1",    // Pyridazine ring
    "B3": "[H][H]",      // Hydrogen
    "D1": "c1ccccn1",    // Pyridine ring
    "R21": "[H][H]",     // Hydrogen
    "R22": "[H][H]"      // Hydrogen
}
```

### 論文での使用例:
- MarkushParser: 画像から拡張SMILESへの変換
- MarkushMatcher: 分子とMarkush構造のマッチング
- 各エージェント: R基の値の検証と分析
"""

# 保護される分子の例（論文より）
SAMPLE_PROTECTED_MOLECULE = "c1ccc([C@]2(CCNCc3cccs3)CCOC3(CCCC3)C2)nc1"
# B5 = thiophenyl (c1cccs1) ✓ - これは保護される
