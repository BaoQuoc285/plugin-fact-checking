function getSelectedText() {
  return window.getSelection().toString();
}

chrome.runtime.onMessage.addListener((request, _sender, sendResponse) => {
  if (request.type === "CHECK_TEXT") {
    sendResponse({ status: "processing" });

    const claim = request.claim.trim();
    if (claim) {
      // Mockup fact-check data
      const mockResponse = {
        evidences: [
          {
            evidence: "Vietnam is a country located in Southeast Asia.",
            label: "Supported",
            source: "https://vnexpress.net",
          },
          {
            evidence:
              "Some sources claim that Vietnam belongs to another region.",
            label: "Refuted",
            source: "https://tuoitre.vn",
          },
        ],
        accuracy_percent: 75,
      };
      sendResponse({
        data: mockResponse,
      });
    } else {
      // Return no data if claim is empty
      sendResponse({
        data: { evidences: [], accuracy_percent: 0 },
      });
    }
  }
  // Return true to indicate async response if needed (not needed here)
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "scrollToText") {
    const targetText = msg.text.trim();
    const paragraphs = document.querySelectorAll("p");

    for (const p of paragraphs) {
      if (p.textContent.includes(targetText)) {
        // Scroll đến đoạn cần tìm
        p.scrollIntoView({ behavior: "smooth", block: "center" });

        // Highlight đoạn khớp
        const html = p.innerHTML;
        const highlighted = html.replace(
          targetText,
          `<span style="background-color: yellow; font-weight: bold;">${targetText}</span>`
        );
        p.innerHTML = highlighted;

        break;
      }
    }
  }
});
