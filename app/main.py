"""PatentFinder - Multi-Agent Molecular Patent Infringement Assessment System

論文再現: Intelligent System for Automated Molecular Patent Infringement Assessment
(arXiv:2412.07819v2)
"""
import streamlit as st
from dotenv import load_dotenv

from agents import (
    plan_and_coordinate,
    extract_markush_structure,
    match_substituents,
    examine_requirements,
    check_facts
)
from sample_data import (
    SAMPLE_QUERY_MOLECULE,
    SAMPLE_PATENT_CLAIM,
    SAMPLE_PROTECTED_MOLECULE,
    EXTENDED_SMILES_EXPLANATION
)

load_dotenv()

st.set_page_config(
    page_title="PatentFinder",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 PatentFinder")
st.markdown("Multi-Agent System for Automated Molecular Patent Infringement Assessment")
st.markdown("*論文再現: arXiv:2412.07819v2*")

# サイドバー
with st.sidebar:
    st.header("システム構成")
    st.markdown("""
    **5つのLLMエージェント:**
    1. 🎯 **Planner** - サブタスク調整・レポート作成
    2. 📐 **Sketch Extractor** - Markush構造抽出 (ダミー)
    3. 🔗 **Substituents Matcher** - 置換基マッチング (ダミー)
    4. 🔬 **Requirements Examinator** - 要件適合性評価
    5. ✅ **Fact Checker** - 出力検証・修正
    
    **ツールモデル (ダミー実装):**
    - MarkushMatcher (T5ベース)
    - MarkushParser (Swin Transformer + BART)
    - RDKit Substructure Matcher
    """)
    
    st.divider()
    
    with st.expander("📖 拡張SMILES形式について"):
        st.markdown(EXTENDED_SMILES_EXPLANATION)

# メイン入力
col1, col2 = st.columns(2)

with col1:
    st.subheader("クエリ分子")
    query_molecule = st.text_area(
        "SMILES形式で入力:",
        height=100,
        placeholder="例: c1ccc([C@]2(CCNCc3ccnnc3)CCOC3(CCCC3)C2)nc1",
        key="query_input"
    )
    
    col1a, col1b = st.columns(2)
    with col1a:
        if st.button("📋 NOT PROTECTED例"):
            st.session_state.query_molecule = SAMPLE_QUERY_MOLECULE
            st.rerun()
    with col1b:
        if st.button("📋 PROTECTED例"):
            st.session_state.query_molecule = SAMPLE_PROTECTED_MOLECULE
            st.rerun()
    
    if "query_molecule" in st.session_state:
        query_molecule = st.session_state.query_molecule
        st.code(query_molecule)
        if query_molecule == SAMPLE_QUERY_MOLECULE:
            st.caption("⚠️ B5=pyridazinyl → NOT PROTECTED")
        elif query_molecule == SAMPLE_PROTECTED_MOLECULE:
            st.caption("✅ B5=thiophenyl → PROTECTED")

with col2:
    st.subheader("特許クレーム")
    patent_info = st.text_area(
        "特許クレームテキスト（拡張SMILES形式のMarkush構造を含む）:",
        height=100,
        placeholder="特許のクレーム情報を入力...",
        key="patent_input"
    )
    
    if st.button("📋 サンプル特許を使用"):
        st.session_state.patent_info = SAMPLE_PATENT_CLAIM
        st.rerun()
    
    if "patent_info" in st.session_state:
        patent_info = st.session_state.patent_info
        with st.expander("特許クレームを表示", expanded=False):
            st.markdown(patent_info)

st.divider()

if st.button("🔍 特許侵害評価を開始", type="primary", use_container_width=True):
    if not query_molecule or not query_molecule.strip():
        st.error("クエリ分子を入力してください")
    elif not patent_info or not patent_info.strip():
        st.error("特許情報を入力してください")
    else:
        # Step 1: Sketch Extractor (ダミー)
        with st.status("📐 Step 1: Markush構造を抽出中...", expanded=True) as status:
            sketch_result = extract_markush_structure(patent_info)
            st.markdown("**抽出結果 (ダミー - MarkushParser + PDF Parser):**")
            st.markdown(f"**コアMarkush構造:**")
            st.code(sketch_result['core_markush_smiles'])
            st.markdown("**クレーム要件:**")
            for key, value in sketch_result["claim_requirements"].items():
                st.markdown(f"- **{key}**: {value}")
            status.update(label="✅ Step 1: Markush構造抽出完了", state="complete")
        
        # Step 2: Substituents Matcher (ダミー)
        with st.status("🔗 Step 2: 置換基グループをマッチング中...", expanded=True) as status:
            matcher_result = match_substituents(query_molecule, sketch_result)
            
            st.markdown("**並列処理結果:**")
            
            col_rdkit, col_nn = st.columns(2)
            
            with col_rdkit:
                st.markdown("**🔧 RDKit (ルールベース):**")
                rdkit_result = matcher_result.get("rdkit_result", {})
                for key, value in rdkit_result.get("r_group_mapping", {}).items():
                    st.markdown(f"- {key}: `{value}`")
                st.caption(f"Confidence: {rdkit_result.get('confidence', 'N/A')}")
            
            with col_nn:
                st.markdown("**🧠 MarkushMatcher (NN):**")
                nn_result = matcher_result.get("nn_result", {})
                for key, value in nn_result.get("r_group_mapping", {}).items():
                    st.markdown(f"- {key}: `{value}`")
                st.caption(f"Confidence: {nn_result.get('confidence', 'N/A')}")
            
            st.markdown("---")
            st.markdown("**✅ 検証済み統合結果 (LLMによる検証):**")
            for key, value in matcher_result["r_group_mapping"].items():
                st.markdown(f"- **{key}**: `{value}`")
            
            st.markdown(f"**Tanimoto類似度:** {matcher_result['tanimoto_similarity']}")
            st.caption(matcher_result.get("verification_notes", ""))
            status.update(label="✅ Step 2: 置換基マッチング完了", state="complete")
        
        # Step 3: Requirements Examinator
        with st.status("🔬 Step 3: 要件適合性を評価中...", expanded=True) as status:
            examinator_result = examine_requirements(
                sketch_result["core_markush_smiles"],
                query_molecule,
                matcher_result,
                patent_info
            )
            st.markdown("**評価結果 (Requirements Examinator - LLM):**")
            st.markdown(examinator_result)
            status.update(label="✅ Step 3: 要件評価完了", state="complete")
        
        # Step 4: Fact Checker
        with st.status("✅ Step 4: 出力を検証中...", expanded=True) as status:
            is_protected = "not_protected" not in examinator_result.lower() and "not protected" not in examinator_result.lower() and "保護されていない" not in examinator_result
            
            fact_check_result = check_facts(
                query_molecule,
                patent_info,
                is_protected,
                examinator_result
            )
            st.markdown("**検証結果 (Fact Checker - LLM):**")
            st.markdown(fact_check_result)
            st.caption("※ Fact Checkerは推論の根拠が特許文書に存在するかを検証します（判定の正誤ではない）")
            status.update(label="✅ Step 4: 事実検証完了", state="complete")
        
        # Step 5: Planner - 最終レポート作成
        with st.status("🎯 Step 5: 侵害レポートを作成中...", expanded=True) as status:
            final_report = plan_and_coordinate(
                query_molecule,
                patent_info,
                sketch_result,
                matcher_result,
                examinator_result,
                fact_check_result
            )
            st.markdown("**最終侵害レポート (Planner - LLM):**")
            st.markdown(final_report)
            status.update(label="✅ Step 5: レポート作成完了", state="complete")
        
        st.success("特許侵害評価が完了しました!")
        st.balloons()

# フッター
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; font-size: 0.8em;">
PatentFinder - 論文再現実装 (arXiv:2412.07819v2)<br>
Sketch Extractor / Substituents Matcher: ダミー実装（MarkushParser, MarkushMatcher, RDKitは別途技術検証済み）<br>
Planner / Requirements Examinator / Fact Checker: Strands Agentで実装
</div>
""", unsafe_allow_html=True)
