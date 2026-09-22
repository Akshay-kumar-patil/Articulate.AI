/* =============================================
   Articulate.AI — Web UI Application Logic
   Vanilla JS SPA for Netlify deployment
   Talks to FastAPI backend on Render
   ============================================= */

'use strict';

// ───────────────────────────────────────────────
// CONFIGURATION
// ───────────────────────────────────────────────
const API_URL = 'https://articulate-ai.onrender.com';

// ───────────────────────────────────────────────
// APPLICATION STATE
// ───────────────────────────────────────────────
const state = {
  userId: null,
  username: null,
  resumeInfo: null,
  questions: [],
  currentQ: 0,
  answers: [],
  difficulty: 'medium',
  saved: false,
  mediaRecorder: null,
  audioChunks: [],
  isRecording: false,
  spokenQ: -1,
  processedQ: -1,
};

// ───────────────────────────────────────────────
// INITIALIZATION
// ───────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const savedUserId = localStorage.getItem('articulate_user_id');
  const savedUsername = localStorage.getItem('articulate_username');

  if (savedUserId) {
    // Verify token is still valid
    fetch(`${API_URL}/auth/verify/${savedUserId}`)
      .then(r => {
        if (r.ok) {
          state.userId = savedUserId;
          state.username = savedUsername || 'User';
          showApp();
        } else {
          clearSession();
          showAuth();
        }
      })
      .catch(() => {
        // If backend is sleeping (Render free tier), show app anyway
        state.userId = savedUserId;
        state.username = savedUsername || 'User';
        showApp();
      });
  } else {
    showAuth();
  }
});

// ───────────────────────────────────────────────
// SCREEN MANAGEMENT
// ───────────────────────────────────────────────
function showAuth() {
  document.getElementById('auth-screen').classList.add('active');
  document.getElementById('app-screen').classList.remove('active');
}

function showApp() {
  document.getElementById('auth-screen').classList.remove('active');
  document.getElementById('app-screen').classList.add('active');
  document.getElementById('nav-username-text').textContent = state.username;
  switchPage('interview');
}

function clearSession() {
  localStorage.removeItem('articulate_user_id');
  localStorage.removeItem('articulate_username');
  state.userId = null;
  state.username = null;
}

// ───────────────────────────────────────────────
// AUTH TAB SWITCHER
// ───────────────────────────────────────────────
function switchAuthTab(tab) {
  const loginForm  = document.getElementById('login-form');
  const signupForm = document.getElementById('signup-form');
  const loginBtn   = document.getElementById('tab-login-btn');
  const signupBtn  = document.getElementById('tab-signup-btn');

  if (tab === 'login') {
    loginForm.classList.add('active');
    signupForm.classList.remove('active');
    loginBtn.classList.add('active');
    signupBtn.classList.remove('active');
    loginBtn.setAttribute('aria-selected', 'true');
    signupBtn.setAttribute('aria-selected', 'false');
  } else {
    signupForm.classList.add('active');
    loginForm.classList.remove('active');
    signupBtn.classList.add('active');
    loginBtn.classList.remove('active');
    signupBtn.setAttribute('aria-selected', 'true');
    loginBtn.setAttribute('aria-selected', 'false');
  }
}

// ───────────────────────────────────────────────
// AUTH — LOGIN
// ───────────────────────────────────────────────
async function handleLogin(e) {
  e.preventDefault();
  const email    = document.getElementById('login-email').value.trim();
  const password = document.getElementById('login-password').value;
  const errEl    = document.getElementById('login-error');
  const btn      = document.getElementById('login-btn');

  setLoading(btn, true);
  hideEl(errEl);

  try {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (res.ok) {
      const data = await res.json();
      state.userId   = data.user_id;
      state.username = data.username;
      localStorage.setItem('articulate_user_id', data.user_id);
      localStorage.setItem('articulate_username', data.username);
      showApp();
    } else {
      const err = await res.json();
      showEl(errEl);
      errEl.textContent = err.detail || 'Invalid email or password';
    }
  } catch (error) {
    showEl(errEl);
    errEl.textContent = 'Network error. Please try again.';
  } finally {
    setLoading(btn, false);
  }
}

// ───────────────────────────────────────────────
// AUTH — SIGNUP
// ───────────────────────────────────────────────
async function handleSignup(e) {
  e.preventDefault();
  const username = document.getElementById('signup-username').value.trim();
  const email    = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;
  const errEl    = document.getElementById('signup-error');
  const sucEl    = document.getElementById('signup-success');
  const btn      = document.getElementById('signup-btn');

  setLoading(btn, true);
  hideEl(errEl);
  hideEl(sucEl);

  try {
    const res = await fetch(`${API_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, email, password }),
    });

    if (res.ok) {
      showEl(sucEl);
      sucEl.textContent = 'Account created! Please login.';
      document.getElementById('signup-form').reset();
      setTimeout(() => switchAuthTab('login'), 1500);
    } else {
      const err = await res.json();
      showEl(errEl);
      errEl.textContent = err.detail || 'Signup failed. Try again.';
    }
  } catch (error) {
    showEl(errEl);
    errEl.textContent = 'Network error. Please try again.';
  } finally {
    setLoading(btn, false);
  }
}

// ───────────────────────────────────────────────
// AUTH — LOGOUT
// ───────────────────────────────────────────────
function handleLogout() {
  if (!confirm('Are you sure you want to logout?')) return;
  clearSession();
  resetInterviewState();
  showAuth();
  showToast('Logged out successfully');
}

// ───────────────────────────────────────────────
// AUTH — DELETE ACCOUNT
// ───────────────────────────────────────────────
async function handleDeleteAccount() {
  if (!confirm('Permanently delete your account and ALL interview history? This cannot be undone.')) return;

  try {
    const res = await fetch(`${API_URL}/analytics/delete-user/${state.userId}`, { method: 'DELETE' });
    if (res.ok) {
      clearSession();
      resetInterviewState();
      showAuth();
      showToast('Account deleted permanently');
    } else {
      showToast('Failed to delete account. Try again.');
    }
  } catch {
    showToast('Network error. Try again.');
  }
}

// ───────────────────────────────────────────────
// PAGE NAVIGATION
// ───────────────────────────────────────────────
function switchPage(page) {
  // Update nav tabs
  document.getElementById('nav-interview').classList.toggle('active', page === 'interview');
  document.getElementById('nav-reports').classList.toggle('active', page === 'reports');

  // Show / hide pages
  document.getElementById('page-interview').classList.toggle('active', page === 'interview');
  document.getElementById('page-reports').classList.toggle('active', page === 'reports');

  if (page === 'reports') loadReports();
}

// ───────────────────────────────────────────────
// RESUME — FILE SELECTION
// ───────────────────────────────────────────────
function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) setSelectedFile(file);
}

function handleDrop(e) {
  e.preventDefault();
  document.getElementById('resume-upload-area').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file && file.type === 'application/pdf') {
    setSelectedFile(file);
  } else {
    showToast('Please drop a PDF file');
  }
}

function handleDragOver(e) {
  e.preventDefault();
  document.getElementById('resume-upload-area').classList.add('drag-over');
}

function handleDragLeave() {
  document.getElementById('resume-upload-area').classList.remove('drag-over');
}

function setSelectedFile(file) {
  document.getElementById('file-name').textContent = file.name;
  showEl(document.getElementById('file-selected'));
  hideEl(document.getElementById('resume-upload-area'));
  document.getElementById('process-resume-btn').disabled = false;
  // store file reference on the input
  const inp = document.getElementById('resume-file');
  if (!inp.files.length) {
    const dt = new DataTransfer();
    dt.items.add(file);
    inp.files = dt.files;
  }
}

function clearFile() {
  document.getElementById('resume-file').value = '';
  hideEl(document.getElementById('file-selected'));
  showEl(document.getElementById('resume-upload-area'));
  document.getElementById('process-resume-btn').disabled = true;
  hideStatusMsg('resume-status');
}

// ───────────────────────────────────────────────
// RESUME — PROCESS
// ───────────────────────────────────────────────
async function processResume() {
  const fileInput = document.getElementById('resume-file');
  const file = fileInput.files[0];
  if (!file) { showToast('Please select a PDF file first'); return; }

  const btn = document.getElementById('process-resume-btn');
  setLoading(btn, true);
  hideStatusMsg('resume-status');

  const formData = new FormData();
  formData.append('file', file, file.name);

  try {
    const res = await fetch(`${API_URL}/resume/upload-resume`, {
      method: 'POST',
      body: formData,
    });

    if (res.ok) {
      const data = await res.json();
      state.resumeInfo = data.resume_info;
      showStatusMsg('resume-status', 'success', 'Resume processed! You can now configure your interview.');

      // Unlock settings section
      document.getElementById('section-settings').classList.remove('locked');
      document.getElementById('generate-btn').disabled = false;
      showEl(document.getElementById('resume-done-badge'));
    } else {
      showStatusMsg('resume-status', 'error', 'Failed to process resume. Please try again.');
    }
  } catch {
    showStatusMsg('resume-status', 'error', 'Network error. Check your connection and try again.');
  } finally {
    setLoading(btn, false);
  }
}

// ───────────────────────────────────────────────
// INTERVIEW — GENERATE QUESTIONS
// ───────────────────────────────────────────────
async function generateQuestions() {
  if (!state.resumeInfo) { showToast('Please upload your resume first'); return; }

  const difficulty     = document.getElementById('difficulty-select').value;
  const totalQuestions = parseInt(document.getElementById('num-questions').value);
  const btn            = document.getElementById('generate-btn');

  setLoading(btn, true);
  hideStatusMsg('generate-status');

  try {
    const res = await fetch(`${API_URL}/question/generate-questions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        resume_info: state.resumeInfo,
        difficulty,
        total_questions: totalQuestions,
      }),
    });

    if (res.ok) {
      const data = await res.json();
      state.questions   = data.questions;
      state.currentQ    = 0;
      state.answers     = [];
      state.difficulty  = difficulty;
      state.saved       = false;
      state.spokenQ     = -1;
      state.processedQ  = -1;

      showStatusMsg('generate-status', 'success', `${state.questions.length} questions ready!`);
      startInterviewScreen();
    } else {
      showStatusMsg('generate-status', 'error', 'Failed to generate questions. Please try again.');
    }
  } catch {
    showStatusMsg('generate-status', 'error', 'Network error. Check your connection and try again.');
  } finally {
    setLoading(btn, false);
  }
}

// ───────────────────────────────────────────────
// INTERVIEW — SHOW QUESTION SCREEN
// ───────────────────────────────────────────────
function startInterviewScreen() {
  hideEl(document.getElementById('section-resume'));
  hideEl(document.getElementById('section-settings'));
  hideEl(document.getElementById('section-complete'));
  showEl(document.getElementById('section-interview'));
  loadQuestion();
}

function loadQuestion() {
  const q      = state.questions[state.currentQ];
  const total  = state.questions.length;
  const qNum   = state.currentQ + 1;
  const pct    = ((state.currentQ) / total) * 100;

  document.getElementById('q-current').textContent     = qNum;
  document.getElementById('q-total').textContent       = total;
  document.getElementById('question-number').textContent = `Q${qNum}`;
  document.getElementById('question-text').textContent = q;
  document.getElementById('progress-bar').style.width  = `${pct}%`;

  // Reset UI state for new question
  hideEl(document.getElementById('transcription-area'));
  hideEl(document.getElementById('score-area'));
  hideEl(document.getElementById('next-btn-wrap'));
  hideEl(document.getElementById('transcribe-spinner'));
  hideEl(document.getElementById('score-spinner'));
  resetRecorder();
  document.getElementById('recorder-hint').textContent = 'Click to start recording your answer';

  // Auto-speak the question (only once per question)
  if (state.spokenQ !== state.currentQ) {
    state.spokenQ = state.currentQ;
    speakQuestion();
  }
}

// ───────────────────────────────────────────────
// TTS — SPEAK QUESTION
// ───────────────────────────────────────────────
function speakQuestion() {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const q = state.questions[state.currentQ];
  const utterance = new SpeechSynthesisUtterance(q);
  utterance.rate  = 0.9;
  utterance.pitch = 1;
  utterance.lang  = 'en-US';
  window.speechSynthesis.speak(utterance);
}

// ───────────────────────────────────────────────
// RECORDING — MediaRecorder API
// ───────────────────────────────────────────────
async function toggleRecording() {
  if (state.isRecording) {
    stopRecording();
  } else {
    await startRecording();
  }
}

async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    state.audioChunks   = [];
    state.mediaRecorder = new MediaRecorder(stream, { mimeType: getSupportedMimeType() });

    state.mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) state.audioChunks.push(e.data);
    };

    state.mediaRecorder.onstop = async () => {
      // Stop all tracks to release mic
      stream.getTracks().forEach(t => t.stop());
      await processAudioAnswer();
    };

    state.mediaRecorder.start();
    state.isRecording = true;

    // Update UI
    const btn = document.getElementById('record-btn');
    btn.classList.add('recording');
    document.getElementById('record-icon').className = 'fa-solid fa-stop record-icon';
    document.getElementById('record-label').textContent = 'Stop Recording';
    document.getElementById('recorder-hint').textContent = 'Recording... Click to stop when done';
  } catch (err) {
    if (err.name === 'NotAllowedError') {
      showToast('Microphone access denied. Please allow mic access and try again.');
    } else {
      showToast('Could not start recording: ' + err.message);
    }
  }
}

function stopRecording() {
  if (state.mediaRecorder && state.isRecording) {
    state.mediaRecorder.stop();
    state.isRecording = false;

    // Update UI to processing state
    const btn = document.getElementById('record-btn');
    btn.classList.remove('recording');
    document.getElementById('record-icon').className = 'fa-solid fa-microphone record-icon';
    document.getElementById('record-label').textContent = 'Processing...';
    document.getElementById('record-btn').disabled = true;
  }
}

function resetRecorder() {
  state.isRecording = false;
  const btn = document.getElementById('record-btn');
  btn.classList.remove('recording');
  btn.disabled = false;
  document.getElementById('record-icon').className = 'fa-solid fa-microphone record-icon';
  document.getElementById('record-label').textContent = 'Start Recording';
}

function getSupportedMimeType() {
  const types = ['audio/webm;codecs=opus', 'audio/webm', 'audio/ogg;codecs=opus', 'audio/mp4'];
  for (const t of types) {
    if (MediaRecorder.isTypeSupported(t)) return t;
  }
  return '';
}

// ───────────────────────────────────────────────
// TRANSCRIPTION + SCORING
// ───────────────────────────────────────────────
async function processAudioAnswer() {
  if (state.processedQ === state.currentQ) return; // prevent double-processing
  state.processedQ = state.currentQ;

  const mimeType  = getSupportedMimeType();
  const extension = mimeType.includes('webm') ? 'webm' : mimeType.includes('ogg') ? 'ogg' : 'mp4';
  const blob      = new Blob(state.audioChunks, { type: mimeType });

  // ---- Step 1: Transcribe ----
  showEl(document.getElementById('transcribe-spinner'));
  const formData = new FormData();
  formData.append('file', blob, `answer.${extension}`);

  let transcribedText = '';
  try {
    const res = await fetch(`${API_URL}/question/answer-audio`, {
      method: 'POST',
      body: formData,
    });

    if (res.ok) {
      const data = await res.json();
      transcribedText = data.text;
    } else {
      showToast('Transcription failed. Please re-record your answer.');
      resetRecorder();
      hideEl(document.getElementById('transcribe-spinner'));
      state.processedQ = -1;
      return;
    }
  } catch {
    showToast('Network error during transcription.');
    resetRecorder();
    hideEl(document.getElementById('transcribe-spinner'));
    state.processedQ = -1;
    return;
  }

  hideEl(document.getElementById('transcribe-spinner'));

  // Show transcription
  document.getElementById('transcription-text').textContent = transcribedText;
  showEl(document.getElementById('transcription-area'));

  // ---- Step 2: Score ----
  showEl(document.getElementById('score-spinner'));
  const question    = state.questions[state.currentQ];
  const isIntro     = state.currentQ < 2;

  try {
    const res = await fetch(`${API_URL}/question/score-answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question,
        answer: transcribedText,
        is_intro_question: isIntro,
      }),
    });

    if (res.ok) {
      const scoreData = await res.json();

      // Save answer
      state.answers.push({
        question,
        answer: transcribedText,
        ...scoreData,
      });

      displayScore(scoreData);
    } else {
      showToast('Scoring failed. Moving to next question.');
    }
  } catch {
    showToast('Network error during scoring.');
  }

  hideEl(document.getElementById('score-spinner'));

  // Show Next button
  const isLast = state.currentQ >= state.questions.length - 1;
  const nextBtn = document.getElementById('next-btn');
  nextBtn.textContent = isLast ? 'Finish Interview' : '';
  if (isLast) {
    nextBtn.innerHTML = 'Finish Interview <i class="fa-solid fa-flag-checkered"></i>';
  } else {
    nextBtn.innerHTML = 'Next Question <i class="fa-solid fa-arrow-right"></i>';
  }
  showEl(document.getElementById('next-btn-wrap'));

  // Re-enable record button (disabled during processing)
  document.getElementById('record-btn').disabled = false;
  document.getElementById('record-label').textContent = 'Start Recording';
}

function displayScore(scoreData) {
  const verdict = scoreData.verdict;
  const badge   = document.getElementById('verdict-badge');

  const icons = { correct: '✅', partial: '⚠️', wrong: '❌' };
  const labels = { correct: 'Correct', partial: 'Partial', wrong: 'Wrong' };

  badge.className = `verdict-badge ${verdict}`;
  badge.textContent = `${icons[verdict] || ''} ${labels[verdict] || verdict}`;

  document.getElementById('score-reason').textContent = scoreData.reason || '';

  if (scoreData.confidence_score !== undefined) {
    const pct = (scoreData.confidence_score / 10) * 100;
    document.getElementById('confidence-bar').style.width = `${pct}%`;
    document.getElementById('confidence-val').textContent = `${scoreData.confidence_score}/10`;
    showEl(document.getElementById('confidence-area'));
  } else {
    hideEl(document.getElementById('confidence-area'));
  }

  showEl(document.getElementById('score-area'));
}

// ───────────────────────────────────────────────
// INTERVIEW — NEXT QUESTION
// ───────────────────────────────────────────────
async function nextQuestion() {
  state.currentQ++;

  if (state.currentQ >= state.questions.length) {
    // Interview complete
    document.getElementById('progress-bar').style.width = '100%';
    await finishInterview();
  } else {
    state.processedQ = -1;
    loadQuestion();
    // Scroll to interview section
    document.getElementById('section-interview').scrollIntoView({ behavior: 'smooth' });
  }
}

// ───────────────────────────────────────────────
// INTERVIEW — FINISH & SAVE
// ───────────────────────────────────────────────
async function finishInterview() {
  hideEl(document.getElementById('section-interview'));
  showEl(document.getElementById('section-complete'));

  // Auto-save
  if (!state.saved && state.answers.length > 0) {
    try {
      const res = await fetch(`${API_URL}/analytics/save-interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: state.userId,
          difficulty: state.difficulty,
          answers: state.answers,
        }),
      });
      if (res.ok) {
        state.saved = true;
        showToast('Interview saved to your report history!');
      }
    } catch {
      showToast('Could not save interview. Check your connection.');
    }
  }

  renderSummary();
  document.getElementById('section-complete').scrollIntoView({ behavior: 'smooth' });
}

function renderSummary() {
  const answers = state.answers;
  const correct = answers.filter(a => a.verdict === 'correct').length;
  const partial = answers.filter(a => a.verdict === 'partial').length;
  const wrong   = answers.filter(a => a.verdict === 'wrong').length;

  // Stats
  document.getElementById('summary-stats').innerHTML = `
    <div class="stat-card stat-correct">
      <span class="stat-num">${correct}</span>
      <span class="stat-label">Correct</span>
    </div>
    <div class="stat-card stat-partial">
      <span class="stat-num">${partial}</span>
      <span class="stat-label">Partial</span>
    </div>
    <div class="stat-card stat-wrong">
      <span class="stat-num">${wrong}</span>
      <span class="stat-label">Wrong</span>
    </div>
  `;

  // Question list
  const icons = { correct: '✅', partial: '⚠️', wrong: '❌' };
  document.getElementById('summary-list').innerHTML = answers.map((a, i) => `
    <div class="summary-item">
      <span class="summary-q">${icons[a.verdict] || ''} Q${i + 1}: ${escapeHtml(a.question)}</span>
      <span class="summary-verdict">${a.verdict} — ${escapeHtml(a.reason || '')}</span>
      ${a.confidence_score !== undefined ? `<span style="font-size:.82rem;color:var(--text-muted)">Confidence: ${a.confidence_score}/10</span>` : ''}
    </div>
  `).join('');
}

// ───────────────────────────────────────────────
// INTERVIEW — RESET
// ───────────────────────────────────────────────
function startNewInterview() {
  resetInterviewState();

  showEl(document.getElementById('section-resume'));
  showEl(document.getElementById('section-settings'));
  hideEl(document.getElementById('section-interview'));
  hideEl(document.getElementById('section-complete'));

  // Lock settings again
  document.getElementById('section-settings').classList.add('locked');
  document.getElementById('generate-btn').disabled = true;
  hideEl(document.getElementById('resume-done-badge'));

  // Clear resume
  clearFile();
  hideStatusMsg('generate-status');

  // Reset progress bar
  document.getElementById('progress-bar').style.width = '0%';

  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function resetInterviewState() {
  state.resumeInfo = null;
  state.questions  = [];
  state.currentQ   = 0;
  state.answers    = [];
  state.saved      = false;
  state.spokenQ    = -1;
  state.processedQ = -1;
  if (window.speechSynthesis) window.speechSynthesis.cancel();
}

// ───────────────────────────────────────────────
// REPORTS — LOAD
// ───────────────────────────────────────────────
async function loadReports() {
  const loadingEl = document.getElementById('reports-loading');
  const emptyEl   = document.getElementById('reports-empty');
  const listEl    = document.getElementById('reports-list');

  showEl(loadingEl);
  hideEl(emptyEl);
  hideEl(listEl);
  listEl.innerHTML = '';

  try {
    const res = await fetch(`${API_URL}/analytics/get-report/${state.userId}`);
    if (!res.ok) throw new Error('Failed to load');

    const data       = await res.json();
    const interviews = data.interviews || [];

    hideEl(loadingEl);

    if (interviews.length === 0) {
      showEl(emptyEl);
    } else {
      interviews.reverse(); // newest first
      listEl.innerHTML = interviews.map(renderReportCard).join('');
      showEl(listEl);
    }
  } catch {
    hideEl(loadingEl);
    showEl(emptyEl);
    document.querySelector('#reports-empty p').textContent = 'Failed to load reports. Check your connection.';
  }
}

function renderReportCard(interview) {
  const answers  = interview.answers || [];
  const correct  = answers.filter(a => a.verdict === 'correct').length;
  const partial  = answers.filter(a => a.verdict === 'partial').length;
  const wrong    = answers.filter(a => a.verdict === 'wrong').length;
  const date     = interview.created_at || 'Unknown date';
  const diff     = (interview.difficulty || 'unknown').toUpperCase();
  const id       = interview._id;

  const icons = { correct: '✅', partial: '⚠️', wrong: '❌' };

  const questionsHtml = answers.map((a, i) => `
    <div class="report-question-item">
      <div class="report-q-text">${icons[a.verdict] || ''} Q${i + 1}: ${escapeHtml(a.question)}</div>
      <div class="report-a-text"><strong>Answer:</strong> ${escapeHtml(a.answer || '')}</div>
      <div class="report-verdict" style="color:${a.verdict==='correct'?'var(--success)':a.verdict==='partial'?'var(--warning)':'var(--danger)'}">
        ${a.verdict} — ${escapeHtml(a.reason || '')}
      </div>
      ${a.confidence_score !== undefined ? `<div style="font-size:.8rem;color:var(--text-muted);margin-top:.25rem">Confidence: ${a.confidence_score}/10</div>` : ''}
    </div>
  `).join('');

  return `
    <div class="report-card" id="report-${id}">
      <div class="report-header" onclick="toggleReport('${id}')">
        <span class="report-date"><i class="fa-regular fa-calendar"></i> ${escapeHtml(date)}</span>
        <div class="report-meta">
          <span class="report-difficulty">${diff}</span>
          <div class="report-scores">
            <span class="score-correct">✅ ${correct}</span>
            <span class="score-partial">⚠️ ${partial}</span>
            <span class="score-wrong">❌ ${wrong}</span>
          </div>
        </div>
        <i class="fa-solid fa-chevron-down report-toggle"></i>
      </div>
      <div class="report-body">
        ${questionsHtml}
        <button class="btn btn-danger btn-sm report-delete-btn" onclick="deleteInterview('${id}')">
          <i class="fa-solid fa-trash"></i> Delete this interview
        </button>
      </div>
    </div>
  `;
}

function toggleReport(id) {
  document.getElementById(`report-${id}`).classList.toggle('open');
}

async function deleteInterview(id) {
  if (!confirm('Delete this interview permanently?')) return;

  try {
    const res = await fetch(`${API_URL}/analytics/delete-session/${id}`, { method: 'DELETE' });
    if (res.ok) {
      document.getElementById(`report-${id}`)?.remove();
      showToast('Interview deleted');
      // Check if list is empty
      if (!document.querySelector('.report-card')) {
        hideEl(document.getElementById('reports-list'));
        showEl(document.getElementById('reports-empty'));
        document.querySelector('#reports-empty p').textContent = 'No interviews yet. Go complete one!';
      }
    } else {
      showToast('Failed to delete interview');
    }
  } catch {
    showToast('Network error. Try again.');
  }
}

// ───────────────────────────────────────────────
// UI HELPERS
// ───────────────────────────────────────────────
function showEl(el) {
  if (el) el.classList.remove('hidden');
}

function hideEl(el) {
  if (el) el.classList.add('hidden');
}

function setLoading(btn, loading) {
  const textEl    = btn.querySelector('.btn-text');
  const spinnerEl = btn.querySelector('.btn-spinner');
  if (loading) {
    btn.disabled = true;
    if (textEl) textEl.classList.add('hidden');
    if (spinnerEl) spinnerEl.classList.remove('hidden');
  } else {
    btn.disabled = false;
    if (textEl) textEl.classList.remove('hidden');
    if (spinnerEl) spinnerEl.classList.add('hidden');
  }
}

function showStatusMsg(id, type, text) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = `status-msg ${type}`;
  el.textContent = text;
  el.classList.remove('hidden');
}

function hideStatusMsg(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('hidden');
}

let toastTimer = null;
function showToast(message, duration = 3500) {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.classList.add('show');
  toast.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove('show');
  }, duration);
}

function escapeHtml(text) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
  return String(text || '').replace(/[&<>"']/g, m => map[m]);
}
