"""Browser acceptance for the five connected journey features; isolated save only."""
import json
import shutil
import sys
import tempfile
import threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from count_queen.adventure import Adventure, AdventureMesa
from count_queen.web import criar_servidor
from check_adventure_ui import arranged, sample
from playwright.sync_api import sync_playwright, expect


def main():
    artifacts=Path(tempfile.mkdtemp(prefix='count-queen-expansion-'))
    with tempfile.TemporaryDirectory() as temp:
        mesa=AdventureMesa(Path(temp)/'save.json',seed=8)
        server=criar_servidor(mesa,port=0)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True)
                page=browser.new_page(viewport={'width':1366,'height':768},reduced_motion='reduce')
                errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                def show(g):
                    with mesa.lock:mesa.game.restore(g.export())
                    page.goto(url);page.wait_for_function('state!==null')
                def command(name):
                    page.get_by_role('button',name=name,exact=True).click()
                    page.wait_for_function('!busy')
                def state():return page.request.get(url+'/api/estado').json()
                page.goto(url)
                expect(page.locator('.origin-card')).to_have_count(4)
                expect(page.locator('input[name=origin]:disabled')).to_have_count(3)
                for width in (320,390,1366):
                    page.set_viewport_size({'width':width,'height':768})
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
                    page.screenshot(path=str(artifacts/f'origens-{width}.png'),full_page=True)
                for origin in ('herdeiro','exilada','trapaceiro'):
                    g=Adventure(8);g.unlock(origin);show(g)
                    page.locator(f'input[value={origin}]').check();page.fill('#name','Áurea')
                    page.locator('#new-game-form button').click()
                    expect(page.locator('#welcome')).not_to_be_visible()
                    assert state()['player']['origem']==origin
                    if page.locator('#loot-dialog').is_visible():command('Continuar')
                page.set_viewport_size({'width':1366,'height':768})
                g=Adventure(8)
                for origin in ('herdeiro','exilada','trapaceiro'):g.unlock(origin)
                show(g);page.screenshot(path=str(artifacts/'origens-desbloqueadas.png'))
                assert page.locator('#new-game-form button').bounding_box()['y']+page.locator('#new-game-form button').bounding_box()['height']<768
                g=arranged(['5','5','7','A','2','3'],['10','7','10','7'],['bolso_falso'])
                show(g);command('Pedir carta [P]');command('Guardar carta · Bolso Falso')
                expect(page.locator('#effect-feed')).to_contain_text('Bolso Falso')
                before=state();page.reload();page.wait_for_function('state!==null');assert state()==before
                command('Parar [S]');expect(page.locator('#result')).to_be_visible();command('Continuar')
                expect(page.locator('#status')).to_contain_text('Bolso Falso abrirá com 7')
                g=arranged(['8','8','2','3','4'],['10','7'],['balanca_carrasco'])
                show(g);command('Dividir');expect(page.locator('#balance-form')).to_be_visible()
                page.locator('#balance-card').select_option(index=1);command('Transferir carta')
                expect(page.locator('#balance-form')).to_have_count(0)
                assert [len(h['cards']) for h in state()['battle']['hands']]==[1,3]
                g=arranged(['7','7','6'],['10','8','3'],['ultima_palavra'])
                show(g);command('Parar [S]');expect(page.locator('#status')).to_contain_text('Última Palavra')
                page.screenshot(path=str(artifacts/'ultima-palavra.png'),full_page=True)
                command('Comprar última carta');expect(page.locator('#result')).to_be_visible()
                page.locator('#result-breakdown summary').click();expect(page.locator('#calculation')).to_contain_text('Lucro recebido: 10')
                g=arranged(['7','10'],['10','6','10'],['forca_sete','broche_prudencia'])
                g.p['juramentos']=['sete'];g.p['origin_debt']=120
                show(g);command('Parar [S]');expect(page.locator('#effect-feed')).to_contain_text('Força do Sete')
                page.locator('#result-breakdown summary').click()
                expect(page.locator('#calculation')).to_contain_text('Broche da Prudência')
                page.screenshot(path=str(artifacts/'combinacoes.png'),full_page=True)
                # Actual sequential story choices, with reload and region transitions.
                g=sample();g.s.update(phase='evento',event='historia:mensageira');show(g)
                page.locator('.story-choice').filter(has=page.get_by_role('heading',name='Escoltar a mensageira')).get_by_role('button').click()
                page.wait_for_function('!busy && state.phase==="mapa"')
                assert state()['player']['prepared']
                with mesa.lock:
                    mesa.game.s.update(phase='evento',event='historia:mensageira',region=1)
                page.reload();page.locator('.story-choice').filter(has=page.get_by_role('heading',name='Vender a informação')).get_by_role('button').click()
                page.wait_for_function('!busy && state.phase==="mapa"')
                with mesa.lock:mesa.game.s.update(phase='evento',event='historia:mensageira',region=2)
                page.reload();expect(page.locator('#adventure-panel')).to_contain_text('sabe quem a vendeu')
                expect(page.get_by_role('heading',name='Receber o legado')).to_have_count(0)
                page.screenshot(path=str(artifacts/'historia.png'),full_page=True)
                page.locator('#journey-button').click()
                expect(page.locator('#info-content')).to_contain_text('Vender a informação')
                page.keyboard.press('Escape')
                for boss in ('ferrugem','sinos','gemeas','cobrador','cinzas','astronomo','rei'):
                    g=sample();g.s.update(king_style='equilibrio',king_face='7');g.start_battle('boss',boss)
                    if boss=='cobrador':g.interact('contrato',{'valor':g.s['offers'][0]})
                    g.start_round(10);show(g)
                    expect(page.locator('.boss-portrait')).to_be_visible()
                    page.screenshot(path=str(artifacts/f'boss-{boss}.png'),full_page=True)
                    for width in (320,390,768,1366):
                        page.set_viewport_size({'width':width,'height':768})
                        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),boss
                    if boss=='sinos':expect(page.locator('.bell-meter i')).to_have_count(7)
                command('Som: desligado');expect(page.locator('#sound-button')).to_have_attribute('aria-pressed','true')
                page.reload();expect(page.locator('#sound-button')).to_have_text('Som: ligado')
                command('Som: ligado');expect(page.locator('#sound-button')).to_have_text('Som: desligado')
                assert not errors,errors
                print(json.dumps({'browser_errors':errors,'origins':3,'tactical_relics':3,'bosses':7,'story_betrayal':True,'sound_toggle':True,'screenshots':str(artifacts)},ensure_ascii=False))
                browser.close()
        finally:server.shutdown();server.server_close()

if __name__=='__main__':main()
