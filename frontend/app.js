/**
 * Hack2Hire - AI Mock Interview Platform
 * Vanilla JavaScript Application
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000';
// UI transition delay (in milliseconds)
const STEP_TRANSITION_DELAY = 2000; // 2 seconds (increase if needed)

// Application State
const state = {
    sessionId: null,
    resumeData: null,
    jdData: null,
    matchData: null,
    currentQuestion: null,
    questionNumber: 0,
    totalQuestions: 10,
    timerInterval: null,
    timeRemaining: 60,
    startTime: null,
    allScores: []
};

// DOM Elements
const elements = {
    // Step sections
    stepUpload: document.getElementById('step-upload'),
    stepJd: document.getElementById('step-jd'),
    stepStart: document.getElementById('step-start'),
    stepInterview: document.getElementById('step-interview'),
    stepResults: document.getElementById('step-results'),
    
    // Upload section
    uploadZone: document.getElementById('uploadZone'),
    resumeFile: document.getElementById('resumeFile'),
    resumePreview: document.getElementById('resumePreview'),
    resumeDetails: document.getElementById('resumeDetails'),
    
    // JD section
    jdText: document.getElementById('jdText'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    matchResults: document.getElementById('matchResults'),
    matchScoreCircle: document.getElementById('matchScoreCircle'),
    matchScoreValue: document.getElementById('matchScoreValue'),
    matchDetails: document.getElementById('matchDetails'),
    
    // Start section
    startInterviewBtn: document.getElementById('startInterviewBtn'),
    
    // Interview section
    currentQuestion: document.getElementById('currentQuestion'),
    totalQuestionsEl: document.getElementById('totalQuestions'),
    progressFill: document.getElementById('progressFill'),
    timerValue: document.getElementById('timerValue'),
    chatMessages: document.getElementById('chatMessages'),
    answerInput: document.getElementById('answerInput'),
    submitAnswerBtn: document.getElementById('submitAnswerBtn'),
    difficultyLevel: document.getElementById('difficultyLevel'),
    
    // Results section
    finalScoreValue: document.getElementById('finalScoreValue'),
    finalScoreStatus: document.getElementById('finalScoreStatus'),
    resultsEmoji: document.getElementById('resultsEmoji'),
    skillBreakdown: document.getElementById('skillBreakdown'),
    strengthsList: document.getElementById('strengthsList'),
    weaknessesList: document.getElementById('weaknessesList'),
    recommendation: document.getElementById('recommendation'),
    restartBtn: document.getElementById('restartBtn'),
    
    // Utility
    loadingOverlay: document.getElementById('loadingOverlay')
};

// ========== UTILITY FUNCTIONS ==========

function showLoading() {
    elements.loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    elements.loadingOverlay.classList.add('hidden');
}

function showStep(stepElement) {
    // Hide all steps
    document.querySelectorAll('.step-section').forEach(step => {
        step.classList.remove('active');
    });
    // Show target step
    stepElement.classList.add('active');
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        alert(`Error: ${error.message}`);
        throw error;
    }
}

// ========== STEP 1: RESUME UPLOAD ==========

elements.uploadZone.addEventListener('click', () => {
    elements.resumeFile.click();
});

elements.uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.uploadZone.style.borderColor = 'var(--primary-blue)';
});

elements.uploadZone.addEventListener('dragleave', () => {
    elements.uploadZone.style.borderColor = 'var(--border-glow)';
});

elements.uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.uploadZone.style.borderColor = 'var(--border-glow)';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleResumeUpload(files[0]);
    }
});

elements.resumeFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleResumeUpload(e.target.files[0]);
    }
});

async function handleResumeUpload(file) {
    // Validate file
    if (!file.name.match(/\.(pdf|txt)$/i)) {
        alert('Please upload a PDF or TXT file');
        return;
    }
    
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const data = await apiCall('/api/upload-resume', {
            method: 'POST',
            body: formData
        });
        
        state.sessionId = data.session_id;
        state.resumeData = data.resume_data;
        
        displayResumePreview(data.resume_data);

        setTimeout(() => {
    showStep(elements.stepJd);
}, STEP_TRANSITION_DELAY);
        
        // Enable analyze button if JD is also filled
        if (elements.jdText.value.trim()) {
            elements.analyzeBtn.disabled = false;
        }
        
    } catch (error) {
        console.error('Resume upload failed:', error);
    } finally {
        hideLoading();
    }
}

function displayResumePreview(resumeData) {
    elements.resumePreview.classList.remove('hidden');
    
    elements.resumeDetails.innerHTML = `
        <div class="detail-item">
            <div class="detail-label">Total Skills</div>
            <div class="detail-value">${resumeData.total_skills}</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Experience</div>
            <div class="detail-value">${resumeData.experience_years || 'N/A'} years</div>
        </div>
        <div class="detail-item">
            <div class="detail-label">Projects</div>
            <div class="detail-value">${resumeData.projects_found}</div>
        </div>
    `;
}

// ========== STEP 2: JOB DESCRIPTION ANALYSIS ==========

elements.jdText.addEventListener('input', () => {
    if (elements.jdText.value.trim() && state.sessionId) {
        elements.analyzeBtn.disabled = false;
    } else {
        elements.analyzeBtn.disabled = true;
    }
});

elements.analyzeBtn.addEventListener('click', analyzeJobDescription);

async function analyzeJobDescription() {
    if (!state.sessionId) {
        alert('Please upload your resume first');
        return;
    }
    
    const jdText = elements.jdText.value.trim();
    if (!jdText) {
        alert('Please paste a job description');
        return;
    }
    
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('session_id', state.sessionId);
        formData.append('jd_text', jdText);
        
        const data = await apiCall('/api/analyze-jd', {
            method: 'POST',
            body: formData
        });

        console.log("JD ANALYSIS RESPONSE:", data);
        
        state.jdData = data.jd_analysis;
        state.matchData = data.skill_match;
        
        displayMatchResults(data.skill_match, data.jd_analysis);
        
        // Enable start interview button
        elements.startInterviewBtn.disabled = false;
        //showStep(elements.stepStart);



    } catch (error) {
        console.error('JD analysis failed:', error);
    } finally {
        hideLoading();
    }
}

function displayMatchResults(matchData, jdData) {
    elements.matchResults.classList.remove('hidden');

    // Animate score
    const targetScore = Math.round(matchData.match_percentage);
    animateScore(0, targetScore, 1500);

    // Set circular progress
    const angle = (targetScore / 100) * 360;
    elements.matchScoreCircle.style.setProperty('--score-angle', angle);

    elements.matchDetails.innerHTML = `
        <div style="margin-bottom: 1rem;">
            <strong>Skill Match Summary</strong>
        </div>

        <div style="margin-bottom: 1rem; color: var(--accent-green);">
            ✔ Matched Skills (${matchData.matched_skills.length})
            <div style="font-size: 0.85rem; margin-top: 0.25rem;">
                ${matchData.matched_skills.length
                    ? matchData.matched_skills.join(', ')
                    : 'No matching skills found'}
            </div>
        </div>

        <div style="margin-bottom: 1rem; color: var(--primary-pink);">
            ✖ Missing Skills (${matchData.missing_skills.length})
            <div style="font-size: 0.85rem; margin-top: 0.25rem;">
                ${matchData.missing_skills.length
                    ? matchData.missing_skills.join(', ')
                    : 'No missing skills 🎉'}
            </div>
        </div>

        <div style="font-size: 0.8rem; color: var(--text-secondary);">
            Role: ${jdData.role_level.toUpperCase()} • Required Experience: ${jdData.experience_required}+ years
        </div>
    `;
}


function animateScore(start, end, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * progress);
        elements.matchScoreValue.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

// ========== STEP 3: START INTERVIEW ==========

elements.startInterviewBtn.addEventListener('click', startInterview);

async function startInterview() {
    if (!state.sessionId) {
        alert('Session not found. Please start over.');
        return;
    }
    
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('session_id', state.sessionId);
        
        const data = await apiCall('/api/start-interview', {
            method: 'POST',
            body: formData
        });
        
        state.currentQuestion = data.question_data;
        state.questionNumber = data.question_data.question_number;
        state.totalQuestions = data.question_data.max_questions;
        
        // Show interview screen
        showStep(elements.stepInterview);
        
        // Display first question
        displayQuestion(data.question_data);
        
        // Start timer
        startTimer();
        
    } catch (error) {
        console.error('Failed to start interview:', error);
    } finally {
        hideLoading();
    }
}

// ========== STEP 4: INTERVIEW ==========

function displayQuestion(questionData) {
    // Update progress
    elements.currentQuestion.textContent = questionData.question_number;
    elements.totalQuestionsEl.textContent = questionData.max_questions;
    
    const progress = (questionData.question_number / questionData.max_questions) * 100;
    elements.progressFill.style.width = `${progress}%`;
    
    // Update difficulty badge
    elements.difficultyLevel.textContent = questionData.difficulty.toUpperCase();
    elements.difficultyLevel.className = `difficulty-badge ${questionData.difficulty}`;
    
    // Add question to chat
    const questionMessage = document.createElement('div');
    questionMessage.className = 'chat-message';
    questionMessage.innerHTML = `
        <div class="message-label interviewer">
            🤖 AI Interviewer
            <span class="question-type">${questionData.question_type}</span>
        </div>
        <div class="message-bubble interviewer">
            ${questionData.question}
        </div>
    `;
    
    elements.chatMessages.appendChild(questionMessage);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    
    // Clear answer input
    elements.answerInput.value = '';
    elements.answerInput.focus();
}

function startTimer() {
    state.timeRemaining = 90;
    state.startTime = Date.now();
    elements.timerValue.textContent = state.timeRemaining;
    elements.timerValue.className = 'timer-value';
    
    if (state.timerInterval) {
        clearInterval(state.timerInterval);
    }
    
    state.timerInterval = setInterval(() => {
        state.timeRemaining--;
        elements.timerValue.textContent = state.timeRemaining;
        
        // Update timer styling
        if (state.timeRemaining <= 10) {
            elements.timerValue.classList.add('danger');
        } else if (state.timeRemaining <= 20) {
            elements.timerValue.classList.add('warning');
        }
        
        // Auto-submit on timeout
        if (state.timeRemaining <= 0) {
            clearInterval(state.timerInterval);
            submitAnswer(true);
        }
    }, 1000);
}

elements.submitAnswerBtn.addEventListener('click', () => submitAnswer(false));

elements.answerInput.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        submitAnswer(false);
    }
});

async function submitAnswer(isTimeout = false) {
    const answer = elements.answerInput.value.trim();
    
    if (!answer && !isTimeout) {
        alert('Please provide an answer');
        return;
    }
    
    // Stop timer
    if (state.timerInterval) {
        clearInterval(state.timerInterval);
    }
    
    // Calculate time taken
    const timeTaken = isTimeout ? 60 : Math.floor((Date.now() - state.startTime) / 1000);
    
    // Display candidate answer in chat
    const answerMessage = document.createElement('div');
    answerMessage.className = 'chat-message';
    answerMessage.innerHTML = `
        <div class="message-label candidate">
            👤 You
        </div>
        <div class="message-bubble candidate">
            ${answer || '(No answer provided)'}
        </div>
    `;
    elements.chatMessages.appendChild(answerMessage);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    
    // Disable input while processing
    elements.answerInput.disabled = true;
    elements.submitAnswerBtn.disabled = true;
    
    showLoading();
    
    try {
        const response = await apiCall('/api/submit-answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                session_id: state.sessionId,
                answer: answer || '',
                time_taken: timeTaken
            })
        });
        
        // Store score
        state.allScores.push(response.current_score);
        
        // Show score feedback briefly
        const scoreMessage = document.createElement('div');
        scoreMessage.className = 'chat-message';
        scoreMessage.innerHTML = `
            <div class="message-label interviewer">
                📊 Score
            </div>
            <div class="message-bubble interviewer">
                Overall: ${response.current_score.overall}/100<br>
                ${response.current_score.feedback}
            </div>
        `;
        elements.chatMessages.appendChild(scoreMessage);
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
        
        // Check if interview is complete
        if (response.interview_complete) {
            setTimeout(() => {
                displayFinalResults(response.final_results);
            }, 6000);
        } else {
            // Continue to next question
            setTimeout(() => {
                state.currentQuestion = response.next_question;
                state.questionNumber = response.next_question.question_number;
                displayQuestion(response.next_question);
                
                // Re-enable input
                elements.answerInput.disabled = false;
                elements.submitAnswerBtn.disabled = false;
                
                // Restart timer
                startTimer();
            }, 2000);
        }
        
    } catch (error) {
        console.error('Failed to submit answer:', error);
        elements.answerInput.disabled = false;
        elements.submitAnswerBtn.disabled = false;
    } finally {
        hideLoading();
    }
}

// ========== STEP 5: RESULTS ==========

function displayFinalResults(results) {
    showStep(elements.stepResults);
    
    // Animate final score
    animateFinalScore(0, Math.round(results.final_score), 2000);
    
    // Set status and emoji
    elements.finalScoreStatus.textContent = results.hiring_readiness;
    
    const emojis = {
        'HIGHLY RECOMMENDED': '🎉',
        'RECOMMENDED': '👍',
        'CONDITIONAL': '🤔',
        'NOT RECOMMENDED': '😔'
    };
    elements.resultsEmoji.textContent = emojis[results.hiring_readiness] || '✅';
    
    // Display skill breakdown
    displaySkillBreakdown(results.skill_breakdown);
    
    // Display strengths
    displayStrengths(results.strengths);
    
    // Display weaknesses
    displayWeaknesses(results.weaknesses);
    
    // Display recommendation
    elements.recommendation.innerHTML = `
        <strong>${results.recommendation}</strong><br><br>
        You answered ${results.total_questions} questions with an average score of ${results.final_score}/100.
        ${results.early_termination ? '<br><br>⚠️ Interview was terminated early due to low performance.' : ''}
    `;
}

function animateFinalScore(start, end, duration) {
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(start + (end - start) * progress);
        elements.finalScoreValue.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    requestAnimationFrame(update);
}

function displaySkillBreakdown(breakdown) {
    const metrics = ['accuracy', 'clarity', 'depth', 'relevance', 'time_efficiency'];
    
    elements.skillBreakdown.innerHTML = metrics.map(metric => {
        const score = Math.round(breakdown[metric] || 0);
        const label = metric.replace('_', ' ').split(' ')
            .map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
        
        return `
            <div class="skill-bar">
                <div class="skill-bar-header">
                    <span>${label}</span>
                    <span>${score}%</span>
                </div>
                <div class="skill-bar-track">
                    <div class="skill-bar-fill" style="width: ${score}%"></div>
                </div>
            </div>
        `;
    }).join('');
}

function displayStrengths(strengths) {
    if (strengths.length === 0 || strengths[0] === 'None identified') {
        elements.strengthsList.innerHTML = '<div style="color: var(--text-secondary);">No specific strengths identified</div>';
        return;
    }
    
    elements.strengthsList.innerHTML = strengths.map(strength => `
        <div class="strength-item">
            <span>✓</span>
            <span>${strength}</span>
        </div>
    `).join('');
}

function displayWeaknesses(weaknesses) {
    if (weaknesses.length === 0 || weaknesses[0] === 'None identified') {
        elements.weaknessesList.innerHTML = '<div style="color: var(--text-secondary);">No major weaknesses identified</div>';
        return;
    }
    
    elements.weaknessesList.innerHTML = weaknesses.map(weakness => `
        <div class="weakness-item">
            <span>!</span>
            <span>${weakness}</span>
        </div>
    `).join('');
}

// ========== RESTART ==========

elements.restartBtn.addEventListener('click', () => {
    // Reset state
    state.sessionId = null;
    state.resumeData = null;
    state.jdData = null;
    state.matchData = null;
    state.currentQuestion = null;
    state.questionNumber = 0;
    state.allScores = [];
    
    // Clear inputs
    elements.resumeFile.value = '';
    elements.jdText.value = '';
    elements.answerInput.value = '';
    
    // Reset UI
    elements.resumePreview.classList.add('hidden');
    elements.matchResults.classList.add('hidden');
    elements.chatMessages.innerHTML = '';
    
    // Disable buttons
    elements.analyzeBtn.disabled = true;
    elements.startInterviewBtn.disabled = true;
    
    // Show first step
    showStep(elements.stepUpload);
});

// ========== INITIALIZATION ==========

// Show first step on load
showStep(elements.stepUpload);

console.log('Hack2Hire initialized and ready!');