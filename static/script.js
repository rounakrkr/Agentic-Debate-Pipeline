const AGENT_NAMES = ["Eldest Sibling", "Middle Sibling", "Youngest Sibling"];
        const API_BASE = window.location.origin;
        let history = [];

        // Enhanced Markdown Parser (Fixes newline bugs inside bold tags)
        function formatText(text) {
            if (!text) return "System returned no data. Awaiting retry..."; 
            const div = document.createElement('div');
            div.textContent = text;
            let safeText = div.innerHTML;
            
            // Added 's' flag so bold/italics work perfectly even across multiple lines!
            safeText = safeText.replace(/\*\*(.*?)\*\*/gs, '<b>$1</b>');
            safeText = safeText.replace(/\*(.*?)\*/gs, '<b>$1</b>');
            return safeText;
        }

        function createLoaderHtml(text) {
            return `<div class="typing-indicator">${text}<div class="typing-dots"><span></span><span></span><span></span></div></div>`;
        }

        async function ask() {
            const userInput = document.getElementById('query').value.trim();
            if (!userInput) return;

            document.getElementById('askBtn').disabled = true;
            document.getElementById('debateBtn').disabled = true;
            document.getElementById('synthesizeBtn').disabled = true;
            document.getElementById('debateStatus').style.display = 'none';

            const container = document.getElementById('answersContainer');
            
            container.innerHTML = `
                <div class="answer-card" id="card_0">
                    <div class="card-header">🧠 ${AGENT_NAMES[0]}</div>
                    <div class="card-content" id="content_0">${createLoaderHtml('Deep Reasoning')}</div>
                </div>
                <div class="answer-card" id="card_1">
                    <div class="card-header">⚡ ${AGENT_NAMES[1]}</div>
                    <div class="card-content" id="content_1">Awaiting Turn...</div>
                </div>
                <div class="answer-card" id="card_2">
                    <div class="card-header">🔥 ${AGENT_NAMES[2]}</div>
                    <div class="card-content" id="content_2">Awaiting Turn...</div>
                </div>
            `;

            try {
                const res1 = await fetch(`${API_BASE}/ask/agent1?query=${encodeURIComponent(userInput)}`);
                const data1 = await res1.json();
                document.getElementById('content_0').innerHTML = formatText(data1.response);
                document.getElementById('content_1').innerHTML = createLoaderHtml('Refining Logic');

                const res2 = await fetch(`${API_BASE}/ask/agent2?query=${encodeURIComponent(userInput)}&agent1_response=${encodeURIComponent(data1.response)}`);
                const data2 = await res2.json();
                document.getElementById('content_1').innerHTML = formatText(data2.response);
                document.getElementById('content_2').innerHTML = createLoaderHtml('Adding Perspective');

                const res3 = await fetch(`${API_BASE}/ask/agent3?query=${encodeURIComponent(userInput)}&agent1_response=${encodeURIComponent(data1.response)}&agent2_response=${encodeURIComponent(data2.response)}`);
                const data3 = await res3.json();
                document.getElementById('content_2').innerHTML = formatText(data3.response);

                history.push({ user: userInput, agent1: data1.response, agent2: data2.response, agent3: data3.response });
                updateHistoryUI();

            } catch (err) {
                alert("API connection failed. Auto-retry exhausted. Check terminal.");
            } finally {
                document.getElementById('askBtn').disabled = false;
                document.getElementById('debateBtn').disabled = false;
                document.getElementById('synthesizeBtn').disabled = false;
            }
        }

        async function runDebate() {
            const userInput = document.getElementById('query').value.trim();
            if (!userInput) return alert("Enter a follow-up query for the debate.");
            
            const rounds = parseInt(document.getElementById('rounds').value) || 1;
            document.getElementById('debateBtn').disabled = true;
            
            const statusBox = document.getElementById('debateStatus');
            statusBox.style.display = 'block';

            let currentHistory = [...history];
            currentHistory.push({ user: userInput, agent1: "", agent2: "", agent3: "" });

            for (let round = 1; round <= rounds; round++) {
                statusBox.innerHTML = `⚔️ Processing Debate Round ${round} of ${rounds}...`;
                
                try {
                    const res = await fetch('/debate_with_history', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ history: currentHistory })
                    });
                    const data = await res.json();
                    
                    const lastIdx = currentHistory.length - 1;
                    currentHistory[lastIdx].agent1 = data.refined_agent1;
                    currentHistory[lastIdx].agent2 = data.refined_agent2;
                    currentHistory[lastIdx].agent3 = data.refined_agent3;
                    
                    renderFinalCards(currentHistory[lastIdx]);
                } catch (e) {
                    alert("Debate failed."); break;
                }
            }

            statusBox.style.display = 'none';
            history = currentHistory;
            updateHistoryUI();
            document.getElementById('debateBtn').disabled = false;
        }

        function renderFinalCards(data) {
            document.getElementById('answersContainer').innerHTML = `
                <div class="answer-card" id="card_0"><div class="card-header">🧠 ${AGENT_NAMES[0]}</div><div class="card-content">${formatText(data.agent1)}</div></div>
                <div class="answer-card" id="card_1"><div class="card-header">⚡ ${AGENT_NAMES[1]}</div><div class="card-content">${formatText(data.agent2)}</div></div>
                <div class="answer-card" id="card_2"><div class="card-header">🔥 ${AGENT_NAMES[2]}</div><div class="card-content">${formatText(data.agent3)}</div></div>
            `;
        }

        async function synthesize() {
            if (history.length === 0) return;
            const last = history[history.length - 1];
            
            document.getElementById('answersContainer').insertAdjacentHTML('beforeend', `
                <div class="answer-card" id="synthesisCard">
                    <div class="card-header">⚖️ Final Verdict (Mediator)</div>
                    <div class="card-content" id="synthContent">${createLoaderHtml('Consolidating data')}</div>
                </div>
            `);

            try {
                const res = await fetch('/synthesize', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: last.user, agent1: last.agent1, agent2: last.agent2, agent3: last.agent3 })
                });
                const data = await res.json();
                document.getElementById('synthContent').innerHTML = formatText(data.synthesis);
            } catch (e) {
                document.getElementById('synthContent').innerHTML = "Failed to synthesize.";
            }
        }

        function updateHistoryUI() {
            const historyDiv = document.getElementById('historyList');
            historyDiv.innerHTML = history.map(exch => `
                <div class="history-entry">
                    <div class="history-user">👤 User: ${formatText(exch.user)}</div>
                    <div class="history-ai">🔵 <b>${AGENT_NAMES[0]}:</b> ${formatText(exch.agent1)}</div>
                    <div class="history-ai">🟠 <b>${AGENT_NAMES[1]}:</b> ${formatText(exch.agent2)}</div>
                    <div class="history-ai">🟣 <b>${AGENT_NAMES[2]}:</b> ${formatText(exch.agent3)}</div>
                </div>
            `).join('');
        }

        function reset() {
            history = [];
            document.getElementById('query').value = "";
            document.getElementById('debateStatus').style.display = 'none';
            document.getElementById('answersContainer').innerHTML = `
                <div class="answer-card" style="color: var(--text-secondary);">
                    <div class="card-header">System Standby</div>
                    <div class="card-content">Session cleared. Waiting for input...</div>
                </div>`;
            document.getElementById('historyList').innerHTML = 'No logs active.';
            document.getElementById('debateBtn').disabled = true;
            document.getElementById('synthesizeBtn').disabled = true;
        }

        function toggleTheme() {
            const html = document.documentElement;
            html.getAttribute('data-theme') === 'light' ? html.removeAttribute('data-theme') : html.setAttribute('data-theme', 'light');
        }