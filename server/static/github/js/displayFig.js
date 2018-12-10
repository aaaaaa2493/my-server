const max_count_of_figures = 20;
const animation_time = 2000;

let colors=["#FFFFCC","#FFFF99","#FFFF66","#FFFF33","#FFFF00","#CCCC00","#FFCC66","#FFCC00","#FFCC33",
    "#CC9933","#996600","#FF9900","#FF9933","#CC9966","#CC6600","#FFCC99","#FF9966","#FF6600",
    "#CC6633","#993300","#FF6633","#CC3300","#FF3300","#FF0000","#CC0000","#990000","#FFCCCC","#FF9999",
    "#FF6666","#FF3333","#FF0033","#CC0033","#CC9999","#CC6666","#CC3333","#993333","#990033","#FF6699",
    "#FF3366","#FF0066","#CC3366","#996666","#663333","#FF99CC","#FF3399","#FF0099","#CC0066","#993366","#660033",
    "#FF66CC","#FF00CC","#FF33CC","#CC6699","#CC0099","#990066","#FFCCFF","#FF99FF","#FF66FF","#FF33FF","#FF00FF",
    "#CC3399","#CC99CC","#CC66CC","#CC00CC","#CC33CC","#990099","#993399","#CC66FF","#CC33FF","#CC00FF","#9900CC",
    "#996699","#660066","#CC99FF","#9933CC","#9933FF","#9900FF","#660099","#663366","#9966CC","#9966FF","#6600CC",
    "#6633CC","#663399","#CCCCFF","#9999FF","#6633FF","#6600FF","#9999CC","#6666FF",
    "#6666CC","#666699","#333399","#333366","#3333FF","#3300FF","#3300CC","#3333CC","#6699FF",
    "#3366FF","#0000FF","#0000CC","#0033CC","#0066FF","#0066CC","#3366CC","#0033FF",
    "#99CCFF","#3399FF","#0099FF","#6699CC","#336699","#006699","#66CCFF","#33CCFF","#00CCFF","#3399CC","#0099CC",
    "#99CCCC","#66CCCC","#339999","#669999","#006666","#336666","#CCFFFF","#99FFFF","#66FFFF","#33FFFF",
    "#00FFFF","#00CCCC","#99FFCC","#66FFCC","#33FFCC","#00FFCC","#33CCCC","#009999","#66CC99","#33CC99","#00CC99",
    "#339966","#009966","#006633","#66FF99","#33FF99","#00FF99","#33CC66","#00CC66","#009933","#99FF99","#66FF66",
    "#33FF66","#00FF66","#339933","#006600","#CCFFCC","#99CC99","#66CC66","#669966","#336633","#33FF33",
    "#00FF33","#00FF00","#00CC00","#33CC33","#00CC33","#66FF00","#66FF33","#33FF00","#33CC00","#339900","#009900",
    "#CCFF99","#99FF66","#66CC00","#66CC33","#669933","#336600","#99FF00","#99FF33","#99CC66","#99CC00","#99CC33",
    "#669900","#CCFF66","#CCFF00","#CCFF33","#CCCC99","#CCCC66","#CCCC33","#999933",
    "#999900"];

let isLight = true;
let infoCount = 0;

let scrolledDown = false;

window.onunload = function(){
    saveStateInCookies();
}

$(document).ready(function () {
    getStateFromCookies();
    let for_comfort_scroll = 60;
    $('#eventfield').scroll(function(){
        scrolledDown = $(this).scrollTop() >= $('#eventfield')[0].scrollHeight - $('#eventfield').height() - for_comfort_scroll;
    });

    $('#changecolors').click(function () {
        if(isLight) {
            $('body').css('background-color','#292929');
            $('#displaydiv').css('background-color','#363535');
            $('#VA').css('color', '#ffffff');
            $('#IE').css('color', '#ffffff');
            $('#bar').css('color', '#ffffff');
            $('#changecolors').html("Go to Light");
            $('#back_figure').css('background-color','#87918F');
            $('#changecolors').removeClass('w3-black').addClass('w3-white');
            $('#eventfield').css('color', '#ffffff');
            isLight = false;
        }
        else{
            $('body').css('background-color','white');
            $('#displaydiv').css('background-color', '#e8e8e7');
            $('#back_figure').css('background-color','#F5F5DC');
            $('#VA').css('color', '#000000');
            $('#IE').css('color', '#000000');
            $('#bar').css('color', '#000000');
            $('#changecolors').html("Go to Dark");
            $('#changecolors').removeClass('w3-white').addClass('w3-black');
            $('#eventfield').css('color', '#000000');

            isLight = true;
        }
        for (let i=0; i<11; i++){
            let button = $('#filt_' + i);
            if (button.hasClass('w3-white'))
                button.removeClass('w3-white').addClass('black');
            else
                button.removeClass('black').addClass('w3-white');
        }
    });
});
setInterval(function(){
    if($(window).width()>$('#displaydiv').width())
        $('#displaydiv').css('min-width',$(window).width()*0.96);
    if($(window).height()>$('#displaydiv').height())
        $('#displaydiv').css('min-height',$(window).height()-55+'px');
},0);
let id=0;


function createFig(type,info) {
    let rand_array = rands();

    playSound(rand_array[4], $('#volinp').val()/100);

    let idl=id++;
    let br = 0;
    let rot = 0;
    if(type === 0){
        br = rand_array[2]/2;
    }
    else if(type === 1){
        rot = 45;
    }
    $("#displaydiv").prepend(`<div id="back_figure" class="box" style="z-index: ${idl-1};width:${rand_array[2]}px;
        height:${rand_array[2]}px;border-radius:${br}px;left:${rand_array[0]}px;top:${rand_array[1]}px;
        transform: rotate(${rot}deg);"></div>
        <a href="${info["url"]}" target="_blank" id="${idl}" class="a_figure"  style="z-index: ${idl};width:${rand_array[2]}px;
        height:${rand_array[2]}px;border-radius:${br}px;left:${rand_array[0]}px;top:${rand_array[1]}px;
        transform: rotate(${rot}deg);background-color: ${colors[rand_array[3]]};opacity: 0.9;">
        <p id ="text_figure" style="transform: rotate(${-rot}deg)">${info["repo"]}</p></a>`);
    $(`#back_figure`).animate({
        "width": "+=50px",
        "margin-left":"-25px",
        "margin-top":"-25px",
        "border-radius":"+50px",
        "height":"+=50px",
        "opacity":"0"
    },animation_time);
    let id_to_remove = idl - max_count_of_figures;
    setTimeout(()=>{$("#displaydiv  div:last").remove();},animation_time);
    $(`#${id_to_remove}`).animate({"opacity": "0"}, animation_time);
    setTimeout(() => {
        $(`#${id_to_remove}`).remove()
    }, animation_time);
}


function rands(){
    let rands_array=[];
    rands_array.push(Math.floor(Math.random() * ($('#displaydiv').width() - 250)+100));
    rands_array.push(Math.floor(Math.random() * ($('#displaydiv').height() - 250)+100));
    rands_array.push(Math.floor(Math.random() * (150 - 40 + 1)+40));
    rands_array.push(Math.floor(Math.random() * (colors.length)));
    rands_array.push(Math.floor(Math.random() * audio_size));
    return rands_array;
}

let filter_flags = [];
function filterChange(id){
    filter_flags=[];
    let button = $('#filt_' + id);
    if (button.hasClass('w3-white')) {
        button.removeClass('w3-white').addClass('black');
    }
    else {
        button.removeClass('black').addClass('w3-white');
    }

    let filter_json = {type: 'filter'};
    for (let i = 1; i <= 9; i++) {
        let button = $('#filt_' + i);
        if (button.hasClass('w3-white'))
            filter_json[button.val()] = !isLight;
        else
            filter_json[button.val()] = isLight;
        if(filter_json[button.val()]===true) {
            filter_flags.push(button.val());
        }
    }
    button = $('#filt_0');
    if(filter_flags.length===9) {
        button = $('#filt_0');
        if (button.hasClass('w3-white') && isLight) {
            button.removeClass('w3-white').addClass('black');
        }
        else if (button.hasClass('black') )
            button.removeClass('black').addClass('w3-white');
    }
    else if (filter_flags.length!==9){
        if(button.hasClass('w3-white') && !isLight){
            button.removeClass('w3-white').addClass('black');
        }
        else if(button.hasClass('black') && isLight)
            button.removeClass('black').addClass('w3-white');
    }
    filterChoose(filter_json);
}

function use_all_filters_flags() {
    let filter_json = {type:'filter'};
    filter_flags=[];
    if($('#filt_0').hasClass('w3-white')){
        $('#filt_0').removeClass('w3-white').addClass('black');
    }
    else if($('#filt_0').hasClass('black'))
        $('#filt_0').removeClass('black').addClass('w3-white');
    for (let i = 1; i <= 9; i++){
        let button = $('#filt_' + i);
        if($('#filt_0').hasClass('w3-white')!==isLight) {
            filter_flags.push(button.val());
            if (button.hasClass('w3-white') && !isLight) {
                button.removeClass('w3-white').addClass('black');
            }
            else if (button.hasClass('black') && isLight) {
                button.removeClass('black').addClass('w3-white');
            }
        }
        if (button.hasClass('w3-white')) {
            button.removeClass('w3-white').addClass('black');
        }
        else {
            button.removeClass('black').addClass('w3-white');
        }
        filter_json[button.val()] = true;
    }
    filterChoose(filter_json);
}

function add_event(type, jsinfo) {
    let date = new Date();
    let year = date.getFullYear();
    let month = date.getMonth() + 1;
    let day = date.getDate();
    let hours = date.getHours();
    let minutes = date.getMinutes();
    if (minutes < 10)
        minutes = '0' + minutes;
    let seconds = date.getSeconds();
    if (seconds < 10)
        seconds = '0' + seconds;
    let date_string = year + '-' + month + '-' + day + '  ' + hours + ':' + minutes + ':' + seconds + ' - ';
    $("#eventfield").append(`<div id="one_event">${date_string}${jsinfo["type"]} - <a href="${jsinfo["url"]}" 
    target="_blank">${jsinfo["owner"]} / ${jsinfo["repo"]}</div>`);
    if (scrolledDown)
        $("#eventfield").scrollTop($("#eventfield")[0].scrollHeight);
    createFig(type, jsinfo);
}

function infoonFig(info) {
    let type = Math.floor(Math.random() * (3));
   // $("#back_figure").remove();
   // alert(info +' '+ filter_flags);
    let jsinfo = JSON.parse(info);

    if(jsinfo['type']==='error'){
        if(jsinfo['where'][0].length === 3){
            document.getElementById('organization').classList.add('error_filter_org');
            document.getElementById('repos').classList.add('error_filter_org');
        }
        else if(jsinfo['where'] === 'org'){
            document.getElementById('organization').classList.add('error_filter_org');
        }
        else
            document.getElementById('repos').classList.add('error_filter_org');
    }
    else if(filter_flags.indexOf(`${jsinfo['type']}`) > -1) {
        if (infoCount <= 50) {
            add_event(type, jsinfo);
            infoCount++;
        } else {
            $("#one_event").remove();
            add_event(type, jsinfo);
        }
    }
}

let cached_sounds = {};

function playSound(index, volume) {
    let file = "static/github/audio/" + (index+1) + ".mp3";
    if(file in cached_sounds){
        cached_sounds[file].volume(volume);
        cached_sounds[file].play();
    }
    else{
        let a = new Howl({
            src: [file],
            volume: volume
        });
        a.play();
        cached_sounds[file] = a;
    }
}

function setCookie(name,value,days = 1) {
    let expires = '';
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = '; expires='+ date.toUTCString();
    }
    document.cookie = name + '=' + value + expires + '; path=/';
}

function getCookie(name) {
    let nameEQ = name + '=';
    let ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0)=== ' '){
            c = c.substring(1, c.length);
        }
        if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}

function  deleteCookie(name) {
    setCookie(name, '', -1);
}



function saveStateInCookies() {
    setCookie("isLight", isLight);
    setCookie("volume", $("#volinp").val());
    setCookie("organization", $("#organization").val());
    setCookie("repos", $("#repos").val());
    let tmp_mass =  $("input:image");

    for ( let key in tmp_mass){
        let black = $( "#"+tmp_mass[key].id ).hasClass( "black" );
        let white = $( "#"+tmp_mass[key].id ).hasClass( "w3-white" );
        let checked = isLight ? black : white;

        setCookie(tmp_mass[key].id, checked);
    }
}

function getStateFromCookies() {


    let isL = getCookie("isLight");
    let vol = getCookie('volume');
    let organization = getCookie('organization');
    let repos = getCookie('repos');
    let tmp_mass = $("input:image");

    if(isL == "false") {
        $('body').css('background-color','#292929');
        $('#displaydiv').css('background-color','#363535');
        $('#VA').css('color', '#ffffff');
        $('#IE').css('color', '#ffffff');
        $('#bar').css('color', '#ffffff');
        $('#changecolors').html("Go to Light");
        $('#back_figure').css('background-color','#87918F');
        $('#changecolors').removeClass('w3-black').addClass('w3-white');
        $('#eventfield').css('color', '#ffffff');
        isLight = false;
        for (let i=0; i<11; i++){
            let button = $('#filt_' + i);
            if (button.hasClass('w3-white'))
                button.removeClass('w3-white').addClass('black');
            else
                button.removeClass('black').addClass('w3-white');
        }
    }
    else{
        $('body').css('background-color','white');
        $('#displaydiv').css('background-color', '#e8e8e7');
        $('#back_figure').css('background-color','#F5F5DC');
        $('#VA').css('color', '#000000');
        $('#IE').css('color', '#000000');
        $('#bar').css('color', '#000000');
        $('#changecolors').html("Go to Dark");
        $('#changecolors').removeClass('w3-white').addClass('w3-black');
        $('#eventfield').css('color', '#000000');

        isLight = true;
    }


    let numVol = Number(vol) >= 0;

    if(vol !== undefined && numVol >= 0 && numVol<=100 ) {
        $("#volinp").val(vol);
    }

    else{
        removeCookiesWithSettings();
        return;
    }

    if(organization !== undefined && repos !== undefined) {
        $("#organization").val(organization);
        $("#repos").val(repos);
    }
    let checkCounter = 0;
  
    filterChange('1');

    if(getCookie("filt_0") == "true") {

        use_all_filters_flags();

        if (isL == "true") {
            $('#filt_0').removeClass('w3-white').addClass('black');
        }
        else {
            $('#filt_0').removeClass('black').addClass('w3-white');
        }
        return;
    }


    for ( let key in tmp_mass){
        let state = getCookie(tmp_mass[key].id+"");

        if(state !== undefined ){
            if (state == "true") {
               // let black = $( "#"+tmp_mass[key].id ).hasClass( "black" );
                filterChange(tmp_mass[key].id[5])
                //$("#" + tmp_mass[key].id).prop('checked', true);
                checkCounter++;
            }
            else{
                $("#" + tmp_mass[key].id).prop('checked', false);
            }
        }
    }

    if(checkCounter == 0) {
        filterChange('1');
        removeCookiesWithSettings()
    }


}

function removeCookiesWithSettings() {
    deleteCookie("isLight");
    deleteCookie('volume');
    deleteCookie('organization');
    deleteCookie('repos');
    let tmp_mass = $("input:image");

    for (let key in tmp_mass) {
        deleteCookie(tmp_mass[key].id + "");
    }

    $("#volinp").val(20);
    $("#1").prop('checked', true);
}