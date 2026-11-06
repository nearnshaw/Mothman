// Runs the real body/host code against a small ECS adapter; no Explorer required.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const vm = require('node:vm')
const path = require('node:path')
const ts = require('typescript')
let nextEntity = 10
const sounds = []
const component = () => {
  const data = new Map()
  return { data, writes: 0, create(e, v) { data.set(e, structuredClone(v)) }, createOrReplace(e,v) { this.create(e,v) },
    get(e) { return data.get(e) }, getMutable(e) { this.writes++; return data.get(e) } }
}
const ecs = { engine: { PlayerEntity: 1, addEntity: () => nextEntity++, addSystem() {} } }
for (const n of ['Transform','AudioSource','GltfContainer','GltfNodeModifiers','Animator','VisibilityComponent']) ecs[n] = component()
ecs.AudioSource.playSound = (e, clip) => sounds.push(clip)
ecs.Animator.playSingleAnimation = (e,n,reset) => { for(const s of ecs.Animator.getMutable(e).states) { s.playing=s.clip===n;s.shouldReset=reset } }
const V = { create:(x=0,y=0,z=0)=>({x,y,z}), add:(a,b)=>V.create(a.x+b.x,a.y+b.y,a.z+b.z),subtract:(a,b)=>V.create(a.x-b.x,a.y-b.y,a.z-b.z),scale:(a,s)=>V.create(a.x*s,a.y*s,a.z*s), length:(a)=>Math.hypot(a.x,a.y,a.z),normalize:(a)=>V.scale(a,1/V.length(a)),dot:(a,b)=>a.x*b.x+a.y*b.y+a.z*b.z }
const math = {Vector3:V, Quaternion:{fromEulerDegrees:()=>({x:0,y:0,z:0,w:1})},Color3:{create:(r,g,b)=>({r,g,b})},Color4:{create:(r,g,b,a)=>({r,g,b,a})}}
const flashlight = {on:true,litFor:0,dead:0,dying:0,flicker:0}
const cabin = {inside:false,visits:0,windowCaptionVisit:0,lampFlicker:0}
const layout = {spawn:[4,4],cabin:{windows:[{x:20,z:13}],bulb:{x:20,z:15},door:{x:20,z:14}}}
const stubs = {
 '@dcl/sdk/ecs':ecs, '@dcl/sdk/math':math, '~system/RestrictedActions':{movePlayerTo(){}},
 '../../htn-planner/htn/planner':{PlanRunner:class{}},'../../htn-planner/htn/world-state':{WorldState:class{}},'../../htn-planner/htn/atom':{sym:v=>v},'./mothman.htn':{mothmanDomain:{}},
 '../../config':{bounds:{w:192,d:192},bands:{near:2.8,mid:9,far:18},roostSpot:()=>({x:20,z:20,top:7.5})},
 '../../flashlight':{flashlight,beamHits:()=>true,cameraRay:()=>({origin:V.create(20,1.6,10),forward:V.create(0,0,1)}),failLight(){}},
 '../../telepathy':{telepathy:{done:false},startTelepathy(){},hud:{},showCaption(){},showHint(){},closeDocument(){},docOpenFor:()=>-1,captionsPending:()=>0},
 '../../audio':{setLoop(){},loopSound:()=>999},'../../cabin':{cabin,setLamp(){}},'../../layout':{layout},'../../objectives':{setObjective(){}},'../../script':{CAPTIONS:{},HINTS:{},OBJECTIVES:{window:[]},DEATHS:{}}
}
const cache={}
function load(name) {
 if(cache[name]) return cache[name]
 const file=path.resolve('src/npc/mothman',name+'.ts')
 const js=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText
 const module={exports:{}}
 const requireMock=n=>{if(n in stubs)return stubs[n];if(n==='./body'||n==='./animations')return load(n.slice(2));throw Error('Unmocked '+n)}
 vm.runInNewContext(js,{module,exports:module.exports,require:requireMock,console,Math},{filename:file})
 return cache[name]=module.exports
}
const {MOTHMAN_CLIPS}=load('animations');const {createMothmanBody}=load('body')
const b=createMothmanBody(V.create(20,0,20));let states=ecs.Animator.get(b.model).states
assert.equal(states.length,15)
assert.equal(states.filter(s=>s.playing)[0].clip,'idle_ground')
for(const s of states)assert.equal(s.loop,MOTHMAN_CLIPS[s.clip].loop)
b.setClip('idle_fly');b.updateAnimation(.09);assert.ok(Math.abs(states.reduce((a,s)=>a+s.weight,0)-1)<1e-6)
b.setClip('hover_menacing');b.updateAnimation(.18);assert.equal(states.filter(s=>s.playing).length,1)
assert.equal(states.find(s=>s.clip==='hover_menacing').weight,1)
const writes=ecs.Animator.writes;b.setClip('hover_menacing');b.updateAnimation(.5);assert.equal(ecs.Animator.writes,writes)
b.setClip('screech',true);b.updateAnimation(.2);states.find(s=>s.clip==='screech').playing=false;assert.equal(b.clipFinished('screech'),true)
b.setClip('screech',true);assert.equal(b.clipFinished('screech'),false);assert.equal(states.find(s=>s.clip==='screech').shouldReset,true)
b.setEyes(3);assert.equal(ecs.GltfNodeModifiers.get(b.model).modifiers[0].material.material.pbr.emissiveIntensity,3)
const {MothmanHost,story}=load('host');ecs.Transform.create(1,{position:V.create(20,1.6,10)});const host=new MothmanHost()
const current=()=>ecs.Animator.get(host.body.model).states.find(s=>s.playing&&s.clip===hostClip()).clip
function hostClip(){const st=ecs.Animator.get(host.body.model).states;return st.find(s=>s.playing&&s.weight===0)?.clip??st.filter(s=>s.playing).sort((a,b)=>b.weight-a.weight)[0].clip}
function start(n,args=[]){const e=host.makeExecutor(n,args);e.start();host.body.updateAnimation(.2);return e}
function place(x,y,z){ecs.Transform.getMutable(host.body.root).position=V.create(x,y,z)}
place(20,4,12.8);let e=start('!approach',['near']);assert.equal(e.update(.01),'running');assert.ok(host.me().y>3)
place(20,.05,12.8);assert.equal(e.update(.1),'running');host.body.updateAnimation(.2);assert.equal(current(),'land')
for(let i=0;i<17;i++)e.update(.1)
host.body.updateAnimation(.2);assert.equal(current(),'idle_ground');assert.equal(host.airborne,false)
place(20,.05,19);e=start('!approach',['mid']);assert.equal(e.update(.01),'running');assert.ok(host.me().y<1.2)
story.phase='revealed';start('!hover',[2]);assert.equal(current(),'hover_menacing')
story.phase='ignorant';start('!wait',[2]);const idle1=current();start('!wait',[2]);assert.notEqual(current(),idle1)
start('!lunge');assert.equal(current(),'lunge');assert.equal(MOTHMAN_CLIPS.lunge.loop,false)
place(20,.05,13);e=start('!window',[5]);e.update(.1);host.body.updateAnimation(.2);assert.equal(current(),'land');for(let i=0;i<17;i++)e.update(.1);host.body.updateAnimation(.2);assert.equal(current(),'window_stare')
place(20,.05,12.4);e=start('!bang');e.update(.01);host.body.updateAnimation(.2);assert.equal(current(),'door_bang')
e=start('!rise');assert.equal(current(),'takeoff');for(let i=0;i<22;i++)e.update(.05);host.body.updateAnimation(.2);assert.equal(current(),'hover_menacing')
start('!speak');assert.equal(current(),'telepathy')
console.log('PASS: 15 clip registrations, crossfades, one-shot restart/completion, eyeshine, altitude-aware landing, idle variants and 8 behavior transitions')
