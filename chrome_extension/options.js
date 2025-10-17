document.addEventListener("DOMContentLoaded", () => {
  // Load API key if saved
  chrome.storage.sync.get(["geminiApiKey"], (result) => {
    const input = document.getElementById("api-key");
    if (result.geminiApiKey && input) {
      input.value = result.geminiApiKey;
    }
  });

  // Handle save button click
  document.getElementById("save-button")?.addEventListener("click", () => {
    const apiKey = document.getElementById("api-key").value.trim();
    const successMsg = document.getElementById("success-message");

    if (!apiKey) {
      alert("Please enter an API key.");
      return;
    }

    chrome.storage.sync.set({ geminiApiKey: apiKey }, () => {
      if (successMsg) {
        successMsg.style.display = "block";
        setTimeout(() => {
          window.close();
          if (chrome.tabs && chrome.tabs.getCurrent) {
            chrome.tabs.getCurrent((tab) => {
              if (tab) chrome.tabs.remove(tab.id);
            });
          }
        }, 1000);
      }
    });
  });
});
