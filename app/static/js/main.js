document.addEventListener('DOMContentLoaded', () => {
    const articleList = document.getElementById('article-list');
    const userInput = document.getElementById('user-input');
    const sendInputButton = document.getElementById('send-input');
    const responseContent = document.getElementById('response-content');

    if (sendInputButton) {
        sendInputButton.addEventListener('click', async () => {
            const input = userInput.value;
            if (input.trim() === '') {
                alert('Please enter some input for the agents.');
                return;
            }

            try {
                const response = await fetch('/api/interact', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_input: input }),
                });

                if (response.ok) {
                    const data = await response.json();
                    responseContent.innerHTML = `<p>${data.response}</p>`;
                    userInput.value = '';
                    
                    // Refresh the article list
                    location.reload();
                } else {
                    alert('Error interacting with agents');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('An error occurred while interacting with agents');
            }
        });
    }

    if (articleList) {
        articleList.addEventListener('click', async (e) => {
            if (e.target.classList.contains('delete-article')) {
                const articleId = e.target.dataset.id;
                if (confirm('Are you sure you want to delete this article?')) {
                    const response = await fetch(`/api/article/${articleId}`, {
                        method: 'DELETE',
                    });
                    if (response.ok) {
                        e.target.closest('li').remove();
                    } else {
                        alert('Error deleting article');
                    }
                }
            }
        });
    }
});
