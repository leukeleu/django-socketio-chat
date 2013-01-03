var conn = null;

// TODO: get rid of `var self = this;`

Chat = {

    debug_log: function(msg) {
        var $control = $('#debug-log');
        var now = new Date();
        var timestamp = ('0' + now.getHours()).slice(-2) + ':' + ('0' + now.getMinutes()).slice(-2) + ':' + ('0' + now.getSeconds()).slice(-2);
        $control.append(timestamp + ': ' + msg + '<br/>');
    },

    connect: function() {
        io.j = [];
        io.sockets = [];

        var self = this;

        conn = io.connect('https://' + window.location.host, {
            'force new connection': false,
            'rememberTransport': true,
            'resource': 'chat/socket.io'
        });

        self.debug_log('Connecting...');

        conn.on('connect', function() {
            self.debug_log('Connected.');
        });

        // TODO: instead of the username, work with a user object from DRF2 / Tornadio2
        conn.on('welcome', function(username) {
            self.debug_log('Received welcome from server.');
            self.user = username;
        });

        conn.on('user_join', function(user) {
            self.debug_log(user + ' joined the chat.');
        });

        conn.on('user_leave', function(user) {
            self.debug_log(user + ' left the chat.');
        });

        conn.on('disconnect', function(data) {
            self.debug_log('Disconnect');
            conn = null;
        });

        conn.on('user_list', function(users) {
            self.update_users_ui(users);
        });

        conn.on('chat_list', function(chats) {
            self.update_chats_ui(chats);
        });

        conn.on('chat_create', function(chat) {
            self.update_chats_chat_ui(chat);
        });

        conn.on('message_create', function(message) {
            self.update_chats_chat_messages_message_ui(message.chat__uuid, message);
        });
    },

    disconnect: function() {
        var self = this;

        if (conn !== null) {
            conn.emit('leave');
            conn.disconnect();
            self.debug_log('Disconnected.');
            self.update_ui();
        }
    },

    update_ui: function() {
        var self = this;

        // TODO: rebuild the entire UI here when necessary
        // self.update_users_ui(users);
        // self.update_chats_ui(chats);
    },

    update_users_ui: function(users) {
        var self = this;

        var $user_list = $('#user-list');
        $user_list.empty();

        $.each(users, function(i, user) {
            if (user.username !== self.user) {
                self.update_users_user_ui(user);
            }
        });
    },

    update_users_user_ui: function(user) {
        var self = this;

        var $user_list = $('#user-list');
        var $user_el = $('<li>' + user.username + ' (' + (user.is_online ? 'online' : 'offline') + ')</li>');
        $user_list.append($user_el);
        $user_el.dblclick(function() {
            conn.emit('chat_create', [user.username]);
        });
    },

    update_chats_ui: function(chats) {
        var self = this;

        var $chat_list = $('#chat-list');
        $chat_list.empty();

        $.each(chats, function(i, chat) {
            self.update_chats_chat_ui(chat);
        });
    },

    update_chats_chat_ui: function(chat) {
        var self = this;

        var $chat_list = $('#chat-list');
        var chat_usernames = $.map(chat.user_chat_statuses, function(user_chat_status) { return user_chat_status.user__username; }).join(', ');

        var $chat_el = $('<div id="chat-' + chat.uuid + '"><h4>' + chat_usernames + '</h4></div>');
        var $messages_el = $('<div class="messages"></div>');
        var $message_input_el = $('<div class="message-input"><textarea placeholder="Type message"></textarea></div>');

        $chat_el.append($messages_el);
        $chat_el.append($message_input_el);

        var $message_input_textarea = $message_input_el.find('textarea');
        $message_input_textarea.keypress(function(e) {
            if (e.which === 13) { // Enter keycode
                e.preventDefault();
                conn.emit('message_req_create', this.value, chat.uuid);
                // TODO: show spinner, and use ack callback to hide the spinner
                this.value = '';
            }
        });

        $chat_list.append($chat_el);
        if (chat.messages.length > 0) {
            self.update_chats_chat_messages_ui(chat.uuid, chat.messages);
        }
    },

    update_chats_chat_messages_ui: function(chat_uuid, messages) {
        var self = this;

        $.each(messages, function(i, message) {
            self.update_chats_chat_messages_message_ui(chat_uuid, message);
        });
    },

    update_chats_chat_messages_message_ui: function(chat_uuid, message) {
        var self = this;

        var $chat_messages_el = $('#chat-list #chat-' + chat_uuid + ' .messages');
        $chat_messages_el.append($('<div id="message-' + message.uuid + '">' + message.user__username + ': ' + message.message_body + '</div>'));
    },

    init: function() {
        var self = this;
        self.connect();
    }
};

$(function() {
    Chat.init();
});
