document.getElementById('ping-server').addEventListener('click', async () => {
    const response = await fetch('/ping');
    const data = await response.json();
    document.getElementById('status').textContent = data.message;
});
