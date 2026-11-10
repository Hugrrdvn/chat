<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>دردشة جماعية</title>
    <!-- مكتبة Socket.io للاتصال الفوري -->
    <script src="/socket.io/socket.io.js"></script>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: Tahoma, sans-serif;
        }
        body {
            background-color: #f0f2f5;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .chat-container {
            flex: 1;
            display: flex;
            flex-direction: column;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            background: #ffffff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .chat-header {
            background-color: #075e54;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 18px;
            font-weight: bold;
        }
        .chat-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .message {
            background-color: #e2f7cb;
            padding: 10px 15px;
            border-radius: 7px;
            max-width: 70%;
            word-wrap: break-word;
            position: relative;
        }
        .message.incoming {
            background-color: #ffffff;
            border: 1px solid #ddd;
            align-self: flex-start;
        }
        .message.outgoing {
            background-color: #dcf8c6;
            align-self: flex-end;
        }
        .message .username {
            font-size: 11px;
            color: #555;
            margin-bottom: 3px;
            font-weight: bold;
        }
        .chat-input-area {
            display: flex;
            padding: 10px;
            background-color: #f0f0f0;
            border-top: 1px solid #ddd;
        }
        .chat-input-area input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #ccc;
            border-radius: 20px;
            outline: none;
            font-size: 14px;
        }
        .chat-input-area button {
            background-color: #075e54;
            color: white;
            border: none;
            padding: 10px 20px;
            margin-right: 8px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
        }
        .chat-input-area button:hover {
            background-color: #0b6f63;
        }
    </style>
</head>
<body>

    <div class="chat-container">
        <div class="chat-header">جروب تعارف ودردشة</div>
        
        <div id="messages" class="chat-messages">
            <!-- الرسائل تظهر هنا تلقائياً -->
        </div>

        <div class="chat-input-area">
            <input type="text" id="messageInput" placeholder="اكتب رسالتك هنا..." autocomplete="off">
            <button id="sendBtn" onclick="sendMessage()">إرسال</button>
        </div>
    </div>

    <script>
        // الاتصال بخادم السوكيت
        const socket = io();

        // طلب اسم المستخدم عند الدخول (أو تعيين اسم افتراضي)
        let username = prompt("الرجاء إدخال اسمك للرخول إلى الدردشة:") || "مستخدم_" + Math.floor(Math.random() * 1000);

        const messagesContainer = document.getElementById('messages');
        const messageInput = document.getElementById('messageInput');

        // استقبال الرسائل من الخادم وبثها للجميع
        socket.on('chat message', function(data) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message');

            // التمييز بين رسائلك ورسائل الآخرين
            if (data.username === username) {
                messageDiv.classList.add('outgoing');
            } else {
                messageDiv.classList.add('incoming');
            }

            messageDiv.innerHTML = `
                <div class="username">${escapeHtml(data.username)}</div>
                <div class="text">${escapeHtml(data.text)}</div>
            `;

            messagesContainer.appendChild(messageDiv);
            // النزول تلقائياً لأسفل الشات عند وصول رسالة جديدة
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        });

        // دالة إرسال الرسالة
        function sendMessage() {
            const text = messageInput.value.trim();
            if (text !== "") {
                // إرسال البيانات للخادم ليقوم بتوزيعها على الجميع
                socket.emit('chat message', {
                    username: username,
                    text: text
                });
                messageInput.value = "";
                messageInput.focus();
            }
        }

        // إرسال الرسالة عبر الضغط على مفتاح Enter
        messageInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // حماية بسيطة ضد ثغرات XSS
        function escapeHtml(text) {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, function(m) { return map[m]; });
        }
    </script>
</body>
</html>
