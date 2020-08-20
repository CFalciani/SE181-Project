const WebSocket = require('ws');
const wss = new WebSocket.Server({
    port: 80
});

/* Empty: 0
 *
 * black:
 * pawn: 1
 * left rook: 2
 * right rook: 3
 * knight: 4
 * bishop: 5
 * queen: 6
 * king: 7
 *
 * White:
 * pawn: 8
 * left rook: 9
 * right rook: 10
 * knight: 11
 * bishop: 12
 * queen: 13
 * king: 14
 */

let board = [
    [2, 4, 5, 6, 7, 5, 4, 3],
    [1, 1, 1, 1, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [9, 11, 12, 13, 14, 12, 11, 10]
];

let p1 = {
    connected: false,
    leftrook: false,
    rightrook: false,
    king: false,
    checkHeartbeat: function() {
        p1.hbInterval = setInterval(function() {
            if (Date.now() - p1.lastAlive >= 10000) {
                console.log("P1 lost connection");
                p1.ws.close()
                p1.connected = false;
                clearInterval(p1.hbInterval);
                if (!p2.connected) {
                    delete p1.ip;
                    delete p2.ip;
                    p2.ws.close()
                }
            }
        }, 10000);
    },
    close: function() {
        this.connected = false;
        this.ws.close();
        delete this.ip;
        this.leftrook = false;
        this.rightrook = false;
        this.king = false;
        clearInterval(this.hbInterval);
    }
}
let p2 = {
    connected: false,
    leftrook: false,
    rightrook: false,
    king: false,
    checkHeartbeat: function() {
        p2.hbInterval = setInterval(function() {
            if (Date.now() - p2.lastAlive >= 10000) {
                console.log("P2 lost connection");
                p2.ws.close()
                p2.connected = false;
                clearInterval(p2.hbInterval);
                if (!p1.connected) {
                    delete p2.ip;
                    delete p1.ip;
                    p1.ws.close();
                }
            }
        }, 10000);
    },
    close: function() {
        this.connected = false;
        this.ws.close();
        delete this.ip;
        this.leftrook = false;
        this.rightrook = false;
        this.king = false;
        clearInterval(this.hbInterval);
    }
}

function validate(move) {
    let letter = move.slice(0, 1);
    let num = parseInt(move.slice(1, 2));
    if ('a' > letter || 'h' < letter) {
        return false;
    }
    if (0 > parseInt(num) || 8 < parseInt(num)) {
        return false;
    }
    return true;
}

function processMessage(message) {
    let move = message.split(' ');
    let returnStr = "";
    for (let side of move) {

    }
}

wss.on('connection', function connection(ws, req) {
    let ip = req.connection.remoteAddress.replace(/\D/g, '');
    let player;
    let opponent;
    if (!p1.connected) {
        if (p1.ip && p1.ip != ip) {
            ws.send("Sorry this server is full!");
            ws.close();
        } else {
            p1.ip;
            p1.connected = true;
            p1.ws = ws;
            player = 'p1';
            opponent = 'p2';
            ws.send("Waiting for opponent");
        }
    } else if (!p2.connected) {
        if (p2.ip && p2.ip != ip) {
            ws.send("Sorry this server is full!");
            ws.close();
        } else {
            p2.ip;
            p2.connected = true;
            p2.ws = ws;
            player = 'p2';
            opponent = 'p1';
            ws.send("Connected to opponent You are team: black");
            eval(opponent + '.ws.send("Connected to opponent You are team: white");');
            eval(player + ".checkHeartbeat(); " + opponent + ".checkHeartbeat();");
        }
    } else {
        ws.send("Sorry this server is full!!");
        ws.close();
    }
    ws.on('message', function incoming(message) {
        console.log('received: %s from %s', message, player);
        if (message === "quit") {
            eval(`${opponent}.ws.send("quit");
		  ${player}.close();
		  ${opponent}.close();`);
        } else if (message == "hb") {
            let str = player + ".lastAlive = " + Date.now() + ";";
            eval(str);
        } else {
            eval(opponent + '.ws.send("' + message + '");');
        }
    });
});
