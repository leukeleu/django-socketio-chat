var conn = null;

// TODO: get rid of `var self = this;`


Chat = {

    debug_log: function(msg) {
        var $control = $('#debug-log');
        var now = new Date();
        $control.append(now.toLocaleTimeString() + ': ' + msg + '<br/>');
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

        conn.on('ev_chat_session_status', function(chat_session) {
            // Not signed in yet
            self.chat_session = chat_session;
            if (self.chat_session.status == 0) {
               self.ui_signed_off()
            }
        })

        conn.on('ev_data_update', function(chat_session, chat_users, chats) {
            // You are signed in
            self.chat_session = chat_session
            self.ui_signed_in();
            self.update_users_ui(chat_users);
            self.update_chats_ui(chats);
        })

        conn.on('disconnect', function(data) {
            self.debug_log('Disconnect');
            conn = null;
        });

        conn.on('ev_user_signed_in', function(username, chat_users) {
            self.debug_log(username + ' signed in.')
            self.update_users_ui(chat_users);
        });

        conn.on('ev_user_signed_off', function(username, chat_users) {
            self.debug_log(username + ' signed off.')
            self.update_users_ui(chat_users);
        });

        conn.on('ev_chat_created', function(chat) {
            self.update_chats_chat_ui(chat);
        });

        conn.on('ev_message_sent', function(message, user_chat_statuses) {
            self.update_chats_chat_messages_message_ui(message);
            var user_chat_status = self.get_user_chat_status(user_chat_statuses);
            self.ui_chat_set_unread_messages(message.chat__uuid, user_chat_status.unread_messages);
        });

        conn.on('ev_chat_activated', function(chat_uuid) {
            self.ui_chat_activate(chat_uuid);
        });

        conn.on('ev_chat_deactivated', function(chat_uuid) {
            self.ui_chat_deactivate(chat_uuid);
        });

        conn.on('ev_chat_archived', function(chat_uuid) {
            self.ui_chat_archive(chat_uuid);
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

    ui_signed_off: function() {
         var $chat_window = $('#chat-window');
        $chat_window.hide();
        var $chat_session_state = $('#chat-session-state');
        $chat_session_state.html('<h1>Signed off</h1><a id="sign-in" href="#">Sign in</a>');
        $('#sign-in').click(function(e) {
            e.preventDefault();
            conn.emit('req_user_sign_in');
        });

    },

    ui_signed_in: function() {
         var $chat_window = $('#chat-window');
        $chat_window.show();
        var $chat_session_state = $('#chat-session-state');
        $chat_session_state.html('<h1>Signed in</h1><a id="sign-off" href="#">Sign off</a>');
        $('#sign-off').click(function(e) {
            e.preventDefault();
            conn.emit('req_user_sign_off');
        });

    },

    update_users_ui: function(users) {
        var self = this;

        var $user_list = $('#user-list');
        $user_list.empty();

        $.each(users, function(i, user) {
            self.ui_add_user(user);
        });
    },

    ui_add_user: function(user) {
        var self = this;

        var $user_list = $('#user-list');
        var $user_el = $('<li>' + user.username + ' (' + (user.is_online ? 'online' : 'offline') + ')</li>');
        $user_list.append($user_el);
        $user_el.dblclick(function() {
            conn.emit('req_chat_create', user.username);
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
        var chat_usernames = $.map(chat.user_chat_statuses, function(user_chat_status) {
            return user_chat_status.user__username;
            }).join(', ');

        var $chat_el = $('<div id="chat-' + chat.uuid + '">                             \
                         <h4>' + chat_usernames + '<a href="#" class="toggle-active"></a>\
                         <a href="#" class="archive">Archive</a><span class="unread-messages"></span></h4>\
                         </div>');
        var $messages_el = $('<div class="messages"></div>');
        var $message_input_el = $('<div class="message-input">                          \
                                  <textarea placeholder="Type message"></textarea>      \
                                  </div>');

        $chat_el.append($messages_el);
        $chat_el.append($message_input_el);

        var $message_input_textarea = $message_input_el.find('textarea');
        $message_input_textarea.keypress(function(e) {
            if (e.which === 13) { // Enter keycode
                e.preventDefault();
                conn.emit('req_message_send', this.value, chat.uuid);
                // TODO: show spinner, and use ack callback to hide the spinner
                this.value = '';
            }
        });

        var $chat_active_toggle = $chat_el.find('.toggle-active');
        var user_chat_status = self.get_user_chat_status(chat.user_chat_statuses);
        $chat_active_toggle.click(function(e) {
            e.preventDefault();
            if ($chat_active_toggle.hasClass('js_active')) {
                conn.emit('req_chat_deactivate', chat.uuid);
            }
            else {
                conn.emit('req_chat_activate', chat.uuid);
            }
        });

        $chat_el.find('.archive').click( function(e) {
            e.preventDefault();
            conn.emit('req_chat_archive', chat.uuid);
        });

        $chat_list.append($chat_el);
        if (user_chat_status.status == 'active') {
            self.ui_chat_activate(chat.uuid);
        }
        else if (user_chat_status.status == 'inactive') {
            self.ui_chat_deactivate(chat.uuid);
            self.ui_chat_set_unread_messages(chat.uuid, user_chat_status.unread_messages);
        }
        if (chat.messages.length > 0) {
            self.update_chats_chat_messages_ui(chat.messages);
        }
    },

    get_user_chat_status: function(user_chat_statuses) {
        var self = this;
        return  $(user_chat_statuses).filter(function() {
            return this.user__username == self.chat_session.username
        })[0]
    },

    ui_chat_activate: function(chat_uuid) {
        var self = this;
        var chat = $("#chat-" + chat_uuid);
        var toggle = chat.find(".toggle-active");
        toggle.text(' Deactivate');
        toggle.addClass('js_active');
        chat.find('.messages').show();
        chat.find('.message-input').show();
        self.ui_chat_clear_unread_messages(chat_uuid);
    },

    ui_chat_deactivate: function(chat_uuid) {
        var self = this;
        var chat = $("#chat-" + chat_uuid);
        var toggle = chat.find(".toggle-active");
        toggle.text(' Activate');
        toggle.removeClass('js_active');
        chat.find('.messages').hide();
        chat.find('.message-input').hide();
    },

    ui_chat_set_unread_messages: function(chat_uuid, count) {
        var self = this;
        var chat = $("#chat-" + chat_uuid);
        if (count > 0) {
            chat.find('.unread-messages').html(count)
        }
    },

    ui_chat_clear_unread_messages: function(chat_uuid) {
        var self = this;
        var chat = $("#chat-" + chat_uuid);
        chat.find('.unread-messages').html('')
    },

    ui_chat_archive: function(chat_uuid) {
        var self = this;
        var chat = $("#chat-" + chat_uuid)
        chat.remove();
    },

    update_chats_chat_messages_ui: function(messages) {
        var self = this;

        $.each(messages, function(i, message) {
            self.update_chats_chat_messages_message_ui(message);
        });
    },

    update_chats_chat_messages_message_ui: function(message) {
        var self = this;
        var $chat_messages_el = $('#chat-list #chat-' + message.chat__uuid + ' .messages');
        var stamp = function(timestamp) {
            return new Date(timestamp).toLocaleTimeString().slice(0, -3);
        }
        var s = '<div id="message-' + message.uuid + '">' + stamp(message.timestamp) + '    \
        ' + message.user_from__username + ': ' + message.message_body +'</div>';
        $chat_messages_el.append($(s));
    },

    init: function() {
        var self = this;
        self.connect();
    }
};

$(function() {
    Chat.init();
});
