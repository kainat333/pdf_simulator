document.addEventListener('DOMContentLoaded', function() {
    const timerDisplay = document.getElementById('timer-display');
    const timerElement = document.getElementById('timer');
    const answerInputs = document.querySelectorAll('input[name="answer"]');
    
    let remainingTime = timeRemaining;
    
    function formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }
    
    function updateTimer() {
        if (remainingTime <= 0) {
            window.location.href = '/submit/';
            return;
        }
        
        timerDisplay.textContent = formatTime(remainingTime);
        
        if (remainingTime <= 300) {
            timerElement.classList.add('warning');
        }
        
        remainingTime--;
    }
    
    updateTimer();
    const timerInterval = setInterval(updateTimer, 1000);
    
    answerInputs.forEach(input => {
        input.addEventListener('change', function() {
            const selectedAnswer = this.value;
            
            fetch('/save-answer/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    question_id: questionId,
                    answer: selectedAnswer
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    console.log('Answer saved successfully');
                }
            })
            .catch(error => {
                console.error('Error saving answer:', error);
            });
        });
    });
    
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
