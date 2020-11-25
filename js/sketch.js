const FFT_BIN = 256;

let audio_file;
let audio_file_path = '../src/audio_input/Janice_back.wav'
let amp;
let fft;
let rainbow;
let title_font;
let bar_width;

document.onreadystatechange = () => {
    if (document.readyState === 'complete') {
        let chord_result = localStorage.getItem('chord_result');
        if(chord_result != null)
            document.getElementById('chord_result').innerHTML = chord_result;
    }
};

// MAIN HTML related
let select_file = () =>{
    let file = document.getElementById("audioFile").files[0];
    let lbl = document.getElementById("audioFileLabel");
    lbl.innerHTML = "> ";
    lbl.innerHTML += file.name;
}
let get_chord_ajax = () =>{
    let request = new XMLHttpRequest();
    let data = document.getElementById("audioFile");
    let audio_name = data.files[0].name;
    let formData = new FormData();

    request.onreadystatechange = ()=>{
        if (request.readyState === 4 && request.status === 200){
            handleResult(request.responseText, audio_name);
        }
    }

    formData.append("audioFile", data.files[0]);
    request.open("POST", "http://localhost:5000/detect");
    request.send(formData);
    document.getElementById('submitBtnId').value = "Loading...";
    console.log(request);
}

let handleResult = (chords, audio_name) =>{
    document.getElementById('chord_result').innerHTML = chords;
    localStorage.setItem('audio_name', 'upload_tmp/' + audio_name);
    localStorage.setItem('chord_result', chords);
    location.reload();
    console.log(chords);
}

function preload() {
    let localAudioName = localStorage.getItem('audio_name');
    audio_file_path = (localAudioName === null)?
        '../src/audio_input/Janice_back.wav': localAudioName;
    audio_file = loadSound(audio_file_path, () => {
        console.log("Audio loaded", audio_file);
    });
    rainbow = [
        color('rgb(255,0,0)'),
        color('rgb(255,127,0)'),
        color('rgb(255,255,0)'),
        color('rgb(0,255,0)'),
        color('rgb(0,0,255)'),
        color('rgb(75,0,130)'),
        color('rgb(148,0,211)')
    ];
    title_font = loadFont('../src/font/Symtext.ttf', () => {
        console.log("Font loaded", title_font);
    });
}

function setup() {
    createCanvas(window.innerWidth, window.innerHeight);
    // createCanvas(displayWidth, displayHeight);
    amp = new p5.Amplitude();
    fft = new p5.FFT(0.9, FFT_BIN);
    bar_width = width / FFT_BIN;

    textFont(title_font);
    textSize(width / 30);
    textAlign(CENTER, CENTER);
    audio_file.loop();
}

function draw_title() {
    fill(color('rgba(255, 255, 255)'));
    text('.meachord', width / 1.4, height / 4);
}

function draw_fft() {
    let spectrum = fft.analyze();
    for (let i = 0; i < FFT_BIN; i++) {
        let bar_h = map(spectrum[i], -140, 0, 0, 250);
        c = rainbow[i % rainbow.length];
        c.setAlpha(0.3 * 255);
        fill(c);
        noStroke();
        rect(i * bar_width, height, bar_width, -(height * spectrum[i] / 250))
        // rect(i * bar_width, height, bar_width, bar_h)
    }
}

function draw_wave(){
    let waveform = fft.waveform();
    noFill();
    beginShape();
    stroke(color('rgba(255, 255, 255)'));
    for (let i = 0; i < waveform.length; i++){
        let x = map(i, 0, waveform.length, 0, width);
        let y = map( waveform[i], -1, 1, 0, 100);
        vertex(width - y,x);
    }
    endShape();
}

function draw() {
    clear();
    draw_title();
    draw_fft();
    draw_wave();
}

