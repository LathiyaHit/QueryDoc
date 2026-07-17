document.addEventListener('DOMContentLoaded', async () => {
  const chatWindow = document.getElementById('chatWindow');
  const chatEmpty = document.getElementById('chatEmpty');
  const composer = document.getElementById('composer');
  const textInput = document.getElementById('textInput');
  const sendButton = document.getElementById('sendButton');
  const micButton = document.getElementById('micButton');
  const uploadButton = document.getElementById('uploadButton');
  const fileInput = document.getElementById('fileInput');
  const statusText = document.getElementById('statusText');
  const connectionPill = document.getElementById('connectionPill');
  const recordingIndicator = document.getElementById('recordingIndicator');
  const docBadge = document.getElementById('docBadge');
  const docBadgeIcon = document.getElementById('docBadgeIcon');
  const docBadgeText = document.getElementById('docBadgeText');

  const userId = window.localStorage.getItem('voiceAssistantUserId') || createUserId();
  window.localStorage.setItem('voiceAssistantUserId', userId);

  let apiUrl = '';
  let wsUrl = '';
  let socket = null;
  let mediaStream = null;
  let audioContext = null;
  let sourceNode = null;
  let processorNode = null;
  let isListening = false;
  let currentAssistantBubble = null;
  let hasUploadedDoc = false;

  try {
    const response = await fetch('/config');
    const data = await response.json();
    apiUrl = data.apiUrl;
    wsUrl = `${data.voiceWsBaseUrl}/${encodeURIComponent(userId)}`;
  } catch (error) {
    setStatus('Offline', false);
    addSystemMessage('Could not load backend configuration.');
    micButton.disabled = true;
    sendButton.disabled = true;
  }

  // ── Text input ──────────────────────────────────────────
  composer.addEventListener('submit', async (event) => {
    event.preventDefault();
    const text = textInput.value.trim();
    if (!text) return;

    addMessage('user', text);
    currentAssistantBubble = addMessage('assistant', '', true);
    textInput.value = '';

    try {
      await connectSocket();
      socket.send(JSON.stringify({ type: 'text_input', text }));
      setStatus('Thinking', true);
    } catch (error) {
      addSystemMessage('Could not reach the assistant. Please try again.');
      setStatus('Error', false);
    }
  });

  // ── Voice input ─────────────────────────────────────────
  micButton.addEventListener('click', async () => {
    if (isListening) {
      await stopListening();
      return;
    }
    await startListening();
  });

  async function startListening() {
    if (!wsUrl) {
      addSystemMessage('Backend configuration is unavailable.');
      return;
    }

    try {
      await connectSocket();
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true },
      });

      audioContext = new AudioContext();
      sourceNode = audioContext.createMediaStreamSource(mediaStream);
      processorNode = audioContext.createScriptProcessor(4096, 1, 1);

      processorNode.onaudioprocess = (event) => {
        if (!isListening || socket?.readyState !== WebSocket.OPEN) return;
        const input = event.inputBuffer.getChannelData(0);
        socket.send(floatTo16BitPcm(downsampleBuffer(input, audioContext.sampleRate, 16000)));
      };

      sourceNode.connect(processorNode);
      processorNode.connect(audioContext.destination);

      setListeningState(true);
      setStatus('Listening', true);
    } catch (error) {
      cleanupAudio();
      setListeningState(false);
      setStatus('Error', false);
      addSystemMessage(`Microphone error: ${error.message}`);
    }
  }

  async function stopListening() {
    setListeningState(false);
    cleanupAudio();
    setStatus('Thinking', true);
    sendTrailingSilence();
  }

  // ── PDF upload ──────────────────────────────────────────
  uploadButton.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', async () => {
    const file = fileInput.files[0];
    if (!file) return;

    addSystemMessage(`Uploading "${file.name}"…`);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${apiUrl}/api/v1/documents/upload/${encodeURIComponent(userId)}`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();

      if (!response.ok) {
        addSystemMessage(data.detail || 'Upload failed.');
        return;
      }

      hasUploadedDoc = true;
      setDocBadge(file.name, true);
      addSystemMessage(data.message || `"${file.name}" is now active.`);
    } catch (error) {
      addSystemMessage('Upload failed — could not reach the backend.');
    } finally {
      fileInput.value = '';
    }
  });

  docBadge.addEventListener('click', async () => {
    if (!hasUploadedDoc) return;
    try {
      await fetch(`${apiUrl}/api/v1/documents/upload/${encodeURIComponent(userId)}`, { method: 'DELETE' });
      hasUploadedDoc = false;
      setDocBadge('Default document', false);
      addSystemMessage('Uploaded document cleared. Back to the default document.');
    } catch (error) {
      addSystemMessage('Could not clear the uploaded document.');
    }
  });

  function setDocBadge(label, isUpload) {
    docBadgeIcon.textContent = isUpload ? '📌' : '📄';
    docBadgeText.textContent = label;
    docBadge.classList.toggle('is-active', isUpload);
    docBadge.title = isUpload ? 'Click to clear and use the default document' : 'No document uploaded — click Upload to add one';
  }

  // ── WebSocket ───────────────────────────────────────────
  function connectSocket() {
    if (socket && socket.readyState === WebSocket.OPEN) {
      return Promise.resolve();
    }
    return new Promise((resolve, reject) => {
      socket = new WebSocket(wsUrl);
      socket.onopen = () => resolve();
      socket.onerror = () => reject(new Error('Could not connect to backend.'));
      socket.onmessage = handleSocketMessage;
      socket.onclose = () => {
        if (isListening) {
          cleanupAudio();
          setListeningState(false);
        }
        setStatus('Disconnected', false);
      };
    });
  }

  function handleSocketMessage(event) {
    const message = JSON.parse(event.data);

    if (message.type === 'status') {
      setStatus('Ready', true);
      return;
    }

    if (message.type === 'transcript') {
      if (isListening) {
        addMessage('user', message.text || '(no speech detected)');
        stopListening();
      } else if (!currentAssistantBubble) {
        addMessage('user', message.text || '(no speech detected)');
      }
      currentAssistantBubble = addMessage('assistant', '', true);
      setStatus('Answering', true);
      return;
    }

    if (message.type === 'rag_source') {
      if (currentAssistantBubble) {
        tagBubbleSource(currentAssistantBubble, message.text);
      }
      return;
    }

    if (message.type === 'response_delta') {
      if (!currentAssistantBubble) {
        currentAssistantBubble = addMessage('assistant', '', true);
      }
      currentAssistantBubble.classList.remove('is-thinking');
      const dots = currentAssistantBubble.querySelector('.thinking-dots');
      if (dots) dots.remove();
      
      currentAssistantBubble.querySelector('.bubble-text').textContent += message.text || '';
      scrollToBottom();
      return;
    }

    if (message.type === 'response_done') {
      currentAssistantBubble = null;
      setStatus('Ready', true);
      return;
    }

    if (message.type === 'error') {
      setStatus('Error', false);
      addSystemMessage(message.message || 'Something went wrong.');
      currentAssistantBubble = null;
    }
  }

  // ── Chat rendering ──────────────────────────────────────
  function addMessage(role, text, thinking = false) {
    chatEmpty.style.display = 'none';

    const bubble = document.createElement('div');
    bubble.className = `message message-${role}${thinking ? ' is-thinking' : ''}`;

    const textEl = document.createElement('p');
    textEl.className = 'bubble-text';
    textEl.textContent = thinking ? '' : text;
    bubble.appendChild(textEl);

    if (thinking) {
      const dots = document.createElement('span');
      dots.className = 'thinking-dots';
      dots.innerHTML = '<span></span><span></span><span></span>';
      bubble.appendChild(dots);
    }

    chatWindow.appendChild(bubble);
    scrollToBottom();
    return bubble;
  }

  function addSystemMessage(text) {
    chatEmpty.style.display = 'none';
    const bubble = document.createElement('div');
    bubble.className = 'message message-system';
    bubble.textContent = text;
    chatWindow.appendChild(bubble);
    scrollToBottom();
  }

  function tagBubbleSource(bubble, source) {
    if (bubble.querySelector('.source-tag')) return;
    const tag = document.createElement('span');
    tag.className = 'source-tag';
    if (source === 'upload') tag.textContent = '📌 from your uploaded document';
    else if (source === 'default') tag.textContent = '📄 from the default document';
    else tag.textContent = '⚠️ no matching document found';
    bubble.prepend(tag);
  }

  function scrollToBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  // ── State helpers ───────────────────────────────────────
  function setListeningState(nextState) {
    isListening = nextState;
    micButton.classList.toggle('is-listening', nextState);
    recordingIndicator.classList.toggle('is-visible', nextState);
    micButton.setAttribute('aria-label', nextState ? 'Stop listening' : 'Start listening');
  }

  function setStatus(text, isLive) {
    statusText.textContent = text;
    connectionPill.classList.toggle('is-live', isLive);
  }

  function cleanupAudio() {
    if (processorNode) { processorNode.disconnect(); processorNode.onaudioprocess = null; }
    if (sourceNode) sourceNode.disconnect();
    if (audioContext) audioContext.close();
    if (mediaStream) mediaStream.getTracks().forEach((track) => track.stop());
    processorNode = null; sourceNode = null; audioContext = null; mediaStream = null;
  }

  function sendTrailingSilence() {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    const silenceFrame = new Int16Array(16000 / 10);
    for (let i = 0; i < 12; i += 1) {
      window.setTimeout(() => {
        if (socket?.readyState === WebSocket.OPEN) socket.send(silenceFrame.buffer);
      }, i * 80);
    }
  }

  function downsampleBuffer(buffer, inputRate, outputRate) {
    if (outputRate === inputRate) return buffer;
    const ratio = inputRate / outputRate;
    const newLength = Math.round(buffer.length / ratio);
    const result = new Float32Array(newLength);
    let offsetResult = 0, offsetBuffer = 0;
    while (offsetResult < result.length) {
      const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio);
      let accum = 0, count = 0;
      for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i += 1) {
        accum += buffer[i]; count += 1;
      }
      result[offsetResult] = accum / count;
      offsetResult += 1; offsetBuffer = nextOffsetBuffer;
    }
    return result;
  }

  function floatTo16BitPcm(floatBuffer) {
    const pcm = new Int16Array(floatBuffer.length);
    for (let i = 0; i < floatBuffer.length; i += 1) {
      const sample = Math.max(-1, Math.min(1, floatBuffer[i]));
      pcm[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
    }
    return pcm.buffer;
  }

  function createUserId() {
    if (window.crypto?.randomUUID) return window.crypto.randomUUID();
    return `user-${Date.now()}-${Math.random().toString(16).slice(2)}`;
  }
});