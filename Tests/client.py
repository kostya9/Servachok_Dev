import json
import socket
import struct
import time
import matplotlib.pyplot as plt
import numpy as np


def request(object):
    string = json.dumps(object)
    return struct.pack('i', len(string)) + string.encode('utf-8')


def display(planets):
    """
    only for test
    """
    coords = []

    plt.figure()

    colors = ['red', 'orange', 'brown', 'purple']

    for i in planets:
        position = (i['coords']['x'], i['coords']['y'])
        coords.append(position)

    X = np.array(coords)

    plt.axis("equal")
    plt.xlim((-120 * 16 / 2 - 150, 120 * 16 / 2 + 150))
    plt.ylim((-120 * 9 / 2 - 150, 120 * 9 / 2 + 150))

    t1 = plt.Polygon(X[:2], fill=False, color="black")
    plt.gca().add_patch(t1)

    screen = plt.Rectangle((-120 * 16 / 2, -120 * 9 / 2), 120 * 16, 120 * 9, fill=False,
                           color="black")
    plt.gca().add_patch(screen)
    colors = [colors[i['type'] - 1] for i in planets]

    plt.scatter(X[:, 0], X[:, 1], color=colors)

    plt.show()


client_socket = socket.socket(type=socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 10800))

# time.sleep(5) # for 3 and more players
client_socket.send(request({
    'name': 'ready',
    'ready': True,
}))

while True:
    data_size = client_socket.recv(struct.calcsize('i'))

    if data_size:
        data_size = struct.unpack('i', data_size)[0]
        event = client_socket.recv(data_size)

        if event:
            event = json.loads(event.decode("utf-8"))

            print(event)
            if event['name'] == 'mapinit':
                display(event['map'])
                break
        else:
            client_socket.close()
    else:
        client_socket.close()
