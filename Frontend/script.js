const requestButton = document.querySelector('#request-button');
const emptyState = document.querySelector('#empty-state');
const loadingState = document.querySelector('#loading-state');
const answer = document.querySelector('#answer');
const errorState = document.querySelector('#error-state');
const errorMessage = document.querySelector('#error-message');
const responseState = document.querySelector('#response-state');

function showState(state) {
  emptyState.hidden = state !== 'empty';
  loadingState.hidden = state !== 'loading';
  answer.hidden = state !== 'answer';
  errorState.hidden = state !== 'error';
}

async function requestAssessment() {
  requestButton.disabled = true;
  requestButton.classList.add('is-loading');
  responseState.textContent = 'Thinking';
  showState('loading');

  try {
    const response = await fetch('http://127.0.0.1:8000/execute-workflow', {
      method: 'POST',
      headers: { Accept: 'text/plain' }
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}.`);
    }

    const result = await response.text();
    if (!result.trim()) {
      throw new Error('The workflow returned an empty answer.');
    }

    answer.textContent = result;
    responseState.textContent = 'Complete';
    showState('answer');
  } catch (error) {
    errorMessage.textContent = error.message.includes('Failed to fetch')
      ? 'Start the FastAPI service at http://127.0.0.1:8000, then try again.'
      : error.message;
    responseState.textContent = 'Unavailable';
    showState('error');
  } finally {
    requestButton.disabled = false;
    requestButton.classList.remove('is-loading');
  }
}

requestButton.addEventListener('click', requestAssessment);
