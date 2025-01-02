const chatContainer = document.getElementById("chat-container");
const messageForm = document.getElementById("message-form");
const userInput = document.getElementById("user-input");
const apiSelector = document.getElementById("api-selector");

// We'll read the API endpoint from an environment variable
const BASE_URL = process.env.API_ENDPOINT;
// This will be replaced at build time by Parcel with the appropriate value
// from the corresponding .env file.

let isLoading = false
let currentThreadId = null;

function createLoadingMessage() {
  const wrapper = document.createElement("div");
  wrapper.classList.add("mb-6", "flex", "items-start", "gap-3");
  wrapper.id = "loading-message";
  
  const avatar = document.createElement("div");
  avatar.classList.add(
    "w-10",
    "h-10",
    "rounded-full",
    "flex-shrink-0",
    "flex",
    "items-center",
    "justify-center",
    "font-bold",
    "text-white",
    "bg-gradient-to-br",
    "from-lime-400",
    "to-green-600"
  );
  avatar.textContent = "🤖";

  const bubble = document.createElement("div");
  bubble.classList.add(
    "max-w-full",
    "p-3",
    "rounded-lg",
    "whitespace-pre-wrap",
    "leading-relaxed",
    "shadow-sm",
    "bg-gray-200",
    "flex",
    "gap-1",
    "items-center"
  );
  
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement("div");
    dot.classList.add(
      "w-2",
      "h-2",
      "rounded-full",
      "bg-gray-500",
      "animate-bounce"
    );

    dot.style.animationDelay = `${i * 0.2}s`;
    bubble.appendChild(dot);
  }

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  return wrapper;
}

function createMessageBubble(content, sender = "user") {
  const wrapper = document.createElement("div");
  wrapper.classList.add("mb-6", "flex", "items-start", "gap-3");

  if (sender === "user") {
    wrapper.classList.add("flex-row-reverse")
  }
  
  const avatar = document.createElement("div");
  avatar.classList.add(
    "w-10",
    "h-10",
    "rounded-full",
    "flex-shrink-0",
    "flex",
    "items-center",
    "justify-center",
    "font-bold",
    "text-white"
  );

  if (sender === "assistant") {
    avatar.classList.add("bg-gradient-to-br", "from-lime-400", "to-green-600");
    avatar.textContent = "🤖";
  } else {
    avatar.classList.add("bg-gradient-to-br", "from-sky-500", "to-blue-600");
    avatar.textContent = "😊";
  }

  const bubble = document.createElement("div");
  bubble.classList.add(
    "max-w-full",
    "md:max-w-2xl",
    "p-3",
    "rounded-lg",
    "whitespace-pre-wrap",
    "leading-relaxed",
    "shadow-sm"
  );

  if (sender === "assistant") {
    bubble.classList.add("bg-gray-200", "text-gray-900");
  } else {
    bubble.classList.add("bg-blue-600", "text-white");
  }

  bubble.textContent = content;

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);
  return wrapper;
}

function scrollToBottom() {
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function getAssistantResponse(userMessage) {
  const mode = apiSelector.value;
  const url =
    mode === "assistant" ? `${BASE_URL}/assistant` : `${BASE_URL}/chat`;
 
  try {
    const requestBody = {
      message: userMessage,
      thread_id: currentThreadId
    };

    const response = await fetch(url, {
      method: "POST", 
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestBody),
    });
 
    if (!response.ok) {
      throw new Error("서버 응답에 문제가 있습니다. 다시 시도해 주세요.");
    }
 
    const data = await response.json();

    if (data.thread_id) {
      currentThreadId = data.thread_id;
    }
    return data.reply;
  } catch (error) {
    throw new Error("죄송합니다. 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.");
  }
 }
 
 messageForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (isLoading) return;
 
  const message = userInput.value.trim();
  if (!message) return;
 
  chatContainer.appendChild(createMessageBubble(message, "user"));
  userInput.value = "";
  scrollToBottom();
 
  isLoading = true;
  const loadingMessage = createLoadingMessage();
  chatContainer.appendChild(loadingMessage);
  scrollToBottom();
 
  try {
    const response = await getAssistantResponse(message);
    loadingMessage.remove();
    chatContainer.appendChild(createMessageBubble(response, "assistant"));
    scrollToBottom();
  } catch (error) {
    loadingMessage.remove();
    chatContainer.appendChild(
      createMessageBubble(
        error.message, // 에러 메시지 표시
        "assistant"
      )
    );
    scrollToBottom();
  } finally {
    isLoading = false;
  }
 });
