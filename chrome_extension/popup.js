document.addEventListener("DOMContentLoaded", () => {
  const resultBox = document.getElementById("resultDisplay");

  chrome.storage.local.get(["lastFactCheckResult"], (res) => {
    const result = res.lastFactCheckResult;
    if (result) {
      if (result.evidences && result.evidences.length > 0) {
        renderEvidenceTabs(result.evidences);
        document.getElementById("btnSupport").onclick = () => {
          showEvidence(result.evidences, "Supported", result.claim);
        };
        document.getElementById("btnRefute").onclick = () => {
          showEvidence(result.evidences, "Refuted", result.claim);
        };
        if (result.accuracy_percent > 50) {
          resultBox.textContent = `✅ Câu claim này có vẻ đúng! với độ tin cậy ${result.accuracy_percent}%`;
        } else if (result.accuracy_percent < 50) {
          resultBox.textContent = `❌ Câu claim này có vẻ sai! với độ tin cậy ${result.accuracy_percent}%`;
        } else {
          resultBox.textContent = "Có thể đúng hoặc sai, không có dữ liệu kiểm chứng rõ ràng.";
        }
      } else {
        resultBox.textContent = "⚠️ Không có dữ liệu kiểm chứng.";
      }
    }
  });

  document.getElementById("checkClaimInput").addEventListener("click", async () => {
    const model = document.getElementById("aiModel").value;
    const claim = document.getElementById("claimInput").value.trim();

    if (!claim) {
      resultBox.textContent = "⚠️ Vui lòng nhập thông tin cần kiểm chứng.";
      return;
    }

    resultBox.textContent = `🔍 Đang kiểm chứng thông tin bằng mô hình ${model}...`;

    const result = await getFactCheckResult(claim).catch((error) => {
      resultBox.textContent = `❌ Đã xảy ra lỗi: ${error.message}`;
      return null;
    });

    if (result) {
      chrome.storage.local.set({ lastFactCheckResult: result });
      if (result.evidences && result.evidences.length > 0) {
        renderEvidenceTabs(result.evidences, result.claim);
        document.getElementById("btnSupport").onclick = () => {
          showEvidence(result.evidences, "Supported", result.claim);
        };
        document.getElementById("btnRefute").onclick = () => {
          showEvidence(result.evidences, "Refuted", result.claim);
        };
        if (result.accuracy_percent > 50) {
          resultBox.textContent = `✅ Câu claim này có vẻ đúng! với độ tin cậy ${result.accuracy_percent}%`;
        } else if (result.accuracy_percent < 50) {
          resultBox.textContent = `❌ Câu claim này có vẻ sai! với độ tin cậy ${result.accuracy_percent}%`;
        } else {
          resultBox.textContent = "Có thể đúng hoặc sai, không có dữ liệu kiểm chứng rõ ràng.";
        }
      } else {
        resultBox.textContent = "⚠️ Không có dữ liệu kiểm chứng.";
      }
    } else {
      resultBox.textContent = "⚠️ Không có dữ liệu kiểm chứng.";
    }
  });
});

function renderEvidenceTabs(evidences, claim) {
  const supportCount = evidences.filter((e) => e.label === "Supported").length;
  const refuteCount = evidences.filter((e) => e.label === "Refuted").length;

  document.getElementById("countSupport").textContent = supportCount;
  document.getElementById("countRefute").textContent = refuteCount;

  document.getElementById("evidenceNav").style.display = "flex";

  showEvidence(evidences, "Supported", claim);
}

function showEvidence(evidences, label, claim) {
  const list = document.getElementById("evidenceList");
  list.innerHTML = "";

  const filtered = evidences.filter((e) => e.label === label);

  filtered.forEach((evi, i) => {
    list.innerHTML += `
      <div class="evidence-item">
        <div>
          <em>Nguồn:</em>
          <a href="#" class="open-source-link" data-source="${evi.source}" data-text="${evi.evidence}">
            ${new URL(evi.source).hostname}
          </a><br>
          <em>Thông tin liên quan:</em>
          <p>${evi.evidence}</p>
          ${
            label === "Refuted"
              ? `<button class="suggest-btn" data-index="${i}" data-original="${evi.evidence}">✏️ Gợi ý chỉnh sửa</button>
                 <div id="suggest-box-${i}" class="suggest-box" style="display:none; position:relative; padding: 8px 12px 8px 12px;">
                   <div id="suggest-text-${i}" class="readonly-box">⏳ Đang xử lý...</div>
                 </div>`
              : ""
          }
        </div>
      </div>
      <hr>`;
  });

  list.style.display = "block";

  document.querySelectorAll(".open-source-link").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const url = link.dataset.source;
      const text = link.dataset.text;

      chrome.tabs.update({ url: url }, () => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          const updatedTab = tabs[0];
          const tabId = updatedTab.id;

          setTimeout(() => {
            chrome.scripting.executeScript(
              {
                target: { tabId: tabId },
                files: ["content.js"],
              },
              () => {
                chrome.tabs.sendMessage(tabId, {
                  action: "scrollToText",
                  text: text,
                });
              }
            );
          }, 1000);
        });
      });
    });
  });

  document.querySelectorAll(".suggest-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const idx = btn.dataset.index;
      const box = document.getElementById(`suggest-box-${idx}`);
      const suggestText = document.getElementById(`suggest-text-${idx}`);
      const evidenceText = btn.dataset.original;

      box.style.display = box.style.display === "none" ? "block" : "none";

      try {
        const apiKey = "AIzaSyDkNjMJpzL_gh-q1nT33GtL1DXbe6keJpc"; // 🔒 Thay bằng key thật
        suggestText.innerText = "⏳ Đang tạo gợi ý...";
        const suggestion = await getGeminiSuggest(claim, evidenceText, apiKey);
        suggestText.innerText = suggestion;
      } catch (err) {
        suggestText.innerText = "⚠️ Không thể tạo gợi ý.";
      }
    });
  });
}

// Hàm gọi Gemini để gợi ý viết lại claim dựa trên evidence
async function getGeminiSuggest(claim, evidence, apiKey) {
  const maxLength = 10000;
  const truncatedClaim = claim.length > maxLength ? claim.substring(0, maxLength) + "..." : claim;
  const truncatedEvidence = evidence.length > maxLength ? evidence.substring(0, maxLength) + "..." : evidence;

  const prompt = `Câu phát biểu sau bị bác bỏ bởi thông tin kiểm chứng. Hãy viết lại câu này một cách chính xác và trung lập hơn, dựa trên bằng chứng được cung cấp.

Phát biểu gốc: "${truncatedClaim}"
Bằng chứng bác bỏ: "${truncatedEvidence}"

Câu viết lại gợi ý (ngắn gọn, trung lập, đúng theo bằng chứng):`;

  try {
    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
          generationConfig: {
            temperature: 0.3,
            topK: 40,
            topP: 0.9,
            maxOutputTokens: 256,
          },
        }),
      }
    );

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error?.message || "API request failed");
    }

    const data = await res.json();
    return data?.candidates?.[0]?.content?.parts?.[0]?.text || "Không có gợi ý viết lại.";
  } catch (error) {
    console.error("Lỗi gọi Gemini API:", error);
    throw new Error("Không thể tạo gợi ý. Vui lòng thử lại sau.");
  }
}

// Gọi API fact-check
async function getFactCheckResult(claim) {
  try {
    const res = await fetch(`http://localhost:8000/api/fact-check`, {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=UTF-8" },
      body: JSON.stringify({ claim }),
    });

    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error?.message || "API request failed");
    }

    const data = await res.json();
    return data || null;
  } catch (error) {
    console.error("Error calling Fact Check API:", error);
    throw new Error("Failed to fact check. Please try again later.");
  }
}
