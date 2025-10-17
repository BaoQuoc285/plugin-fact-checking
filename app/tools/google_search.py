import random
import time
import bs4
import requests
import warnings
import re
from typing import Any, Optional, Literal
from urllib.parse import urlparse
from bs4 import MarkupResemblesLocatorWarning
from readability import Document
import trafilatura
from typing import List

_SERPER_URL = 'https://google.serper.dev'
NO_RESULT_MSG = 'No good Google Search result was found'

def extract_sentences_dot(text: str, min_sentences: int = 2) -> str:
    # Tách câu bằng dấu chấm hoặc dấu kết câu
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if len(s.strip()) > 10]
    selected_sentences = []
    for s in sentences:
        selected_sentences.append(s)
        if len(selected_sentences) >= min_sentences and not s.endswith("..."):
            break
    return ' '.join(selected_sentences)


class SerperAPI:
    """Class for querying the Google Serper API."""

    def __init__(
        self,
        serper_api_key: str,
        gl: str = 'vn',
        hl: str = 'vi',
        k: int = 1,
        tbs: Optional[str] = None,
        search_type: Literal['news', 'search', 'places', 'images'] = 'search',
    ):
        self.serper_api_key = serper_api_key
        self.gl = gl
        self.hl = hl
        self.k = k
        self.tbs = tbs
        self.search_type = search_type
        self.result_key_for_type = {
            'news': 'news',
            'places': 'places',
            'images': 'images',
            'search': 'organic',
        }
        self.trusted_domains = [
            "vnexpress.net", "tuoitre.vn", "thanhnien.vn", "vietnamnet.vn",
            "zingnews.vn", "nld.com.vn", "laodong.vn", "tienphong.vn",
            "dantri.com.vn", "cand.com.vn", "baochinhphu.vn", "baomoi.com",
            "suckhoedoisong.vn", "plo.vn", "vtv.vn", "vov.vn"
        ]
        self.not_trusted_domains = [
            "facebook.com", "youtube.com", "tiktok.com", "twitter.com",
            "instagram.com", "reddit.com"
        ]
    def is_trusted_domain(self, url: str) -> bool:
        domain = urlparse(url).netloc.replace("https.", "")
        if any(not_domain in domain for not_domain in self.not_trusted_domains):
            return False
        else:
            return True
        # return domain in self.trusted_domains

    def run(self, query: str, **kwargs: Any) -> str | list[str]:
        assert self.serper_api_key, 'Missing serper_api_key.'
        # Allow override of k (number of results) via kwargs
        k = kwargs.get('k', self.k)
        results = self._google_serper_api_results(
            query,
            gl=self.gl,
            hl=self.hl,
            num=k,
            tbs=self.tbs,
            search_type=self.search_type,
            **kwargs,
        )
        snippets = self._parse_snippets(results, k=k)
        return snippets

    def _google_serper_api_results(
        self,
        search_term: str,
        search_type: str = 'search',
        max_retries: int = 20,
        **kwargs: Any,
    ) -> dict[Any, Any]:
        headers = {
            'X-API-KEY': self.serper_api_key or '',
            'Content-Type': 'application/json',
        }
        # Ensure 'num' is sent as a top-level parameter for Serper API
        params = {
            'q': search_term,
            'num': kwargs.get('num', self.k),  # Always send num
            **{key: value for key, value in kwargs.items() if value is not None and key != 'num'},
        }
        response, num_fails, sleep_time = None, 0, 0

        while not response and num_fails < max_retries:
            try:
                response = requests.post(f'{_SERPER_URL}/{search_type}', headers=headers, params=params)
            except Exception:
                response = None
                num_fails += 1
                sleep_time = random.uniform(1, 10) if not sleep_time else min(sleep_time * 2, 600)
                time.sleep(sleep_time)

        if not response:
            raise ValueError('Failed to get result from Google Serper API')

        response.raise_for_status()
        return response.json()

    def bs4_parse_text(self, url: str, snippet: str) -> str:
        """
        Tries to extract the full text from a URL using trafilatura, then readability, then falls back to the snippet.
        Returns a clean string of the best available evidence text.
        """
        if ".pdf" in url:
            return snippet
        # Try trafilatura first
        text = self.extract_text_from_url(url)
        if text:
            return text
        # Fallback: requests + readability
        try:
            response = requests.get(url, timeout=5, verify=False)
            warnings.warn(f"[WARNING] Đang bỏ qua xác thực SSL cho {url}")
            if response.status_code != 200:
                print(f"[DEBUG] {url} trả về status code {response.status_code}, dùng snippet")
                return snippet
            doc = Document(response.text)
            content_html = doc.summary()
            content_text = bs4.BeautifulSoup(content_html, "html.parser").get_text()
            return content_text.strip() if content_text.strip() else snippet
        except Exception as e:
            print(f"Error while parsing {url}: {e}")
            return snippet if snippet.strip() else "[Không tìm thấy nội dung bằng chứng]"

    def _parse_snippets(self, results: dict[Any, Any], k: int = None) -> list[dict[str, str]]:
        """
        Parse search results and extract evidence text and source link for each result.
        Always returns at least one item (with NO_RESULT_MSG if nothing found).
        """
        snippets = []
        result_key = self.result_key_for_type.get(self.search_type, 'organic')
        k = k if k is not None else self.k
        for result in results.get(result_key, [])[:k]:
            link = result.get('link', '')
            snippet = result.get('snippet', '')
            if len(snippet) < 15:
                print(f"[DEBUG] Bỏ qua kết quả không có snippet đủ dài: {snippet}")
                continue
            # Bỏ qua các nguồn không uy tín (facebook, youtube, ...)
            if not self.is_trusted_domain(link):
                continue
            if link.startswith("http") and snippet:
                full_text = self.bs4_parse_text(url=link, snippet=snippet)
                snippets.append({"text": full_text, "source": link})
        if not snippets:
            snippets.append({"text": NO_RESULT_MSG, "source": "None"})
        return snippets

    def _parse_results(self, results: dict[Any, Any]) -> str:
        """
        Returns a single string concatenating all evidence texts from the parsed snippets.
        """
        return ' '.join(s["text"] for s in self._parse_snippets(results))

    def extract_text_from_url(self, url: str) -> str:
        """
        Extracts the main text content from a URL using trafilatura. Returns empty string if not available.
        """
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return ''
        text = trafilatura.extract(downloaded, output_format="txt", include_comments=False)
        return text or ''

if __name__ == "__main__":
    serper_api_key = "297e5175d5055b5816ceb37fe503851598633097"
    serper = SerperAPI(serper_api_key)
    query = "Jack có con và trách nhiệm không?"
    # Lấy 5 evidence thay vì mặc định 1
    results = serper.run(query, return_raw_snippets=True, k=5)
    for result in results:
        print(f"Source: {result['source']}\nText: {result['text']}\n")