$(function () {

    function setUserOnlineOffline(username, status) {
        /* This function enables the client to switch the user connection
        status, allowing to show if an user is connected or not.
        */
        var elem = $("online-stat-" + username);
        if (elem) {
            if (status === 'online') {
                elem.attr("class", "btn btn-success btn-circle");
            } else {
                elem.attr("class", "btn btn-danger btn-circle");
            }
            ;
        }
        ;
    };

    function addNewMessage(message_id) {
        /* This function calls the respective AJAX view, so it will be able to
        load the received message in a proper way.
         */
        $.ajax({
            url: '/messages/receive-message/',
            data: {'message_id': message_id},
            cache: false,
            success: function (data) {
                $(".messages-list").append(data);
                scrollConversationScreen();
            }
        });
    };

    function markSenderReadMessages(sender) {
        $.ajax({
            url: '/messages/mark-read-messages/',
            data: {'sender': sender},
            cache: false,
            success: function (data) {
                var success = data.mark_messages_state
            },
        });
    };

    function updateSenderUnreadMessages(sender) {
        $.ajax({
            url: '/messages/get-unread-messages/',
            data: {'sender': sender},
            cache: false,
            success: function (data) {
                var unreadNum = data.unread_messages
                if (unreadNum != null && unreadNum > 0) {
                    if (unreadNum > 9) {
                        unreadNum = '9+'
                    }
                    $("#new-message-" + sender).text(unreadNum);
                } else {
                    $("#new-message-" + sender).text("");
                }
            },
        });
    };

    function scrollConversationScreen() {
        /* Set focus on the input box from the form, and rolls to show the
        the most recent message.
        */
        var ta = document.getElementById('message-input');
        if (ta) ta.focus();
        $('.messages-list').scrollTop($('.messages-list')[0].scrollHeight);
    }

    // --- Auto-grow textarea ---
    function autoResizeTextarea(el) {
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 160) + 'px';
    }

    const msgInput = document.getElementById('message-input');
    if (msgInput) {
        msgInput.addEventListener('input', function() {
            autoResizeTextarea(this);
        });

        // Enter = send, Shift+Enter = newline
        msgInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                $('#send').trigger('submit');
            }
        });

        // Paste: strip HTML but preserve newlines
        msgInput.addEventListener('paste', function(e) {
            e.preventDefault();
            var text = '';
            if (e.clipboardData) {
                // Prefer plain text; convert HTML line breaks if only HTML available
                text = e.clipboardData.getData('text/plain');
                if (!text) {
                    var html = e.clipboardData.getData('text/html');
                    text = html
                        .replace(/<br\s*\/?>/gi, '\n')
                        .replace(/<\/p>/gi, '\n')
                        .replace(/<[^>]+>/g, '')
                        .replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&nbsp;/g,' ');
                }
            }
            // Insert at cursor position
            var start = this.selectionStart;
            var end   = this.selectionEnd;
            var before = this.value.substring(0, start);
            var after  = this.value.substring(end);
            this.value = before + text + after;
            this.selectionStart = this.selectionEnd = start + text.length;
            autoResizeTextarea(this);
        });
    }

    $("#send").submit(function (e) {
        e.preventDefault();
        
        var form = this;
        var formData = new FormData(form);
        
        $.ajax({
            url: '/messages/send-message/',
            data: formData,
            cache: false,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                if(data.trim() !== '') {
                    $(".messages-list").append(data);
                    // Reset textarea and shrink back to one row
                    var ta = document.getElementById('message-input');
                    ta.value = '';
                    ta.style.height = 'auto';
                    $("#message-image-input").val('');
                    scrollConversationScreen();
                }
            }
        });
        return false;
    });

    // WebSocket connection management block.
    // Correctly decide between ws:// and wss://
    var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
    var ws_path = ws_scheme + '://' + window.location.host + "/" + currentUser + "/";
    var webSocket = new channels.WebSocketBridge();
    webSocket.connect(ws_path);

    window.onbeforeunload = function () {
        // Small function to run instruction just before closing the session.
        payload = {
            "type": "recieve",
            "sender": currentUser,
            "set_status": "offline"
        };
        webSocket.send(payload);
    }

    // Helpful debugging
    webSocket.socket.onopen = function () {
        console.log("Connected to inbox stream");
        // Commenting this block until I find a better way to manage how to
        // report the user status.

        /* payload = {
          "type": "recieve",
          "sender": currentUser,
          "set_status": "online"
        };
        webSocket.send(payload); */
    };

    webSocket.socket.onclose = function () {
        console.log("Disconnected from inbox stream");
    };

    // onmessage management.
    webSocket.listen(function (event) {
        switch (event.key) {
            case "message":
                if (event.sender === activeUser) {
                    addNewMessage(event.message_id);
                    markSenderReadMessages(event.sender);
                } else {
                    updateSenderUnreadMessages(event.sender);
                }
                break;
            case "set_status":
                setUserOnlineOffline(event.sender, event.status);
                break;
            default:
                console.log('error: ', event);
                console.log(typeof (event))
                break;
        }
    });

    // Emoji Picker Logic
    const emojiButton = document.getElementById('emoji-button');
    const emojiPickerContainer = document.getElementById('emoji-picker-container');
    const messageInput = document.getElementById('message-input');

    if (emojiButton && emojiPickerContainer && messageInput) {
        emojiButton.addEventListener('click', (e) => {
            e.preventDefault();
            emojiPickerContainer.classList.toggle('hidden');
        });

        document.querySelector('emoji-picker').addEventListener('emoji-click', event => {
            var ta = document.getElementById('message-input');
            var start = ta.selectionStart;
            var end   = ta.selectionEnd;
            ta.value = ta.value.substring(0, start) + event.detail.unicode + ta.value.substring(end);
            ta.selectionStart = ta.selectionEnd = start + event.detail.unicode.length;
            ta.focus();
            autoResizeTextarea(ta);
            emojiPickerContainer.classList.add('hidden');
        });

        document.addEventListener('click', (event) => {
            if (!emojiButton.contains(event.target) && !emojiPickerContainer.contains(event.target)) {
                emojiPickerContainer.classList.add('hidden');
            }
        });
    }

    // Image Preview Modal Logic
    const imageInput = document.getElementById('message-image-input');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            if (this.files && this.files.length > 0) {
                var reader = new FileReader();
                reader.onload = function(e) {
                    $('#imagePreviewImg').attr('src', e.target.result);
                    $('#imagePreviewCaption').val($('#message-input').val());
                    toggleModal('imagePreviewModal');
                };
                reader.readAsDataURL(this.files[0]);
            }
        });
    }

    window.sendImagePreview = function() {
        var form = document.getElementById('send');
        var formData = new FormData(form);
        formData.set('message', $('#imagePreviewCaption').val());
        
        $.ajax({
            url: '/messages/send-message/',
            data: formData,
            cache: false,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                if(data.trim() !== '') {
                    $(".messages-list").append(data);
                    var ta = document.getElementById('message-input');
                    ta.value = '';
                    ta.style.height = 'auto';
                    $("#message-image-input").val('');
                    toggleModal('imagePreviewModal');
                    scrollConversationScreen();
                }
            }
        });
    };

    let messageToDelete = null;

    window.confirmDeleteMessage = function(messageId) {
        messageToDelete = messageId;
        toggleModal('deleteMessageModal');
    };

    const confirmDeleteBtn = document.getElementById('confirmDeleteMsgBtn');
    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', function() {
            if (!messageToDelete) return;
            var messageId = messageToDelete;
            $.ajax({
                url: '/messages/delete/' + messageId + '/',
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    if (response.status === 'deleted') {
                        let bubble = $('#message-bubble-' + messageId);
                        bubble.empty();
                        bubble.removeClass();
                        bubble.addClass('relative px-3.5 py-2 text-[15px] break-words shadow-sm leading-[1.35] bg-transparent border border-fb-lightBorder/50 dark:border-fb-border/50 text-fb-lightMuted dark:text-fb-muted italic rounded-2xl');
                        bubble.html('<i class="text-[13px]">Message deleted</i>');
                        
                        let reactBadge = $('#reaction-badge-' + messageId);
                        if(reactBadge.length) reactBadge.remove();
                        
                        let actionsMenu = $('#message-container-' + messageId).siblings('.msg-actions');
                        if (actionsMenu.length) actionsMenu.remove();

                        toggleModal('deleteMessageModal');
                        messageToDelete = null;
                    }
                }
            });
        });
    }

    window.reactToMessage = function(messageId, reaction) {
        $.ajax({
            url: '/messages/react/' + messageId + '/',
            type: 'POST',
            data: {
                'reaction': reaction,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                let badge = $('#reaction-badge-' + messageId);
                if (response.reaction) {
                    badge.text(response.reaction);
                    badge.removeClass('hidden');
                } else {
                    badge.addClass('hidden');
                }
                
                let dropdown = document.getElementById('msgReactOptions-' + messageId);
                if(dropdown && !dropdown.classList.contains('hidden')) {
                    toggleDropdown('msgReactOptions-' + messageId);
                }
            }
        });
    };

    // Mute Conversation Logic
    window.muteConversation = function(username) {
        $.ajax({
            url: '/messages/mute/' + username + '/',
            type: 'POST',
            data: {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.status === 'success') {
                    let icon = $('#mute-icon-' + username);
                    let text = $('#mute-text-' + username);
                    if (response.muted) {
                        icon.removeClass('fa-bell').addClass('fa-bell-slash');
                        text.text('Unmute Notifications');
                    } else {
                        icon.removeClass('fa-bell-slash').addClass('fa-bell');
                        text.text('Mute Notifications');
                    }
                    toggleDropdown('userMsgOptions-' + username);
                }
            }
        });
    };

    // Delete Conversation Logic
    let conversationToDelete = null;

    window.confirmDeleteConversation = function(username) {
        conversationToDelete = username;
        toggleModal('deleteConversationModal');
        toggleDropdown('userMsgOptions-' + username);
    };

    const confirmDeleteConvBtn = document.getElementById('confirmDeleteConversationBtn');
    if (confirmDeleteConvBtn) {
        confirmDeleteConvBtn.addEventListener('click', function() {
            if (!conversationToDelete) return;
            var username = conversationToDelete;
            $.ajax({
                url: '/messages/delete-conversation/' + username + '/',
                type: 'POST',
                data: {
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function(response) {
                    if (response.status === 'success') {
                        toggleModal('deleteConversationModal');
                        conversationToDelete = null;
                        if (activeUser === username) {
                            window.location.href = '/messages/';
                        } else {
                            window.location.reload();
                        }
                    }
                }
            });
        });
    }

    // Search Users Logic
    const searchInput = document.getElementById('messenger-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const term = this.value.toLowerCase();
            const users = document.querySelectorAll('.users-list > div');
            
            users.forEach(userDiv => {
                const nameText = userDiv.querySelector('h3') ? userDiv.querySelector('h3').textContent.toLowerCase() : '';
                const usernameText = userDiv.querySelector('p') ? userDiv.querySelector('p').textContent.toLowerCase() : '';
                
                if (nameText.includes(term) || usernameText.includes(term)) {
                    userDiv.style.display = 'flex';
                } else {
                    userDiv.style.display = 'none';
                }
            });
        });
    }

});
