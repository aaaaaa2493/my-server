const time_of_life = 150;
const audio_size = 67;

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

let pushOnly = false;
let pullOnly = false;

let infoCount = 0;


$(document).ready(function () {
    filterChange();
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
    if(id === 1000)
        id=0;
    let br = 0;
    let rot = 0;
    let back_fig_anim_time = 2000;
    if(time_of_life < 50)
        back_fig_anim_time=40*time_of_life;
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
    },back_fig_anim_time);
    setTimeout(()=>{$("#displaydiv  div:last").remove();},2000);
    setTimeout(function(){
        if(time_of_life >= 200) {
            $(`#${idl}`).animate({"opacity": "0"}, 1000);
            setTimeout(() => {
                $(`#${idl}`).remove()
            }, 1000);
        }
        else
            $(`#${idl}`).remove();
    },40*time_of_life);

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

function filter_push() {
    $("#eventfield").empty();
    infoCount=0;
    if(pushOnly)
        pushOnly = false;
    else
    {
        pullOnly = false;
        pushOnly = true;
    }
}

function filter_pull() {
    $("#eventfield").empty();
    infoCount=0;
    if(pullOnly)
        pullOnly = false;
    else
    {
        pushOnly = false;
        pullOnly = true;
    }
}

let filter_flags = [];
function filterChange(){
    filter_flags=[];
    let tmp_mass =  $("input:checkbox:checked");
    for ( let key in tmp_mass){
        filter_flags.push(tmp_mass[key].value)
    }
    if(tmp_mass.length===10 && $('.filterMain')[0].checked === false )
        $('.filterMain').prop('checked', true);
    else if (tmp_mass.length!==11)
        $('.filterMain').prop('checked', false);
}

function use_all_filters_flags() {
    if($('.filterMain')[0].checked === true)
        $('.filtercheck').prop('checked', true);
    else
        $('.filtercheck').prop('checked', false);
    filterChange();
}
function add_event(type, jsinfo) {
    $("#eventfield").append(`<div id="one_event"><a href="${jsinfo["url"]}" target="_blank">${jsinfo["repo"]} ${jsinfo["url"]}</div>`);
    $("#eventfield").scrollTop($("#eventfield")[0].scrollHeight);
    createFig(type, jsinfo);
}

function infoonFig(info) {
    let type = Math.floor(Math.random() * (3));
   // $("#back_figure").remove();
    let jsinfo = JSON.parse(info);
    if(filter_flags.indexOf(`${jsinfo['type']}`) > -1) {
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
