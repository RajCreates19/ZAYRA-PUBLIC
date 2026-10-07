/* ZAYRA frontend — single coherent script. Talks only to POST /api/chat. */
(() => {
  'use strict';

  /* ---------- DOM ---------- */
  const IDS = ['login','loginForm','loginName','loginPass','loginError','guestBtn','app','menuBtn','profileBtn',
    'profileInitial','profileMenu','profileName','profileRole','logoutBtn','statusText','chat','chatInner',
    'listeningItem','stopListenBtn','speakingItem','stopSpeakBtn','composer','micBtn','input','sendBtn',
    'sidebar','overlay','closeSidebarBtn','newChatBtn','recentList','settingsBtn','settingsModal',
    'closeSettingsBtn','themeSeg','voiceSwitch','voiceState','toneSeg','toast','particles','themeColor'];
  const el = {};
  IDS.forEach(id => { el[id] = document.getElementById(id); });

  /* ---------- State ---------- */
  const DEFAULTS = { theme: 'dark', voice: true, tone: 'natural' };
  const THEME_COLORS = { dark: '#050816', midnight: '#000106', light: '#eef0fc' };
  const TONES = { calm: { rate: 0.9, pitch: 0.95 }, natural: { rate: 1, pitch: 1 }, clear: { rate: 0.95, pitch: 1.08 } };
  const PLACEHOLDERS = ['Enter your text...', 'Ask ZAYRA...'];

  const state = {
    user: null,
    chats: [],
    activeId: null,
    pending: false,
    listening: false,
    speaking: false,
    settings: loadSettings()
  };
  let recognizer = null;
  let speechToken = 0;
  let toastTimer = null;

  const synth = 'speechSynthesis' in window ? window.speechSynthesis : null;
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;

  /* ---------- Helpers ---------- */
  const uid = () => Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  const fmtTime = t => new Date(t).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
  const activeChat = () => state.chats.find(c => c.id === state.activeId) || null;

  function formatReply(text) {
    return esc(text)
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/`([^`\n]+)`/g, '<code>$1</code>')
      .replace(/^\s*[*-]\s+/gm, '• ');
  }

  function toast(msg) {
    el.toast.textContent = msg;
    el.toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.toast.classList.remove('show'), 4200);
  }

  function makeTitle(text) {
    const t = text.replace(/\s+/g, ' ').trim();
    return t.length > 28 ? t.slice(0, 27).trim() + '…' : t;
  }

  /* ---------- Settings ---------- */
  function loadSettings() {
    try { return { ...DEFAULTS, ...JSON.parse(localStorage.getItem('zayra.settings') || '{}') }; }
    catch { return { ...DEFAULTS }; }
  }
  function saveSettings() {
    try { localStorage.setItem('zayra.settings', JSON.stringify(state.settings)); } catch { /* storage unavailable */ }
  }
  function applySettings() {
    const s = state.settings;
    document.documentElement.dataset.theme = s.theme;
    el.themeColor.setAttribute('content', THEME_COLORS[s.theme] || THEME_COLORS.dark);
    el.themeSeg.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.theme === s.theme)));
    el.toneSeg.querySelectorAll('button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.tone === s.tone)));
    el.voiceSwitch.setAttribute('aria-checked', String(s.voice));
    el.voiceState.textContent = s.voice ? 'ON' : 'OFF';
  }

  /* ---------- Chat storage ---------- */
  const chatKey = () => 'zayra.chats.' + (state.user.guest ? 'guest' : state.user.name.toLowerCase());
  function loadChats() {
    try {
      const data = JSON.parse(localStorage.getItem(chatKey()) || '[]');
      return Array.isArray(data) ? data : [];
    } catch { return []; }
  }
  function saveChats() {
    try { localStorage.setItem(chatKey(), JSON.stringify(state.chats)); } catch { /* storage unavailable */ }
  }

  /* ---------- Rendering ---------- */
  function scrollDown() {
    requestAnimationFrame(() => { el.chat.scrollTop = el.chat.scrollHeight; });
  }

  function appendMessage(m, opts = {}) {
    const row = document.createElement('div');
    row.className = 'msg ' + (m.role === 'user' ? 'user' : 'bot') + (opts.error ? ' error' : '');
    if (m.role !== 'user') {
      const icon = document.createElement('div');
      icon.className = 'bot-icon';
      icon.innerHTML = '<svg width="18" height="18"><use href="#mark"/></svg>';
      row.appendChild(icon);
    }
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    const text = document.createElement('div');
    text.className = 'text';
    if (m.role === 'user') text.textContent = m.text; else text.innerHTML = formatReply(m.text);
    bubble.appendChild(text);
    if (m.t) {
      const time = document.createElement('span');
      time.className = 'time';
      time.textContent = fmtTime(m.t);
      bubble.appendChild(time);
    }
    row.appendChild(bubble);
    el.chatInner.appendChild(row);
    scrollDown();
    return row;
  }

  function appendThinking() {
    const row = document.createElement('div');
    row.className = 'msg bot';
    row.innerHTML = '<div class="bot-icon"><svg width="18" height="18"><use href="#mark"/></svg></div>' +
      '<div class="bubble"><div class="dots" aria-label="ZAYRA is thinking"><i></i><i></i><i></i></div></div>';
    el.chatInner.appendChild(row);
    scrollDown();
    return row;
  }

  function renderChat() {
    el.chatInner.innerHTML = '';
    const chat = activeChat();
    if (chat) chat.messages.forEach(m => appendMessage(m));
    el.chat.scrollTop = el.chat.scrollHeight;
  }

  function renderRecents() {
    el.recentList.innerHTML = '';
    if (!state.chats.length) {
      const p = document.createElement('div');
      p.className = 'empty';
      p.textContent = 'No chats yet. Send a message to start one.';
      el.recentList.appendChild(p);
      return;
    }
    [...state.chats].sort((a, b) => b.updated - a.updated).forEach(c => {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'recent-item' + (c.id === state.activeId ? ' active' : '');
      b.textContent = c.title;
      b.dataset.id = c.id;
      el.recentList.appendChild(b);
    });
  }

  function setMode() {
    const chat = activeChat();
    const chatting = !!(chat && chat.messages.length);
    el.app.classList.toggle('home', !chatting);
    el.app.classList.toggle('chatting', chatting);
  }

  function refreshStatus() {
    el.statusText.textContent = state.pending ? 'Thinking…' : state.listening ? 'Listening…' : state.speaking ? 'Speaking…' : 'Online';
    el.listeningItem.hidden = !state.listening;
    el.speakingItem.hidden = !state.speaking;
    el.composer.classList.toggle('listening', state.listening);
    el.micBtn.setAttribute('aria-pressed', String(state.listening));
    el.sendBtn.disabled = state.pending;
  }

  /* ---------- Chats: new / open ---------- */
  function newChat() {
    stopSpeech();
    stopListening();
    state.activeId = null;
    el.chatInner.innerHTML = '';
    el.input.value = '';
    autosize();
    setMode();
    renderRecents();
  }

  function openChat(id) {
    if (!state.chats.some(c => c.id === id)) return;
    stopSpeech();
    stopListening();
    state.activeId = id;
    renderChat();
    setMode();
    renderRecents();
  }

  /* ---------- Backend ---------- */
  async function askBackend(message) {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 90000);
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
        signal: ctrl.signal
      });
      if (!res.ok) throw new Error('http');
      const data = await res.json();
      if (typeof data.reply !== 'string' || !data.reply.trim()) throw new Error('empty');
      return data.reply;
    } finally {
      clearTimeout(timer);
    }
  }

  async function send() {
    if (state.pending) return;
    const text = el.input.value.trim();
    if (!text) return;
    stopSpeech();
    stopListening();

    let chat = activeChat();
    if (!chat) {
      chat = { id: uid(), title: makeTitle(text), updated: Date.now(), messages: [] };
      state.chats.unshift(chat);
      state.activeId = chat.id;
    }
    const userMsg = { role: 'user', text, t: Date.now() };
    chat.messages.push(userMsg);
    chat.updated = Date.now();
    saveChats();

    el.input.value = '';
    autosize();
    setMode();
    renderRecents();
    appendMessage(userMsg);

    state.pending = true;
    refreshStatus();
    const thinking = appendThinking();

    let reply = null;
    let errorText = null;
    try {
      reply = await askBackend(text);
    } catch (err) {
      errorText = (err instanceof TypeError || err.name === 'AbortError')
        ? 'ZAYRA is temporarily unable to connect. Please check that the server is running.'
        : 'ZAYRA ran into a problem while answering. Please try again.';
    }

    state.pending = false;
    thinking.remove();
    const stillOpen = state.activeId === chat.id;

    if (reply !== null) {
      const botMsg = { role: 'bot', text: reply, t: Date.now() };
      chat.messages.push(botMsg);
      chat.updated = Date.now();
      saveChats();
      renderRecents();
      if (stillOpen) {
        appendMessage(botMsg);
        speak(reply);
      }
    } else if (stillOpen) {
      appendMessage({ role: 'bot', text: errorText, t: Date.now() }, { error: true });
    } else {
      toast(errorText);
    }
    refreshStatus();
  }

  /* ---------- Voice output ---------- */
  function pickVoice(kind) {
    if (!synth) return null;
    const voices = synth.getVoices();
    const inLang = (v, p) => v.lang && v.lang.toLowerCase().replace('_', '-').startsWith(p);
    const best = list => list.find(v => v.localService) || list.find(v => /natural|neural|google|online/i.test(v.name)) || list[0] || null;
    if (kind === 'hi') return best(voices.filter(v => inLang(v, 'hi')));
    const indian = best(voices.filter(v => inLang(v, 'en-in')));
    if (indian) return indian;
    const lang = (navigator.language || 'en-US').toLowerCase();
    const base = lang.split('-')[0];
    const matches = voices.filter(v => v.lang && v.lang.toLowerCase().startsWith(base));
    return matches.find(v => /natural|google|online/i.test(v.name)) || matches.find(v => v.lang.toLowerCase() === lang) || matches[0] || null;
  }

  function chunkText(text) {
    const parts = text.match(/[^.!?\n]+[.!?]*\s*/g) || [text];
    const chunks = [];
    let cur = '';
    parts.forEach(p => {
      if ((cur + p).length > 180 && cur) { chunks.push(cur); cur = p; } else { cur += p; }
    });
    if (cur.trim()) chunks.push(cur);
    return chunks;
  }

  function speak(text) {
    if (!synth || !state.settings.voice) return;
    stopSpeech();
    const clean = text.replace(/[*_`#>]/g, '').replace(/\s+/g, ' ').trim();
    if (!clean) return;
    const tone = TONES[state.settings.tone] || TONES.natural;
    const chunks = chunkText(clean);
    const token = ++speechToken;
    let left = chunks.length;
    state.speaking = true;
    refreshStatus();
    chunks.forEach(chunk => {
      const u = new SpeechSynthesisUtterance(chunk);
      u.rate = tone.rate;
      u.pitch = tone.pitch;
      const hindi = /[\u0900-\u097F]/.test(chunk);
      const voice = pickVoice(hindi ? 'hi' : 'en');
      if (voice) { u.voice = voice; u.lang = voice.lang; } else if (hindi) { u.lang = 'hi-IN'; }
      const done = () => {
        if (token !== speechToken) return;
        left -= 1;
        if (left <= 0) { state.speaking = false; refreshStatus(); }
      };
      u.onend = done;
      u.onerror = done;
      synth.speak(u);
    });
  }

  function stopSpeech() {
    speechToken += 1;
    if (synth && (synth.speaking || synth.pending)) synth.cancel();
    if (state.speaking) { state.speaking = false; refreshStatus(); }
  }

  /* ---------- Voice input ---------- */
  function startListening() {
    if (!SpeechRec) {
      toast("Voice input isn't available in this browser. Try Chrome, or type your message.");
      return;
    }
    if (state.listening) { stopListening(); return; }
    stopSpeech();
    const base = el.input.value.trim();
    let finalText = '';
    const rec = new SpeechRec();
    rec.lang = navigator.language || 'en-US';
    rec.interimResults = true;
    rec.continuous = false;
    rec.onstart = () => { state.listening = true; refreshStatus(); };
    rec.onresult = e => {
      let interim = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        const r = e.results[i];
        if (r.isFinal) finalText += r[0].transcript; else interim += r[0].transcript;
      }
      el.input.value = ((base ? base + ' ' : '') + (finalText + interim)).trim();
      autosize();
    };
    rec.onerror = e => {
      const msgs = {
        'not-allowed': 'Microphone access was blocked. Allow it in your browser settings to use voice input.',
        'service-not-allowed': 'Microphone access was blocked. Allow it in your browser settings to use voice input.',
        'no-speech': "I didn't hear anything. Tap the microphone and try again.",
        'audio-capture': 'No microphone was found on this device.',
        'network': 'Voice input needs an internet connection.'
      };
      if (e.error !== 'aborted') toast(msgs[e.error] || 'Voice input stopped unexpectedly. Please try again.');
    };
    rec.onend = () => {
      state.listening = false;
      if (recognizer === rec) recognizer = null;
      refreshStatus();
    };
    recognizer = rec;
    try { rec.start(); } catch { recognizer = null; toast('Voice input could not start. Please try again.'); }
  }

  function stopListening() {
    if (recognizer) { try { recognizer.stop(); } catch { /* already stopped */ } }
  }

  /* ---------- Composer ---------- */
  function autosize() {
    el.input.style.height = 'auto';
    el.input.style.height = Math.min(el.input.scrollHeight, 120) + 'px';
  }

  function startPlaceholderRotation() {
    let i = 0;
    setInterval(() => {
      if (document.hidden) return;
      el.input.classList.add('ph-out');
      setTimeout(() => {
        i = (i + 1) % PLACEHOLDERS.length;
        el.input.placeholder = PLACEHOLDERS[i];
        el.input.classList.remove('ph-out');
      }, 320);
    }, 4000);
  }

  /* ---------- Panels ---------- */
  function openSidebar() {
    el.sidebar.classList.add('open');
    el.overlay.classList.add('show');
    el.sidebar.setAttribute('aria-hidden', 'false');
    closeProfileMenu();
  }
  function closeSidebar() {
    el.sidebar.classList.remove('open');
    el.overlay.classList.remove('show');
    el.sidebar.setAttribute('aria-hidden', 'true');
  }
  function toggleProfileMenu() {
    const open = !el.profileMenu.classList.contains('open');
    el.profileMenu.classList.toggle('open', open);
    el.profileBtn.setAttribute('aria-expanded', String(open));
  }
  function closeProfileMenu() {
    el.profileMenu.classList.remove('open');
    el.profileBtn.setAttribute('aria-expanded', 'false');
  }
  function openSettings() {
    el.settingsModal.classList.add('open');
    el.settingsModal.setAttribute('aria-hidden', 'false');
  }
  function closeSettings() {
    el.settingsModal.classList.remove('open');
    el.settingsModal.setAttribute('aria-hidden', 'true');
  }

  /* ---------- Login / logout ---------- */
  function enterApp(user) {
    state.user = user;
    state.chats = loadChats();
    state.activeId = null;
    state.pending = false;
    el.profileInitial.textContent = (user.name.trim()[0] || 'G').toUpperCase();
    el.profileName.textContent = user.name;
    el.profileRole.textContent = user.guest ? 'Guest' : 'ZAYRA user';
    el.login.hidden = true;
    el.app.hidden = false;
    newChat();
    refreshStatus();
  }

  function logout() {
    stopSpeech();
    stopListening();
    closeProfileMenu();
    closeSidebar();
    closeSettings();
    state.user = null;
    state.chats = [];
    state.activeId = null;
    el.chatInner.innerHTML = '';
    el.input.value = '';
    el.loginPass.value = '';
    el.loginError.hidden = true;
    el.app.hidden = true;
    el.login.hidden = false;
  }

  /* ---------- Background particles ---------- */
  function buildParticles() {
    const frag = document.createDocumentFragment();
    for (let i = 0; i < 22; i++) {
      const s = document.createElement('span');
      const size = 2 + Math.random() * 3;
      s.style.cssText = 'left:' + (Math.random() * 100).toFixed(1) + '%;top:' + (10 + Math.random() * 85).toFixed(1) +
        '%;width:' + size.toFixed(1) + 'px;height:' + size.toFixed(1) + 'px;--d:' + (9 + Math.random() * 10).toFixed(1) +
        's;--dl:' + (-Math.random() * 12).toFixed(1) + 's';
      frag.appendChild(s);
    }
    el.particles.appendChild(frag);
  }

  /* ---------- Events (each bound exactly once) ---------- */
  function bindEvents() {
    el.loginForm.addEventListener('submit', e => {
      e.preventDefault();
      const name = el.loginName.value.trim();
      if (!name || !el.loginPass.value) {
        el.loginError.textContent = 'Enter your name and password, or continue as guest.';
        el.loginError.hidden = false;
        return;
      }
      el.loginError.hidden = true;
      enterApp({ name, guest: false });
      el.loginPass.value = '';
    });
    el.guestBtn.addEventListener('click', () => {
      el.loginError.hidden = true;
      enterApp({ name: 'Guest', guest: true });
    });

    el.menuBtn.addEventListener('click', openSidebar);
    el.closeSidebarBtn.addEventListener('click', closeSidebar);
    el.overlay.addEventListener('click', closeSidebar);
    el.newChatBtn.addEventListener('click', newChat);
    el.recentList.addEventListener('click', e => {
      const item = e.target.closest('.recent-item');
      if (item) openChat(item.dataset.id);
    });
    el.settingsBtn.addEventListener('click', openSettings);

    el.profileBtn.addEventListener('click', e => { e.stopPropagation(); toggleProfileMenu(); });
    el.logoutBtn.addEventListener('click', logout);
    document.addEventListener('click', e => {
      if (el.profileMenu.classList.contains('open') && !el.profileMenu.contains(e.target) && !el.profileBtn.contains(e.target)) closeProfileMenu();
    });

    el.closeSettingsBtn.addEventListener('click', closeSettings);
    el.settingsModal.addEventListener('click', e => { if (e.target === el.settingsModal) closeSettings(); });
    el.themeSeg.addEventListener('click', e => {
      const b = e.target.closest('button[data-theme]');
      if (!b) return;
      state.settings.theme = b.dataset.theme;
      saveSettings();
      applySettings();
    });
    el.toneSeg.addEventListener('click', e => {
      const b = e.target.closest('button[data-tone]');
      if (!b) return;
      state.settings.tone = b.dataset.tone;
      saveSettings();
      applySettings();
    });
    el.voiceSwitch.addEventListener('click', () => {
      state.settings.voice = !state.settings.voice;
      if (!state.settings.voice) stopSpeech();
      saveSettings();
      applySettings();
    });

    el.sendBtn.addEventListener('click', send);
    el.micBtn.addEventListener('click', startListening);
    el.stopListenBtn.addEventListener('click', stopListening);
    el.stopSpeakBtn.addEventListener('click', stopSpeech);
    el.input.addEventListener('input', autosize);
    // Plain Enter inserts a newline (default). Ctrl/Cmd+Enter is the only keyboard send shortcut.
    el.input.addEventListener('keydown', e => {
      if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); send(); }
    });

    document.addEventListener('keydown', e => {
      if (e.key !== 'Escape') return;
      closeSettings();
      closeSidebar();
      closeProfileMenu();
    });
    window.addEventListener('pagehide', stopSpeech);
  }

  /* ---------- Occasional eye blink (overlay only; character image untouched) ---------- */
  function startBlinking() {
    const blink = document.querySelector('#character .blink');
    if (!blink) return;
    const once = () => { blink.classList.add('go'); setTimeout(() => blink.classList.remove('go'), 190); };
    const next = () => setTimeout(() => {
      if (!document.hidden && !el.app.hidden) {
        once();
        if (Math.random() < 0.2) setTimeout(once, 330);
      }
      next();
    }, 2800 + Math.random() * 3800);
    next();
  }

  /* ---------- Init ---------- */
  function init() {
    applySettings();
    buildParticles();
    bindEvents();
    startPlaceholderRotation();
    if (synth) { synth.getVoices(); if (synth.onvoiceschanged !== undefined) synth.onvoiceschanged = () => synth.getVoices(); }
    startBlinking();
    el.login.hidden = false;   // always begin on the login screen
    el.app.hidden = true;
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();
