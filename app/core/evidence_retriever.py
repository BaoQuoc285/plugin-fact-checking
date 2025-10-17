# TODO: Implement evidence retrieval from corpus or knowledge base
import time
import logging
import sys
import os
from typing import List, Union
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from app.tools.google_search import SerperAPI
from app.tools.llm import get_llm
from app.tools.prompts import PROMPTS

class EvidenceRetriever:
    """
        EvidenceRetriever is a class for retrieving evidence snippets from the Google Serper API or other sources.
    Attributes:
        search_api_key (str): API key for accessing the Serper API.
        search_tool (SerperAPI): Instance of the SerperAPI search tool.
        llm: Language model instance used for query optimization.
    Methods:
        __init__(search_api_key: str, num_results: int = 5):
            Initializes the EvidenceRetriever with the given API key and number of results.
        optimize_query(query: str) -> str:
            Optimizes a search query for use with the Serper API, potentially removing unnecessary words and normalizing the format.
        retrieve_evidence_with_raw_snippets(
            query: str,
            num_results: int = 5,
            return_raw_snippets: bool = True,
            Retrieves evidence in the form of raw snippets from the Serper API.
            Returns a list of dictionaries (if successful) or strings (if an error occurs or no snippets are found).
    """
    def __init__(self, search_api_key: str, num_results: int = 5):
        self.search_api_key = search_api_key
        self.search_tool = SerperAPI(serper_api_key=search_api_key, k=num_results)

    def optimize_query(self, query: str,provider:str, model_name:str, llm_api_key:str) -> str:
        """
        Tối ưu hóa truy vấn để phù hợp với Serper API.
        Args:
            query (str): Truy vấn ban đầu.
        Returns:
            str: Truy vấn đã được tối ưu hóa.
        """
        llm= get_llm(provider=provider, model_name=model_name, api_key=llm_api_key)
        # Ví dụ: loại bỏ các từ không cần thiết, chuẩn hóa định dạng
        optimized_query = query.strip().lower()
        OPTIMIZE_PROMPT_TEMPLATE = PROMPTS["OPTIMIZE_QUERY"]
        OPTIMIZE_PROMPT = OPTIMIZE_PROMPT_TEMPLATE.format(claim=optimized_query)
        optimized_query = llm.generate(OPTIMIZE_PROMPT)
        optimized_query = optimized_query
        print(f"Optimized query: {optimized_query}")
        return optimized_query

    def retrieve_evidence_with_full_text(
        self, query: str, num_results: int = 5) -> List[Union[str, dict]]:
        """
        Truy xuất bằng chứng dạng raw snippet từ SerperAPI.
        Returns: List các dict (nếu có) hoặc string (nếu lỗi hoặc không có snippet).
        """
        # query = self.optimize_query(query)
        logging.info(f"Retrieving evidence for query: {query} with num_results={num_results}")
        if not query:
            logging.warning("Empty query provided, returning empty results.")
            return []
        try:
            results = self.search_tool.run(query, k=num_results)
            return results
        except Exception as e:
            logging.error(f"Error retrieving evidence: {e}")
            return []
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    search_api_key = "297e5175d5055b5816ceb37fe503851598633097"
    retriever = EvidenceRetriever(search_api_key=search_api_key, num_results=5)
    
    # Test with a sample query
    query = "jack bỏ con"
    start_time = time.time()
    # Optimize the query if needed
    optimized_query = retriever.optimize_query(query, provider="GEMINI", model_name="gemini-2.0-flash", llm_api_key="AIzaSyCe78RhtA-88OgTPRXDCBCR4gP3XwX6w-Y")
    evidence = retriever.retrieve_evidence_with_full_text(query, num_results=1)
    end_time = time.time()
    logging.info(f"Retrieved evidence: {evidence}")
    logging.info(f"Time taken: {end_time - start_time:.2f} seconds")
    # print(evidence)
