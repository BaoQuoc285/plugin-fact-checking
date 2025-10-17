from typing import List, Optional
import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from app.core.evidence_retriever import EvidenceRetriever
from app.core.veracity_predictor import VeracityPredictor
from app.core.evidence_selection import get_selector
from sentence_transformers import SentenceTransformer
import sys
sys.stdout.reconfigure(encoding='utf-8')
class FactCheck:
    """
    Thực hiện quy trình fact-check: lấy bằng chứng, chọn bằng chứng liên quan, dự đoán độ xác thực.
    """
    def __init__(self,search_api_key= None, model_path: str= None,llm_api_params:dict= None, selector_method: str = None):
        self.model_path = model_path
        self.search_api_key = search_api_key
        self.llm_api_params = llm_api_params  # fix: should use llm_api_params, not llm_api_key
        self.selector_method = selector_method
        # Load veracity model trước, chỉ load 1 lần
        self.veracity_predictor = VeracityPredictor(model_path=self.model_path) if self.model_path else None
        # Tối ưu: chỉ khởi tạo EvidenceRetriever một lần
        self._retriever = EvidenceRetriever(search_api_key=self.search_api_key) if self.search_api_key else None
        self.rerank_model=SentenceTransformer("all-MiniLM-L6-v2")
    def retrieve_evidence(self, claim: str, num_results: int = 5) -> List[dict]:
        """
        Truy xuất bằng chứng từ Serper API.
        Returns: List các dict chứa text và source của bằng chứng.
        """
        if not self._retriever:
            raise ValueError("search_api_key is required for EvidenceRetriever")
        return self._retriever.retrieve_evidence_with_full_text(claim, num_results=num_results)

    def select_evidence(self, claim: str, contexts: List[dict], top_k: int = 3) -> List[dict]:
        """
        Chọn các đoạn văn bản liên quan nhất từ danh sách contexts.
        Returns: List các dict chứa text và source của các đoạn đã chọn.
        """
        if not self.selector_method:
            raise ValueError("selector_method is required for EvidenceSelector")
        selector = get_selector(method=self.selector_method)
        context_pairs = [(ev.get("text", ""), ev.get("source", "")) for ev in contexts]
        selected_pairs = selector.select(claim=claim, contexts=context_pairs, top_k=top_k,rerank_model=self.rerank_model)
        return [{
            "text": '.'.join(text.split('.')[:2]).strip() + '.',
            "source": source
        } for text, source in selected_pairs]
    
    def optimize_query(self, claim: str) -> str:
        """
        Tối ưu hóa truy vấn để phù hợp với Serper API.
        Returns: Truy vấn đã được tối ưu hóa.
        """
        if not self.llm_api_params:
            raise ValueError("llm_api_params is required for query optimization")
        provider = self.llm_api_params.get("provider")
        model_name = self.llm_api_params.get("model_name")
        api_key = self.llm_api_params.get("api_key")
        # Tối ưu: chỉ khởi tạo retriever 1 lần nếu có thể
        if not hasattr(self, '_retriever'):
            self._retriever = EvidenceRetriever(search_api_key=self.search_api_key)
        return self._retriever.optimize_query(query=claim, provider=provider, model_name=model_name, llm_api_key=api_key)

    def predict_veracity(self, claim: str, evidence: list) -> str:
        """
        Dự đoán độ xác thực của claim dựa trên evidence.
        Returns: Nhãn độ xác thực (supported, refuted, undetermined).
        """
        if not self.veracity_predictor:
            raise ValueError("model_path is required for VeracityPredictor")
        return self.veracity_predictor.predict(claim, evidence)

    def check(self, claim: str, num_evidence: int = 5, top_k: int = 3) -> dict:
        """
        Thực hiện kiểm tra fact-check cho một claim.
        Returns: dict chứa claim, results (list các dict: source, evidence, label), accuracy_percent
        """
        import time
        import logging
        timings = {}
        logger = logging.getLogger(__name__)
        t0 = time.time()
        query=None
        # 1. Optimize query (nếu có)
        if self.llm_api_params:
            if len(claim.split())>5:
                query = self.optimize_query(claim)
            else:
                query = claim
        else:
            query = claim
        #Preprocess query
        query = query.strip().replace("\n", " ").replace("  ", " ")
        #Remove "" ** 
        query = query.replace('"', '').replace('**', '').replace("'", "")
        #Remove *
        query = query.replace('*', '').replace('?', '').replace('!', '').replace('.', '')
        t1 = time.time()
        timings['optimize_query'] = t1 - t0
        logger.info(f"Timing - optimize_query: {timings['optimize_query']:.4f}s")

        # 2. Retrieve evidence
        evidence_list = self.retrieve_evidence(query, num_results=num_evidence)
        t2 = time.time()
        timings['retrieve_evidence'] = t2 - t1
        logger.info(f"Timing - retrieve_evidence: {timings['retrieve_evidence']:.4f}s")

        # 3. Select evidence
        evidence_select = self.select_evidence(claim=query, contexts=evidence_list, top_k=top_k) if self.selector_method else evidence_list
        t3 = time.time()
        timings['select_evidence'] = t3 - t2
        logger.info(f"Timing - select_evidence: {timings['select_evidence']:.4f}s")

        # 4. Predict veracity (tính tổng thời gian predict cho tất cả evidence)
        predict_time = 0
        evidences = []
        supported_or_refuted = 0
        supported = 0
        for ev in evidence_select:
            text = ev.get("text", "")
            src = ev.get("source", "")
            if '...' in text:
                continue
            t_pred_start = time.time()
            label = self.predict_veracity(claim, text)
            t_pred_end = time.time()
            predict_time += (t_pred_end - t_pred_start)
            if label.lower() == "neutral":
                label = "Refuted"
            evidences.append({"source": src, "evidence": text, "label": label})
            if label.lower() in ["supported", "refuted"]:
                supported_or_refuted += 1
                if label.lower() == "supported":
                    supported = supported + 1
        timings['predict_veracity_total'] = predict_time
        logger.info(f"Timing - predict_veracity_total: {timings['predict_veracity_total']:.4f}s")
        accuracy_percent = (supported / supported_or_refuted) * 100 if evidences and evidences[0]["source"] is not None else 0.0
        timings['total'] = time.time() - t0
        logger.info(f"Timing - total: {timings['total']:.4f}s")
        return {
            "claim": claim,
            "evidences": evidences,
            "accuracy_percent": round(accuracy_percent,2),
        }
    
if __name__ == "__main__":
    import logging
    import time
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("Starting FactCheck")    
    search_api_key = "297e5175d5055b5816ceb37fe503851598633097"
    model_path = "C://Users//PC//Downloads//app-20250612T075040Z-1-001//app//models//weights//model_pho_bert_base.pth"
    llm_api_key ={
        "provider": "GEMINI",
        "model_name": "gemini-2.0-flash",
        "api_key": "AIzaSyCe78RhtA-88OgTPRXDCBCR4gP3XwX6w-Y"
    }
    fact_checker = FactCheck(
        search_api_key=search_api_key,
        model_path=model_path,
        llm_api_params=llm_api_key,
        selector_method='bm25'  # Ví dụ: sử dụng phương pháp BM25 để chọn bằng chứng
    )
    
    claim = "Nhà thờ Đức Bà Sài Gòn đang trong quá trình trùng tu từ năm 2017 đến nay."
    start_time = time.time()
    result = fact_checker.check(claim, num_evidence=3, top_k=5)
    end_time = time.time()
    
    logger.info(f"Fact-check completed in {end_time - start_time:.2f} seconds")
    #Print accuracy percent
    logger.info(f"Accuracy: {result['accuracy_percent']:.2f}%")
    # Xuất kết quả ra file JSON
    with open("factcheck_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\nFull result saved to factcheck_result.json")