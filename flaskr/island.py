from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

from flaskr import socketio
from flask_socketio import SocketIO, Namespace, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from flaskr import thread, thread_lock, all_rooms
import pdb

bp = Blueprint('island', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    return render_template('island/test.html', async_mode=socketio.async_mode)

class Room:
    def __init__(self, user, room_id):
        self.owner_id = user['user_id']
        self.room_id = room_id
        self.members = {
            self.owner_id: {
                'name': user['username'],
                'score': 0,
                'location': None,
            },
        }
        self.boxes = []
        self.status = 0 

    def empty(self):
        return len(self.members) == 0

    def add_user(self, user):
        self.members[user['user_id']] = {
            'name': user['username'],
            'score': 0,
            'location': None,
        }

    def leave(self, user_id):
        self.members.remove(user_id)

    def sync(self):
        socketio.emit('room_sync', (self.members, self.boxes), room=self.room_id, namespace='/test')

    def get_boxes(self):
        raise NotImplementedError

    def start_game(self):
        self.boxes = self.get_boxes()
        self.status = 1

    def event_handler(self, msg, user_id):
        raise NotImplementedError


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit('my_response',
                      {'data': 'Server generated event', 'count': count},
                      namespace='/test')
        for room in all_rooms.values():
            room.sync()

class MyNamespace(Namespace):
    def on_my_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']})

    def on_my_broadcast_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']},
             broadcast=True)

    def on_join(self, message):
        join_room(message['room'])
        room_id = message['room']
        if room_id in all_rooms:
            room = all_rooms[room_id]
            room.add_user(session['user'])
        else:
            all_rooms[room_id] = Room(session['user'], room_id)
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms()),
              'count': session['receive_count']})

    def on_leave(self, message):
        leave_room(message['room'])
        room_id = message['room']
        if room_id in all_rooms:
            all_rooms[room_id].leave(session['user']['user_id'])
            if all_rooms[room_id].empty():
                all_rooms.remove(room_id)
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'In rooms: ' + ', '.join(rooms()),
              'count': session['receive_count']})

    # def on_close_room(self, message):
    #     room_id = message['room']
    #     if room_id in all_rooms:
    #         all_rooms[room_id].close()
    #     session['receive_count'] = session.get('receive_count', 0) + 1
    #     emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.',
    #                          'count': session['receive_count']},
    #          room=message['room'])
    #     close_room(message['room'])

    def on_my_room_event(self, message):
        session['receive_count'] = session.get('receive_count', 0) + 1
        room_id = message['room']
        all_rooms[room_id].event_handler(message, session['user']['user_id'])
        emit('my_response',
             {'data': message['data'], 'count': session['receive_count']},
             room=message['room'])

    def on_disconnect_request(self):
        session['receive_count'] = session.get('receive_count', 0) + 1
        emit('my_response',
             {'data': 'Disconnected!', 'count': session['receive_count']})
        disconnect()

    def on_my_ping(self):
        emit('my_pong')

    def on_connect(self):
        user_id = session.get('user_id')
        session['user'] = get_db().user_info.find_one({'user_id': user_id}, {'_id': 0})
        global thread
        with thread_lock:
            if thread is None:
                thread = socketio.start_background_task(background_thread)
        emit('my_response', {'data': 'Connected', 'count': 0})

    def on_disconnect(self):
        print('Client disconnected', request.sid)


socketio.on_namespace(MyNamespace('/test'))


# def get_post(id, check_author=True):
#     """Get a post and its author by id.

#     Checks that the id exists and optionally that the current user is
#     the author.

#     :param id: id of post to get
#     :param check_author: require the current user to be the author
#     :return: the post with author information
#     :raise 404: if a post with the given id doesn't exist
#     :raise 403: if the current user isn't the author
#     """
#     post = get_db().execute(
#         'SELECT p.id, title, body, created, author_id, username'
#         ' FROM post p JOIN user u ON p.author_id = u.id'
#         ' WHERE p.id = ?',
#         (id,)
#     ).fetchone()

#     if post is None:
#         abort(404, "Post id {0} doesn't exist.".format(id))

#     if check_author and post['author_id'] != g.user['id']:
#         abort(403)

#     return post


# @bp.route('/create', methods=('GET', 'POST'))
# @login_required
# def create():
#     """Create a new post for the current user."""
#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'INSERT INTO post (title, body, author_id)'
#                 ' VALUES (?, ?, ?)',
#                 (title, body, g.user['id'])
#             )
#             db.commit()
#             return redirect(url_for('island.index'))

#     return render_template('island/create.html')


# @bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
# def update(id):
#     """Update a post if the current user is the author."""
#     post = get_post(id)

#     if request.method == 'POST':
#         title = request.form['title']
#         body = request.form['body']
#         error = None

#         if not title:
#             error = 'Title is required.'

#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 'UPDATE post SET title = ?, body = ? WHERE id = ?',
#                 (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for('island.index'))

#     return render_template('island/update.html', post=post)


# @bp.route('/<int:id>/delete', methods=('POST',))
# @login_required
# def delete(id):
#     """Delete a post.

#     Ensures that the post exists and that the logged in user is the
#     author of the post.
#     """
#     get_post(id)
#     db = get_db()
#     db.execute('DELETE FROM post WHERE id = ?', (id,))
#     db.commit()
#     return redirect(url_for('island.index'))
