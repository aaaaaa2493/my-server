var camera, scene, renderer, cube3D;
var interval, n = 0;
var planeSize = 50;
var scrambleLen = 20;

var loadercount = 0;

var defaultCameraZ = 400;
var defaultCameraX = 200;
var defaultCameraY = 200;

var texture = {};

var xv = new THREE.Vector3(1,0,0);
var yv = new THREE.Vector3(0,1,0);
var zv = new THREE.Vector3(0,0,1);

var colors = {
    white:  0xffffff,
    blue:   0x0022ee,
    orange: 0xee7700,
    green:  0x11ee11,
    red:    0xee2200,
    yellow: 0xeeee11,
    gray:   0x333333
};

var saverotates = [], repeatrotates = [], rrindex = 0;
var isScrambled = false;

var innerPlane;

function openrepeattab(){
    document.getElementById('solve').style.display = 'none';
    document.getElementById('repeat').style.display = 'block';

    document.getElementById('tosolve').classList.remove('chosen');
    document.getElementById('torepeat').classList.add('chosen');

    document.getElementById('cube2').appendChild(renderer.domElement);
    repeatrotates = [];
    for(var i = 0; i < saverotates.length; i++){
        repeatrotates.push(saverotates[i]);
    }
    rrindex = repeatrotates.length - 1;


    scr = '';
    for(var i = saverotates.length - 1; i >= 0; i--){

        var p = saverotates[i];

        if(p == 'd' || p == 't' || p == 'l' || p == 'r'){

            if(p == 't')p = 'd';
            else if(p == 'b')p = 'u';
            else if(p == 'l')p = 'r';
            else if(p == 'r')p = 'l';

        }
        else{
            if(p.length == 2)p = p[0];
            else p += '\''
        }

        if(rrindex == i){
            p = '<u>' + p + '</u>'
        }


        scr += p + ' ';
    }

    document.getElementById('repeatscramble').innerHTML = scr;
}

function opensolvetab(){
    document.getElementById('repeat').style.display = 'none';
    document.getElementById('solve').style.display = 'block';

    document.getElementById('torepeat').classList.remove('chosen');
    document.getElementById('tosolve').classList.add('chosen');

    document.getElementById('cube').appendChild(renderer.domElement);
}

window.onload = function() {
    // instantiate a loader
    var loader = new THREE.TextureLoader();

    // load a resource
    loader.load(
        // resource URL
        '/img/rubiks/colors/white.png',
        // Function when resource is loaded
        function ( texture1 ) {
            texture.white = texture1;
            if(++loadercount == 7){
                init();
                animate();
            }
        },
        // Function called when download progresses
        function ( xhr ) {
            console.log( (xhr.loaded / xhr.total * 100) + '% loaded' );
        },
        // Function called when download errors
        function ( xhr ) {
            console.log( 'An error happened' );
        }
    );

    var loader2 = new THREE.TextureLoader();

    // load a resource
    loader2.load(
        // resource URL
        '/img/rubiks/colors/yellow.png',
        // Function when resource is loaded
        function ( texture1 ) {
            texture.yellow = texture1;
            if(++loadercount == 7){
				init();
            	animate();
            }
            
        },
        // Function called when download progresses
        function ( xhr ) {
            console.log( (xhr.loaded / xhr.total * 100) + '% loaded' );
        },
        // Function called when download errors
        function ( xhr ) {
            console.log( 'An error happened' );
        }
    );


    var loader3 = new THREE.TextureLoader();

    // load a resource
    loader3.load(
        // resource URL
        '/img/rubiks/colors/red.png',
        // Function when resource is loaded
        function ( texture1 ) {
            texture.red = texture1;
            if(++loadercount == 7){
                init();
                animate();
            }
        },
        // Function called when download progresses
        function ( xhr ) {
            console.log( (xhr.loaded / xhr.total * 100) + '% loaded' );
        },
        // Function called when download errors
        function ( xhr ) {
            console.log( 'An error happened' );
        }
    );

    var loader4 = new THREE.TextureLoader();

    // load a resource
    loader4.load(
        // resource URL
        '/img/rubiks/colors/orange.png',
        // Function when resource is loaded
        function ( texture1 ) {
            texture.orange = texture1;
            if(++loadercount == 7){
                init();
                animate();
            }
        },
        // Function called when download progresses
        function ( xhr ) {
            console.log( (xhr.loaded / xhr.total * 100) + '% loaded' );
        },
        // Function called when download errors
        function ( xhr ) {
            console.log( 'An error happened' );
        }
    );

    var loader5 = new THREE.TextureLoader();

    // load a resource
    loader5.load(
        // resource URL
        '/img/rubiks/colors/green.png',
        // Function when resource is loaded
        function ( texture1 ) {
            texture.green = texture1;
            if(++loadercount == 7){
                init();
                animate();
            }
        },
        // Function called when download progresses
        function ( xhr ) {
            console.log( (xhr.loaded / xhr.total * 100) + '% loaded' );
        },
        // Function called when download errors
        function ( xhr ) {
            console.log( 'An error happened' );
        }
    );

    var loader6 = new THREE.TextureLoader();

    // load a resource
    loader6.load(
        // resource URL
        '/img/rubiks/colors/blue.png',
        // Function when resource is loaded
        function ( texture1 ) {
            texture.blue = texture1;
            if(++loadercount == 7){
                init();
                animate();
            }
        },
        // Function called when download progresses
        function ( xhr ) {
            console.log( (xhr.loaded / xhr.total * 100) + '% loaded' );
        },
        // Function called when download errors
        function ( xhr ) {
            console.log( 'An error happened' );
        }
    );

    var loader7 = new THREE.TextureLoader();

    // load a resource
    loader7.load(
        // resource URL
        '/img/rubiks/colors/gray.png',
        // Function when resource is loaded
        function ( texture1 ) {
            texture.gray = texture1;
            if(++loadercount == 7){
                init();
                animate();
            }
        },
        // Function called when download progresses
        function ( xhr ) {
            console.log( (xhr.loaded / xhr.total * 100) + '% loaded' );
        },
        // Function called when download errors
        function ( xhr ) {
            console.log( 'An error happened' );
        }
    );


}

var rotWorldMatrix;

// Rotate an object around an arbitrary axis in world space       
function rw(object, axis, radians) {
    rotWorldMatrix = new THREE.Matrix4();
    rotWorldMatrix.makeRotationAxis(axis.normalize(), radians);
    rotWorldMatrix.multiply(object.matrix);                // pre-multiply

    object.matrix = rotWorldMatrix;
    object.rotation.setFromRotationMatrix(object.matrix);
}

function init() {

    //camera
    camera = new THREE.PerspectiveCamera( 30, window.innerWidth / window.innerHeight * 0.25 / 0.5 , 1, 1000 );
    camera.position.z = defaultCameraZ;
    camera.position.y = defaultCameraY;
    camera.position.x = defaultCameraX;
    camera.lookAt(new THREE.Vector3(0, -15, 0));

    //renderer
    renderer = new THREE.WebGLRenderer();
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth * 0.8 * 0.25 * 0.92, window.innerHeight * 0.8 * 0.5 * 0.92);
    renderer.autoClear = true;
    renderer.setClearColor(0xffffff, 1);
    document.getElementById('cube').appendChild(renderer.domElement);
    window.addEventListener("resize", onWindowResize, false);

    cube3D = createCube3D();
    scene = new THREE.Scene();
    for (var i = 0; i < cube3D.planes.length; i++)
        scene.add(cube3D.planes[i]);


}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight * 0.25 / 0.5;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth * 0.8 * 0.25 * 0.92, window.innerHeight * 0.8 * 0.5 * 0.92);

    animate();
}

function animate() {
    renderer.render(scene, camera);
}

function createCube3D() {

    var cube3D, plane;
    cube3D = {
        front: [],
        back: [],
        top: [],
        bottom: [],
        left: [],
        right: [],
        planes: [],
    };

    for (var y = 1; y >= -1; y--) {
        for (var x = -1; x <= 1; x++) {
            var plane = getPlane(x * planeSize, y * planeSize, planeSize * 1.5, 0, 0, 0, planeSize, "white");
            cube3D.front.push(plane);
            cube3D.planes.push(plane);
        }
    }

    for (var y = 1; y >= -1; y--) {
        for (var x = -1; x <= 1; x++) {
            var plane = getPlane(x * planeSize, y * planeSize, -planeSize * 1.5, Math.PI, 0, 0, planeSize, "yellow");
            cube3D.back.push(plane);
            cube3D.planes.push(plane);
        }
    }

    for (var z = -1; z <= 1; z++) {
        for (var x = -1; x <= 1; x++) {
            var plane = getPlane(x * planeSize, planeSize * 1.5, planeSize * z, -Math.PI/2, 0, 0, planeSize, "blue");
            cube3D.top.push(plane);
            cube3D.planes.push(plane);
        }
    }

    for (var z = 1; z >= -1; z--) {
        for (var x = -1; x <= 1; x++) {
            var plane = getPlane(x * planeSize, -planeSize * 1.5, planeSize * z, Math.PI/2, 0, 0, planeSize, "green");
            cube3D.bottom.push(plane);
            cube3D.planes.push(plane);
        }
    }

    for (var y = 1; y >= -1; y--) {
        for (var z = -1; z <= 1; z++) {
            var plane = getPlane(-planeSize * 1.5, planeSize * y, planeSize * z, 0, -Math.PI/2, 0, planeSize, "orange");
            cube3D.left.push(plane);
            cube3D.planes.push(plane);
        }
    }

    for (var y = 1; y >= -1; y--) {
        for (var z = 1; z >= -1; z--) {
            var plane = getPlane(planeSize * 1.5, planeSize * y, planeSize * z, 0, Math.PI/2, 0, planeSize, "red");
            cube3D.right.push(plane);
            cube3D.planes.push(plane);
        }
    }

    return cube3D;

}

function getPlane(x, y, z, rx, ry, rz, size, colorName) {
    var geometry = new THREE.PlaneBufferGeometry(size, size);

    material = new THREE.MeshBasicMaterial({map: texture[colorName]});




    plane = new THREE.Mesh(geometry, material);
    plane.position.x = x;
    plane.position.y = y;
    plane.position.z = z;
    plane.rotation.x = rx;
    plane.rotation.y = ry;
    plane.rotation.z = rz;
    return plane;
}

//--------------------------------------
//cube3D functions
//

function rotateFrontLayerRight(s=0) {

    if(s){
        changeFrontLayerAngle(- Math.PI/2,0);
        cube3D = {
                front: [cube3D.front[6], cube3D.front[3], cube3D.front[0], 
                        cube3D.front[7], cube3D.front[4], cube3D.front[1], 
                        cube3D.front[8], cube3D.front[5], cube3D.front[2]],

                back: cube3D.back,

                top: [cube3D.top[0], cube3D.top[1], cube3D.top[2],
                      cube3D.top[3], cube3D.top[4], cube3D.top[5],
                      cube3D.left[8], cube3D.left[5], cube3D.left[2],],

                bottom: [cube3D.right[6], cube3D.right[3], cube3D.right[0],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.bottom[6], cube3D.bottom[7], cube3D.bottom[8],],

                left: [cube3D.left[0], cube3D.left[1], cube3D.bottom[0],
                       cube3D.left[3], cube3D.left[4], cube3D.bottom[1],
                       cube3D.left[6], cube3D.left[7], cube3D.bottom[2],],

                right: [cube3D.top[6], cube3D.right[1], cube3D.right[2],
                        cube3D.top[7], cube3D.right[4], cube3D.right[5],
                        cube3D.top[8], cube3D.right[7], cube3D.right[8],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('F');

    innerPlane = getPlane(0, 0, planeSize/2, 0, 0, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeFrontLayerAngle(- Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.front[6], cube3D.front[3], cube3D.front[0], 
                        cube3D.front[7], cube3D.front[4], cube3D.front[1], 
                        cube3D.front[8], cube3D.front[5], cube3D.front[2]],

                back: cube3D.back,

                top: [cube3D.top[0], cube3D.top[1], cube3D.top[2],
                      cube3D.top[3], cube3D.top[4], cube3D.top[5],
                      cube3D.left[8], cube3D.left[5], cube3D.left[2],],

                bottom: [cube3D.right[6], cube3D.right[3], cube3D.right[0],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.bottom[6], cube3D.bottom[7], cube3D.bottom[8],],

                left: [cube3D.left[0], cube3D.left[1], cube3D.bottom[0],
                       cube3D.left[3], cube3D.left[4], cube3D.bottom[1],
                       cube3D.left[6], cube3D.left[7], cube3D.bottom[2],],

                right: [cube3D.top[6], cube3D.right[1], cube3D.right[2],
                        cube3D.top[7], cube3D.right[4], cube3D.right[5],
                        cube3D.top[8], cube3D.right[7], cube3D.right[8],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}


function rotateFrontLayerLeft(s=0) {

    if(s){
        changeFrontLayerAngle(Math.PI/2,0);
        cube3D = {
                front: [cube3D.front[2], cube3D.front[5], cube3D.front[8], 
                        cube3D.front[1], cube3D.front[4], cube3D.front[7], 
                        cube3D.front[0], cube3D.front[3], cube3D.front[6]],

                back: cube3D.back,

                top: [cube3D.top[0], cube3D.top[1], cube3D.top[2],
                      cube3D.top[3], cube3D.top[4], cube3D.top[5],
                      cube3D.right[0], cube3D.right[3], cube3D.right[6],],

                bottom: [cube3D.left[2], cube3D.left[5], cube3D.left[8],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.bottom[6], cube3D.bottom[7], cube3D.bottom[8],],

                left: [cube3D.left[0], cube3D.left[1], cube3D.top[8],
                       cube3D.left[3], cube3D.left[4], cube3D.top[7],
                       cube3D.left[6], cube3D.left[7], cube3D.top[6],],

                right: [cube3D.bottom[2], cube3D.right[1], cube3D.right[2],
                        cube3D.bottom[1], cube3D.right[4], cube3D.right[5],
                        cube3D.bottom[0], cube3D.right[7], cube3D.right[8],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('F\'');

    innerPlane = getPlane(0, 0, planeSize/2, 0, 0, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeFrontLayerAngle(Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.front[2], cube3D.front[5], cube3D.front[8], 
                        cube3D.front[1], cube3D.front[4], cube3D.front[7], 
                        cube3D.front[0], cube3D.front[3], cube3D.front[6]],

                back: cube3D.back,

                top: [cube3D.top[0], cube3D.top[1], cube3D.top[2],
                      cube3D.top[3], cube3D.top[4], cube3D.top[5],
                      cube3D.right[0], cube3D.right[3], cube3D.right[6],],

                bottom: [cube3D.left[2], cube3D.left[5], cube3D.left[8],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.bottom[6], cube3D.bottom[7], cube3D.bottom[8],],

                left: [cube3D.left[0], cube3D.left[1], cube3D.top[8],
                       cube3D.left[3], cube3D.left[4], cube3D.top[7],
                       cube3D.left[6], cube3D.left[7], cube3D.top[6],],

                right: [cube3D.bottom[2], cube3D.right[1], cube3D.right[2],
                        cube3D.bottom[1], cube3D.right[4], cube3D.right[5],
                        cube3D.bottom[0], cube3D.right[7], cube3D.right[8],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}

function rotateRightLayerRight(s=0) {

    if(s){
        changeRightLayerAngle(Math.PI/2,0);
        cube3D = {
                front: [cube3D.front[0], cube3D.front[1], cube3D.bottom[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.bottom[5], 
                        cube3D.front[6], cube3D.front[7], cube3D.bottom[8]],

                back: [cube3D.back[0], cube3D.back[1], cube3D.top[8],
                       cube3D.back[3], cube3D.back[4], cube3D.top[5],
                       cube3D.back[6], cube3D.back[7], cube3D.top[2],],

                top: [cube3D.top[0], cube3D.top[1], cube3D.front[2],
                      cube3D.top[3], cube3D.top[4], cube3D.front[5],
                      cube3D.top[6], cube3D.top[7], cube3D.front[8],],

                bottom: [cube3D.bottom[0], cube3D.bottom[1], cube3D.back[8],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.back[5],
                         cube3D.bottom[6], cube3D.bottom[7], cube3D.back[2],],

                left: cube3D.left,

                right: [cube3D.right[6], cube3D.right[3], cube3D.right[0],
                        cube3D.right[7], cube3D.right[4], cube3D.right[1],
                        cube3D.right[8], cube3D.right[5], cube3D.right[2],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('R');

    innerPlane = getPlane(planeSize/2, 0, 0, 0, Math.PI / 2, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeRightLayerAngle(Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.front[0], cube3D.front[1], cube3D.bottom[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.bottom[5], 
                        cube3D.front[6], cube3D.front[7], cube3D.bottom[8]],

                back: [cube3D.back[0], cube3D.back[1], cube3D.top[8],
                       cube3D.back[3], cube3D.back[4], cube3D.top[5],
                       cube3D.back[6], cube3D.back[7], cube3D.top[2],],

                top: [cube3D.top[0], cube3D.top[1], cube3D.front[2],
                      cube3D.top[3], cube3D.top[4], cube3D.front[5],
                      cube3D.top[6], cube3D.top[7], cube3D.front[8],],

                bottom: [cube3D.bottom[0], cube3D.bottom[1], cube3D.back[8],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.back[5],
                         cube3D.bottom[6], cube3D.bottom[7], cube3D.back[2],],

                left: cube3D.left,

                right: [cube3D.right[6], cube3D.right[3], cube3D.right[0],
                        cube3D.right[7], cube3D.right[4], cube3D.right[1],
                        cube3D.right[8], cube3D.right[5], cube3D.right[2],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}


function rotateRightLayerLeft(s=0) {

    if(s){
        changeRightLayerAngle(-Math.PI/2,0);
        cube3D = {
                front: [cube3D.front[0], cube3D.front[1], cube3D.top[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.top[5], 
                        cube3D.front[6], cube3D.front[7], cube3D.top[8]],

                back: [cube3D.back[0], cube3D.back[1], cube3D.bottom[8],
                       cube3D.back[3], cube3D.back[4], cube3D.bottom[5],
                       cube3D.back[6], cube3D.back[7], cube3D.bottom[2],],

                top: [cube3D.top[0], cube3D.top[1], cube3D.back[8],
                      cube3D.top[3], cube3D.top[4], cube3D.back[5],
                      cube3D.top[6], cube3D.top[7], cube3D.back[2],],

                bottom: [cube3D.bottom[0], cube3D.bottom[1], cube3D.front[2],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.front[5],
                         cube3D.bottom[6], cube3D.bottom[7], cube3D.front[8],],

                left: cube3D.left,

                right: [cube3D.right[2], cube3D.right[5], cube3D.right[8],
                        cube3D.right[1], cube3D.right[4], cube3D.right[7],
                        cube3D.right[0], cube3D.right[3], cube3D.right[6],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('R\'');

    innerPlane = getPlane(planeSize/2, 0, 0, 0, Math.PI / 2, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeRightLayerAngle(-Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.front[0], cube3D.front[1], cube3D.top[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.top[5], 
                        cube3D.front[6], cube3D.front[7], cube3D.top[8]],

                back: [cube3D.back[0], cube3D.back[1], cube3D.bottom[8],
                       cube3D.back[3], cube3D.back[4], cube3D.bottom[5],
                       cube3D.back[6], cube3D.back[7], cube3D.bottom[2],],

                top: [cube3D.top[0], cube3D.top[1], cube3D.back[8],
                      cube3D.top[3], cube3D.top[4], cube3D.back[5],
                      cube3D.top[6], cube3D.top[7], cube3D.back[2],],

                bottom: [cube3D.bottom[0], cube3D.bottom[1], cube3D.front[2],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.front[5],
                         cube3D.bottom[6], cube3D.bottom[7], cube3D.front[8],],

                left: cube3D.left,

                right: [cube3D.right[2], cube3D.right[5], cube3D.right[8],
                        cube3D.right[1], cube3D.right[4], cube3D.right[7],
                        cube3D.right[0], cube3D.right[3], cube3D.right[6],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}


function rotateLeftLayerRight(s=0) {

    if(s){
        changeLeftLayerAngle(-Math.PI/2,0);
        cube3D = {
                front: [cube3D.top[0], cube3D.front[1], cube3D.front[2], 
                        cube3D.top[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.top[6], cube3D.front[7], cube3D.front[8]],

                back: [cube3D.bottom[6], cube3D.back[1], cube3D.back[2],
                       cube3D.bottom[3], cube3D.back[4], cube3D.back[5],
                       cube3D.bottom[0], cube3D.back[7], cube3D.back[8],],

                top: [cube3D.back[6], cube3D.top[1], cube3D.top[2],
                      cube3D.back[3], cube3D.top[4], cube3D.top[5],
                      cube3D.back[0], cube3D.top[7], cube3D.top[8],],

                bottom: [cube3D.front[0], cube3D.bottom[1], cube3D.bottom[2],
                         cube3D.front[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.front[6], cube3D.bottom[7], cube3D.bottom[8],],

                left: [cube3D.left[6], cube3D.left[3], cube3D.left[0],
                       cube3D.left[7], cube3D.left[4], cube3D.left[1],
                       cube3D.left[8], cube3D.left[5], cube3D.left[2],],

                right: cube3D.right,

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('L');

    innerPlane = getPlane(-planeSize/2, 0, 0, 0,  Math.PI / 2, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeLeftLayerAngle(-Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.top[0], cube3D.front[1], cube3D.front[2], 
                        cube3D.top[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.top[6], cube3D.front[7], cube3D.front[8]],

                back: [cube3D.bottom[6], cube3D.back[1], cube3D.back[2],
                       cube3D.bottom[3], cube3D.back[4], cube3D.back[5],
                       cube3D.bottom[0], cube3D.back[7], cube3D.back[8],],

                top: [cube3D.back[6], cube3D.top[1], cube3D.top[2],
                      cube3D.back[3], cube3D.top[4], cube3D.top[5],
                      cube3D.back[0], cube3D.top[7], cube3D.top[8],],

                bottom: [cube3D.front[0], cube3D.bottom[1], cube3D.bottom[2],
                         cube3D.front[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.front[6], cube3D.bottom[7], cube3D.bottom[8],],

                left: [cube3D.left[6], cube3D.left[3], cube3D.left[0],
                       cube3D.left[7], cube3D.left[4], cube3D.left[1],
                       cube3D.left[8], cube3D.left[5], cube3D.left[2],],

                right: cube3D.right,

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}


function rotateLeftLayerLeft(s=0) {

    if(s){
        changeLeftLayerAngle(Math.PI/2,0);
        cube3D = {
                front: [cube3D.bottom[0], cube3D.front[1], cube3D.front[2], 
                        cube3D.bottom[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.bottom[6], cube3D.front[7], cube3D.front[8]],

                back: [cube3D.top[6], cube3D.back[1], cube3D.back[2],
                       cube3D.top[3], cube3D.back[4], cube3D.back[5],
                       cube3D.top[0], cube3D.back[7], cube3D.back[8],],

                top: [cube3D.front[0], cube3D.top[1], cube3D.top[2],
                      cube3D.front[3], cube3D.top[4], cube3D.top[5],
                      cube3D.front[6], cube3D.top[7], cube3D.top[8],],

                bottom: [cube3D.back[6], cube3D.bottom[1], cube3D.bottom[2],
                         cube3D.back[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.back[0], cube3D.bottom[7], cube3D.bottom[8],],

                left: [cube3D.left[2], cube3D.left[5], cube3D.left[8],
                       cube3D.left[1], cube3D.left[4], cube3D.left[7],
                       cube3D.left[0], cube3D.left[3], cube3D.left[6],],

                right: cube3D.right,

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('L\'');

    innerPlane = getPlane(-planeSize/2, 0, 0, 0,  Math.PI / 2, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeLeftLayerAngle(Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.bottom[0], cube3D.front[1], cube3D.front[2], 
                        cube3D.bottom[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.bottom[6], cube3D.front[7], cube3D.front[8]],

                back: [cube3D.top[6], cube3D.back[1], cube3D.back[2],
                       cube3D.top[3], cube3D.back[4], cube3D.back[5],
                       cube3D.top[0], cube3D.back[7], cube3D.back[8],],

                top: [cube3D.front[0], cube3D.top[1], cube3D.top[2],
                      cube3D.front[3], cube3D.top[4], cube3D.top[5],
                      cube3D.front[6], cube3D.top[7], cube3D.top[8],],

                bottom: [cube3D.back[6], cube3D.bottom[1], cube3D.bottom[2],
                         cube3D.back[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.back[0], cube3D.bottom[7], cube3D.bottom[8],],

                left: [cube3D.left[2], cube3D.left[5], cube3D.left[8],
                       cube3D.left[1], cube3D.left[4], cube3D.left[7],
                       cube3D.left[0], cube3D.left[3], cube3D.left[6],],

                right: cube3D.right,

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}



function rotateUpLayerRight(s=0) {

    if(s){
        changeUpLayerAngle(- Math.PI/2,0);
        cube3D = {
                front: [cube3D.right[0], cube3D.right[1], cube3D.right[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.front[6], cube3D.front[7], cube3D.front[8]],

                back: [cube3D.left[2], cube3D.left[1], cube3D.left[0],
                       cube3D.back[3], cube3D.back[4], cube3D.back[5],
                       cube3D.back[6], cube3D.back[7], cube3D.back[8],],

                top: [cube3D.top[6], cube3D.top[3], cube3D.top[0],
                      cube3D.top[7], cube3D.top[4], cube3D.top[1],
                      cube3D.top[8], cube3D.top[5], cube3D.top[2],],

                bottom: cube3D.bottom,

                left: [cube3D.front[0], cube3D.front[1], cube3D.front[2],
                       cube3D.left[3], cube3D.left[4], cube3D.left[5],
                       cube3D.left[6], cube3D.left[7], cube3D.left[8],],

                right: [cube3D.back[2], cube3D.back[1], cube3D.back[0],
                        cube3D.right[3], cube3D.right[4], cube3D.right[5],
                        cube3D.right[6], cube3D.right[7], cube3D.right[8],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('U');

    innerPlane = getPlane(0, planeSize/2, 0, -Math.PI / 2, 0, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeUpLayerAngle(- Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.right[0], cube3D.right[1], cube3D.right[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.front[6], cube3D.front[7], cube3D.front[8]],

                back: [cube3D.left[2], cube3D.left[1], cube3D.left[0],
                       cube3D.back[3], cube3D.back[4], cube3D.back[5],
                       cube3D.back[6], cube3D.back[7], cube3D.back[8],],

                top: [cube3D.top[6], cube3D.top[3], cube3D.top[0],
                      cube3D.top[7], cube3D.top[4], cube3D.top[1],
                      cube3D.top[8], cube3D.top[5], cube3D.top[2],],

                bottom: cube3D.bottom,

                left: [cube3D.front[0], cube3D.front[1], cube3D.front[2],
                       cube3D.left[3], cube3D.left[4], cube3D.left[5],
                       cube3D.left[6], cube3D.left[7], cube3D.left[8],],

                right: [cube3D.back[2], cube3D.back[1], cube3D.back[0],
                        cube3D.right[3], cube3D.right[4], cube3D.right[5],
                        cube3D.right[6], cube3D.right[7], cube3D.right[8],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}


function rotateUpLayerLeft(s=0) {

    if(s){
        changeUpLayerAngle(Math.PI/2,0);
        cube3D = {
                front: [cube3D.left[0], cube3D.left[1], cube3D.left[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.front[6], cube3D.front[7], cube3D.front[8]],

                back: [cube3D.right[2], cube3D.right[1], cube3D.right[0],
                       cube3D.back[3], cube3D.back[4], cube3D.back[5],
                       cube3D.back[6], cube3D.back[7], cube3D.back[8],],

                top: [cube3D.top[2], cube3D.top[5], cube3D.top[8],
                      cube3D.top[1], cube3D.top[4], cube3D.top[7],
                      cube3D.top[0], cube3D.top[3], cube3D.top[6],],

                bottom: cube3D.bottom,

                left: [cube3D.back[2], cube3D.back[1], cube3D.back[0],
                       cube3D.left[3], cube3D.left[4], cube3D.left[5],
                       cube3D.left[6], cube3D.left[7], cube3D.left[8],],

                right: [cube3D.front[0], cube3D.front[1], cube3D.front[2],
                        cube3D.right[3], cube3D.right[4], cube3D.right[5],
                        cube3D.right[6], cube3D.right[7], cube3D.right[8],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('U\'');

    innerPlane = getPlane(0, planeSize/2, 0, -Math.PI / 2, 0, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeUpLayerAngle(Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.left[0], cube3D.left[1], cube3D.left[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.front[6], cube3D.front[7], cube3D.front[8]],

                back: [cube3D.right[2], cube3D.right[1], cube3D.right[0],
                       cube3D.back[3], cube3D.back[4], cube3D.back[5],
                       cube3D.back[6], cube3D.back[7], cube3D.back[8],],

                top: [cube3D.top[2], cube3D.top[5], cube3D.top[8],
                      cube3D.top[1], cube3D.top[4], cube3D.top[7],
                      cube3D.top[0], cube3D.top[3], cube3D.top[6],],

                bottom: cube3D.bottom,

                left: [cube3D.back[2], cube3D.back[1], cube3D.back[0],
                       cube3D.left[3], cube3D.left[4], cube3D.left[5],
                       cube3D.left[6], cube3D.left[7], cube3D.left[8],],

                right: [cube3D.front[0], cube3D.front[1], cube3D.front[2],
                        cube3D.right[3], cube3D.right[4], cube3D.right[5],
                        cube3D.right[6], cube3D.right[7], cube3D.right[8],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}


function rotateBottomLayerRight(s=0) {

    if(s){
        changeBottomLayerAngle(Math.PI/2,0);
        cube3D = {
                front: [cube3D.front[0], cube3D.front[1], cube3D.front[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.left[6], cube3D.left[7], cube3D.left[8]],

                back: [cube3D.back[0], cube3D.back[1], cube3D.back[2],
                       cube3D.back[3], cube3D.back[4], cube3D.back[5],
                       cube3D.right[8], cube3D.right[7], cube3D.right[6],],

                top: cube3D.top,

                bottom: [cube3D.bottom[6], cube3D.bottom[3], cube3D.bottom[0],
                         cube3D.bottom[7], cube3D.bottom[4], cube3D.bottom[1],
                         cube3D.bottom[8], cube3D.bottom[5], cube3D.bottom[2],],

                left: [cube3D.left[0], cube3D.left[1], cube3D.left[2],
                       cube3D.left[3], cube3D.left[4], cube3D.left[5],
                       cube3D.back[8], cube3D.back[7], cube3D.back[6],],

                right: [cube3D.right[0], cube3D.right[1], cube3D.right[2],
                        cube3D.right[3], cube3D.right[4], cube3D.right[5],
                        cube3D.front[6], cube3D.front[7], cube3D.front[8],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('D');

    innerPlane = getPlane(0, -planeSize/2, 0, -Math.PI / 2,  0, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeBottomLayerAngle(Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.front[0], cube3D.front[1], cube3D.front[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.left[6], cube3D.left[7], cube3D.left[8]],

                back: [cube3D.back[0], cube3D.back[1], cube3D.back[2],
                       cube3D.back[3], cube3D.back[4], cube3D.back[5],
                       cube3D.right[8], cube3D.right[7], cube3D.right[6],],

                top: cube3D.top,

                bottom: [cube3D.bottom[6], cube3D.bottom[3], cube3D.bottom[0],
                         cube3D.bottom[7], cube3D.bottom[4], cube3D.bottom[1],
                         cube3D.bottom[8], cube3D.bottom[5], cube3D.bottom[2],],

                left: [cube3D.left[0], cube3D.left[1], cube3D.left[2],
                       cube3D.left[3], cube3D.left[4], cube3D.left[5],
                       cube3D.back[8], cube3D.back[7], cube3D.back[6],],

                right: [cube3D.right[0], cube3D.right[1], cube3D.right[2],
                        cube3D.right[3], cube3D.right[4], cube3D.right[5],
                        cube3D.front[6], cube3D.front[7], cube3D.front[8],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}


function rotateBottomLayerLeft(s=0) {

    if(s){
        changeBottomLayerAngle(-Math.PI/2,0);
        cube3D = {
                front: [cube3D.front[0], cube3D.front[1], cube3D.front[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.right[6], cube3D.right[7], cube3D.right[8]],

                back: [cube3D.back[0], cube3D.back[1], cube3D.back[2],
                       cube3D.back[3], cube3D.back[4], cube3D.back[5],
                       cube3D.left[8], cube3D.left[7], cube3D.left[6],],

                top: cube3D.top,

                bottom: [cube3D.bottom[2], cube3D.bottom[5], cube3D.bottom[8],
                         cube3D.bottom[1], cube3D.bottom[4], cube3D.bottom[7],
                         cube3D.bottom[0], cube3D.bottom[3], cube3D.bottom[6],],

                left: [cube3D.left[0], cube3D.left[1], cube3D.left[2],
                       cube3D.left[3], cube3D.left[4], cube3D.left[5],
                       cube3D.front[6], cube3D.front[7], cube3D.front[8],],

                right: [cube3D.right[0], cube3D.right[1], cube3D.right[2],
                        cube3D.right[3], cube3D.right[4], cube3D.right[5],
                        cube3D.back[8], cube3D.back[7], cube3D.back[6],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('D\'');

    innerPlane = getPlane(0, -planeSize/2, 0, -Math.PI / 2,  0, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeBottomLayerAngle(-Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: [cube3D.front[0], cube3D.front[1], cube3D.front[2], 
                        cube3D.front[3], cube3D.front[4], cube3D.front[5], 
                        cube3D.right[6], cube3D.right[7], cube3D.right[8]],

                back: [cube3D.back[0], cube3D.back[1], cube3D.back[2],
                       cube3D.back[3], cube3D.back[4], cube3D.back[5],
                       cube3D.left[8], cube3D.left[7], cube3D.left[6],],

                top: cube3D.top,

                bottom: [cube3D.bottom[2], cube3D.bottom[5], cube3D.bottom[8],
                         cube3D.bottom[1], cube3D.bottom[4], cube3D.bottom[7],
                         cube3D.bottom[0], cube3D.bottom[3], cube3D.bottom[6],],

                left: [cube3D.left[0], cube3D.left[1], cube3D.left[2],
                       cube3D.left[3], cube3D.left[4], cube3D.left[5],
                       cube3D.front[6], cube3D.front[7], cube3D.front[8],],

                right: [cube3D.right[0], cube3D.right[1], cube3D.right[2],
                        cube3D.right[3], cube3D.right[4], cube3D.right[5],
                        cube3D.back[8], cube3D.back[7], cube3D.back[6],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}



function rotateBackLayerRight(s=0) {

    if(s){
        changeBackLayerAngle(Math.PI/2,0);
        cube3D = {
                front: cube3D.front,

                back: [cube3D.back[2], cube3D.back[5], cube3D.back[8],
                      cube3D.back[1], cube3D.back[4], cube3D.back[7],
                      cube3D.back[0], cube3D.back[3], cube3D.back[6],],

                top: [cube3D.right[2], cube3D.right[5], cube3D.right[8],
                      cube3D.top[3], cube3D.top[4], cube3D.top[5],
                      cube3D.top[6], cube3D.top[7], cube3D.top[8],],

                bottom: [cube3D.bottom[0], cube3D.bottom[1], cube3D.bottom[2],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.left[0], cube3D.left[3], cube3D.left[6],],

                left: [cube3D.top[2], cube3D.left[1], cube3D.left[2],
                       cube3D.top[1], cube3D.left[4], cube3D.left[5],
                       cube3D.top[0], cube3D.left[7], cube3D.left[8],],

                right: [cube3D.right[0], cube3D.right[1], cube3D.bottom[8],
                        cube3D.right[3], cube3D.right[4], cube3D.bottom[7],
                        cube3D.right[6], cube3D.right[7], cube3D.bottom[6],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('B');

    innerPlane = getPlane(0, 0, -planeSize/2, 0, 0, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeBackLayerAngle(Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: cube3D.front,

                back: [cube3D.back[2], cube3D.back[5], cube3D.back[8],
                      cube3D.back[1], cube3D.back[4], cube3D.back[7],
                      cube3D.back[0], cube3D.back[3], cube3D.back[6],],

                top: [cube3D.right[2], cube3D.right[5], cube3D.right[8],
                      cube3D.top[3], cube3D.top[4], cube3D.top[5],
                      cube3D.top[6], cube3D.top[7], cube3D.top[8],],

                bottom: [cube3D.bottom[0], cube3D.bottom[1], cube3D.bottom[2],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.left[0], cube3D.left[3], cube3D.left[6],],

                left: [cube3D.top[2], cube3D.left[1], cube3D.left[2],
                       cube3D.top[1], cube3D.left[4], cube3D.left[5],
                       cube3D.top[0], cube3D.left[7], cube3D.left[8],],

                right: [cube3D.right[0], cube3D.right[1], cube3D.bottom[8],
                        cube3D.right[3], cube3D.right[4], cube3D.bottom[7],
                        cube3D.right[6], cube3D.right[7], cube3D.bottom[6],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}


function rotateBackLayerLeft(s=0) {


    if(s){
        changeBackLayerAngle(-Math.PI/2,0);
        cube3D = {
                front: cube3D.front,

                back: [cube3D.back[6], cube3D.back[3], cube3D.back[0],
                      cube3D.back[7], cube3D.back[4], cube3D.back[1],
                      cube3D.back[8], cube3D.back[5], cube3D.back[2],],

                top: [cube3D.left[6], cube3D.left[3], cube3D.left[0],
                      cube3D.top[3], cube3D.top[4], cube3D.top[5],
                      cube3D.top[6], cube3D.top[7], cube3D.top[8],],

                bottom: [cube3D.bottom[0], cube3D.bottom[1], cube3D.bottom[2],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.right[8], cube3D.right[5], cube3D.right[2],],

                left: [cube3D.bottom[6], cube3D.left[1], cube3D.left[2],
                       cube3D.bottom[7], cube3D.left[4], cube3D.left[5],
                       cube3D.bottom[8], cube3D.left[7], cube3D.left[8],],

                right: [cube3D.right[0], cube3D.right[1], cube3D.top[0],
                        cube3D.right[3], cube3D.right[4], cube3D.top[1],
                        cube3D.right[6], cube3D.right[7], cube3D.top[2],],

                planes: cube3D.planes,

            }
        return;
    }

    if (n != 0) return;

    saverotates.push('B\'');

    innerPlane = getPlane(0, 0, -planeSize/2, 0, 0, 0, planeSize*3, "gray");
    innerPlane.name = 'innerPlane';
    scene.add(innerPlane);

    n = 0;
    interval = setInterval(function() {
        changeBackLayerAngle(-Math.PI/2 / 10);
        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);

            scene.remove(scene.getObjectByName('innerPlane'));

            cube3D = {
                front: cube3D.front,

                back: [cube3D.back[6], cube3D.back[3], cube3D.back[0],
                      cube3D.back[7], cube3D.back[4], cube3D.back[1],
                      cube3D.back[8], cube3D.back[5], cube3D.back[2],],

                top: [cube3D.left[6], cube3D.left[3], cube3D.left[0],
                      cube3D.top[3], cube3D.top[4], cube3D.top[5],
                      cube3D.top[6], cube3D.top[7], cube3D.top[8],],

                bottom: [cube3D.bottom[0], cube3D.bottom[1], cube3D.bottom[2],
                         cube3D.bottom[3], cube3D.bottom[4], cube3D.bottom[5],
                         cube3D.right[8], cube3D.right[5], cube3D.right[2],],

                left: [cube3D.bottom[6], cube3D.left[1], cube3D.left[2],
                       cube3D.bottom[7], cube3D.left[4], cube3D.left[5],
                       cube3D.bottom[8], cube3D.left[7], cube3D.left[8],],

                right: [cube3D.right[0], cube3D.right[1], cube3D.top[0],
                        cube3D.right[3], cube3D.right[4], cube3D.top[1],
                        cube3D.right[6], cube3D.right[7], cube3D.top[2],],

                planes: cube3D.planes,

            }

            animate();

        }
    }, 20);
}

function changeLayersAfterRightRotate() {
    cube3D = {
        front: cube3D.right,

        right: [cube3D.back[2], cube3D.back[1], cube3D.back[0], 
                cube3D.back[5], cube3D.back[4], cube3D.back[3], 
                cube3D.back[8], cube3D.back[7], cube3D.back[6], ],

        back: [cube3D.left[2], cube3D.left[1], cube3D.left[0], 
                cube3D.left[5], cube3D.left[4], cube3D.left[3], 
                cube3D.left[8], cube3D.left[7], cube3D.left[6], ],

        left: cube3D.front,

        top: [cube3D.top[6], cube3D.top[3], cube3D.top[0], 
              cube3D.top[7], cube3D.top[4], cube3D.top[1], 
              cube3D.top[8], cube3D.top[5], cube3D.top[2], ],

        bottom: [cube3D.bottom[2], cube3D.bottom[5], cube3D.bottom[8], 
                 cube3D.bottom[1], cube3D.bottom[4], cube3D.bottom[7], 
                 cube3D.bottom[0], cube3D.bottom[3], cube3D.bottom[6], ],

        planes: cube3D.planes,
    }
}

function changeLayersAfterLeftRotate() {
    cube3D = {
        front: cube3D.left,

        right: cube3D.front,

        back: [cube3D.right[2], cube3D.right[1], cube3D.right[0], 
                cube3D.right[5], cube3D.right[4], cube3D.right[3], 
                cube3D.right[8], cube3D.right[7], cube3D.right[6], ],

        left: [cube3D.back[2], cube3D.back[1], cube3D.back[0], 
                cube3D.back[5], cube3D.back[4], cube3D.back[3], 
                cube3D.back[8], cube3D.back[7], cube3D.back[6], ],

        top: [cube3D.top[2], cube3D.top[5], cube3D.top[8], 
              cube3D.top[1], cube3D.top[4], cube3D.top[7], 
              cube3D.top[0], cube3D.top[3], cube3D.top[6], ],

        bottom: [cube3D.bottom[6], cube3D.bottom[3], cube3D.bottom[0], 
                 cube3D.bottom[7], cube3D.bottom[4], cube3D.bottom[1], 
                 cube3D.bottom[8], cube3D.bottom[5], cube3D.bottom[2], ],

        planes: cube3D.planes,
    }
}

function changeLayersTopRotate() {
    cube3D = {
        front: cube3D.top,

        right: [cube3D.right[2], cube3D.right[5], cube3D.right[8], 
              cube3D.right[1], cube3D.right[4], cube3D.right[7], 
              cube3D.right[0], cube3D.right[3], cube3D.right[6], ],

        back: [cube3D.bottom[6], cube3D.bottom[7], cube3D.bottom[8], 
                cube3D.bottom[3], cube3D.bottom[4], cube3D.bottom[5], 
                cube3D.bottom[0], cube3D.bottom[1], cube3D.bottom[2], ],

        left: [cube3D.left[6], cube3D.left[3], cube3D.left[0], 
                 cube3D.left[7], cube3D.left[4], cube3D.left[1], 
                 cube3D.left[8], cube3D.left[5], cube3D.left[2], ],

        top:  [cube3D.back[6], cube3D.back[7], cube3D.back[8], 
                cube3D.back[3], cube3D.back[4], cube3D.back[5], 
                cube3D.back[0], cube3D.back[1], cube3D.back[2], ],

        bottom: cube3D.front,

        planes: cube3D.planes,
    }
}

function changeLayersBottomRotate() {
    cube3D = {
        front: cube3D.bottom,

        right: [cube3D.right[6], cube3D.right[3], cube3D.right[0], 
                 cube3D.right[7], cube3D.right[4], cube3D.right[1], 
                 cube3D.right[8], cube3D.right[5], cube3D.right[2], ],

        back: [cube3D.top[6], cube3D.top[7], cube3D.top[8], 
                cube3D.top[3], cube3D.top[4], cube3D.top[5], 
                cube3D.top[0], cube3D.top[1], cube3D.top[2], ],

        left: [cube3D.left[2], cube3D.left[5], cube3D.left[8], 
              cube3D.left[1], cube3D.left[4], cube3D.left[7], 
              cube3D.left[0], cube3D.left[3], cube3D.left[6], ],

        top:  cube3D.front,

        bottom: [cube3D.back[6], cube3D.back[7], cube3D.back[8], 
                cube3D.back[3], cube3D.back[4], cube3D.back[5], 
                cube3D.back[0], cube3D.back[1], cube3D.back[2], ],

        planes: cube3D.planes,
    }
}

function rotateCubeRight(s = 0) {
    if (n != 0) return;

    if (s === 1) {
        var angle = Math.PI / 2;
        for (var i = 0; i < cube3D.planes.length; i++) {
                rw(cube3D.planes[i], yv, -angle);
                var x = cube3D.planes[i].position.x, z = cube3D.planes[i].position.z;
                cube3D.planes[i].position.x = x * Math.cos(angle) - z * Math.sin(angle);
                cube3D.planes[i].position.z = x * Math.sin(angle) + z * Math.cos(angle);
        }
        changeLayersAfterRightRotate();
        return;
    }

    saverotates.push("r");

    n = 0;
    interval = setInterval(function() {

        var angle = Math.PI / 2 / 10;

        for (var i = 0; i < cube3D.planes.length; i++) {
                rw(cube3D.planes[i], yv, -angle);
                var x = cube3D.planes[i].position.x, z = cube3D.planes[i].position.z;
                cube3D.planes[i].position.x = x * Math.cos(angle) - z * Math.sin(angle);
                cube3D.planes[i].position.z = x * Math.sin(angle) + z * Math.cos(angle);
        }

        animate();

        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);
            changeLayersAfterRightRotate();
            animate();
        }
    }, 20);
}


function rotateCubeLeft(s = 0) {
    if (n != 0) return;

    if (s === 1) {
        var angle = Math.PI / 2;
        for (var i = 0; i < cube3D.planes.length; i++) {
            rw(cube3D.planes[i], yv, angle);
            var x = cube3D.planes[i].position.x, z = cube3D.planes[i].position.z;
            cube3D.planes[i].position.x = x * Math.cos(-angle) - z * Math.sin(-angle);
            cube3D.planes[i].position.z = x * Math.sin(-angle) + z * Math.cos(-angle);
        }
        changeLayersAfterLeftRotate();
        return;
    }

    saverotates.push("l");

    n = 0;
    interval = setInterval(function() {

        var angle = Math.PI / 2 / 10;

        for (var i = 0; i < cube3D.planes.length; i++) {
                rw(cube3D.planes[i], yv, angle);
                var x = cube3D.planes[i].position.x, z = cube3D.planes[i].position.z;
                cube3D.planes[i].position.x = x * Math.cos(-angle) - z * Math.sin(-angle);
                cube3D.planes[i].position.z = x * Math.sin(-angle) + z * Math.cos(-angle);
        }

        animate();

        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);
            changeLayersAfterLeftRotate();
            animate();

        }
    }, 20);
}


function rotateCubeTop(s = 0) {
    if (n != 0) return;

    if (s === 1) {
        var angle = Math.PI / 2;
        for (var i = 0; i < cube3D.planes.length; i++) {
            rw(cube3D.planes[i], xv, angle);
            var y = cube3D.planes[i].position.y, z = cube3D.planes[i].position.z;
            cube3D.planes[i].position.y = y * Math.cos(angle) - z * Math.sin(angle);
            cube3D.planes[i].position.z = y * Math.sin(angle) + z * Math.cos(angle);
        }
        changeLayersTopRotate();
        return;
    }

    saverotates.push("t");

    n = 0;
    interval = setInterval(function() {

        var angle = Math.PI/2/10;

        for (var i = 0; i < cube3D.planes.length; i++) {
                rw(cube3D.planes[i], xv, angle);
                var y = cube3D.planes[i].position.y, z = cube3D.planes[i].position.z;
                cube3D.planes[i].position.y = y * Math.cos(angle) - z * Math.sin(angle);
                cube3D.planes[i].position.z = y * Math.sin(angle) + z * Math.cos(angle);
        }

        animate();

        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);
            changeLayersTopRotate()
            animate();

        }
    }, 20);
}


function rotateCubeBottom(s = 0) {
    if (n != 0) return;

    if (s === 1) {
        var angle = -Math.PI / 2;
        for (var i = 0; i < cube3D.planes.length; i++) {
            rw(cube3D.planes[i], xv, angle);
            var y = cube3D.planes[i].position.y, z = cube3D.planes[i].position.z;
            cube3D.planes[i].position.y = y * Math.cos(angle) - z * Math.sin(angle);
            cube3D.planes[i].position.z = y * Math.sin(angle) + z * Math.cos(angle);
        }
        changeLayersBottomRotate();
        return;
    }

    saverotates.push("b");

    n = 0;
    interval = setInterval(function() {

        var angle = -Math.PI/2/10;

        for (var i = 0; i < cube3D.planes.length; i++) {
                rw(cube3D.planes[i], xv, angle);
                var y = cube3D.planes[i].position.y, z = cube3D.planes[i].position.z;
                cube3D.planes[i].position.y = y * Math.cos(angle) - z * Math.sin(angle);
                cube3D.planes[i].position.z = y * Math.sin(angle) + z * Math.cos(angle);
        }

        animate();

        n++;
        if (n >= 10) {
            n = 0;
            clearInterval(interval);
            changeLayersBottomRotate();
            animate();

        }
    }, 20);
}



function changeFrontLayerAngle(angle, s=1) {

    for (var i = 0; i < 9; i++) {
        rw(cube3D.front[i], zv, angle);
        var x = cube3D.front[i].position.x, y = cube3D.front[i].position.y;
        cube3D.front[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.front[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 6; i < 9; i++) {
        rw(cube3D.top[i], zv, angle);
        var x = cube3D.top[i].position.x, y = cube3D.top[i].position.y;
        cube3D.top[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.top[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 0; i < 9; i += 3) {
        rw(cube3D.right[i], zv, angle);
        var x = cube3D.right[i].position.x, y = cube3D.right[i].position.y;
        cube3D.right[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.right[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 2; i < 9; i += 3) {
        rw(cube3D.left[i], zv, angle);
        var x = cube3D.left[i].position.x, y = cube3D.left[i].position.y;
        cube3D.left[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.left[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 0; i < 3; i++) {
        rw(cube3D.bottom[i], zv, angle);
        var x = cube3D.bottom[i].position.x, y = cube3D.bottom[i].position.y;
        cube3D.bottom[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.bottom[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    animate();
}

function changeRightLayerAngle(angle, s=1) {

    for (var i = 0; i < 9; i++) {
        rw(cube3D.right[i], xv, -angle);
        var z = cube3D.right[i].position.z, y = cube3D.right[i].position.y;
        cube3D.right[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.right[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 2; i < 9; i+=3) {
        rw(cube3D.top[i], xv, -angle);
        var z = cube3D.top[i].position.z, y = cube3D.top[i].position.y;
        cube3D.top[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.top[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 2; i < 9; i += 3) {
        rw(cube3D.front[i], xv, -angle);
        var z = cube3D.front[i].position.z, y = cube3D.front[i].position.y;
        cube3D.front[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.front[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 2; i < 9; i += 3) {
        rw(cube3D.back[i], xv, -angle);
        var z = cube3D.back[i].position.z, y = cube3D.back[i].position.y;
        cube3D.back[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.back[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 2; i < 9; i+=3) {
        rw(cube3D.bottom[i], xv, -angle);
        var z = cube3D.bottom[i].position.z, y = cube3D.bottom[i].position.y;
        cube3D.bottom[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.bottom[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }
    
    animate();
}

function changeUpLayerAngle(angle, s=1) {

    for (var i = 0; i < 9; i++) {
        rw(cube3D.top[i], yv, angle);
        var z = cube3D.top[i].position.z, x = cube3D.top[i].position.x;
        cube3D.top[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.top[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }

    for (var i = 0; i < 3; i++) {
        rw(cube3D.back[i], yv, angle);
        var z = cube3D.back[i].position.z, x = cube3D.back[i].position.x;
        cube3D.back[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.back[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }

    for (var i = 0; i < 3; i ++) {
        rw(cube3D.left[i], yv, angle);
        var z = cube3D.left[i].position.z, x = cube3D.left[i].position.x;
        cube3D.left[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.left[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }

    for (var i = 0; i < 3; i++) {
        rw(cube3D.right[i], yv, angle);
        var z = cube3D.right[i].position.z, x = cube3D.right[i].position.x;
        cube3D.right[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.right[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }

    for (var i = 0; i < 3; i++) {
        rw(cube3D.front[i], yv, angle);
        var z = cube3D.front[i].position.z, x = cube3D.front[i].position.x;
        cube3D.front[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.front[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }
    
    animate();
}


function changeLeftLayerAngle(angle, s=1) {

    for (var i = 0; i < 9; i++) {
        rw(cube3D.left[i], xv, -angle);
        var z = cube3D.left[i].position.z, y = cube3D.left[i].position.y;
        cube3D.left[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.left[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 0; i < 9; i+=3) {
        rw(cube3D.top[i], xv, -angle);
        var z = cube3D.top[i].position.z, y = cube3D.top[i].position.y;
        cube3D.top[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.top[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 0; i < 9; i += 3) {
        rw(cube3D.back[i], xv, -angle);
        var z = cube3D.back[i].position.z, y = cube3D.back[i].position.y;
        cube3D.back[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.back[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 0; i < 9; i += 3) {
        rw(cube3D.front[i], xv, -angle);
        var z = cube3D.front[i].position.z, y = cube3D.front[i].position.y;
        cube3D.front[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.front[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 0; i < 9; i+=3) {
        rw(cube3D.bottom[i], xv, -angle);
        var z = cube3D.bottom[i].position.z, y = cube3D.bottom[i].position.y;
        cube3D.bottom[i].position.z = z * Math.cos(angle) - y * Math.sin(angle);
        cube3D.bottom[i].position.y = z * Math.sin(angle) + y * Math.cos(angle);
    }

    if(s)innerPlane.rotateZ(-angle);
    
    animate();
}


function changeBottomLayerAngle(angle, s=1) {

    for (var i = 0; i < 9; i++) {
        rw(cube3D.bottom[i], yv, angle);
        var z = cube3D.bottom[i].position.z, x = cube3D.bottom[i].position.x;
        cube3D.bottom[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.bottom[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }

    for (var i = 6; i < 9; i++) {
        rw(cube3D.front[i], yv, angle);
        var z = cube3D.front[i].position.z, x = cube3D.front[i].position.x;
        cube3D.front[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.front[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }

    for (var i = 6; i < 9; i ++) {
        rw(cube3D.left[i], yv, angle);
        var z = cube3D.left[i].position.z, x = cube3D.left[i].position.x;
        cube3D.left[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.left[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }

    for (var i = 6; i < 9; i++) {
        rw(cube3D.right[i], yv, angle);
        var z = cube3D.right[i].position.z, x = cube3D.right[i].position.x;
        cube3D.right[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.right[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }

    for (var i = 6; i < 9; i++) {
        rw(cube3D.back[i], yv, angle);
        var z = cube3D.back[i].position.z, x = cube3D.back[i].position.x;
        cube3D.back[i].position.z = z * Math.cos(angle) - x * Math.sin(angle);
        cube3D.back[i].position.x = z * Math.sin(angle) + x * Math.cos(angle);
    }

    if(s)innerPlane.rotateZ(angle);
    
    animate();
}

function changeBackLayerAngle(angle, s=1) {

    for (var i = 0; i < 9; i++) {
        rw(cube3D.back[i], zv, angle);
        var x = cube3D.back[i].position.x, y = cube3D.back[i].position.y;
        cube3D.back[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.back[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 6; i < 9; i++) {
        rw(cube3D.bottom[i], zv, angle);
        var x = cube3D.bottom[i].position.x, y = cube3D.bottom[i].position.y;
        cube3D.bottom[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.bottom[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 2; i < 9; i += 3) {
        rw(cube3D.right[i], zv, angle);
        var x = cube3D.right[i].position.x, y = cube3D.right[i].position.y;
        cube3D.right[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.right[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 0; i < 9; i += 3) {
        rw(cube3D.left[i], zv, angle);
        var x = cube3D.left[i].position.x, y = cube3D.left[i].position.y;
        cube3D.left[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.left[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    for (var i = 0; i < 3; i++) {
        rw(cube3D.top[i], zv, angle);
        var x = cube3D.top[i].position.x, y = cube3D.top[i].position.y;
        cube3D.top[i].position.x = x * Math.cos(angle) - y * Math.sin(angle);
        cube3D.top[i].position.y = x * Math.sin(angle) + y * Math.cos(angle);
    }

    if(s)innerPlane.rotateZ(angle);

    animate();
}

function scramblecube(){

    isScrambled = true;
    repeatrotates = [];

    while(saverotates.length){
        p = saverotates.pop();
        if(p == 'R'){
            rotateRightLayerLeft(1);
        }
        else if(p == 'R\''){
            rotateRightLayerRight(1)
        }
        else if(p == 'F'){
            rotateFrontLayerLeft(1);
        }
        else if(p == 'F\''){
            rotateFrontLayerRight(1);
        }
        else if(p == 'U'){
            rotateUpLayerLeft(1);
        }
        else if(p == 'U\''){
            rotateUpLayerRight(1);
        }
        else if(p == 'L'){
            rotateLeftLayerLeft(1);
        }
        else if(p == 'L\''){
            rotateLeftLayerRight(1);
        }
        else if(p == 'B'){
            rotateBackLayerLeft(1);
        }
        else if(p == 'B\''){
            rotateBackLayerRight(1);
        }
        else if(p == 'D'){
            rotateBottomLayerLeft(1);
        }
        else if(p == 'D\''){
            rotateBottomLayerRight(1);
        }
        else if(p == 'r'){
            rotateCubeLeft(1);
        }
        else if(p == 'l'){
            rotateCubeRight(1);
        }
        else if(p == 't'){
            rotateCubeBottom(1);
        }
        else if(p == 'b'){
            rotateCubeTop(1);
        }
    }

    var scr = '';
    var choise = [[rotateRightLayerRight, 'R'], [rotateRightLayerLeft, 'R\''], [rotateFrontLayerRight, 'F'], [rotateFrontLayerLeft, 'F\''],
    [rotateUpLayerRight, 'U'], [rotateUpLayerLeft, 'U\''], [rotateLeftLayerRight, 'L'], [rotateLeftLayerLeft, 'L\''],
    [rotateBackLayerRight, 'B'], [rotateBackLayerLeft, 'B\''], [rotateBottomLayerRight, 'D'], [rotateBottomLayerLeft, 'D\'']];

    var last = ' ', f = [[], ' '];
    for(var i = 0; i < scrambleLen; i++){
        while(last[0] == f[1][0]){
            f=choise[Math.random() * 12| 0];
        }
        f[0](1);
        saverotates.push(f[1]);
        repeatrotates.push(f[1]);
        scr += f[1] + ' ';
        last = f[1];
    }

    rrindex = repeatrotates.length - 1;

    document.getElementById('solvescramble').innerHTML = scr;

    scr = '';
    for(var i = repeatrotates.length - 1; i >= 0; i--){

        var p = saverotates[i];
        if(p.length == 2)p = p[0];
        else{
            p += '\''
        }

        scr += p + ' ';
    }

    document.getElementById('repeatscramble').innerHTML = scr;

    scr = '';
        for(var i = repeatrotates.length - 1; i >= 0; i--){

            var p = repeatrotates[i];

            if(p == 'd' || p == 't' || p == 'l' || p == 'r'){

                if(p == 't')p = 'd';
                else if(p == 'b')p = 'u';
                else if(p == 'l')p = 'r';
                else if(p == 'r')p = 'l';

            }
            else{
                if(p.length == 2)p = p[0];
                else p += '\''
            }

            if(rrindex == i){
                p = '<u>' + p + '</u>'
            }

            scr += p + ' ';
        }

        document.getElementById('repeatscramble').innerHTML = scr;

    animate();
}

function repeatprev(){
    // [[rotateRightLayerRight, 'R'], [rotateRightLayerLeft, 'R\''], [rotateFrontLayerRight, 'F'], [rotateFrontLayerLeft, 'F\''],
    // [rotateUpLayerRight, 'U'], [rotateUpLayerLeft, 'U\''], [rotateLeftLayerRight, 'L'], [rotateLeftLayerLeft, 'L\''],
    // [rotateBackLayerRight, 'B'], [rotateBackLayerLeft, 'B\''], [rotateBottomLayerRight, 'D'], [rotateBottomLayerLeft, 'D\'']][Math.random() * 12| 0][0]();
    console.log(repeatrotates, rrindex, repeatrotates.length, n, repeatrotates[rrindex]);

    if(rrindex < 0)rrindex = -1;

    if(n == 0 && rrindex < repeatrotates.length - 1){
        var p = repeatrotates[++rrindex];
        if(p == 'R\''){
            rotateRightLayerLeft();
        }
        else if(p == 'R'){
            rotateRightLayerRight()
        }
        else if(p == 'F\''){
            rotateFrontLayerLeft();
        }
        else if(p == 'F'){
            rotateFrontLayerRight();
        }
        else if(p == 'U\''){
            rotateUpLayerLeft();
        }
        else if(p == 'U'){
            rotateUpLayerRight();
        }
        else if(p == 'L\''){
            rotateLeftLayerLeft();
        }
        else if(p == 'L'){
            rotateLeftLayerRight();
        }
        else if(p == 'B\''){
            rotateBackLayerLeft();
        }
        else if(p == 'B'){
            rotateBackLayerRight();
        }
        else if(p == 'D\''){
            rotateBottomLayerLeft();
        }
        else if(p == 'D'){
            rotateBottomLayerRight();
        }
        else if(p == 'l'){
            rotateCubeLeft();
        }
        else if(p == 'r'){
            rotateCubeRight();
        }
        else if(p == 'b'){
            rotateCubeBottom();
        }
        else if(p == 't'){
            rotateCubeTop();
        }

        scr = '';
        for(var i = repeatrotates.length - 1; i >= 0; i--){

            var p = repeatrotates[i];

            if(p == 'd' || p == 't' || p == 'l' || p == 'r'){

                if(p == 't')p = 'd';
                else if(p == 'b')p = 'u';
                else if(p == 'l')p = 'r';
                else if(p == 'r')p = 'l';

            }
            else{
                if(p.length == 2)p = p[0];
                else p += '\''
            }

            if(rrindex == i){
                p = '<u>' + p + '</u>'
            }

            scr += p + ' ';
        }

        document.getElementById('repeatscramble').innerHTML = scr;
    }

}

function repeatnext(){
    console.log(n);
    // [[rotateRightLayerRight, 'R'], [rotateRightLayerLeft, 'R\''], [rotateFrontLayerRight, 'F'], [rotateFrontLayerLeft, 'F\''],
    // [rotateUpLayerRight, 'U'], [rotateUpLayerLeft, 'U\''], [rotateLeftLayerRight, 'L'], [rotateLeftLayerLeft, 'L\''],
    // [rotateBackLayerRight, 'B'], [rotateBackLayerLeft, 'B\''], [rotateBottomLayerRight, 'D'], [rotateBottomLayerLeft, 'D\'']][Math.random() * 12| 0][0]();
    if (n == 0){
        rrindex -= 1;
        undomove(true);

        scr = '';
        for(var i = repeatrotates.length - 1; i >= 0; i--){

            var p = repeatrotates[i];

            if(p == 'd' || p == 't' || p == 'l' || p == 'r'){

                if(p == 't')p = 'd';
                else if(p == 'b')p = 'u';
                else if(p == 'l')p = 'r';
                else if(p == 'r')p = 'l';

            }
            else{
                if(p.length == 2)p = p[0];
                else p += '\''
            }

            if(rrindex == i){
                p = '<u>' + p + '</u>'
            }

            scr += p + ' ';
        }

        document.getElementById('repeatscramble').innerHTML = scr;
    }
}

function undomove(forceUndo = false){
    if((saverotates.length > scrambleLen || !isScrambled || forceUndo) && n == 0){
        p = saverotates.pop();
        if(p == 'R'){
            rotateRightLayerLeft();
        }
        else if(p == 'R\''){
            rotateRightLayerRight()
        }
        else if(p == 'F'){
            rotateFrontLayerLeft();
        }
        else if(p == 'F\''){
            rotateFrontLayerRight();
        }
        else if(p == 'U'){
            rotateUpLayerLeft();
        }
        else if(p == 'U\''){
            rotateUpLayerRight();
        }
        else if(p == 'L'){
            rotateLeftLayerLeft();
        }
        else if(p == 'L\''){
            rotateLeftLayerRight();
        }
        else if(p == 'B'){
            rotateBackLayerLeft();
        }
        else if(p == 'B\''){
            rotateBackLayerRight();
        }
        else if(p == 'D'){
            rotateBottomLayerLeft();
        }
        else if(p == 'D\''){
            rotateBottomLayerRight();
        }
        else if(p == 'r'){
            rotateCubeLeft();
        }
        else if(p == 'l'){
            rotateCubeRight();
        }
        else if(p == 't'){
            rotateCubeBottom();
        }
        else if(p == 'b'){
            rotateCubeTop();
        }
        saverotates.pop();
    }
}