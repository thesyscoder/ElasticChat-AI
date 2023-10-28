// app/static/js/script.js

async function search() {
    const query = document.getElementById('query').value;

    const response = await fetch(`/search?query=${encodeURIComponent(query)}`);
    const data = await response.json();

    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<p>${data.result}</p>`;
}
