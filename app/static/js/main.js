// static/js/main.js

// Helper function to wait for Plotly to load
function waitForPlotly(callback) {
    if (typeof Plotly !== 'undefined') {
        callback();
    } else {
        setTimeout(() => waitForPlotly(callback), 50); 
    }
}

// Typing Animation Function
function typeAnswer(elementId, text, speed = 20) { 
    const targetElement = document.getElementById(elementId);
    if (!targetElement) {
        console.error(`Target element with ID "${elementId}" not found for typing animation.`);
        return;
    }

    targetElement.textContent = ''; 
    let i = 0;

    function typeWriterStep() {
        if (i < text.length) {
            targetElement.textContent += text.charAt(i);
            i++;
            setTimeout(typeWriterStep, speed);
        }
    }
    typeWriterStep(); 
}

// Dynamic Loading Messages
const loadingMessages = {
    'sql': "Generating SQL query... 🔍",
    'execute': "Fetching data from database... 📊",
    'chart': "Analyzing results & generating visualization... 📈",
    'humanize': "Humanizing the answer... 💬",
    'done': "Process complete!"
};
let loadingMessageInterval;
let currentLoadingStage = '';

function startLoadingAnimation(stage = 'sql') {
    stopLoadingAnimation(); // Clear any existing interval
    currentLoadingStage = stage;
    const loadingMessageElement = document.getElementById('loadingMessage');
    let messageIndex = 0;
    loadingMessageElement.textContent = loadingMessages[stage];

    loadingMessageInterval = setInterval(() => {
        // Simple animation: append dots
        loadingMessageElement.textContent += '.';
        if (loadingMessageElement.textContent.endsWith('....')) {
            loadingMessageElement.textContent = loadingMessages[stage];
        }
    }, 500); // Add a dot every 0.5 seconds
}

function stopLoadingAnimation() {
    clearInterval(loadingMessageInterval);
}


document.addEventListener('DOMContentLoaded', () => { 

    window.scrollTo(0, 0); 

    const queryForm = document.getElementById('queryForm');
    const questionInput = document.getElementById('questionInput');
    const resultsContainer = document.getElementById('resultsContainer');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorDisplay = document.getElementById('errorDisplay');
    const displayChartDiv = document.getElementById('displayChart');
    const chartsContainerDiv = document.getElementById('chartsContainer'); 
    const displayAnswerP = document.getElementById('displayAnswer'); 
    const displayQuestionP = document.getElementById('displayQuestion'); // Ensure this is obtained
    const displaySqlCode = document.getElementById('displaySql');
    const displayRawResultsDiv = document.getElementById('displayRawResults');
    const formLabel = document.querySelector('.form-label');
    const submitButton = document.querySelector('.submit-button');

    const themeToggle = document.getElementById('themeToggle'); 

    // Theme Toggle Logic (remains the same)
    function setTheme(theme) {
        document.body.classList.remove('light-mode', 'dark-mode');
        document.body.classList.add(theme + '-mode');
        localStorage.setItem('theme', theme); 
    }

    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        setTheme(savedTheme);
    } else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        setTheme('dark'); 
    } else {
        setTheme('light');
    }

    themeToggle.addEventListener('click', () => {
        const currentTheme = localStorage.getItem('theme'); 
        setTheme(currentTheme === 'light' ? 'dark' : 'light'); 
    });

    // Label Text Reveal Animation Control (remains the same)
    let labelAnimationTimeout;
    questionInput.addEventListener('input', () => {
        formLabel.classList.add('hide-animation');
        submitButton.classList.add('blinking');
        clearTimeout(labelAnimationTimeout);
        if (questionInput.value.trim() === '') {
            labelAnimationTimeout = setTimeout(() => {
                formLabel.classList.remove('hide-animation');
                submitButton.classList.remove('blinking');
            }, 1000); 
        }
    });
    questionInput.addEventListener('blur', () => {
        if (questionInput.value.trim() === '') {
            labelAnimationTimeout = setTimeout(() => {
                formLabel.classList.remove('hide-animation');
                submitButton.classList.remove('blinking');
            }, 500); 
        }
    });
    if (questionInput.value.trim() !== '') {
        formLabel.classList.add('hide-animation');
    }

    // --- Main Query Submission Logic (Refactored for Sequential API Calls) ---
    queryForm.addEventListener('submit', async function(event) {
        event.preventDefault();

        const question = questionInput.value;

        // Reset UI states
        resultsContainer.style.display = 'none';
        errorDisplay.style.display = 'none';
        loadingIndicator.style.display = 'block';
        displayChartDiv.innerHTML = ''; 
        displayChartDiv.removeAttribute('data-plotly-ready'); 
        chartsContainerDiv.style.display = 'none'; 
        displayAnswerP.textContent = ''; 
        displayAnswerP.className = 'ai-answer-text'; 
        displaySqlCode.textContent = ''; 
        displayRawResultsDiv.innerHTML = ''; 
        displayQuestionP.textContent = ''; // Clear question display before new query

        // Stop button blinking and hide label animation during submission
        submitButton.classList.remove('blinking');
        formLabel.classList.add('hide-animation');

        let generatedSql = null;
        let rawResultsRecords = null; // Store raw data for charting/humanizing

        try {
            // Stage 1: Generate SQL
            startLoadingAnimation('sql');
            const sqlResponse = await fetch('/api/generate_sql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question }),
            });
            const sqlData = await sqlResponse.json();
            console.log(sqlData);

            if (!sqlResponse.ok) { throw new Error(sqlData.error || 'SQL generation failed.'); }
            generatedSql = sqlData.sql;
            displaySqlCode.textContent = generatedSql; // Show SQL

            // --- FIX: Display the user's question here ---
            displayQuestionP.textContent = question; // Set the user's question
            // --- End FIX ---
            
            stopLoadingAnimation(); startLoadingAnimation('execute'); // Update loading message


            // Stage 2: Execute Query
            const queryResponse = await fetch('/api/execute_query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sql: generatedSql, question: question }), // Pass question for context
            });
            const queryData = await queryResponse.json();
            console.log(queryData);
            

            if (!queryResponse.ok) { throw new Error(queryData.error || 'Query execution failed.'); }
            displayRawResultsDiv.innerHTML = queryData.raw_results_html; // Show raw results HTML
            rawResultsRecords = queryData.raw_results_records; // Store records
            stopLoadingAnimation(); startLoadingAnimation('chart'); // Update loading message


            // Stage 3: Generate Chart
            const chartResponse = await fetch('/api/generate_chart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ raw_results_records: rawResultsRecords, sql: generatedSql, question: question }),
            });
            const chartData = await chartResponse.json();
            console.log(chartData);
            

            if (!chartResponse.ok) { throw new Error(chartData.error || 'Chart generation failed.'); }
            if (chartData.chart_data_json) { // Check if a chart was actually generated
                waitForPlotly(() => { // Wait for Plotly.js to be ready
                    try {
                        const figData = chartData.chart_data_json; 
                        Plotly.newPlot(displayChartDiv, figData.data, figData.layout, {responsive: true});
                        chartsContainerDiv.style.display = 'block'; 
                    } catch (chartRenderError) {
                        console.error('Plotly Render Error:', chartRenderError);
                        displayChartDiv.innerHTML = `<p class="error-message-text">Error rendering chart: ${chartRenderError.message}</p>`;
                        chartsContainerDiv.style.display = 'block';
                    }
                }); 
            } else {
                displayChartDiv.innerHTML = '<p>No suitable chart could be generated for this data.</p>';
                chartsContainerDiv.style.display = 'block';
            }
            stopLoadingAnimation(); startLoadingAnimation('humanize'); // Update loading message


            // Stage 4: Humanize Answer
            const humanizeResponse = await fetch('/api/humanize_answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ raw_results_records: rawResultsRecords, sql: generatedSql, question: question }),
            });
            const humanizeData = await humanizeResponse.json();
            console.log(humanizeData);
            

            if (!humanizeResponse.ok) { throw new Error(humanizeData.error || 'Answer humanization failed.'); }
            typeAnswer('displayAnswer', humanizeData.answer, 20); // Type out the final answer
            stopLoadingAnimation(); 


            resultsContainer.style.display = 'block'; // Show overall results container
            resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (error) {
            console.error('Full process error:', error);
            errorDisplay.textContent = `Error: ${error.message || 'An unexpected error occurred during processing.'} 🚨`;
            errorDisplay.style.display = 'block';
            resultsContainer.style.display = 'none'; // Hide results if whole process failed
        } finally {
            stopLoadingAnimation(); 
            loadingIndicator.style.display = 'none'; 
            if (questionInput.value.trim() === '') {
                formLabel.classList.remove('hide-animation');
            }
        }
    });
});
