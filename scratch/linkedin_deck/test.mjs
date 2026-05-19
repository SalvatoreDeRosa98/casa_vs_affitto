import { Presentation, PresentationFile, column, row, text, panel, fill, hug, fixed, wrap, grow, rule, shape, layers } from '@oai/artifact-tool';
const p = Presentation.create({ slideSize: { width: 1920, height: 1080 } });
const s = p.slides.add();
s.compose(
  column({name:'root', width: fill, height: fill, padding: 80, gap: 20}, [
    text('Test title', {name:'title', width: wrap(1000), height: hug, style:{fontSize:80,bold:true,color:'#111827'}}),
    row({name:'row', width: fill, height: grow(1), gap: 32}, [
      panel({name:'p1', width: grow(1), height: fill, padding: 30, fill:'#EAF3FF', borderRadius:8}, text('Panel text', {width: fill, height: hug, style:{fontSize:40,color:'#0A66C2',bold:true}})),
      panel({name:'p2', width: grow(1), height: fill, padding: 30, fill:'#111827', borderRadius:8}, text('Dark panel', {width: fill, height: hug, style:{fontSize:40,color:'#fff',bold:true}}))
    ])
  ]),
  {frame:{left:0,top:0,width:1920,height:1080}, baseUnit:8}
);
const pptx = await PresentationFile.exportPptx(p);
await pptx.save('scratch/linkedin_deck/test.pptx');
const png = await s.export({format:'png'});
await png.save('scratch/linkedin_deck/test.png');
console.log('ok');
