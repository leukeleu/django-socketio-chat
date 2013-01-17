# Requests and Responses

Messages starting with `req` are requests sent by a client to the server.
Messages starting with `ev` are events or announcements sent by the server to clients.

Both messages may contain data that is relevant for the receiving party to properly handle the message.

**TODO** USER_SIGNED_IN state expires after 60 seconds?

## Summary

| Events / requests                                | Sent to           | UI (pseudo-code)                      |
| :----------------                                | :------           | :---------------                      |
| `req_user_become_available`                      |                   |                                       |
| `ev_user_became_available(username, users)`      | users that see me | UserList.update(users)                |
| `req_user_become_busy`                           |                   |                                       |
| `ev_user_became_busy(username, users)`           | users that see me | UserList.update(users)                |
| `req_user_become_invisible`                      |                   |                                       |
| `req_user_sign_off`                              |                   | UserList.update(users)                |
| `ev_user_signed_off(username, users)`            | users that see me | UserList.update(users)                |
| `ev_data_update(chat_session, chats, users)`     | signed in user    | new ChatApp()                         |
| `ev_chat_session_status(chat_session)`           | connected user    | show sign-in button                   |
| `req_chat_create(username)`                      |                   |                                       |
| `ev_chat_created(chat)`                          | chat.users        | chats[chat_uuid] = new Chat()         |
| `req_chat_add_user(chat_uuid, username)`         |                   |                                       |
| `ev_chat_you_were_added(chat)`                   | invitee           | chats[chat_uuid] = new Chat()         |
| `ev_chat_user_added(chat_uuid, username, users)` | chat.users        | chats[chat_uuid].set_users(users)     |
| `req_chat_activate(chat_uuid)`                   |                   |                                       |
| `ev_chat_activated(chat_uuid)`                   | chatstatus.user   | chats[chat_uuid].activate()           |
| `req_chat_deactivate(chat_uuid)`                 |                   |                                       |
| `ev_chat_deactivated(chat_uuid)`                 | chatstatus.user   | chats[chat_uuid].deactivate()         |
| `req_chat_archive(chat_uuid)`                    |                   |                                       |
| `ev_chat_archived(chat_uuid)`                    | chatstatus.user   | chats.pop(chat_uuid)                  |
| `req_message_send(message, chat_uuid)`           |                   |                                       |
| `ev_message_sent(message, user_chat_statuses)`   | chat.users        | chats[chat_uuid].add_message(message) |


**Session states**: SIGNED_OFF | AVAILABLE | BUSY | INVISIBLE

## UI

The UI is concists of the classes displayed below.

![UI Classes](http://www.gliffy.com/pubdoc/4232961/L.png)

### REQ: Sign in `req_user_sign_in`

Sign a user in. This makes the user visible to other users, that have permission to *see* the other user.
The server filters the users that others will see, and thus which clients will be notified.

### EV: Signed in `ev_user_signed_in(username, users)`

This  message is sent to any clients that can *see* this user indicating that this user has become available.
The server can send this message after it received `req_sign_in`.
`users` is a new list of all the users that the client receiving this message can see.

### REQ: Sign off `req_user_sign_off`

Sign a user off. This makes the user `unavailable` to other users that have permission to *see* this user.
The user can no longer see chats, nor can he see the availablity of others.

### EV: Signed off `ev_user_signed_off(username, users)`

Sent to all users that can *see* user when this user signs off or goes invisible.
`users` is a new list of all the users that the client receiving this message can see.

### REQ: Go invisible `req_user_invisible`

**Low priority feature**

The same as when signed in, but others will not see this user as available.
This user can still start chats and will also receive new messages.

### EV: Data update `ev_data_update(chat_session, chats, users)`

Reloads all data. Typically sent when a client connects. Server may also decide to resend all data at any time,
the client should build or update the entire UI based on the data.
`chat_session` contains state information about the signed in state of the user.
`chats` are all the non-archived chats for this users including their messages 
`users` are all the users that this user can see.

### EV: Chat session status `ev_chat_session_statusz(chat_session)`
Only sent when a user is logged in , but nog signed in to chat.

### REQ: Create chat `req_chat_create(username)`

Start a new chat with user.
A chat is intially between two users, but others can be invited once the chat is started.

### EV: Chat created `ev_chat_created(chat)`

Sent to all particiapnts in the chat session.
The `chat` is added to the UI by the client.

### REQ Activate chat `req_chat_activate(chat_uuid)`

Activate a chat. Activating can mean, depending on the UI implementation, that a chat is unfolded in the UI and 
messages become visible. This is UI related state stored server-side.

### EV: Chat activated `ev_chat_activated(chat_uuid)`

Sent by server to indicate a chat was activated. The UI may uncollapse the chat.

### REQ: Deactivate chat `req_chat_deactivate(chat_uuid)`

Deactivate a chat. This is the inverse of `req_activate`.

### EV: Chat deactivated `ev_chat_deactivated(chat_uuid)`

Sent by server to indicate a chat was deactivated. The UI may collapse the chat.

### REQ: Archive chat `req_chat_archive(chat_uuid)`

Archive a chat.

Typically the UI will remove the chat from the window. 

Other users can still send messages to this chat. If they do, the chat will become active, resulting in 
the server sending `ev_chat_created(chat)` to all the user that had archived the chat.

The following statediagram applies:

![FSM Archiving](http://www.gliffy.com/pubdoc/4206080/L.png)

If *A*, *B* and *C* are in a chat. *A* leaves and *B* sends a message. *A* gets notified in the same way as he would have been
in case of a new chat, but in this case there's a backlog.

### EV: Chat archived `ev_chat_archived(chat_uuid)`

Sent to the user for which this chat is archived. Other users are not notified of this.

### REQ: send `req_message_send(message_body, chat_uuid)`

The actual chat-message sending.

### EV: message sent `ev_message_sent(message, user_chat_statuses)`

Broadcast to all users in the chat. Sent in response to `req_send`.
`user_chat_statuses` contains chat-window related state info, like the amount of unread messags and active/inactive/archived
state.
