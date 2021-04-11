const root = document.getElementById('root');
const usernameInput = document.getElementById('username');
const button = document.getElementById('join_leave');
const btnSubmit = document.getElementById('btnSubmit');
const btnRec = document.getElementById('btnRec');
const stopVid = document.getElementById('stopVid')
const button_gen = document.getElementById('join_leave_gen');
const speechbutton = document.getElementById('s2t');
// const shareScreen = document.getElementById('share_screen');
// const toggleChat = document.getElementById('toggle_chat');
const cross = document.getElementById('cross');
const container = document.getElementById('container');
const count = document.getElementById('count');
const chatScroll = document.getElementById('chat-scroll');
const chatContent = document.getElementById('chat-content');
const chatInput = document.getElementById('chat-input');
const recordInput = document.getElementById('record-input');

var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition || window.mozSpeechRecognition || window.msSpeechRecognition)();
recognition.lang = 'en-US';
recognition.interimResults = false;
recognition.maxAlternatives = 5;

let connected = false;
let room;
let chat;
let conv;
let screenTrack;

function addLocalVideo() {
    Twilio.Video.createLocalVideoTrack().then(track => {
        let video = document.getElementById('local').firstChild;
        let trackElement = track.attach();
        trackElement.addEventListener('click', () => { zoomTrack(trackElement); });
        video.appendChild(trackElement);
    });
};

function connectButtonHandler() {
    event.preventDefault();
    if (!connected) {
        let username = usernameInput.value;
        if (!username) {
            alert('Enter your name before connecting');
            return;
        }
        if (window.value == 1){ 
            button.disabled = true; 
            button.innerHTML = 'Connecting...'; 
        }   
        else{   
            button_gen.disabled = true; 
            button_gen.innerHTML = 'Connecting...'; 
        }
        connect(username).then(() => {
            document.styleSheets[0].disabled = true;
            var head = document.head;
            if (window.value == 1){
                var link = document.createElement("link");
                link.type = "text/css";
                link.rel = "stylesheet";
                link.href = "static/css/style.css";
                head.appendChild(link);
                
            }
            else{
                var link = document.createElement("link");
                link.type = "text/css";
                link.rel = "stylesheet";
                link.href = "static/css/style-gen.css";
                head.appendChild(link);
            }
            button.innerHTML = "<li class='fa fa-phone'></li> Leave";
            button.disabled = false;
            // shareScreen.disabled = false;
        }).catch(() => {
            alert('Connection failed. Is the backend running?');
            button.innerHTML = "<li class='fa fa-phone'></li> Specially Abled";
            button.disabled = false;
            button_gen.innerHTML = "<li class='fa fa-phone'></li> Abled";
            button_gen.disabled = false;
        });
    }
    else {
        disconnect();
        document.styleSheets[0].disabled = false;
        var elements = document.querySelectorAll('link[rel=stylesheet]');
        elements[3].parentNode.removeChild(elements[3]);
        // button.innerHTML = "<li class='fa fa-phone'></li> Join";
        
        button.innerHTML = "<li class='fa fa-phone'></li>Specially Abled";
        button_gen.innerHTML = "<li class='fa fa-phone'></li> Abled";

        connected = false;
        if (window.value == 1){
            button_gen.disabled=false;
        }
        else{
            button.disabled=false;
        }
        // shareScreen.innerHTML = 'Share screen';
        // shareScreen.disabled = true;
    }
};

function connect(username) {
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
            room = _room;
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
    return promise;
};

function updateParticipantCount() {
    if (!connected)
        count.innerHTML = 'Disconnected.';
    else
        count.innerHTML = (room.participants.size + 1) + ' participants online.';
};

function participantConnected(participant) {
    let participantDiv = document.createElement('div');
    participantDiv.setAttribute('id',participant.identity);
    participantDiv.setAttribute('class', 'participant col-sm-6');

    let tracksDiv = document.createElement('div');
    participantDiv.appendChild(tracksDiv);

    let labelDiv = document.createElement('div');
    labelDiv.setAttribute('class', 'label');
    labelDiv.innerHTML = participant.identity;
    participantDiv.appendChild(labelDiv);

    container.appendChild(participantDiv);

    participant.tracks.forEach(publication => {
        if (publication.isSubscribed)
            trackSubscribed(tracksDiv, publication.track);
    });
    participant.on('trackSubscribed', track => trackSubscribed(tracksDiv, track));
    participant.on('trackUnsubscribed', trackUnsubscribed);

    updateParticipantCount();
};

function participantDisconnected(participant) {
    document.getElementById(participant.sid).remove();
    updateParticipantCount();
};

function trackSubscribed(div, track) {
    let trackElement = track.attach();
    trackElement.addEventListener('click', () => { zoomTrack(trackElement); });
    div.appendChild(trackElement);
};

function trackUnsubscribed(track) {
    track.detach().forEach(element => {
        if (element.classList.contains('participantZoomed')) {
            zoomTrack(element);
        }
        element.remove()
    });
};

function disconnect() {
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
    // toggleChat.disabled = true;
    connected = false;
    updateParticipantCount();
};

// function shareScreenHandler() {
//     event.preventDefault();
//     if (!screenTrack) {
//         navigator.mediaDevices.getDisplayMedia().then(stream => {
//             screenTrack = new Twilio.Video.LocalVideoTrack(stream.getTracks()[0]);
//             room.localParticipant.publishTrack(screenTrack);
//             screenTrack.mediaStreamTrack.onended = () => { shareScreenHandler() };
//             shareScreen.innerHTML = 'Stop sharing';
//         }).catch(() => {
//             alert('Could not share the screen.')
//         });
//     }
//     else {
//         room.localParticipant.unpublishTrack(screenTrack);
//         screenTrack.stop();
//         screenTrack = null;
//         shareScreen.innerHTML = 'Share screen';
//     }
// };

function zoomTrack(trackElement) {
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
};

function connectChat(token, conversationSid) {
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
                    // console.log(message.items[i].body)
                    addMessageToChat(messages.items[i].author, messages.items[i].body);
                }
                // toggleChat.disabled = false;
            });
        });
    }).catch(e => {
        console.log(e);
    });
};

function addMessageToChat(user, message) {
    chatContent.innerHTML += `<p><b>${user}</b>: ${message}`;
    chatScroll.scrollTop = chatScroll.scrollHeight;
}

// function toggleChatHandler() {
//     event.preventDefault();
//     if (root.classList.contains('withChat')) {
//         root.classList.remove('withChat');
//     }
//     else {
//         root.classList.add('withChat');
//         chatScroll.scrollTop = chatScroll.scrollHeight;
//     }
// };

function showvideo(){
    console.log("showvideo")
    let video = document.getElementById('genvid');
    // let video2 = document.getElementById('gen-video');
    // video.setAttribute('src', '/static/video.webm');
    // setTimeout(function(){ alert("Hello"); }, 10000);
    console.log(video)
    let stream = video.captureStream() ? video.captureStream() : video.mozCaptureStream();
    console.log(stream)
    // setTimeout(function(){ alert("Hello"); }, 10000);
    let s = stream.getTracks()
    console.log(s)
    screenTrack = new Twilio.Video.LocalVideoTrack(s[0]);
    console.log(screenTrack)
    room.localParticipant.publishTrack(screenTrack);

    // Twilio.Video.createLocalVideoTr(stream.getTracks()[1]).then(track => {
    //     console.log(track)
    //     let video2 = document.getElementById('show-id').firstChild;
        // let trackElement = screenTrack.attach();
    //     console.log(trackElement)
    //     // trackElement.addEventListener('click', () => { zoomTrack(trackElement); });
        // video2.appendChild(trackElement);
    // });
    // screenTrack.mediaStreamTrack.onended = () => { shareScreenHandler() };
    // shareScreen.innerHTML = 'Stop sharing';  
}

function onChatInputKey(ev) {
    if (ev.keyCode == 13) {
        conv.sendMessage(chatInput.value);
        generation(chatInput.value).then(function(path){
            console.log(path)
            chatInput.value = '';
            // var c = document.getElementById("gen-video");
            // Create an element <video>
            // var v = document.createElement ("video");
            // Set the attributes of the video
            // v.src = `{{ url_for('static', filename="video.mp4")}`;
            // v.controls = true;
            // Add the video to <div>
            // c.appendChild (v);
            let vid = document.getElementById("genvid");
            // vid.pause();
            vid.setAttribute('src', path);
            vid.load();
            setTimeout(function(){ showvideo()}, 5000);
            
            // vid.play();
            
        })
    }
};

function startrec(participant_id){
    let parent = document.getElementById(participant_id).children[0]    
    let leftVideo = parent.children[0].tagName == "VIDEO"? parent.children[0] : parent.children[1]
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
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
                blob = new Blob(recordedChunks, {
                    type: "video/webm"
                });
                var url = URL.createObjectURL(blob);
                var a = document.createElement("a");
                document.body.appendChild(a);
                a.style = "display: none";
                a.href = url;
                a.download = "test.webm";
                a.click();
                window.URL.revokeObjectURL(url);
                recordedChunks=[];
            } else {
                console.log("event.data.size error")
            }
        }
        start.addEventListener('click', (ev)=>{
            mediaRecorder.ondataavailable = handleDataAvailable;
            mediaRecorder.start();

            document.getElementById("change").className = "fa fa-pause";
        })
        stop.addEventListener('click', (ev)=>{
            mediaRecorder.stop();
            document.getElementById("change").className = "fa fa-play";
            document.getElementById("vid2").style.display = "block";
            document.getElementById("cross").style.display = "block";
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
    startrec(nameVal)
};


function recognition(){
    fetch('/recognition', {
        method: 'POST',
    }).then(res => res.json()).then(_data => {
        data = _data;
        console.log(data)
        conv.sendMessage(data.word);
    }).catch(e => {
        console.log(e);
    });
};

function generation(sentence){
    // console.log(sentence)
    // let path = fetch('/generation', {
    //     method: 'POST',
    //     body: JSON.stringify({"sentence": sentence})
    // }).then(res => res.json()).then(_data => {
    //     data = _data;
    //     return data.path
    // }).catch(e => {
    //     console.log(e);
    // });
    // return path
};
function close(){
    document.getElementById("vid2").style.display = "none";
    document.getElementById("cross").style.display = "none";
};
function connectrec(){
    window.value = 1;
    button_gen.disabled=true;
    connectButtonHandler();
};
function connectgen(){
    window.value = 0;
    button.disabled=true;
    connectButtonHandler();
};

function stopVideo(){
    room.localParticipant.unpublishTrack(screenTrack);
    screenTrack.stop();
    screenTrack = null;
}

function startlistening(){
    recognition.start();
    recognition.onresult = function(event) {
        console.log('You said: ', event.results[0][0].transcript);
        document.getElementById("text-display").value = event.results[0][0].transcript;
        generation(event.results[0][0].transcript).then(function(path){
            console.log(path)
            // var c = document.getElementById("gen-video");
            // Create an element <video>
            // var v = document.createElement ("video");
            // Set the attributes of the video
            // v.src = `{{ url_for('static', filename="video.mp4")}`;
            // v.controls = true;
            // Add the video to <div>
            // c.appendChild (v);
            let vid = document.getElementById("genvid");
            // vid.pause();
            vid.setAttribute('src', path);
            vid.load();
            setTimeout(function(){ showvideo()}, 5000);
            
            // vid.play();
        })
    }
}

addLocalVideo();
speechbutton.addEventListener('click', startlistening);
btnSubmit.addEventListener('click',submit);
cross.addEventListener('click',close);
btnRec.addEventListener('click',recognition);
button.addEventListener('click', connectrec);
stopVid.addEventListener('click', stopVideo);
button_gen.addEventListener('click', connectgen);
// shareScreen.addEventListener('click', shareScreenHandler);
// toggleChat.addEventListener('click', toggleChatHandler);
chatInput.addEventListener('keyup', onChatInputKey);
