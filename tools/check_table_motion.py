"""Browser checks for real dealing, reveal, cancellation and reduced motion."""
import json
import tempfile
import threading
from pathlib import Path

from check_adventure_ui import AdventureMesa, criar_servidor, sample
from playwright.sync_api import sync_playwright, expect


def ready():
    g = sample()
    g.p.update(juramentos=[], itens=[])
    def ordered(ranks):
        d = g.deck(ranks)
        d['draw'] = list(reversed(list(d['cards'])))
        return d
    g.p['deck'] = ordered(['2', '3', '4', '5'] + ['6'] * 20)
    g.start_battle('mesa', 'mesa')
    g.b['decks'][g.b['active']] = ordered(['10', '7'] * 12)
    return g.export()


def settled(page):
    page.evaluate('() => Promise.all([...liveAnimations].map(a => a.finished.catch(() => {})))')


def main():
    artifacts = Path(tempfile.mkdtemp(prefix='count-queen-motion-'))
    with tempfile.TemporaryDirectory() as temp:
        mesa = AdventureMesa(Path(temp) / 'save.json', seed=8)
        mesa.game.restore(ready())
        server = criar_servidor(mesa, port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url = f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context(viewport={'width':1366,'height':768}, record_video_dir=str(artifacts), record_video_size={'width':1366,'height':768})
                context.add_init_script('''
                  window.motionCalls = [];
                  const original = Element.prototype.animate;
                  Element.prototype.animate = function(frames, options) {
                    motionCalls.push({id:this.id, cls:this.className, frames, options});
                    return original.call(this, frames, options);
                  };
                ''')
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                page.goto(url)
                expect(page.locator('#bet-form')).to_be_visible()
                assert page.evaluate('motionCalls.length') == 0
                page.locator('#deal').click()
                expect(page.locator('#actions')).to_be_visible()
                expect(page.locator('#player-hands .card')).to_have_count(2)
                settled(page)
                calls = page.evaluate('motionCalls')
                assert len([c for c in calls if c['cls'].startswith('card') and c['frames'][0].get('opacity') == 0]) == 4
                assert page.locator('#player-hands .card-value').all_text_contents() == ['2','3']
                assert page.locator('.card-value').first.evaluate('(e)=>getComputedStyle(e).fontFamily') == 'Arial, sans-serif'
                page.evaluate('motionCalls.length=0')
                page.get_by_role('button',name='Pedir carta [P]',exact=True).click()
                expect(page.locator('#player-hands .card')).to_have_count(3)
                settled(page)
                calls = page.evaluate('motionCalls')
                assert len([c for c in calls if c['cls'].startswith('card') and c['frames'][0].get('opacity') == 0]) == 1, 'Existing cards were dealt again'
                page.screenshot(path=str(artifacts/'numeros-legiveis.png'))
                page.evaluate('motionCalls.length=0')
                page.get_by_role('button',name='Parar [S]',exact=True).click()
                expect(page.locator('#result')).to_be_visible()
                settled(page)
                calls = page.evaluate('motionCalls')
                assert any('rotateY' in str(c['frames']) for c in calls), 'Hidden card did not flip'
                assert any(c['id']=='result' for c in calls)
                expect(page.locator('.motion-card,.resource-change')).to_have_count(0)
                saved = page.request.get(url+'/api/estado').json()
                page.reload()
                expect(page.locator('#result')).to_be_visible()
                assert page.evaluate('motionCalls.length') == 0, 'Reload replayed a completed round'
                assert saved == page.request.get(url+'/api/estado').json()
                page.get_by_role('button',name='Continuar',exact=True).click()
                expect(page.locator('#bet-form')).to_be_visible()
                settled(page)
                assert any('motion-card' in c['cls'] for c in page.evaluate('motionCalls'))
                # Changing the preference cancels active effects and removes clones.
                with mesa.lock: mesa.game.restore(ready())
                page.reload();expect(page.locator('#bet-form')).to_be_visible()
                page.evaluate("act('apostar', 10)")
                page.emulate_media(reduced_motion='reduce')
                page.wait_for_function('liveAnimations.size === 0 && motionLayers.size === 0')
                page.evaluate('motionCalls.length=0')
                page.get_by_role('button',name='Pedir carta [P]',exact=True).click()
                expect(page.locator('#player-hands .card')).to_have_count(3)
                assert page.evaluate('motionCalls.length') == 0
                # A second action during an animation still executes exactly once.
                page.emulate_media(reduced_motion='no-preference')
                before = page.request.get(url+'/api/estado').json()['revisao']
                page.evaluate("async () => { await act('pedir'); await act('parar'); }")
                expect(page.locator('#result')).to_be_visible()
                settled(page)
                assert page.request.get(url+'/api/estado').json()['revisao'] == before+2
                expect(page.locator('.motion-card,.resource-change')).to_have_count(0)
                assert not errors, errors
                video = page.video
                context.close()
                print(json.dumps({'browser_errors':errors,'animation_checks':'passed','screenshots':str(artifacts),'video':str(video.path())}))
                browser.close()
        finally:
            server.shutdown();server.server_close();thread.join()


if __name__ == '__main__':
    main()
