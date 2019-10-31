const max_count_of_figures = 50;
const animation_time = 2000;
let animation_flag = true;
let last_events_count = 0;
const lag_figures_per_second = 8;

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
let show_icons_on_figures = false;
let infoCount = 0;

let scrolledDown = false;

window.onunload = function(){
    saveStateInCookies();
};

$(document).ready(function () {
    getStateFromCookies();
    $('#displaydiv').css('min-height',$('#displaydiv').height());

    let for_comfort_scroll = 60;
    $('#eventfield').scroll(function(){
        scrolledDown = $(this).scrollTop() >= $('#eventfield')[0].scrollHeight - $('#eventfield').height() - for_comfort_scroll;
    });

    $(document).on('input', '#organization', function(){
        orgChoose();
        $('#organization').removeClass('error_filter_org')
    });

    $(document).on('input', '#repos', function(){
        orgChoose();
        $('#repos').removeClass('error_filter_org')
    });

    orgChoose();
});


setInterval(function(){
    if($(window).width()*0.96>$('#displaydiv').width())
        $('#displaydiv').css('min-width',$(window).width()*0.96);
    if($(window).height()*0.95>$('#displaydiv').height())
        $('#displaydiv').css('min-height',$(window).height()*0.95);
},0);

// for calculating lag
setInterval(() => {
    if(last_events_count > lag_figures_per_second) {
        animation_flag = false;
    }
    else if(last_events_count < lag_figures_per_second) {
        animation_flag = true;
    }
    last_events_count = 0;
}, 1000);


let id=0;

function changecolrs() {
    if(isLight) {
        $('body').css('background-color','#292929');
        $('#displaydiv').css('background-color','#363535');
        $('#VA').css('color', '#ffffff');
        $('#IE').css('color', '#ffffff');
        $('#bar').css('color', '#ffffff');
        $('#OR').css('color', '#ffffff');
        $('#slash').css('color', '#ffffff');
        $('#changecolors').html("Go to Light");
        $('#soundslabel').css('color', '#ffffff');
        $('#selectsound').css('border', '3px solid white');
        $('#selectsound').css('color', '#ffffff');
        $('#selectsound').css('background-color', '#000000');
        $('.optS').css('background-color', '#292929');
        $('#back_figure').css('background-color','#87918F');
        $('#changecolors').removeClass('w3-black').addClass('w3-white');
        $('#navbar').removeClass('navbar-light').addClass('navbar-dark');
        $('#navbar').css('background-color', '#000000');
        $('#eventfield').css('color', '#ffffff');
        isLight = false;
    }
    else{
        $('body').css('background-color','white');
        $('#displaydiv').css('background-color', '#e8e8e7');
        $('#back_figure').css('background-color','#F5F5DC');
        $('#selectsound').css('border', '3px solid black');
        $('#selectsound').css('color', '#000000');
        $('#selectsound').css('background-color', '#ffffff');
        $('.optS').css('background-color', '#ffffff' );
        $('#OR').css('color', '#000000');
        $('#slash').css('color', '#000000');
        $('#VA').css('color', '#000000');
        $('#IE').css('color', '#000000');
        $('#bar').css('color', '#000000');
        $('#soundslabel').css('color', '#000000');
        $('#changecolors').html("Go to Dark");
        $('#changecolors').removeClass('w3-white').addClass('w3-black');
        $('#navbar').removeClass('navbar-dark').addClass('navbar-light');
        $('#navbar').css('background-color', '#ffffff');
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
}

function createFig(type,info) {
    if(audio_files == null) {
        return;
    }
    last_events_count++;

    let rand_array = rands(info);

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
    $("#id01").css('z-index',`${idl+2}`);
    $("#navbar").css('z-index',`${idl+1}`);
    if (show_icons_on_figures)
        $("#displaydiv").prepend(`<div id="back_figure" class="box" style="z-index: ${idl};width:${rand_array[2]}px;
            height:${rand_array[2]}px;border-radius:${br}px;left:${rand_array[0]}px;top:${rand_array[1]}px;
            transform: rotate(${rot}deg);"></div>
            <a href="${info["url"]}" target="_blank" id="${idl}" class="a_figure"  style="z-index: ${idl};width:${rand_array[2]}px;
            height:${rand_array[2]}px;border-radius:${br}px;left:${rand_array[0]}px;top:${rand_array[1]}px;
            transform: rotate(${rot}deg);background-color: ${colors[rand_array[3]]};opacity: 0.9;">
            <p id ="text_figure" style="transform: rotate(${-rot}deg); word-wrap: break-word;
             overflow: hidden;width:${rand_array[2]-10}px;
             max-height:${rand_array[2]-10}px " ><b><img src="../icons/${info['type']}.png" width="25px" height="25px"><br> ${info["repo"]}</b></p></a>`);
    else
        $("#displaydiv").prepend(`<div id="back_figure" class="box" style="z-index: ${idl};width:${rand_array[2]}px;
            height:${rand_array[2]}px;border-radius:${br}px;left:${rand_array[0]}px;top:${rand_array[1]}px;
            transform: rotate(${rot}deg);"></div>
            <a href="${info["url"]}" target="_blank" id="${idl}" class="a_figure"  style="z-index: ${idl};width:${rand_array[2]}px;
            height:${rand_array[2]}px;border-radius:${br}px;left:${rand_array[0]}px;top:${rand_array[1]}px;
            transform: rotate(${rot}deg);background-color: ${colors[rand_array[3]]};opacity: 0.9;">
            <p id ="text_figure" style="transform: rotate(${-rot}deg); word-wrap: break-word;
             overflow: hidden;width:${rand_array[2]-10}px;
             max-height:${rand_array[2]-10}px " ><b>${info["repo"]}</b></p></a>`);
    let animate_time_with_flag = animation_time;
    if(!animation_flag){
        animate_time_with_flag=0;
    }
    let color_obv=increase_brightness(colors[rand_array[3]],50);
    document.getElementById('text_figure').style.color = `${hexToComplimentary(color_obv)}`
    $(`#back_figure`).animate({
        "width": "+=50px",
        "margin-left": "-25px",
        "margin-top": "-25px",
        "border-radius": "+50px",
        "height": "+=50px",
        "opacity": "0"
    }, animate_time_with_flag);
    let id_to_remove = idl - max_count_of_figures;
    setTimeout(()=>{$("#displaydiv  div:last").remove();},animate_time_with_flag);
    $(`#${id_to_remove}`).animate({"opacity": "0"}, animate_time_with_flag);
    setTimeout(() => {
        $(`#${id_to_remove}`).remove()
    }, animate_time_with_flag);
}

function get_curr_category() {
    let select = document.getElementById("selectsound");
    return select.options[select.selectedIndex].value;
}

function rands(info){
    let length = info["repo"].length;
    if (length >= 17)
        length = 17;
    length /= Math.sqrt(2)*0.75;
    let audio_size = audio_files[get_curr_category()];
    let rands_array=[];
    rands_array.push(Math.floor(Math.random() * ($('#displaydiv').width() - 280)+100));
    rands_array.push(Math.floor(Math.random() * ($('#displaydiv').height() - 280)+100));
    rands_array.push(Math.floor(length*6/100 * (180 - 70 + 1)+70));
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

    let filter_json = {type: 'filter_types'};
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
    let filter_json = {type:'filter_types'};
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

function changehovercolor(clas){
    if(!isLight)
        $(`.${clas}`).css('background-color','#333333')
    else
        $(`.${clas}`).css('background-color','#f2f2f2')
}
function changeunhovercolor(clas){
    $(`.${clas}`).css('background-color','inherit')
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
    $("#eventfield").append(`<div id="one_event" class="${id}" onmouseout="changeunhovercolor(${id});" onmousemove="changehovercolor(${id});"><img src="static/github/icons/${jsinfo['type']}.png" width="25px" height="25px"> 
        ${date_string} <a href="${jsinfo["url"]}" 
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

    if(jsinfo['type'] === 'init') {
        audio_files = JSON.parse(jsinfo['categories']);
        for (let i in audio_files) {
            $('#selectsound').append(`<option class=\"optS\" value=\"${i}\">${i}</option>`);
        }
    }
    else if(jsinfo['type'] === 'error') {
        if(jsinfo['where'] === 'owner') {
            document.getElementById('organization').classList.add('error_filter_org');
        }
        else if (jsinfo['where'] === 'repo') {
            document.getElementById('repos').classList.add('error_filter_org');
        }
    }
    else if(filter_flags.indexOf(`${jsinfo['type']}`) > -1)  {
        if (infoCount <= 50) {
            infoCount++;
        } else {
            $("#one_event").remove();
        }

        add_event(type, jsinfo);
    }
}

let cached_sounds = {};

function playSound(index, volume) {
    let category = get_curr_category();
    let file = "static/github/audio/" + category + '/' + index + ".mp3";
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
        $('#OR').css('color', '#ffffff');
        $('#IE').css('color', '#ffffff');
        $('#bar').css('color', '#ffffff');
        $('#OR').css('color', '#ffffff');
        $('#slash').css('color', '#ffffff');
        $('#changecolors').html("Go to Light");
        $('#soundslabel').css('color', '#ffffff');
        $('#selectsound').css('border', '3px solid white');
        $('#selectsound').css('color', '#ffffff');
        $('#selectsound').css('background-color', '#000000');
        $('.optS').css('background-color', '#292929');
        $('#back_figure').css('background-color','#87918F');
        $('#changecolors').removeClass('w3-black').addClass('w3-white');
        $('#navbar').removeClass('navbar-light').addClass('navbar-dark');
        $('#navbar').css('background-color', '#000000');
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
        $('#selectsound').css('border', '3px solid black');
        $('#selectsound').css('color', '#000000');
        $('#selectsound').css('background-color', '#ffffff');
        $('.optS').css('background-color', '#ffffff' );
        $('#VA').css('color', '#000000');
        $('#OR').css('color', '#000000');
        $('#IE').css('color', '#000000');
        $('#bar').css('color', '#000000');
        $('#OR').css('color', '#000000');
        $('#slash').css('color', '#000000');
        $('#soundslabel').css('color', '#000000');
        $('#changecolors').html("Go to Dark");
        $('#changecolors').removeClass('w3-white').addClass('w3-black');
        $('#navbar').removeClass('navbar-dark').addClass('navbar-light');
        $('#navbar').css('background-color', '#ffffff');
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
            if (state == "true" ) {
                filterChange(tmp_mass[key].id[5]);
                if(tmp_mass[key].id[5] == "1") {
                    filterChange(tmp_mass[key].id[5]);
                }
                checkCounter++;
            }
            else{
                $("#" + tmp_mass[key].id).prop('checked', false);
            }
        }
    }

    if(checkCounter == 0) {
        filterChange();
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

function hexToComplimentary(hex){

    // Convert hex to rgb
    var rgb = 'rgb(' + (hex = hex.replace('#', '')).match(new RegExp('(.{' + hex.length/3 + '})', 'g')).map(function(l) { return parseInt(hex.length%2 ? l+l : l, 16); }).join(',') + ')';
    // Get array of RGB values
    rgb = rgb.replace(/[^\d,]/g, '').split(',');
    var r = rgb[0], g = rgb[1], b = rgb[2];
    // Convert RGB to HSL
    r /= 255.0;
    g /= 255.0;
    b /= 255.0;
    var max = Math.max(r, g, b);
    var min = Math.min(r, g, b);
    var h, s, l = (max + min) / 2.0;

    if(max == min) {
        h = s = 0;  //achromatic
    } else {
        var d = max - min;
        s = (l > 0.5 ? d / (2.0 - max - min) : d / (max + min));

        if(max == r && g >= b) {
            h = 1.0472 * (g - b) / d ;
        } else if(max == r && g < b) {
            h = 1.0472 * (g - b) / d + 6.2832;
        } else if(max == g) {
            h = 1.0472 * (b - r) / d + 2.0944;
        } else if(max == b) {
            h = 1.0472 * (r - g) / d + 4.1888;
        }
    }

    h = h / 6.2832 * 360.0 + 0;

    // Shift hue to opposite side of wheel and convert to [0-1] value
    h+= 180;
    if (h > 360) { h -= 360; }
    h /= 360;
    // Convert h s and l values into r g and b values
    if(s === 0){
        r = g = b = l; // achromatic
    } else {
        var hue2rgb = function hue2rgb(p, q, t){
            if(t < 0) t += 1;
            if(t > 1) t -= 1;
            if(t < 1/6) return p + (q - p) * 6 * t;
            if(t < 1/2) return q;
            if(t < 2/3) return p + (q - p) * (2/3 - t) * 6;
            return p;
        };

        var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
        var p = 2 * l - q;

        r = hue2rgb(p, q, h + 1/3);
        g = hue2rgb(p, q, h);
        b = hue2rgb(p, q, h - 1/3);
    }

    r = Math.round(r * 255);
    g = Math.round(g * 255);
    b = Math.round(b * 255);

    // Convert r b and g values to hex
    rgb = b | (g << 8) | (r << 16);
    return "#" + (0x1000000 | rgb).toString(16).substring(1);
}
function increase_brightness(hex, percent){
    // strip the leading # if it's there
    hex = hex.replace(/^\s*#|\s*$/g, '');

    // convert 3 char codes --> 6, e.g. `E0F` --> `EE00FF`
    if(hex.length == 3){
        hex = hex.replace(/(.)/g, '$1$1');
    }

    var r = parseInt(hex.substr(0, 2), 16),
        g = parseInt(hex.substr(2, 2), 16),
        b = parseInt(hex.substr(4, 2), 16);

    return '#' +
        ((0|(1<<8) + r + (256 - r) * percent / 100).toString(16)).substr(1) +
        ((0|(1<<8) + g + (256 - g) * percent / 100).toString(16)).substr(1) +
        ((0|(1<<8) + b + (256 - b) * percent / 100).toString(16)).substr(1);
}