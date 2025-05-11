const messageContainer = document.getElementById('messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');

// Fungsi untuk mendapatkan waktu dalam format jam:menit AM/PM
function getCurrentTime() {
    const now = new Date();
    let hours = now.getHours();
    let minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM'; // Tentukan AM/PM
    hours = hours % 12;
    hours = hours ? hours : 12; // jam 0 harus menjadi 12
    minutes = minutes < 10 ? '0' + minutes : minutes; // Format menit agar selalu dua digit
    return `${hours}:${minutes} ${ampm}`;
}

// Fungsi untuk menambahkan pesan dari pengguna
function addUserMessage(message) {
    const userMessage = document.createElement('div');
    userMessage.classList.add('message', 'user-message');
    userMessage.innerHTML = `
        ${message}
        <span class="time">${getCurrentTime()}</span>
    `;
    messageContainer.appendChild(userMessage);
    scrollToBottom();
}

// Fungsi untuk menambahkan pesan dari bot
function addBotMessage(message) {
    const botMessage = document.createElement('div');
    botMessage.classList.add('message', 'bot-message');
    botMessage.innerHTML = `
        ${message}
        <span class="time">${getCurrentTime()}</span>
    `;
    messageContainer.appendChild(botMessage);
    scrollToBottom();
}

// Fungsi untuk menggulir ke bawah setiap kali pesan baru ditambahkan
function scrollToBottom() {
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

// Fungsi untuk memproses respons kaya (rich response)
function handleRichResponse(response) {
    // Jika response adalah string biasa
    if (typeof response === 'string') {
        const formattedMessage = formatBotMessage(response);
        addBotMessage(formattedMessage);
        return;
    }
    
    // Jika response adalah object (dari Dialogflow yang sudah dimodifikasi)
    if (response.formatted) {
        addBotMessage(response.formatted);
    } else if (response.raw) {
        // Fallback ke raw response jika formatted tidak ada
        const formattedMessage = formatBotMessage(response.raw);
        addBotMessage(formattedMessage);
    }
}

// Fungsi utama untuk menangani respons dari server
async function sendMessage() {
    const message = userInput.value.trim();
    if (message) {
        addUserMessage(message);
        userInput.value = '';
        
        try {
            const response = await fetch('http://localhost:8000/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    user_input: message
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            handleRichResponse(data.response); // Panggil fungsi handler di sini
            
        } catch (error) {
            console.error('Error:', error);
            addBotMessage("Maaf, terjadi kesalahan saat memproses permintaan Anda.");
        }
    }
}

// Update event listener
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Fungsi untuk memformat pesan bot
function formatBotMessage(message) {
    // Biarkan HTML tags tetap utuh
    return message
        .replace(/\n/g, '<br>')
        .replace(/•/g, '•');
}

// Update fungsi addBotMessage
function addBotMessage(message) {
    const botMessage = document.createElement('div');
    botMessage.classList.add('message', 'bot-message');
    botMessage.innerHTML = `
        <div class="chat-message">${message}</div>
        <span class="time">${getCurrentTime()}</span>
    `;
    messageContainer.appendChild(botMessage);
    scrollToBottom();
}