# Requests and Responses

Messages starting with `req` are requests sent by a client to the server.
Messages starting with `ev` are events or announcements sent by the server to clients.

Both messages may contain data that is relevant for the receiving party to properly handle the message.

**TODO** USER_SIGNED_IN state expires after 60 seconds?

## Summary

| Events                                | Sent to         | Requests                          | UI (pseudo-code)               |
| :-------                              | ---             | :-------                          | -----------                    |
|                                       |                 | `req_user_sign_in`                |                                |
|                                       |                 | `req_user_sign_off`               |                                |
|                                       |                 | `req_user_invisible`              |                                |
| `ev_user_signed_in(user)`             | all 'friends'   |                                   | users[username] = user         |
| `ev_data_update(chats, users)`        | signed in user  |                                   | build or update entire UI      |
| `ev_user_signed_off(user)`            | all 'friends'   |                                   | users.pop(username)            |
|                                       |                 | `req_chat_create(user)`           |                                |
| `ev_chat_created(chat)`               | chat.users      |                                   | chats.append(chat)             |
|                                       |                 | `req_chat_add_user(chat, user)`   |                                |
| `ev_chat_you_were_added(chat)`        | new_user        |                                   | chats.append(chat)             |
| `ev_chat_user_added(chat_uuid, user)` | chat.users      |                                   | chats[chat].append(user)       |
|                                       |                 | `req_chat_activate(chat)`         |                                |
| `ev_chat_activated(chat)`             | chatstatus.user |                                   | uncollapse(chat)               |
|                                       |                 | `req_chat_deactivate(chat)`         |                                |
| `ev_chat_deactivated(chat)`           | chatstatus.user |                                   | collapse(chat)                 |
|                                       |                 | `req_chat_archive(chat)`          |                                |
| `ev_chat_archived(chat)`              | chatstatus.user |                                   | chats.pop(chat)                |
| `ev_user_left_chat(user)`             | other users     |                                   | chats[chat].users.pop(user)    |
|                                       |                 | `req_message_send(chat_uuid, message)` |                                |
| `ev_message_sent(chat_uuid, message)`      | chat.users      |                                   | chats.messages.append(message) |


## REQ: Sign in `req_user_sign_in`

Sign a user in. This makes the user visible to other users, that have permission to `see` the other user.
The server filters the users that others will see, and thus which clients will be notified.

## REQ: Sign off `req_user_sign_off`

Sign a user off. This makes the user `unavailable` to other users that have permission to `see` this user.
The user can no longer see chats, nor can he see the availablity of others.

## REQ: Go invisible `req_user_invisible`

**Low priority feature**

The same as when signed in, but others will not see this user as available.
This user can still start chats and will also receive new messages.

## EV: Signed in `ev_user_signed_in(user)`

This is a message sent to any clients that can `see` this user indicating that this user has become available.
The server can send this message after it received `req_sign_in`, but it is not an answer nor an acknowledgement.

## EV: Data update `ev_data_update(chats, users)`

Reloads all data. Typically sent when a client connects. Server may also decide to resend all data at any time,
the client should build or update the entire UI based on the data.

## EV: Signed off `ev_user_signed_off(user)`

Sent to all users that can `see` user when this user signs off or goes invisible.

## REQ: Create chat `req_chat_create(user)`

Start a new chat with user.

Server checks if the user sending the request `sees` `user`. If not, the `req` is ignored.
A chat is intially between two users, but others can be invited once the chat is started.

## EV: Chat created `ev_chat_created(chat)`

Sent to all particiapnts in the chat session.

## REQ Activate chat `req_chat_activate(chat)`

Activate a chat. Activating can mean, depending on the UI implementation, that a chat is unfolded in the UI and 
messages become visible. This is UI related state stored server-side.

## EV: Chat activated `ev_chat_activated(chat)`

Sent by server to indicate a chat was activated. The UI may uncollapse the chat.

## REQ: Deactivate chat `req_chat_deactivate(chat)`

Deactivate a chat. This is the inverse of `req_activate`.

## EV: Chat deactivated `ev_chat_deactivated(chat)`

Sent by server to indicate a chat was deactivated. The UI may collapse the chat.

## REQ: Archive chat `req_chat_archive(chat)`

Archive a chat.

Typically the UI will remove the chat from the window. 

Other users will be notified with an event `ev_user_left_chat(chat, user)`

Other users can still send messages to this chat.If they do, the chat will become inactive, resulting in 
the server sending `ev_chat_deactivated(chat)`.

The following statediagram applies:

![FSM Archiving](http://www.gliffy.com/pubdoc/4206080/L.png)

If *A*, *B* and *C* are in a chat. *A* leaves and *B* sends a message. *A* gets notified in the same way as he would have been
in case of a new chat, but in this case there's a backlog.

## EV: Chat archived `ev_chat_archived(chat)`

Sent to the user for which this chat is archived. Server must send `ev_user_left_chat` to other users in the chat.

## EV: User left chat `ev_user_left_chat(user)`

Sent to notify other users that a user archived a chat.

## REQ: send `req_message_send(chat, message)`

The actual chat-message sending.

## EV: message sent `ev_message_sent(chat, message)`

Sent by server to users in the chat. Sent in response to `req_send`. Server must check sendig user is actually in the chat.
