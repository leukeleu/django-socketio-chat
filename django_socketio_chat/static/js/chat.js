var conn = null;
var online_users = [];
var offline_users = [];
var user = 'anonymous';

Chat = {

  log:function(msg) {
    var control = $('#log #modal-collapse');
    date = new Date();
    timestamp =  date.getHours() + ':' +
                 date.getMinutes()+ ':' +
                 date.getSeconds();
    control.html(control.html() + timestamp+ ': ' + msg + '<br/>');
    control.scrollTop(control.scrollTop() + 1000);
  },

  log_private:function(sender, msg) {
    var control = $('#user-' + sender + '.accordion-inner');
    date = new Date();
    timestamp =  date.getHours() + ':' +
                 date.getMinutes()+ ':' +
                 date.getSeconds();
  },

  connect: function() {
    io.j = [];
    io.sockets = [];

    conn = io.connect('https://' + window.location.host + '/chat', {
              'force new connection': true,
              //transports: transports,
              rememberTransport: true,
              resource: 'chat/socket.io'
           });

    this.log('Connecting...');
    
    var self = this;

    conn.on('connect', function() {
      self.log('Connected.');
      self.show_users();
      self.update_ui();
    });

    conn.on('public_message', function(sender, message) {
      self.log(sender + ' says: ' + message);
      self.update_ui();
    });

    conn.on('private_message', function(sender, message) {
      self.log('Private: ' + sender + ' says: ' + message);
      self.update_ui();
    });

    conn.on('users', function(data){
      online_users = data['online'];
      offline_users = data['offline'];
      self.update_ui();
    });
    
    conn.on('welcome', function(user_name){
      self.log('Received welcome from server.');
      user = user_name;
      self.update_ui();
    });

    conn.on('user_joined', function(user){
      self.log(user + ' joined the chat.');
      online_users.push(user);
      offline_users.pop(user);
      self.update_ui();
    });

    conn.on('user_left', function(user){
      self.log(user + ' left the chat.');
      online_users.pop(user);
      offline_users.push(user);
      self.update_ui();
    });

    conn.on('disconnect', function(data) {
      conn = null;
      self.update_ui();
      self.hide_users();
    });
  },

  disconnect: function() {
    if (conn !== null) {
      conn.emit('leave');
      conn.disconnect();
      this.log('Disconnected.');
      this.update_ui();
    }
  },

  show_users: function() {
    $('.online-users').css('display', 'inherit');
    $('.offline-users').css('display', 'inherit');
  },
  
  hide_users: function() {
    $('.online-users').css('display', 'none');
    $('.offline-users').css('display', 'none');
  },

  update_ui: function() {
    var msg = '';

    if (conn === null || !conn.socket || !conn.socket.connected) {
      msg = 'disconnected';
      $('#toggle-connect').text('Connect');
    } else {
      msg = 'connected (' + conn.socket.transport.name + ') as ' + '<b>' + user + '</b>';
      $('#toggle-connect').text('Disconnect');
    }

    $('#status').html(msg);

    function populate(ul, list) {
      ul.html('');
      $.each(list, function() {
        ul.html(ul.html() + '<li>' + this + '</li>');
      });
    }

    populate($('.online-users ul'), online_users);
    populate($('.offline-users ul'), offline_users);
  },

  init: function() {
    var self= this;
    $('#toggle-connect').click(function() {
      if (conn === null) {
        self.connect();
      } else {
        self.disconnect();
      }
      self.update_ui();
      return false;
    });

    $('form.#chatform').submit(function() {
      var text = $('#public-text').val();
      conn.emit('public_message', text);
      $('#public-text').val('').focus();
      return false;
    });

    $('form.#private-chatform').submit(function() {
      var text = $('#private-text').val();
      
      var selected = $('#private-chatform input:checked');
      if (selected.length) {
        target_user = selected[0].getAttribute('val');
        conn.emit('private_message', target_user, text);
      }
      $('#private-text').val('').focus();
      return false;
    });
  }
};