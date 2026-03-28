import * as THREE from 'three';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, treehouseDeck, mesh;

init();
animate();

function init() {
    const container = document.getElementById('canvas-container');
    
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xa0a0a0);
    scene.fog = new THREE.Fog(0xa0a0a0, 20, 100);
    
    camera = new THREE.PerspectiveCamera(35, container.clientWidth / container.clientHeight, 1, 500);
    camera.position.set(30, 20, 30);
    
    // Lights
    const hemiLight = new THREE.HemisphereLight(0xffffff, 0x444444, 3);
    hemiLight.position.set(0, 20, 0);
    scene.add(hemiLight);
    
    const dirLight = new THREE.DirectionalLight(0xffffff, 3);
    dirLight.position.set(-3, 10, -10);
    scene.add(dirLight);
    
    // Add simple grid
    const grid = new THREE.GridHelper(50, 50, 0x444444, 0x888888);
    grid.position.y = -5; // Lower grid
    scene.add(grid);
    
    // STL Loader
    const loader = new STLLoader();
    loader.load('../stl_files/grounds.stl', function (geometry) {
        geometry.computeVertexNormals();
        geometry.center(); // Center the geometry for easy viewing
        
        const material = new THREE.MeshPhongMaterial({ color: 0x90b090, specular: 0x111111, shininess: 10 });
        mesh = new THREE.Mesh(geometry, material);
        // STL from LIDAR is frequently rotated, adjust -90deg X to make it flat
        mesh.rotation.x = -Math.PI / 2; 
        scene.add(mesh);
    }, undefined, function (error) {
        console.error("Error loading STL:", error);
    });
    
    // Treehouse Deck Geometry (Interactive bounds representation)
    const deckGeo = new THREE.BoxGeometry(10, 0.5, 10);
    const deckMat = new THREE.MeshPhongMaterial({ color: 0x8b5a2b, transparent: true, opacity: 0.8 });
    treehouseDeck = new THREE.Mesh(deckGeo, deckMat);
    // Position it slightly above ground to start
    treehouseDeck.position.y = 8;
    scene.add(treehouseDeck);
    
    // Central Box to represent main trunk safely
    const trunkGeo = new THREE.CylinderGeometry(1.5, 1.5, 20, 16);
    const trunkMat = new THREE.MeshPhongMaterial({ color: 0x3d2817 });
    const trunk = new THREE.Mesh(trunkGeo, trunkMat);
    trunk.position.y = 5;
    scene.add(trunk);
    
    // Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(container.clientWidth, container.clientHeight);
    container.appendChild(renderer.domElement);
    
    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 5, 0);
    controls.update();
    
    window.addEventListener('resize', onWindowResize);
    
    setupUI();
}

function setupUI() {
    const wSlider = document.getElementById('deck-width');
    const dSlider = document.getElementById('deck-depth');
    const hSlider = document.getElementById('deck-height');
    const rotSlider = document.getElementById('deck-rot');
    
    const updateDeck = () => {
        const w = parseFloat(wSlider.value);
        const d = parseFloat(dSlider.value);
        const h = parseFloat(hSlider.value);
        const r = parseFloat(rotSlider.value);
        
        treehouseDeck.scale.set(w/10, 1, d/10);
        treehouseDeck.position.y = h;
        treehouseDeck.rotation.y = r * (Math.PI / 180);
        
        document.getElementById('w-val').innerText = w;
        document.getElementById('d-val').innerText = d;
        document.getElementById('h-val').innerText = h;
        document.getElementById('r-val').innerText = r;
    };
    
    wSlider.addEventListener('input', updateDeck);
    dSlider.addEventListener('input', updateDeck);
    hSlider.addEventListener('input', updateDeck);
    rotSlider.addEventListener('input', updateDeck);
}

function onWindowResize() {
    const container = document.getElementById('canvas-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
