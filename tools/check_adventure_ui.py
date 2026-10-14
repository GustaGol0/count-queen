"""QA opcional: exige Playwright e Chromium instalados. Não altera saves pessoais."""
import copy
import json
import shutil
import sys
import tempfile
import threading
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from count_queen.adventure import Adventure, AdventureMesa
from count_queen.web import criar_servidor
from playwright.sync_api import sync_playwright, expect


def sample():
    g=Adventure(12);g.new('Áurea','m');g.interact('juramento',{'valor':g.s['offers'][0]})
    g.p.update(fichas=800,prestigio=42,juramentos=['fortuna','dobrar','sete','estrada'],itens=['forca_sete','bussola_contrabandista'])
    return g


def main():
    artifacts=Path(tempfile.mkdtemp(prefix='count-queen-ui-'))
    with tempfile.TemporaryDirectory() as temp:
        mesa=AdventureMesa(Path(temp)/'save.json',seed=8)
        server=criar_servidor(mesa,port=0)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        url=f'http://127.0.0.1:{server.server_port}'
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
                page=browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
                errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                page.goto(url);page.fill('#name','Áurea');page.select_option('#gender','m');page.locator('#new-game-form button').click()
                expect(page.locator('#welcome')).not_to_be_visible()
                expect(page.locator('.choice-card')).to_have_count(3)
                expect(page.locator('.oath-contract')).to_have_count(3)
                page.screenshot(path=str(artifacts/'juramentos.png'),full_page=True)
                page.locator('.choice-card button').first.click()
                expect(page.locator('.map-board')).to_be_visible()
                page.screenshot(path=str(artifacts/'mapa.png'),full_page=True)
                before=page.request.get(url+'/api/estado').json();page.reload();expect(page.locator('.map-board')).to_be_visible()
                assert before==page.request.get(url+'/api/estado').json()
                for width in [390,768,1024]:
                    page.set_viewport_size({'width':width,'height':950})
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'Map overflow {width}'
                    page.screenshot(path=str(artifacts/f'mapa-{width}.png'),full_page=True)
                page.set_viewport_size({'width':1440,'height':1000})
                page.locator('.map-node.available button').first.click();expect(page.get_by_role('button',name='Entrar no encontro')).to_be_visible()
                page.get_by_role('button',name='Entrar no encontro').click()
                # Conferência de todas as telas da máquina de estados com fixtures isoladas.
                cases={}
                for kind in ['loja','oficina','evento','refugio','sacrario']:
                    g=sample();g.enter({'type':kind});cases[kind]=g.export()
                g=sample();g.start_battle('boss','ferrugem');g.end_encounter(True);cases['recompensa']=g.export()
                g=sample();g.start_battle('boss','cobrador');cases['contrato']=g.export()
                g=sample();g.start_battle('boss','ferrugem');g.start_round(10);cases['combate']=g.export()
                g=sample();g.s.update(region=3,king_style='dobras',king_face='7');g.start_battle('boss','rei');g.b.update(act=2);g.s.update(phase='cobranca_real',offers=['dobrar','sete']);cases['cobranca-real']=g.export()
                g.s['phase']='consagrar';cases['consagrar']=g.export()
                g.s['phase']='destino';cases['destino']=g.export()
                g.s['phase']='pedagio';cases['pedagio']=g.export()
                g=sample();g.start_battle('boss','cinzas');g.end_encounter(False);cases['revanche']=g.export()
                g=sample();g.finish(False,'Uma nova lenda espera.');cases['fim']=g.export()
                for label,data in cases.items():
                    with mesa.lock:mesa.game.restore(data)
                    page.goto(url);expect(page.locator('#player-name')).to_have_text('Áurea')
                    page.screenshot(path=str(artifacts/f'{label}.png'),full_page=True)
                    page.set_viewport_size({'width':390,'height':950})
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'Overflow: {label}'
                    if label in ('combate','destino','recompensa'):page.screenshot(path=str(artifacts/f'{label}-390.png'),full_page=True)
                    page.set_viewport_size({'width':1440,'height':1000})
                # Aquisição real: quatro raridades, fechamento e sem repetir ao recarregar.
                from count_queen.content import RELICS
                assert set(page.evaluate('Object.keys(sigils)')) == set(RELICS)
                for rarity in ['comum','incomum','raro','mitico']:
                    g=sample();g.start_battle('boss','ferrugem');g.end_encounter(True)
                    key=next(k for k,v in RELICS.items() if v['raridade']==rarity and k not in g.p['itens'])
                    g.s['offers']=[key]
                    with mesa.lock:mesa.game.restore(g.export())
                    page.goto(url);page.emulate_media(reduced_motion='no-preference')
                    page.get_by_role('button',name='Escolher',exact=True).click()
                    expect(page.locator('#loot-dialog')).to_be_visible()
                    assert rarity in page.locator('#loot-dialog').get_attribute('class')
                    assert key in page.request.get(url+'/api/estado').json()['player']['itens']
                    page.locator('#loot-dialog .loot-art').evaluate('(el) => Promise.all(el.getAnimations().map(a => a.finished))')
                    page.screenshot(path=str(artifacts/f'loot-{rarity}.png'))
                    page.keyboard.press('Escape');expect(page.locator('#loot-dialog')).not_to_be_visible()
                    page.reload();expect(page.locator('#loot-dialog')).not_to_be_visible()
                page.emulate_media(reduced_motion='reduce')
                if page.evaluate('document.fullscreenEnabled'):
                    page.locator('#fullscreen-button').click()
                    expect(page.locator('#fullscreen-button')).to_have_attribute('aria-pressed','true')
                    page.locator('#fullscreen-button').click()
                    expect(page.locator('#fullscreen-button')).to_have_attribute('aria-pressed','false')
                # Serviço real de oficina, loja e inspeção do baralho.
                with mesa.lock:mesa.game.restore(cases['oficina'])
                page.goto(url);page.locator('#workshop-form').wait_for();page.select_option('#work-kind','transformar');page.select_option('#work-rank','7');page.get_by_role('button',name='Confirmar alteração').click();expect(page.locator('.map-board')).to_be_visible()
                with mesa.lock:mesa.game.restore(cases['loja'])
                page.goto(url);page.locator('.shop-grid .primary').first.click()
                expect(page.get_by_role('button',name='Adquirida',exact=True)).to_be_visible()
                expect(page.locator('#loot-dialog')).to_be_visible()
                page.locator('#loot-close').click()
                page.locator('#deck-button').click();expect(page.locator('.deck-grid')).to_be_visible();page.get_by_role('button',name='Fechar janela').click()
                page.locator('#inventory-button').click();expect(page.get_by_role('heading',name='Relíquias & juramentos')).to_be_visible();page.get_by_role('button',name='Fechar janela').click()
                with mesa.lock:mesa.game.restore(cases['destino'])
                page.goto(url);page.get_by_role('button',name='Usurpar',exact=True).click();expect(page.locator('#bet-form')).to_be_visible();page.locator('#bet').fill('10');page.locator('#deal').click();expect(page.locator('#crown-form')).to_be_visible();page.locator('#crown-value').fill('1');page.get_by_role('button',name='Fixar valor').click()
                assert not errors,errors
                print(json.dumps({'browser_errors':errors,'screens':list(cases),'save_survives_reload':True,'screenshots':str(artifacts)},ensure_ascii=False))
                browser.close()
        finally:
            server.shutdown();server.server_close();thread.join()

if __name__=='__main__':main()
