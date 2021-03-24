const root = document.getElementById('root');
const usernameInput = document.getElementById('username');
const button = document.getElementById('join_leave');
const btnSubmit = document.getElementById('btnSubmit');
const shareScreen = document.getElementById('share_screen');
const toggleChat = document.getElementById('toggle_chat');
const container = document.getElementById('container');
const count = document.getElementById('count');
const chatScroll = document.getElementById('chat-scroll');
const chatContent = document.getElementById('chat-content');
const chatInput = document.getElementById('chat-input');
const recordInput = document.getElementById('record-input');

let connected = false;
let room;
let chat;
let conv;
let screenTrack;

function addLocalVideo() {
    console.log("addLocalVideo")
    Twilio.Video.createLocalVideoTrack().then(track => {
        let video = document.getElementById('local').firstChild;
        let trackElement = track.attach();
        trackElement.addEventListener('click', () => { zoomTrack(trackElement); });
        video.appendChild(trackElement);
    });
    console.log("addLocalVideoe")
};

function connectButtonHandler(event) {
    console.log("connectButtonHandler")
    event.preventDefault();
    if (!connected) {
        let username = usernameInput.value;
        if (!username) {
            alert('Enter your name before connecting');
            return;
        }
        button.disabled = true;
        button.innerHTML = 'Connecting...';
        connect(username).then(() => {
            button.innerHTML = 'Leave call';
            button.disabled = false;
            shareScreen.disabled = false;
        }).catch(() => {
            alert('Connection failed. Is the backend running?');
            button.innerHTML = 'Join call';
            button.disabled = false;
        });
    }
    else {
        disconnect();
        button.innerHTML = 'Join call';
        connected = false;
        shareScreen.innerHTML = 'Share screen';
        shareScreen.disabled = true;
    }
    console.log("connectButtonHandlere")
};

function connect(username) {
    console.log("connect")
    let promise = new Promise((resolve, reject) => {
        // get a token from the back end
        let data;
        fetch('/login', {
            method: 'POST',
            body: JSON.stringify({'username': username})
        }).then(res => res.json()).then(_data => {
            // join video call
            data = _data;
            return Twilio.Video.connect(data.token);
        }).then(_room => {
            console.log("room")
            room = _room;
            console.log(room)
            room.participants.forEach(participantConnected);
            room.on('participantConnected', participantConnected);
            room.on('participantDisconnected', participantDisconnected);
            connected = true;
            updateParticipantCount();
            connectChat(data.token, data.conversation_sid);
            resolve();
        }).catch(e => {
            console.log(e);
            reject();
        });
    });
    console.log("connecte")
    return promise;
};

function updateParticipantCount() {
    console.log("updateParticipantCount")
    if (!connected)
        count.innerHTML = 'Disconnected.';
    else
        count.innerHTML = (room.participants.size + 1) + ' participants online.';
    console.log("updateParticipantCounte")
};

function participantConnected(participant) {
    console.log("participantConnected")
    let participantDiv = document.createElement('div');
    participantDiv.setAttribute('id',participant.identity);
    participantDiv.setAttribute('class', 'participant col-sm-5');

    let tracksDiv = document.createElement('div');
    participantDiv.appendChild(tracksDiv);

    let labelDiv = document.createElement('div');
    labelDiv.setAttribute('class', 'label');
    labelDiv.innerHTML = participant.identity;
    participantDiv.appendChild(labelDiv);

    container.appendChild(participantDiv);

    participant.tracks.forEach(publication => {
        console.log(participant)
        if (publication.isSubscribed)
            trackSubscribed(tracksDiv, publication.track);
    });
    participant.on('trackSubscribed', track => trackSubscribed(tracksDiv, track));
    participant.on('trackUnsubscribed', trackUnsubscribed);

    updateParticipantCount();
    console.log("participantConnectede")
};

function participantDisconnected(participant) {
    console.log("participantDisconnected")
    document.getElementById(participant.sid).remove();
    updateParticipantCount();
    console.log("participantDisconnectede")
};

function trackSubscribed(div, track) {
    console.log("trackSubscribed")
    let trackElement = track.attach();
    trackElement.addEventListener('click', () => { zoomTrack(trackElement); });
    div.appendChild(trackElement);
    console.log("trackSubscribede");
};

function trackUnsubscribed(track) {
    console.log("trackUnsubscribed")
    track.detach().forEach(element => {
        if (element.classList.contains('participantZoomed')) {
            zoomTrack(element);
        }
        element.remove()
    });
    console.log("trackUnsubscribede")
};

function disconnect() {
    console.log("disconnect")
    room.disconnect();
    if (chat) {
        chat.shutdown().then(() => {
            conv = null;
            chat = null;
        });
    }
    while (container.lastChild.id != 'local')
        container.removeChild(container.lastChild);
    button.innerHTML = 'Join call';
    if (root.classList.contains('withChat')) {
        root.classList.remove('withChat');
    }
    toggleChat.disabled = true;
    connected = false;
    updateParticipantCount();
    console.log("disconnecte")
};

function shareScreenHandler() {
    event.preventDefault();
    console.log("shareScreenHandler")
    if (!screenTrack) {
        navigator.mediaDevices.getDisplayMedia().then(stream => {
            screenTrack = new Twilio.Video.LocalVideoTrack(stream.getTracks()[0]);
            room.localParticipant.publishTrack(screenTrack);
            screenTrack.mediaStreamTrack.onended = () => { shareScreenHandler() };
            console.log(screenTrack);
            shareScreen.innerHTML = 'Stop sharing';
        }).catch(() => {
            alert('Could not share the screen.')
        });
    }
    else {
        room.localParticipant.unpublishTrack(screenTrack);
        screenTrack.stop();
        screenTrack = null;
        shareScreen.innerHTML = 'Share screen';
    }
    console.log("shareScreenHandlere")
};

function zoomTrack(trackElement) {
    console.log("zoomTrack")
    if (!trackElement.classList.contains('trackZoomed')) {
        // zoom in
        container.childNodes.forEach(participant => {
            if (participant.classList && participant.classList.contains('participant')) {
                let zoomed = false;
                participant.childNodes[0].childNodes.forEach(track => {
                    if (track === trackElement) {
                        track.classList.add('trackZoomed')
                        zoomed = true;
                    }
                });
                if (zoomed) {
                    participant.classList.add('participantZoomed');
                }
                else {
                    participant.classList.add('participantHidden');
                }
            }
        });
    }
    else {
        // zoom out
        container.childNodes.forEach(participant => {
            if (participant.classList && participant.classList.contains('participant')) {
                participant.childNodes[0].childNodes.forEach(track => {
                    if (track === trackElement) {
                        track.classList.remove('trackZoomed');
                    }
                });
                participant.classList.remove('participantZoomed')
                participant.classList.remove('participantHidden')
            }
        });
    }
    console.log("zoomTracke")
};

function connectChat(token, conversationSid) {
    console.log("connectChat")
    return Twilio.Conversations.Client.create(token).then(_chat => {
        chat = _chat;
        return chat.getConversationBySid(conversationSid).then((_conv) => {
            conv = _conv;
            conv.on('messageAdded', (message) => {
                addMessageToChat(message.author, message.body);
            });
            return conv.getMessages().then((messages) => {
                chatContent.innerHTML = '';
                for (let i = 0; i < messages.items.length; i++) {
                    addMessageToChat(messages.items[i].author, messages.items[i].body);
                }
                toggleChat.disabled = false;
            });
        });
    }).catch(e => {
        console.log(e);
    });
};

function addMessageToChat(user, message) {
    console.log("addMessageToChat")
    chatContent.innerHTML += `<p><b>${user}</b>: ${message}`;
    chatScroll.scrollTop = chatScroll.scrollHeight;
    console.log("addMessageToChate")
}

function toggleChatHandler() {
    console.log("toggleChatHandler")
    event.preventDefault();
    if (root.classList.contains('withChat')) {
        root.classList.remove('withChat');
    }
    else {
        root.classList.add('withChat');
        chatScroll.scrollTop = chatScroll.scrollHeight;
    }
    console.log("toggleChatHandlere")
};

function onChatInputKey(ev) {
    console.log("onChatInputKey")
    if (ev.keyCode == 13) {
        conv.sendMessage(chatInput.value);
        chatInput.value = '';
    }
    console.log("onChatInputKeye")
};

function startrec(participant_id){
    console.log("startrec")
    let parent = document.getElementById(participant_id).children[0]    
    let leftVideo = parent.children[0].tagName == "VIDEO"? parent.children[0] : parent.children[1]
    console.log(leftVideo)
    if(leftVideo){
        let stream = leftVideo.captureStream() ? leftVideo.captureStream() : leftVideo.mozCaptureStream();
        let start = document.getElementById('btnStart');
        let stop = document.getElementById('btnStop');
        let vidSave = document.getElementById('vid2');
        var recordedChunks = [];
        var options = { mimeType: "video/webm" };
        var mediaRecorder = new MediaRecorder(stream, options);
        var blob;

        function handleDataAvailable(event) {
            console.log("data-available");
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
                console.log(recordedChunks);
                blob = new Blob(recordedChunks, {
                    type: "video/mp4"
                });
                var url = URL.createObjectURL(blob);
                var a = document.createElement("a");
                document.body.appendChild(a);
                a.style = "display: none";
                console.log(url)
                a.href = url;
                a.download = "test.mp4";
                a.click();
                window.URL.revokeObjectURL(url);
                recordedChunks=[];
                fetch('/recognition', {
                    method: 'POST',
                }).then(res => res.json()).then(_data => {
                    data = _data;
                    console.log(data)
                    btnSubmit.disabled=true
                    start.disabled=true
                    stop.disabled=true
                    alert(data.data);
                }).catch(e => {
                    console.log(e);
                });
            } else {
                console.log("event.data.size error")
            }
        }
        start.addEventListener('click', (ev)=>{
            console.log("start")
            mediaRecorder.ondataavailable = handleDataAvailable;
            mediaRecorder.start();
        })
        stop.addEventListener('click', (ev)=>{
            mediaRecorder.stop();
            document.getElementById("vid2").style.display = "block";
            console.log(mediaRecorder.state);
        });
        mediaRecorder.ondataavailable = function(ev) {
            chunks.push(ev.data);
        }
        mediaRecorder.onstop = (ev)=>{
            let videoURL = window.URL.createObjectURL(blob);
            vidSave.src = videoURL;
        }
    }
};

function submit(){
    let nameVal = recordInput.value.trim();
    console.log(nameVal)
    startrec(nameVal)
};
addLocalVideo();
btnSubmit.addEventListener('click',submit);
button.addEventListener('click', connectButtonHandler);
shareScreen.addEventListener('click', shareScreenHandler);
toggleChat.addEventListener('click', toggleChatHandler);
chatInput.addEventListener('keyup', onChatInputKey);
