"""Recurring encounters. Choices and consequences are stored in the journey."""
STORY_NAMES = {'credor': 'A dívida da família', 'falsificadora': 'Tinta que não seca',
               'mensageira': 'Cartas para o exílio'}


def select_story(g):
    region = g.s['region']
    stories = g.p['stories']
    available = [k for k in STORY_NAMES if stories.get(k, {}).get('stage', 0) < 3
                 and stories.get(k, {}).get('next_region', 0) <= region]
    favorite = {'herdeiro':'credor', 'exilada':'mensageira', 'trapaceiro':'falsificadora'}.get(g.p['origem'])
    if favorite in available:
        return favorite
    continuing = [k for k in available if stories.get(k, {}).get('stage', 0)]
    if continuing:
        return g.rng.choice(continuing)
    return g.rng.choice(available) if available and g.rng.random() < .65 else None


def scene(g):
    key = g.s['event'].removeprefix('historia:')
    progress = g.p['stories'].get(key, {})
    stage = progress.get('stage', 0)
    debt = g.p['origin_debt']
    options = []
    def option(id, name, text, cost=0, prestige=0):
        options.append({'id':id, 'nome':name, 'descricao':text, 'cost':cost, 'prestige':prestige,
                        'enabled':g.p['fichas'] >= cost and g.p['prestigio'] >= prestige})
    if key == 'falsificadora':
        texts = ['Lia precisa de uma testemunha para passar pelo posto da fronteira.',
                 'Lia reconhece você no mercado. Dentro do casaco, carrega uma carta feita à mão.',
                 'O sete falso foi rastreado até Lia. O Cobrador reuniu provas; ela pede ajuda para desaparecer.' if progress.get('choice')=='carta' else
                 'Sem os registros, os guardas perderam a pista de Lia. Ela pede ajuda para completar a fuga.']
        if stage == 0:
            option('ajudar','Pagar sua passagem','Pague 20 fichas. Lia voltará a procurar você.',20)
            option('denunciar','Entregar seus documentos','Ganhe 4 de prestígio. Encerra esta história.')
        elif stage == 1:
            option('carta','Aceitar o sete dourado','Adicione um 7 Dourado ao descarte. As autoridades podem descobrir.')
            options[-1]['enabled'] = len(g.p['deck']['cards']) < 80
            option('limpar','Apagar os registros','Pague 20 fichas e ganhe 3 de prestígio. Lia prepara a fuga.',20)
        else:
            cost = 20 if g.p['origem']=='trapaceiro' else 30
            option('salvar','Financiar a fuga',f'Pague {cost} fichas e receba Bolso Falso; se já possui, receba 45 fichas.',cost)
            option('entregar','Entregar Lia','Receba 80 fichas e perca 5 de prestígio. Escolhe Tirania.')
    elif key == 'credor':
        texts = [f'Baltasar abre o livro da sua família. Dívida atual: {debt:g} fichas.',
                 f'Baltasar reservou uma cadeira. Sua dívida agora é de {debt:g} fichas.',
                 f'O livro chega à corte. Restam {debt:g} fichas para encerrar a conta.']
        if not debt and stage:
            option('recibo','Exigir o recibo','Dívida quitada: receba 25 fichas e 3 de prestígio. Encerra a história.')
        elif stage == 0:
            option('emprestar','Aceitar o adiantamento','Receba 60 fichas; acrescente 90 à dívida. 25% do lucro das vitórias paga essa dívida.')
            if debt:
                option('quitar','Quitar a dívida',f'Pague {debt:g} fichas. A cobrança retorna apenas para entregar o recibo.',debt)
        else:
            option('quitar','Pagar o saldo',f'Pague {debt:g} fichas. Ganhe 3 de prestígio e encerre a conta.',debt)
            option('nome','Usar sua influência','Gaste 8 de prestígio para cancelar a dívida. Encerra a conta.',prestige=8)
            option('adiar','Assinar uma prorrogação','A dívida aumenta em 20 fichas. A retenção de 25% do lucro continua.')
    else:
        betrayed = progress.get('choice') == 'vender'
        texts = ['Uma mensageira procura alguém que conheça a estrada do exílio.',
                 'A mensageira retorna com uma carta selada. Há uma recompensa por esse nome.',
                 'Guardas interceptaram a correspondência. A mensageira sabe quem a vendeu.' if betrayed else
                 'A última carta traz um selo real. Seu auxílio chegou a quem precisava.']
        if stage == 0:
            option('escoltar','Escoltar a mensageira','Pague 15 fichas. Ganhe uma bênção para o próximo encontro.',15)
        elif stage == 1:
            option('proteger','Proteger o nome','Pague 20 fichas e ganhe 4 de prestígio. Escolhe Nobreza.',20)
            option('vender','Vender a informação','Receba 60 fichas e perca 4 de prestígio. Escolhe Tirania; haverá consequências.')
        elif betrayed:
            option('reparar','Comprar a liberdade dela','Pague 25 fichas e ganhe 2 de prestígio.',25)
            option('abandonar','Abandoná-la','Perca 6 de prestígio. Encerra esta história.')
        else:
            option('legado','Receber o legado','Ganhe Última Palavra; se já possui, receba 60 fichas. Escolhe Nobreza.')
    # The final betrayal has an affordable exit, but cannot bypass its consequence.
    if not (key=='mensageira' and stage==2 and progress.get('choice')=='vender'):
        option('seguir','Seguir viagem','Encerra esta história. Dívidas existentes continuam sendo descontadas dos lucros.' if key=='credor' else 'Encerra esta história sem outra alteração.')
    return {'id':key, 'title':STORY_NAMES[key], 'chapter':stage+1, 'text':texts[stage], 'options':options}


def resolve(g, value):
    current = scene(g)
    option = next((o for o in current['options'] if o['id']==value), None)
    from .adventure import require
    require(option and option['enabled'], 'Recursos insuficientes para esta escolha.')
    p = g.p
    p['fichas'] -= option['cost']
    p['prestigio'] -= option['prestige']  # Voluntary spending, not a penalty.
    key = current['id']
    progress = p['stories'].setdefault(key, {'stage':0})
    stage = progress['stage']
    def relic(id, duplicate):
        if id in p['itens']: p['fichas'] += duplicate
        else: p['itens'].append(id)
    if key=='falsificadora':
        if value=='denunciar': g.prestige(4)
        if value=='carta': g.add_card('7','dourada')
        if value=='limpar': g.prestige(3)
        if value=='salvar': relic('bolso_falso',45)
        if value=='entregar': p['fichas']+=80;g.prestige(-5);p['caminho']='tirania'
    elif key=='credor':
        if value=='emprestar': p['fichas']+=60;p['origin_debt']+=90
        if value in ('quitar','nome'): p['origin_debt']=0
        if value=='quitar' and stage: g.prestige(3)
        if value=='adiar': p['origin_debt']+=20
        if value=='recibo': p['fichas']+=25;g.prestige(3)
    else:
        if value=='escoltar': p['prepared']=True
        if value=='proteger': g.prestige(4);p['caminho']='nobreza'
        if value=='vender': p['fichas']+=60;g.prestige(-4);p['caminho']='tirania'
        if value=='reparar': g.prestige(2)
        if value=='abandonar': g.prestige(-6)
        if value=='legado': relic('ultima_palavra',60);p['caminho']='nobreza'
    end = value in ('seguir','denunciar','recibo','nome') or (key=='credor' and value=='quitar' and stage>0)
    progress.update(stage=3 if end else stage+1, next_region=g.s['region']+1, choice=value)
    p['story_log'].append({'title':current['title'], 'chapter':current['chapter'], 'choice':option['nome'], 'consequence':option['descricao']})
    g.s.update(phase='mapa', notice=f'{current["title"]}: {option["nome"]}.')
