from abc import ABC, abstractmethod
from typing import List, Tuple
import numpy as np
import re

# SBERT
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.preprocessing import MinMaxScaler

# BM25
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, util


def simple_sentence_split(text: str) -> List[str]:
    """ Tách đoạn theo câu"""
    return [s.split('.')[0].strip() for s in text.split('.') if s.strip()]
def simple_paragraph_split(text: str) -> List[str]:
    """Tách đoạn văn bản theo dấu xuống dòng hoặc ký tự phân tách đoạn như |."""
    # Tách theo | hoặc xuống dòng liên tiếp
    return [s.strip() for s in re.split(r'\|+|\r?\n+', text) if s.strip()]


class EvidenceSelector(ABC):
    @abstractmethod
    def select(self, claim: str, contexts: List[Tuple[str, str]], top_k: int = 5) -> List[Tuple[str, str]]:
        """
        contexts: List of (text, source) tuples
        Returns: List of (selected_sentence, source)
        """
        pass


class BM25EvidenceSelector(EvidenceSelector):
    def select(self, claim: str, contexts: List[Tuple[str, str]], top_k: int = 1,rerank_model=None) -> List[Tuple[str, str]]:
        result = []
        for context in contexts:
            paragraph_source_pairs = []
            text, source = context
            paragraphs = simple_paragraph_split(text)
            for paragraph in paragraphs:
                paragraph_source_pairs.append((paragraph, source))
            if not paragraph_source_pairs:
                continue
            tokenized_corpus = [p[0].split() for p in paragraph_source_pairs]
            bm25 = BM25Okapi(tokenized_corpus)
            scores = bm25.get_scores(claim.split())
            ranked_indices = np.argsort(scores)[::-1]
            selected = [i for i in ranked_indices if scores[i] > 0]
            if selected:
                if rerank_model is not None:
                # Chọn top-k để rerank (giảm chi phí, ví dụ top 5)
                    top_selected = selected[:top_k]
                    candidate_paragraphs = [paragraph_source_pairs[i][0] for i in top_selected]
                    candidate_sources = [paragraph_source_pairs[i][1] for i in top_selected]

                    # Embed claim + candidate paragraphs
                    claim_embed = rerank_model.encode(claim, convert_to_tensor=True)
                    para_embeds = rerank_model.encode(candidate_paragraphs, convert_to_tensor=True)

                    # Tính cosine similarity
                    similarities = util.cos_sim(claim_embed, para_embeds)[0]  # 1D vector
                    best_idx = similarities.argmax().item()

                    # Lấy đoạn tốt nhất
                    best_paragraph = candidate_paragraphs[best_idx]
                    best_source = candidate_sources[best_idx]
                    result.append((best_paragraph, best_source))
                else:
                    # Nếu không có mô hình rerank, chỉ lấy top-k đoạn văn bản
                    for i in selected[:top_k]:
                        result.append(paragraph_source_pairs[i])
                        break
        return result

class SBERTEvidenceSelector(EvidenceSelector):
    def __init__(self, model_name='sentence-transformers/paraphrase-xlm-r-multilingual-v1'):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)

    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def select(self, claim: str, contexts: List[Tuple[str, str]], top_k: int = 5) -> List[Tuple[str, str]]:
        result = []
        for context in contexts:
            paragraph_source_pairs = []
            text, source = context
            paragraphs = simple_paragraph_split(text)
            for paragraph in paragraphs:
                paragraph_source_pairs.append((paragraph, source))
            if not paragraph_source_pairs:
                continue
            all_paragraphs = [claim] + [p for p, _ in paragraph_source_pairs]
            encoded_input = self.tokenizer(all_paragraphs, padding=True, truncation=True, return_tensors='pt').to(self.device)
            with torch.no_grad():
                model_output = self.model(**encoded_input)
            embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])
            claim_emb = embeddings[0].unsqueeze(0)
            context_embs = embeddings[1:]
            scores = torch.nn.functional.cosine_similarity(claim_emb, context_embs).cpu().numpy()
            top_indices = np.argsort(scores)[::-1][:top_k]
            for i in top_indices[:top_k]:
                result.append(paragraph_source_pairs[i])
        return result

class HybridEvidenceSelector(EvidenceSelector):
    def __init__(self, model_name='sentence-transformers/paraphrase-xlm-r-multilingual-v1'):
        self.sbert = SBERTEvidenceSelector(model_name)

    def select(self, claim: str, contexts: List[Tuple[str, str]], top_k: int = 5) -> List[Tuple[str, str]]:
        result = []
        for context in contexts:
            sentence_source_pairs = []
            text, source = context
            sentences = simple_sentence_split(text)
            for sentence in sentences:
                sentence_source_pairs.append((sentence, source))
            if not sentence_source_pairs:
                continue
            all_sentences = [claim] + [s for s, _ in sentence_source_pairs]
            encoded_input = self.sbert.tokenizer(all_sentences, padding=True, truncation=True, return_tensors='pt').to(self.sbert.device)
            with torch.no_grad():
                model_output = self.sbert.model(**encoded_input)
            embeddings = self.sbert.mean_pooling(model_output, encoded_input['attention_mask'])
            claim_emb = embeddings[0].unsqueeze(0)
            context_embs = embeddings[1:]
            sbert_scores = torch.nn.functional.cosine_similarity(claim_emb, context_embs).cpu().numpy()
            bm25 = BM25Okapi([s.split() for s, _ in sentence_source_pairs])
            bm25_scores = bm25.get_scores(claim.split())
            scaler = MinMaxScaler()
            sbert_scores_norm = scaler.fit_transform(sbert_scores.reshape(-1, 1)).flatten()
            bm25_scores_norm = scaler.fit_transform(np.array(bm25_scores).reshape(-1, 1)).flatten()
            hybrid_scores = 0.5 * sbert_scores_norm + 0.5 * bm25_scores_norm
            top_indices = np.argsort(hybrid_scores)[::-1][:top_k]
            # Đảm bảo chỉ lấy tối đa top_k câu
            for i in top_indices[:top_k]:
                result.append(sentence_source_pairs[i])
            #Lấy thằng độ dài ngắn nhất trong các result

        return result


class LLMEvidenceSelector(EvidenceSelector):
    def __init__(self, llm_api_params: dict):
        """
        Initialize the LLM Evidence Selector with API parameters.
        Args:
            llm_api_params (dict): Parameters for the LLM API, including provider, model_name, and api_key.
        """
        self.llm_api_params = llm_api_params
        # Initialize the LLM client here if needed

    def select(self, claim: str, contexts: List[Tuple[str, str]], top_k: int = 5) -> List[Tuple[str, str]]:
        """
        Select evidence using an LLM based on the claim and contexts.
        Args:
            claim (str): The claim to verify.
            contexts (List[Tuple[str, str]]): List of (text, source) tuples.
            top_k (int): Number of top pieces of evidence to return.
        Returns:
            List[Tuple[str, str]]: Selected evidence as (text, source) tuples.
        """
        # Implement the logic to use the LLM to select evidence
        raise NotImplementedError("LLMEvidenceSelector is not implemented yet.")
        

def get_selector(method: str = "bm25") -> EvidenceSelector:
    """
    Factory function to get the appropriate evidence selector based on the method.
    Args:
        method (str): The selection method to use ("bm25", "sbert", or "hybrid").
    Returns:
        EvidenceSelector: An instance of the selected evidence selector.
    """
    if method == "bm25":
        return BM25EvidenceSelector()
    elif method == "sbert":
        return SBERTEvidenceSelector()
    elif method == "hybrid":
        return HybridEvidenceSelector()
    else:
        raise ValueError(f"Unknown selection method: {method}")

if __name__ == "__main__":
    # Example usage
    claim = "Sơn tùng đạo nhạc"
    text1="""Cụ thể, MV "Chúng ta của hiện tại" của Sơn Tùng M-TP bị gỡ khỏi YouTube vì đã bị 1 tài khoản người Việt báo cáo với kênh YouTube GC từ 3 tuần trước. Theo đó, tài khoản này cho rằng beat bản "Chúng ta của hiện tại" giống với bản beat "Is your mine" của Bruno Mars.\nPhản hồi ý kiến này, kênh YouTube GC đáp (tạm dịch): "Quả thật có sự tương đồng. Bạn có nghĩ đó là việc ăn cắp ý tưởng không?".\nSơn Tùng M-TP dính liên hoàn phốt từ năm ngoái đến năm nay chỉ vì chia tay người yêu cũ Thiều Bảo Trâm và yêu người mới là diễn viên Hải Tú\nĐến tối 22-2, tài khoản YouTube GC đánh bản quyền MV "Chúng ta của hiện tại" (gỡ khỏi Youtube) và cho biết phía Sơn Tùng M-TP thừa nhận đạo nhạc. "Clip đã được rút về rồi. Nhà sản xuất thừa nhận anh ấy (Sơn Tùng M-TP) đã sao chép tác phẩm. Kiếm tiền từ công việc của người khác. Chúng tôi không làm điều đó ở phương Tây. Bạn không bao giờ tìm cách biết câu chuyện phải không. Video đó sẽ sớm trở lại thôi, thư giãn đi" - tài khoản YouTube GC đưa ra bình luận (tạm dịch).\nTrước một số ý kiến thắc mắc liệu kênh YouTube GC có khiếu nại Sơn Tùng M-TP hay không? tài khoản này khẳng định: "Tôi không gửi khiếu nại mà không có lý do. Tôi đã làm việc với nhiều nghệ sĩ Việt Nam trong quá khứ".\nKhông chỉ lập group anti, cư dân mạng còn tố MV mới nhất của Sơn Tùng M-TP với công ty sở hữu bản quyền\nSau những phản hồi từ kênh YouTube - đơn vị đánh bản quyền MV "Chúng ta của hiện tại", có thể thấy giai điệu được cho là Sơn Tùng M-TP đạo nhạc đang đều có sự tương đồng giai điệu với hai ca khúc "R&B All Night" (KnowKnow) và bản beat "Is yoyr mine" theo style Bruno Mars.\nNhư vậy, đoạn beat thuộc quyền sở hữu của đơn vị GC đã được bán cho nhiều bên và Sơn Tùng M-TP đã sử dụng lại đoạn beat được tái sử dụng. GC là một producer chuyên sản xuất beat bán trên các trang nhạc online. Bản beat được cho là giống với "Chúng ta của hiện tại" đã được bán cho đơn vị 88 Rising từ trước đó và có lẽ ekip thực hiện sản phẩm mới của Sơn Tùng đã mua beat qua một đơn vị trung gian mà không tìm tới chính chủ.\nNói một cách khác, Sơn Tùng M-TP đã mua hoặc sử dụng lại đoạn beat từ bên trung gian và không mua beat gốc từ phía GC. Với động thái xóa bỏ đoạn bình luận phía Sơn Tùng M-TP đạo nhái của GC và khẳng định "Chúng ta của hiện tại" của Sơn Tùng M-TP sẽ sớm trở lại, rất có thể, GC đã hiểu lầm phía Sơn Tùng M-TP đạo nhạc. Nhưng phía Sơn Tùng M-TP vẫn chưa có phản hồi chính thức.\nĐiều đó khiến cho MV bị "bay màu" khỏi YouTube\nTuy nhiên, ở trong nước, Sơn Tùng M-TP đang vấp phải màn chỉ trích của cư dân mạng. "Trăm năm Tùng vẫn là Tùng, thấy hay thì đạo là điều hiển nhiên", "Hóa ra vài ngày trước Sơn Tùng M-TP đăng số tài khoản lên là để fan góp tiền trả tiền bản quyền đây", " Một ngày là đạo sĩ, cả đời là đạo sĩ", "Tổ nghề đạo sĩ không độ nữa rồi, giờ tổ bột giặt cũng bỏ luôn rồi", "Đây có phải là lần đầu tiên Sơn Tùng đạo nhạc đâu mà bất ngờ thế", " Chúng ta của hiện tại cái gì cũng có chỉ là không có beat nhạc",…\nChưa biết thực hư thế nào nhưng rõ ràng, anti fan đang thể hiện rõ quyền lực của mình"""

    contexts = [
        (text1, "source1"),
    ]

    selector = get_selector("bm25")  # or "sbert", "hybrid", etc.
    selected_evidence = selector.select(claim, contexts, top_k=5)
    for text, source in selected_evidence:
        print(f"Selected: {text} (Source: {source})")