"""Playtest sem UI e sem saves pessoais: python tools/playthrough_adventure.py 100."""
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from count_queen.adventure import Adventure


def decide(g, policy):
    s=g.s; phase=s['phase']; p=g.p
    if phase=='juramento': return 'juramento',{'valor':policy.choice(s['offers'])}
    if phase=='mapa':
        options=[n for n in s['maps'][s['region']] if g.possible_node(n)]
        return 'no',{'valor':policy.choice(options)['id']}
    if phase=='encontro': return 'entrar',{}
    if phase=='loja':
        shop=s['shop']; affordable=[k for k in shop['offers'] if k not in p['itens'] and g.shop_price(k)<p['fichas']-60]
        if len(shop['bought'])<2 and affordable:return 'comprar',{'valor':policy.choice(affordable)}
        return 'sair',{}
    if phase=='oficina':
        unmarked=[c for c in p['deck']['cards'].values() if not c['marca'] and not c['temporaria'] and c['id']!=p['reserved']]
        if unmarked:return 'marcar',{'carta':policy.choice(unmarked)['id'],'valor':policy.choice(['real','dourada','quebradica','maldita'])}
        return 'sair',{}
    if phase in ('evento','refugio','sacrario'):
        options=[o['id'] for o in g.public()['options'] if o.get('enabled',True)]
        if phase=='refugio':return 'escolha',{'valor':'reserva'}
        if p['fichas']<30:options=[x for x in options if x not in ('pacto','caridade','pagar','estudar')]
        if p['prestigio']<5:options=[x for x in options if x!='favor']
        return 'escolha',{'valor':policy.choice(options)}
    if phase=='recompensa':return 'reliquia',{'valor':policy.choice(s['offers'])}
    if phase=='conclusao':
        r=s['result']
        if r['retry'] and p['fichas']>=r['cost']:return 'revanche',{}
        return 'seguir',{}
    if phase=='contrato':return 'contrato',{'valor':policy.choice(s['offers'])}
    if phase=='cobranca':return 'cobranca',{'valor':'prestigio'}
    if phase=='cobranca_real':return 'cobranca_real',{'valor':policy.choice(s['offers'])}
    if phase=='consagrar':return 'consagrar',{'valor':policy.choice(p['juramentos'])}
    if phase=='destino':return 'destino',{'valor':policy.choice(['governar','usurpar'])}
    if phase=='pedagio':return 'pedagio',{'valor':'revelar'}
    if phase=='aposta':return 'apostar',{'valor':max(1,min(10,int(p['fichas'])))}
    if phase=='seguro':return 'recusar_seguro',{}
    if phase=='revelacao':return ('cetro' if g.total(g.b['dealer'])>=17 else 'liquidar'),{}
    if phase=='ultima_palavra':return ('comprar_final' if g.total(g.b['hands'][0])<17 else 'aceitar_resultado'),{}
    if phase=='resultado':return 'continuar',{}
    if phase=='oraculo':
        hand=g.b['hands'][g.b['current']]
        scores=[g.total({**hand,'cards':hand['cards']+[c]}) for c in g.b['choices']]
        i=max(range(len(scores)),key=lambda i:scores[i] if scores[i]<=g.b['limit'] else -scores[i])
        return 'escolher',{'valor':i}
    if phase=='jogando':
        b=g.b; hand=b['hands'][b['current']]; score=g.total(hand); actions=g.available()
        if 'guardar' in actions and score>=18:return 'guardar',{}
        if 'transferir' in actions and score>=17:return 'transferir',{'carta':hand['cards'][-1]['id'],'destino':b['current']+1}
        if 'coroa' in actions:return 'coroa',{'valor':max(1,min(11,b['limit']-score))}
        if 'bencao' in actions and 12<=score<18:return 'bencao',{}
        if 'brasa' in actions and score<14:return 'brasa',{}
        if 'dividir' in actions and hand['cards'][0]['valor'] in ('A','8'):return 'dividir',{}
        if 'dobrar' in actions and score in (10,11):return 'dobrar',{}
        if b.get('peek') and score+min(10,11 if b['peek']['valor']=='A' else int(b['peek']['valor']) if b['peek']['valor'].isdigit() else 10)>b['limit']:return 'parar',{}
        return ('pedir' if 'pedir' in actions and score<b['limit']-4 else 'parar'),{}
    raise AssertionError(f'Unhandled phase: {phase}')


def play(seed):
    g=Adventure(seed); g.s['unlocks']=['origem_herdeiro','origem_exilada','origem_trapaceiro']; g.new('Viajante','m',['viajante','herdeiro','exilada','trapaceiro'][seed%4]); policy=random.Random(seed)
    phases=Counter()
    for step in range(2000):
        phases[g.s['phase']]+=1
        if g.s['phase']=='fim':return g,phases
        action,data=decide(g,policy)
        g.interact(action,data)
        g.public()
        if step%13==0:
            payload=json.loads(json.dumps(g.export()))
            restored=Adventure();restored.restore(payload)
            assert restored.public()==g.public(),f'Reload mismatch at {g.s["phase"]}'
            g=restored
    raise AssertionError(f'Jornada presa: seed {seed}, {g.s["phase"]}')


if __name__=='__main__':
    runs=int(sys.argv[1]) if len(sys.argv)>1 else 100
    outcomes=Counter();phases=Counter()
    for seed in range(runs):
        game,visited=play(seed)
        outcomes['vitoria' if game.s['victory'] else 'derrota_regiao_'+str(game.s['region']+1)]+=1
        phases.update(visited)
    print(json.dumps({'jornadas':runs,'resultados':outcomes,'fases_exercitadas':phases},ensure_ascii=False,indent=2))
