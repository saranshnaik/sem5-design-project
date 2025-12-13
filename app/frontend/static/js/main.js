let sanitizedText = "";

const filterPopup = document.getElementById("filterPopup");
const sanitizeBtn = document.getElementById("sanitizeBtn");
const compareBtn = document.getElementById("compareBtn");
const tagsDiv = document.getElementById("tags");
const resultsDiv = document.getElementById("results");
const userQuery = document.getElementById("userQuery");

sanitizeBtn && sanitizeBtn.addEventListener("click", sanitize);
compareBtn && compareBtn.addEventListener("click", compare);

// Press Enter to send, Shift+Enter to newline
userQuery.addEventListener("keydown", function (e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    // Decide which action to trigger:
    // - if tags are present and compare button is visible -> compare
    // - otherwise trigger sanitize
    const tagsHaveContent = tagsDiv && tagsDiv.innerText.trim().length > 0;
    const compareVisible = compareBtn && getComputedStyle(compareBtn).display !== "none";

    if (tagsHaveContent && compareVisible) {
      compare();
    } else {
      sanitize();
    }
  }
});

async function sanitize() {
  const query = userQuery.value.trim();
  if (!query) return alert("Enter a query first!");

  sanitizeBtn.disabled = true;
  sanitizeBtn.textContent = "Sending...";

  try {
    const res = await fetch("/sanitize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });
    const data = await res.json();
    sanitizedText = data.sanitized || "";
    const tags = data.tags || {};

    const tagsDiv = document.getElementById("tags");
    tagsDiv.innerHTML = "";
    tagsDiv.style.display = "none";

    // If sensitive tags detected → show popup
    if (Object.keys(tags).length > 0) {
      showWarningAndTags(query, tags);
    } else {
      // No tags → directly send
      addMessage(query, "user");
      await sendMessageToLLM(query);
      userQuery.value = "";
    }
  } catch (err) {
    console.error(err);
    alert("Sanitization failed. Check the server logs.");
  } finally {
    sanitizeBtn.disabled = false;
    sanitizeBtn.textContent = "Send";
  }
}


// ----- Popup and Tag display -----
function showWarningAndTags(query, tags) {
  const tagsDiv = document.getElementById("tags");
  const filterPopup = document.getElementById("filterPopup");

  tagsDiv.innerHTML = "";
  tagsDiv.style.display = "block";

  for (const [tag, values] of Object.entries(tags)) {
    values.forEach((val) => {
      //   console.log(tag, ": tag value:", val);

      const wrapper = document.createElement("div");
      wrapper.classList.add("tag-item");

      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.name = tag;
      checkbox.dataset.tag = tag; // guaranteed tag name for backend
      checkbox.value = val;
      checkbox.checked = true;

      const span = document.createElement("span");
      span.innerHTML = `<strong>${tag}</strong>: ${escapeHtml(val)}`;

      wrapper.appendChild(checkbox);
      wrapper.appendChild(span);
      tagsDiv.appendChild(wrapper);
    });
  }

  filterPopup.style.display = "flex";

  // Hook buttons
  document.getElementById("applyFilter").onclick = async () => {
    filterPopup.style.display = "none";
    await filterTags();
    userQuery.value = "";
  };

  document.getElementById("keepOriginal").onclick = async () => {
    filterPopup.style.display = "none";
    addMessage(query, "user");
    await sendMessageToLLM(query);
    userQuery.value = "";
  };
}


// ----- Chat message display -----
function addMessage(text, sender = "user") {
  const chatContainer = document.getElementById("chatContainer");
  if (!chatContainer) return console.warn("Chat container not found.");

  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${sender}`;
  messageDiv.textContent = text;
  chatContainer.appendChild(messageDiv);

  chatContainer.scrollTop = chatContainer.scrollHeight;
}


// ----- Filter tags -----
async function filterTags() {
  const tagsDiv = document.getElementById("tags");
  const filterPopup = document.getElementById("filterPopup");
  const applyBtn = document.getElementById("applyFilter");

  // collect unchecked tag *names*
  const unchecked = Array.from(tagsDiv.querySelectorAll('input[type="checkbox"]:not(:checked)'))
    .map(cb => cb.dataset.tag || cb.name)
    .filter(Boolean);

  //   console.log("Unchecked tag names:", unchecked);

  if (applyBtn) {
    applyBtn.disabled = true;
    applyBtn.textContent = "Applying...";
  }

  try {
    const res = await fetch("/filter", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sanitized: sanitizedText, remove_tags: unchecked })
    });

    const data = await res.json();
    sanitizedText = data.filtered || sanitizedText;

    addMessage(sanitizedText, "user");
    await sendMessageToLLM(sanitizedText);

    // clean up popup
    filterPopup.style.display = "none";
    tagsDiv.innerHTML = "";
    userQuery.value = "";

  } catch (err) {
    console.error(err);
    alert("Filtering failed. Check server logs.");
  } finally {
    if (applyBtn) {
      applyBtn.disabled = false;
      applyBtn.textContent = "Apply Filter";
    }
  }
}

async function sendMessageToLLM(query) {
  const chatContainer = document.getElementById("chatContainer");
  if (!chatContainer) return;

  // show placeholder first
  const botMsg = document.createElement("div");
  botMsg.className = "message bot";
  botMsg.textContent = "Thinking...";
  chatContainer.appendChild(botMsg);
  chatContainer.scrollTop = chatContainer.scrollHeight;

  try {
    const res = await fetch("/llm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    });

    const data = await res.json();
    const reply = data.response || "(No response from model)";
    botMsg.textContent = reply;
    compare();
  } catch (err) {
    console.error("LLM fetch error:", err);
    botMsg.textContent = "(Error fetching LLM response)";
  }
}

async function compare() {
  const original = userQuery.value.trim();
  if (!original) return alert("Enter a query first!");

  compareBtn.disabled = true;
  compareBtn.textContent = "Generating...";

  try {
    const res = await fetch("/compare", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ original: original, filtered: sanitizedText })
    });
    const data = await res.json();
    // const filteredResponse = data.filtered_response || "[No response]";
    // const resultsDiv = document.getElementById("results");
    // if (resultsDiv) {
    //   resultsDiv.innerHTML = `
    //     <div style="color:#dbeef0">
    //       <strong>Response</strong>
    //     </div>
    //     <div style="margin-top:8px">${escapeHtml(filteredResponse)}</div>`;
    // } else {
    //   console.warn("resultsDiv not found in DOM — skipping UI update.");
    // }
  }
  catch (err) {
    console.error(err);
    alert("Failed to generate response. See server logs.");
  } finally {
    // compareBtn.disabled = false;
    // compareBtn.textContent = "Compare LLM Responses";
  }
}

// small helper to avoid XSS in displayed values
function escapeHtml(unsafe) {
  if (!unsafe) return "";
  return unsafe
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
