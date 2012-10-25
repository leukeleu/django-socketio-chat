var conn = null;
var user = 'anonymous';

Chat = {

    debug_log: function(msg) {
        var control = $('#debug-log');
        var now = new Date();
        var timestamp = ('0' + now.getHours()).slice(-2) + ':' + ('0' + now.getMinutes()).slice(-2) + ':' + ('0' + now.getSeconds()).slice(-2);
        control.html(control.html() + timestamp + ': ' + msg + '<br/>');
        control.scrollTop(control.scrollTop() + 1000);
    },

    chat_log: function(msg) {
        var control = $('#chat-log');
        var now = new Date();
        var timestamp = ('0' + now.getHours()).slice(-2) + ':' + ('0' + now.getMinutes()).slice(-2) + ':' + ('0' + now.getSeconds()).slice(-2);
        control.html(control.html() + timestamp + ': ' + msg + '<br/>');
        control.scrollTop(control.scrollTop() + 1000);
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
            self.update_ui();
        });

        conn.on('message', function(sender, message) {
            self.chat_log(sender + ' says: ' + message);
            self.update_ui();
        });

        conn.on('users', function(data) {
            var chat_users_list = $('#chat-users-list');

            // TODO: store users, then update UI in update_ui()
            chat_users_list.empty();
            $.each(data, function(i, chat_user) {
                if (chat_user.username != user)
                chat_users_list.append('<li>' + chat_user.username + ' (' + (chat_user.online?'online':'offline') + ')</li>');
            });
            self.update_ui();
        });

        conn.on('welcome', function(username) {
            self.debug_log('Received welcome from server.');
            user = username;
            self.update_ui();
        });

        conn.on('user_joined', function(user) {
            self.debug_log(user + ' joined the chat.');
            self.update_ui();
        });

        conn.on('user_left', function(user) {
            self.debug_log(user + ' left the chat.');
            self.update_ui();
        });

        conn.on('disconnect', function(data) {
            self.debug_log('Disconnect');
            conn = null;
            self.update_ui();
        });
    },

    disconnect: function() {
        if (conn !== null) {
            conn.emit('leave');
            conn.disconnect();
            this.debug_log('Disconnected.');
            this.update_ui();
        }
    },

    update_ui: function() {
        if (conn === null || !conn.socket || !conn.socket.connected) {
            $('#toggle-connect').text('Connect');
        } else {
            $('#toggle-connect').text('Disconnect');
        }
    },

    init: function() {
        var self = this;
        self.connect();

        $('#toggle-connect').click(function() {
            if (conn === null) {
                self.connect();
            } else {
                self.disconnect();
            }
            self.update_ui();
            return false;
        });

        $('form#chat-form').submit(function() {
            var text = $('#message').val();
            conn.emit('message', text);
            $('#message').val('').focus();
            return false;
        });
    }
};

$(function() {
    Chat.init();
});
