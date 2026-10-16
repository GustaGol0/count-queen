"""Presentation acceptance: illustrated portraits, interleaved deal, payout and cleanup."""
import json
import tempfile
import threading
from pathlib import Path
from check_adventure_ui import sample, AdventureMesa, criar_servidor
from playwright.sync_api import sync_playwright, expect


def ready():
    g=sample();g.p.update(juramentos=['sete'],itens=['forca_sete','broche_prudencia'])
    def ordered(ranks):
        d=g.deck(ranks);d['draw']=list(reversed(list(d['cards'])))
        return d
    g.p['deck']=ordered(['7','10','2','3','4','5']*8)
    g.start_battle('boss','ferrugem');g.b['decks']['a']=ordered(['10','6','10']*12)
    return g.export()


def settle(page):
    page.evaluate('() => Promise.all([...liveAnimations].map(a=>a.finished.catch(()=>{})))')


def main():
    artifacts=Path(tempfile.mkdtemp(prefix='count-queen-atelier-'))
    with tempfile.TemporaryDirectory() as temp:
        mesa=AdventureMesa(Path(temp)/'save.json');mesa.game.restore(ready())
        server=criar_servidor(mesa,port=0);threading.Thread(target=server.serve_forever,daemon=True).start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True)
                context=browser.new_context(viewport={'width':1440,'height':900},record_video_dir=str(artifacts),record_video_size={'width':1440,'height':900})
                context.add_init_script('''window.motionCalls=[];const original=Element.prototype.animate;Element.prototype.animate=function(frames,options){motionCalls.push({id:this.id,cls:this.className,parent:this.parentElement?.id,frames,options});return original.call(this,frames,options)};''')
                page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                page.goto(url);expect(page.locator('#bet-form')).to_be_visible()
                response=page.request.get(url+'/portraits-atlas.png')
                assert response.status==200 and response.headers['content-type']=='image/png'
                assert response.body()[:8]==b'\x89PNG\r\n\x1a\n'
                page.evaluate("() => new Promise((resolve,reject)=>{const art=new Image();art.onload=resolve;art.onerror=reject;art.src='/portraits-atlas.png';})")
                expect(page.locator('.boss-portrait')).to_be_visible()
                assert 'portraits-atlas.png' in page.locator('.boss-portrait').evaluate('(e)=>getComputedStyle(e).backgroundImage')
                page.evaluate('window.firstPortrait=document.querySelector(".boss-portrait")')
                page.screenshot(path=str(artifacts/'mesa-pronta.png'))
                page.locator('#deal').click();expect(page.locator('#actions')).to_be_visible();settle(page)
                calls=page.evaluate('motionCalls')
                dealt=[c for c in calls if c['cls'].startswith('card') and c['frames'][0].get('opacity')==0]
                assert [c['parent'] for c in dealt]==['','dealer-cards','','dealer-cards']
                assert [c['options']['delay'] for c in dealt]==[0,115,230,345]
                assert page.evaluate('firstPortrait===document.querySelector(".boss-portrait")')
                assert any(c['cls']=='flying-chip' for c in calls)
                page.screenshot(path=str(artifacts/'mesa-ilustrada.png'))
                page.evaluate('motionCalls.length=0')
                page.get_by_role('button',name='Parar [S]',exact=True).click()
                expect(page.locator('#result')).to_be_visible();settle(page)
                calls=page.evaluate('motionCalls')
                assert sum(c['cls']=='victory-mote' for c in calls)==12
                assert sum(c['cls']=='flying-chip' for c in calls)==6
                assert any(c['cls']=='table-flare' for c in calls)
                assert any(c['cls']=='portrait-frame' for c in calls)
                assert any(c['cls'].startswith('relic ') for c in calls)
                expect(page.locator('.table-flare,.victory-mote,.flying-chip,.motion-card,.resource-change')).to_have_count(0)
                assert page.evaluate('liveAnimations.size===0 && motionLayers.size===0')
                page.screenshot(path=str(artifacts/'vitoria-ilustrada.png'))
                before=page.request.get(url+'/api/estado').json();page.reload();expect(page.locator('#result')).to_be_visible()
                assert page.evaluate('motionCalls.length')==0
                assert before==page.request.get(url+'/api/estado').json()
                for width,height in [(1366,768),(1024,768),(768,950),(390,844),(320,800)]:
                    page.set_viewport_size({'width':width,'height':height})
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
                    page.screenshot(path=str(artifacts/f'vitoria-{width}.png'),full_page=True)
                # Cancelling a win mid-effect must remove every temporary layer.
                with mesa.lock:mesa.game.restore(ready())
                page.reload();expect(page.locator('#bet-form')).to_be_visible()
                page.evaluate("async()=>{await act('apostar',10);await act('parar');}")
                page.emulate_media(reduced_motion='reduce')
                page.wait_for_function('liveAnimations.size===0 && motionLayers.size===0')
                expect(page.locator('.table-flare,.victory-mote,.flying-chip,.motion-card,.resource-change')).to_have_count(0)
                assert page.evaluate('document.getAnimations().filter(a=>a.playState==="running").length')==0
                page.evaluate('motionCalls.length=0');page.get_by_role('button',name='Continuar',exact=True).click();expect(page.locator('#bet-form')).to_be_visible()
                assert page.evaluate('motionCalls.length')==0
                # A rapid next action cancels queued payout visuals, preserving server revision.
                with mesa.lock:mesa.game.restore(ready())
                page.reload();expect(page.locator('#bet-form')).to_be_visible();page.emulate_media(reduced_motion='no-preference')
                page.evaluate("async()=>{await act('apostar',10);await act('parar');await act('continuar');}")
                expect(page.locator('#bet-form')).to_be_visible();settle(page)
                assert page.request.get(url+'/api/estado').json()['revisao']==3
                expect(page.locator('.table-flare,.victory-mote,.flying-chip,.motion-card,.resource-change')).to_have_count(0)
                assert not errors,errors
                video=page.video;context.close()
                print(json.dumps({'browser_errors':errors,'interleaved_deal':True,'illustration_loaded':True,'win_effects_and_cleanup':True,'reduced_motion':True,'screenshots':str(artifacts),'video':str(video.path())}))
                browser.close()
        finally:server.shutdown();server.server_close()

if __name__=='__main__':main()
