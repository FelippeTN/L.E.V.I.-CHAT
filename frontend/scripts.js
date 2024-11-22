
const base_url = 'http://localhost:8001'; // llama-server

const url = `${base_url}/llama_chat`;

const textarea = document.getElementById('userInput');
const fileInput = document.getElementById('fileInput');
const fileNameSpan = document.getElementById('fileName');
const removeFileIcon = document.getElementById('removeFileIcon');
const webSearchDropdownCheckbox = document.getElementById('webSearchCheckbox');


textarea.addEventListener('input', () => {
    const scrollHeight = textarea.scrollHeight;
    textarea.style.height = `${scrollHeight}px`;
});

document.getElementById('userInput').addEventListener('keydown', function (event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
});

function updateFileName() {
    const file = fileInput.files[0];
    if (file) {
        fileNameSpan.textContent = file.name;
        removeFileIcon.style.display = 'inline';
    } else {
        fileNameSpan.textContent = '';
        removeFileIcon.style.display = 'none';
    }
}

function removeFile() {
    fileInput.value = '';
    fileNameSpan.textContent = '';
    removeFileIcon.style.display = 'none';
}

async function extractTextFromPDF(file) {
    const pdf = await pdfjsLib.getDocument(URL.createObjectURL(file)).promise;
    let text = '';

    for (let i = 0; i < pdf.numPages; i++) {
        const page = await pdf.getPage(i + 1);
        const content = await page.getTextContent();
        text += content.items.map(item => item.str).join(' ');
    }

    return text;
}

async function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    const file = fileInput.files[0];
    const isWebSearchChecked = document.getElementById('webSearchCheckbox').checked;
    let pdfText = '';
    let pdfBase64 = null;

    if (file) {
        pdfText = await extractTextFromPDF(file);
        pdfBase64 = await fileToBase64(file);
    }

    if (!userInput && !pdfText) return;

    appendMessage(userInput || pdfText, 'user');
    document.getElementById('userInput').value = '';
    fileInput.value = ''; // Reset file input
    fileNameSpan.textContent = '';
    removeFileIcon.style.display = 'none';
    textarea.style.height = 'auto'; // Reset height after sending
    
    const requestBody = {
        prompt: userInput,
        pdf_base64: pdfBase64 || undefined,
        pdf_path: pdfText,
        web_search: isWebSearchChecked  // Passa o valor da checkbox
    };

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',

        },
        body: JSON.stringify(requestBody),
    })
    .then(response => response.json())
    .then(data => {
        const botResponse = data.response.response;
        typeMessage(botResponse, 'bot');

        console.log('Links recebidos:', data.links);

        if (data.links && Array.isArray(data.links)) {
            console.log('Links recebidos:', data.links);
            data.links.forEach(link => {
                addConsultedLink(link);
            });
        }
    })
    .catch(error => {
        typeMessage('Error: ' + error, 'bot');
    });
}

function appendMessage(text, sender) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message', sender);
    messageContainer.innerText = text;
    document.getElementById('messages').appendChild(messageContainer);
    scrollToBottom();
}

function typeMessage(text, sender) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message', sender);
    document.getElementById('messages').appendChild(messageContainer);

    let i = 0;
    const typingSpeed = 25; // Typing speed in ms

    function type() {
        if (i < text.length) {
            if (text.charAt(i) === '\n') {
                messageContainer.innerHTML += '<br>'; // Line break for new lines in text
            } else {
                messageContainer.innerHTML += text.charAt(i);
            }
            i++;
            scrollToBottom(); // Update scroll as text is typed
            setTimeout(type, typingSpeed);
        }
    }
    type();
}

function scrollToBottom() {
    const messages = document.getElementById('messages');
    messages.scrollTop = messages.scrollHeight;
}

function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = error => reject(error);
        reader.readAsDataURL(file);
    });
}

// Função para converter texto em fala
function speak(text) {
const utterance = new SpeechSynthesisUtterance(text);
utterance.lang = 'pt-BR';
window.speechSynthesis.speak(utterance);
}

function typeMessage(text, sender) {
const messageContainer = document.createElement('div');
messageContainer.classList.add('message', sender);
document.getElementById('messages').appendChild(messageContainer);

let i = 0;
const typingSpeed = 25; // Velocidade de digitação em ms

function type() {
    if (i < text.length) {
        if (text.charAt(i) === '\n') {
            messageContainer.innerHTML += '<br>'; // Quebra de linha
        } else {
            messageContainer.innerHTML += text.charAt(i);
        }
        i++;
        scrollToBottom(); // Atualizar rolagem conforme digita
        setTimeout(type, typingSpeed);
    } else if (sender === 'bot') {
        // Adicionar o ícone de som após a mensagem ser digitada
        const soundIcon = document.createElement('i');
        soundIcon.className = 'fa-solid fa-volume-high';
        soundIcon.style.cursor = 'pointer';
        soundIcon.style.marginLeft = '10px';
        soundIcon.title = 'Ouvir resposta';
        soundIcon.onclick = () => speak(text);
        messageContainer.appendChild(soundIcon);
    }
}
type();
}

let consultedLinks = [];


function openModal() {
    // Preenche o container de links
    const linksContainer = document.getElementById('linksContainer');
    linksContainer.innerHTML = ''; 
    if (consultedLinks.length > 0) {
        
        consultedLinks.forEach(link => {
            const linkElement = document.createElement('div');
            linkElement.classList.add('link-item');
            linkElement.innerHTML = `<a href="${link}" target="_blank">${link}</a>`;
            linksContainer.appendChild(linkElement);
        });
    } else {
        linksContainer.innerHTML = '<p>Nenhum link consultado ainda.</p>';
    }

    // Exibe o modal
    const modal = document.getElementById('modal');
    modal.style.display = 'block';
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.style.display = 'none';
}



function addConsultedLink(link) {
    if (!consultedLinks.includes(link)) {
        consultedLinks.push(link);
    }
    console.log('Links armazenados:', consultedLinks);
}
function insertDocument() {
    fileInput.click(); 
}

function toggleWebSearch() {
    // Alterna o estado do checkbox
    webSearchDropdownCheckbox.checked = !webSearchDropdownCheckbox.checked;

    const button = document.getElementById('webSearchCheckbox'); 
    button.classList.toggle('pressed', webSearchDropdownCheckbox.checked);
}
